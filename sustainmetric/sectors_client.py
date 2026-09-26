"""Sectors Financial API v2 client with disk cache and credit quota protection."""

import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Optional

import httpx

logger = logging.getLogger("sustainmetric.sectors_client")

CACHE_DIR_DEFAULT = Path(".cache/sectors")
FIXTURES_DIR = Path(__file__).parent / "data" / "fixtures"

TTL_FINANCIALS_SEC = int(os.getenv("CACHE_TTL_FINANCIALS_SEC", 7 * 86400))  # 7 days
TTL_NEWS_SEC = int(os.getenv("CACHE_TTL_NEWS_SEC", 86400))                  # 24 hours
TTL_SUBSECTORS_SEC = 30 * 86400                                             # 30 days


class SectorsClient:
    """Async client for Sectors Financial API v2 with strict disk caching."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        cache_dir: Optional[Path] = None,
        use_fixtures_fallback: bool = True,
    ):
        self.api_key = api_key or os.getenv("SECTORS_API_KEY")
        self.base_url = "https://api.sectors.app/v2"
        self.cache_dir = cache_dir or CACHE_DIR_DEFAULT
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.use_fixtures_fallback = use_fixtures_fallback
        self.api_calls_count = 0
        self.cache_hits_count = 0

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
        fixture_path = FIXTURES_DIR / f"{ticker.upper()}.json"
        if fixture_path.exists():
            with open(fixture_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    async def get_company_report(
        self, ticker: str, sections: list[str] = ["overview", "financials"]
    ) -> dict[str, Any]:
        """Fetch company financial and profile report with disk caching."""
        sec_param = ",".join(sorted(sections))
        cache_key = f"company_report:{ticker.upper()}:{sec_param}"
        cached = self._read_cache(cache_key, TTL_FINANCIALS_SEC)
        if cached:
            return cached

        if not self.api_key:
            if self.use_fixtures_fallback:
                fixture = self._load_fixture(ticker)
                if fixture:
                    report = {
                        "symbol": ticker.upper(),
                        "overview": fixture.get("overview", {}),
                        "financials": fixture.get("financials", {}),
                        "_source": "fixture",
                    }
                    self._write_cache(cache_key, report)
                    return report
            raise ValueError(f"No SECTORS_API_KEY provided and no fixture found for {ticker}")

        url = f"{self.base_url}/company/report/{ticker.upper()}/"
        headers = {"Authorization": self.api_key}
        params = {"sections": sec_param}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                self.api_calls_count += 1
                if resp.status_code == 200:
                    payload = resp.json()
                    payload["_source"] = "api"
                    self._write_cache(cache_key, payload)
                    return payload
                elif self.use_fixtures_fallback:
                    fixture = self._load_fixture(ticker)
                    if fixture:
                        return {"symbol": ticker.upper(), **fixture, "_source": "fixture_fallback"}
                resp.raise_for_status()
        except Exception as e:
            if self.use_fixtures_fallback:
                fixture = self._load_fixture(ticker)
                if fixture:
                    return {"symbol": ticker.upper(), **fixture, "_source": "fixture_fallback"}
            raise e

        return {}

    async def get_company_news(self, ticker: str) -> list[dict[str, Any]]:
        """Fetch recent disclosures and news for ticker."""
        cache_key = f"company_news:{ticker.upper()}"
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

        url = f"{self.base_url}/news/"
        headers = {"Authorization": self.api_key}
        params = {"symbol": ticker.upper()}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(url, headers=headers, params=params)
                self.api_calls_count += 1
                if resp.status_code == 200:
                    payload = resp.json()
                    self._write_cache(cache_key, payload)
                    return payload
                elif self.use_fixtures_fallback:
                    fixture = self._load_fixture(ticker)
                    if fixture:
                        return fixture.get("news", [])
                resp.raise_for_status()
        except Exception as e:
            if self.use_fixtures_fallback:
                fixture = self._load_fixture(ticker)
                if fixture:
                    return fixture.get("news", [])
            raise e

        return []

    async def get_companies_by_subsector(self, subsector: str) -> list[dict[str, Any]]:
        """Screen companies by subsector name."""
        cache_key = f"companies_subsector:{subsector.lower()}"
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

        url = f"{self.base_url}/companies/"
        headers = {"Authorization": self.api_key}
        params = {"sub_sector": subsector.lower()}

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(url, headers=headers, params=params)
            self.api_calls_count += 1
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
            "credits_remaining_estimate": max(0, 1000 - self.api_calls_count),
        }
