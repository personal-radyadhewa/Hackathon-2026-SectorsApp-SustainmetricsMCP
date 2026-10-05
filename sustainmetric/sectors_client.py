import asyncio
import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

import httpx
from dotenv import find_dotenv, load_dotenv

# Auto-load .env from working directory or parent directories
load_dotenv(find_dotenv(usecwd=True))

logger = logging.getLogger("sustainmetric.sectors_client")

CACHE_DIR_DEFAULT = Path(".cache/sectors")
FIXTURES_DIR = Path(__file__).parent / "data" / "fixtures"

TTL_FINANCIALS_SEC = int(os.getenv("CACHE_TTL_FINANCIALS_SEC", 7 * 86400))  # 7 days
TTL_NEWS_SEC = int(os.getenv("CACHE_TTL_NEWS_SEC", 86400))                  # 24 hours
TTL_SUBSECTORS_SEC = 30 * 86400                                             # 30 days
DEFAULT_MAX_CREDITS = 1000


class SectorsClient:
    """Async client for Sectors Financial API v2 with strict disk caching and credit quota protection."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        use_fixtures_fallback: bool = True,
        max_credits: Optional[int] = None,
    ):
        if api_key is not None:
            self.api_key = api_key if api_key != "" else None
        else:
            self.api_key = os.getenv("SECTORS_API_KEY")

        self.base_url = "https://api.sectors.app/v2"
        self.cache_dir = cache_dir or CACHE_DIR_DEFAULT
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_fixtures_fallback = use_fixtures_fallback
        self.max_credits = max_credits if max_credits is not None else int(os.getenv("SECTORS_MAX_CREDITS", str(DEFAULT_MAX_CREDITS)))
        self.quota_file = self.cache_dir / "quota.json"
        self.cache_hits_count = 0
        self._inflight_locks: dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._load_quota()

    def _load_quota(self) -> None:
        """Load persisted quota accounting from disk."""
        self.api_calls_count = 0
        if self.quota_file.exists():
            try:
                with open(self.quota_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.api_calls_count = int(data.get("api_calls_count", 0))
            except Exception as e:
                logger.warning(f"Error reading quota file {self.quota_file}: {e}")

    def _record_api_call(self) -> None:
        """Increment and persist quota usage to disk atomically."""
        self.api_calls_count += 1
        try:
            with open(self.quota_file, "w", encoding="utf-8") as f:
                json.dump({"api_calls_count": self.api_calls_count, "last_updated": time.time()}, f)
        except Exception as e:
            logger.warning(f"Error persisting quota usage: {e}")

    def _has_quota_available(self) -> bool:
        return self.api_calls_count < self.max_credits

    async def _get_key_lock(self, key: str) -> asyncio.Lock:
        async with self._global_lock:
            if key not in self._inflight_locks:
                self._inflight_locks[key] = asyncio.Lock()
            return self._inflight_locks[key]

    def _get_cache_path(self, cache_key: str) -> Path:
        hashed = hashlib.sha256(cache_key.encode("utf-8")).hexdigest()
        return self.cache_dir / f"{hashed}.json"

    def _read_cache(self, cache_key: str, ttl_seconds: int) -> Optional[dict[str, Any]]:
        path = self._get_cache_path(cache_key)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            cached_at = data.get("_cached_at", 0)
            if time.time() - cached_at > ttl_seconds:
                return None
            self.cache_hits_count += 1
            return data.get("payload")
        except Exception as e:
            logger.warning(f"Cache read error for {cache_key}: {e}")
            return None

    def _write_cache(self, cache_key: str, payload: Any) -> None:
        path = self._get_cache_path(cache_key)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"_cached_at": time.time(), "cache_key": cache_key, "payload": payload}, f)
        except Exception as e:
            logger.warning(f"Cache write error for {cache_key}: {e}")

    def _load_fixture(self, ticker: str) -> Optional[dict[str, Any]]:
        clean_sym = ticker.upper().replace(".JK", "")
        fixture_path = FIXTURES_DIR / f"{clean_sym}.json"
        if fixture_path.exists():
            with open(fixture_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    def _normalize_report_payload(self, raw_payload: dict[str, Any]) -> dict[str, Any]:
        """Normalize Sectors API v2 response structure into consistent overview & financials."""
        if not raw_payload:
            return {}

        payload = dict(raw_payload)
        raw_symbol = str(payload.get("symbol", "")).upper()
        symbol = raw_symbol.replace(".JK", "")
        payload["symbol"] = symbol
        company_name = payload.get("company_name") or payload.get("overview", {}).get("company_name", symbol)

        overview = dict(payload.get("overview", {}))
        overview["company_name"] = company_name
        overview["symbol"] = symbol
        if "sub_sector" in overview and "subsector" not in overview:
            overview["subsector"] = overview["sub_sector"]
        if "sub_industry" in overview and "industry" not in overview:
            overview["industry"] = overview["sub_industry"]
        if not overview.get("description"):
            sec = overview.get("sector") or overview.get("subsector") or "Indonesian Equities"
            overview["description"] = f"{company_name} is an IDX-listed company operating in {sec}."

        financials = dict(payload.get("financials", {}))

        # Check if financials contains historical series (Sectors API format)
        hf = financials.get("historical_financials")
        if isinstance(hf, list) and len(hf) > 0:
            sorted_hf = sorted(hf, key=lambda x: int(x.get("year") or 0))
            latest_hf = sorted_hf[-1]

            ocf = latest_hf.get("operating_cash_flow")
            if ocf is None:
                ocf = latest_hf.get("operating_pnl") or 0.0
            financials["operating_cash_flow"] = float(ocf or 0.0)

            capex = latest_hf.get("capital_expenditures")
            if capex is None:
                capex = latest_hf.get("realized_capital_goods_investment") or abs(latest_hf.get("investing_cash_flow") or 0.0)
            financials["capital_expenditures"] = float(capex or 0.0)

            rev = latest_hf.get("revenue") or latest_hf.get("interest_income") or 0.0
            financials["revenue"] = float(rev or 0.0)

            net_inc = latest_hf.get("earnings") or latest_hf.get("net_income") or latest_hf.get("earnings_before_tax") or 0.0
            financials["net_income"] = float(net_inc or 0.0)

            total_debt = latest_hf.get("total_debt") or latest_hf.get("total_liabilities") or 0.0
            financials["total_debt"] = float(total_debt or 0.0)

            cash = latest_hf.get("total_cash_and_due_from_banks") or latest_hf.get("cash_and_equivalents") or latest_hf.get("cash_only") or 0.0
            financials["cash_and_equivalents"] = float(cash or 0.0)

            ebitda = latest_hf.get("ebitda") or latest_hf.get("operating_pnl") or 0.0
            financials["ebitda"] = float(ebitda or 0.0)

            total_assets = latest_hf.get("total_assets") or 0.0
            financials["total_assets"] = float(total_assets or 0.0)

            # Ratios
            hr = financials.get("historical_financial_ratio")
            if isinstance(hr, list) and len(hr) > 0:
                sorted_hr = sorted(hr, key=lambda x: int(str(x.get("year") or "0")))
                latest_hr = sorted_hr[-1]
                roa_val = latest_hr.get("profitability", {}).get("roa")
                if roa_val is not None:
                    financials["roa_pct"] = round(float(roa_val) * 100.0, 2)

            if "roa_pct" not in financials:
                if financials["total_assets"] > 0:
                    financials["roa_pct"] = round((financials["net_income"] / financials["total_assets"]) * 100.0, 2)
                else:
                    financials["roa_pct"] = 0.0

            if financials["capital_expenditures"] > 0:
                financials["capex_coverage_ratio"] = round(financials["operating_cash_flow"] / financials["capital_expenditures"], 2)
            else:
                financials["capex_coverage_ratio"] = 2.0 if financials["operating_cash_flow"] > 0 else 0.0

            if financials["revenue"] > 0 and financials["capital_expenditures"] > 0:
                financials["capex_to_revenue_pct"] = round((financials["capital_expenditures"] / financials["revenue"]) * 100.0, 2)
            else:
                financials["capex_to_revenue_pct"] = 0.0

        for key in [
            "operating_cash_flow",
            "capital_expenditures",
            "revenue",
            "net_income",
            "total_debt",
            "cash_and_equivalents",
            "ebitda",
            "total_assets",
            "roa_pct",
            "capex_coverage_ratio",
            "capex_to_revenue_pct",
        ]:
            if financials.get(key) is None:
                financials[key] = 0.0

        payload["overview"] = overview
        payload["financials"] = financials
        return payload

    async def get_company_report(
        self, ticker: str, sections: list[str] = ["overview", "financials"]
    ) -> dict[str, Any]:
        """Fetch company financial and profile report with disk caching and deduplication."""
        sec_param = ",".join(sorted(sections))
        cache_key = f"company_report:{ticker.upper()}:{sec_param}"
        cached = self._read_cache(cache_key, TTL_FINANCIALS_SEC)
        if cached:
            return self._normalize_report_payload(cached)

        key_lock = await self._get_key_lock(cache_key)
        async with key_lock:
            # Re-check cache under lock
            cached = self._read_cache(cache_key, TTL_FINANCIALS_SEC)
            if cached:
                return self._normalize_report_payload(cached)

            if not self.api_key:
                if self.use_fixtures_fallback:
                    fixture = self._load_fixture(ticker)
                    if fixture:
                        report = {
                            "symbol": ticker.upper(),
                            "company_name": fixture.get("overview", {}).get("company_name", fixture.get("name", ticker.upper())),
                            "overview": fixture.get("overview", {}),
                            "financials": fixture.get("financials", {}),
                            "_source": "fixture",
                        }
                        normalized = self._normalize_report_payload(report)
                        self._write_cache(cache_key, normalized)
                        return normalized
                raise ValueError(
                    f"SECTORS_API_KEY is not set in environment or .env, and no local fixture exists for '{ticker}'. "
                    "Please configure SECTORS_API_KEY in .env to audit any IDX ticker."
                )

            if not self._has_quota_available():
                logger.warning("Sectors API quota ceiling reached (%s/%s). Enforcing credit protection.", self.api_calls_count, self.max_credits)
                if self.use_fixtures_fallback:
                    fixture = self._load_fixture(ticker)
                    if fixture:
                        fallback = self._normalize_report_payload({"symbol": ticker.upper(), **fixture, "_source": "fixture_fallback"})
                        self._write_cache(cache_key, fallback)
                        return fallback
                raise RuntimeError(f"Sectors API credit quota of {self.max_credits} calls exceeded ({self.api_calls_count} used).")

            url = f"{self.base_url}/company/report/{ticker.upper()}/"
            headers = {"Authorization": self.api_key}
            params = {"sections": sec_param}

            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.get(url, headers=headers, params=params)
                    self._record_api_call()
                    if resp.status_code == 200:
                        payload = resp.json()
                        payload["_source"] = "api"
                        normalized = self._normalize_report_payload(payload)
                        self._write_cache(cache_key, normalized)
                        return normalized
                    elif self.use_fixtures_fallback:
                        fixture = self._load_fixture(ticker)
                        if fixture:
                            fallback = self._normalize_report_payload({"symbol": ticker.upper(), **fixture, "_source": "fixture_fallback"})
                            self._write_cache(cache_key, fallback)
                            return fallback
                    resp.raise_for_status()
            except Exception as e:
                if self.use_fixtures_fallback:
                    fixture = self._load_fixture(ticker)
                    if fixture:
                        fallback = self._normalize_report_payload({"symbol": ticker.upper(), **fixture, "_source": "fixture_fallback"})
                        self._write_cache(cache_key, fallback)
                        return fallback
                raise e

            return {}

    async def get_company_news(self, ticker: str) -> list[dict[str, Any]]:
        """Fetch recent disclosures and news for ticker with disk caching and deduplication."""
        cache_key = f"company_news:{ticker.upper()}"
        cached = self._read_cache(cache_key, TTL_NEWS_SEC)
        if cached is not None:
            return cached

        key_lock = await self._get_key_lock(cache_key)
        async with key_lock:
            # Re-check cache under lock
            cached = self._read_cache(cache_key, TTL_NEWS_SEC)
            if cached is not None:
                return cached

            if not self.api_key:
                if self.use_fixtures_fallback:
                    fixture = self._load_fixture(ticker)
                    if fixture:
                        news = fixture.get("news", [])
                        self._write_cache(cache_key, news)
                        return news
                raise ValueError(f"No SECTORS_API_KEY provided and no fixture found for {ticker}")

            if not self._has_quota_available():
                logger.warning("Sectors API quota ceiling reached (%s/%s). Enforcing credit protection.", self.api_calls_count, self.max_credits)
                if self.use_fixtures_fallback:
                    fixture = self._load_fixture(ticker)
                    if fixture:
                        news_fallback = fixture.get("news", [])
                        self._write_cache(cache_key, news_fallback)
                        return news_fallback
                raise RuntimeError(f"Sectors API credit quota of {self.max_credits} calls exceeded ({self.api_calls_count} used).")

            url = f"{self.base_url}/news/"
            headers = {"Authorization": self.api_key}
            clean_sym = ticker.upper().replace(".JK", "")
            params = {"symbols": clean_sym}

            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    resp = await client.get(url, headers=headers, params=params)
                    self._record_api_call()
                    if resp.status_code == 200:
                        payload = resp.json()
                        news_list = payload.get("results", []) if isinstance(payload, dict) else payload
                        self._write_cache(cache_key, news_list)
                        return news_list
                    elif self.use_fixtures_fallback:
                        fixture = self._load_fixture(ticker)
                        if fixture:
                            news_fallback = fixture.get("news", [])
                            self._write_cache(cache_key, news_fallback)
                            return news_fallback
                    resp.raise_for_status()
            except Exception as e:
                if self.use_fixtures_fallback:
                    fixture = self._load_fixture(ticker)
                    if fixture:
                        news_fallback = fixture.get("news", [])
                        self._write_cache(cache_key, news_fallback)
                        return news_fallback
                raise e

            return []

    async def get_companies_by_subsector(self, subsector: str) -> list[dict[str, Any]]:
        """Screen companies by subsector name with deduplication."""
        cache_key = f"companies_subsector:{subsector.lower()}"
        cached = self._read_cache(cache_key, TTL_SUBSECTORS_SEC)
        if cached is not None:
            return cached

        key_lock = await self._get_key_lock(cache_key)
        async with key_lock:
            cached = self._read_cache(cache_key, TTL_SUBSECTORS_SEC)
            if cached is not None:
                return cached

            if not self.api_key:
                # Fallback mock universe
                mock_universe = [
                    {"symbol": "PGEO", "company_name": "Pertamina Geothermal Energy", "subsector": "alternative-energy"},
                    {"symbol": "BREN", "company_name": "Barito Renewables Energy", "subsector": "alternative-energy"},
                    {"symbol": "ADRO", "company_name": "Adaro Energy Indonesia", "subsector": "coal-mining"},
                    {"symbol": "BUMI", "company_name": "Bumi Resources", "subsector": "coal-mining"},
                    {"symbol": "BBRI", "company_name": "Bank Rakyat Indonesia", "subsector": "banks"},
                ]
                matched = [c for c in mock_universe if subsector.lower() in c.get("subsector", "").lower()]
                self._write_cache(cache_key, matched)
                return matched

            if not self._has_quota_available():
                logger.warning("Sectors API quota ceiling reached (%s/%s).", self.api_calls_count, self.max_credits)
                raise RuntimeError(f"Sectors API credit quota of {self.max_credits} calls exceeded ({self.api_calls_count} used).")

            url = f"{self.base_url}/companies/"
            headers = {"Authorization": self.api_key}
            params = {"sub_sector": subsector.lower()}

            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                self._record_api_call()
                if resp.status_code == 200:
                    payload = resp.json()
                    self._write_cache(cache_key, payload)
                    return payload
                resp.raise_for_status()

            return []

    def get_quota_stats(self) -> dict[str, int]:
        """Return credit usage and cache statistics."""
        return {
            "api_calls_made": self.api_calls_count,
            "cache_hits": self.cache_hits_count,
            "credits_remaining_estimate": max(0, self.max_credits - self.api_calls_count),
            "max_credits": self.max_credits,
        }
