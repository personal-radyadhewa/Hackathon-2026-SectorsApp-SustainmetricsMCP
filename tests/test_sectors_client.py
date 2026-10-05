"""Unit tests for SectorsClient caching, persistent quota, and concurrency protection."""

import asyncio
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest
import shutil
from sustainmetric.sectors_client import SectorsClient

TEST_CACHE_DIR = Path(".cache/test_sectors")


@pytest.fixture(autouse=True)
def clean_test_cache():
    if TEST_CACHE_DIR.exists():
        shutil.rmtree(TEST_CACHE_DIR)
    yield
    if TEST_CACHE_DIR.exists():
        shutil.rmtree(TEST_CACHE_DIR)


@pytest.mark.asyncio
async def test_sectors_client_fixture_fallback():
    client = SectorsClient(api_key="", cache_dir=TEST_CACHE_DIR, use_fixtures_fallback=True)
    report = await client.get_company_report("PGEO")
    assert report["symbol"] == "PGEO"
    assert "financials" in report
    assert report["financials"]["operating_cash_flow"] > 0
    assert report["_source"] == "fixture"

    # Second call should hit disk cache
    report2 = await client.get_company_report("PGEO")
    stats = client.get_quota_stats()
    assert stats["cache_hits"] == 1
    assert stats["api_calls_made"] == 0


@pytest.mark.asyncio
async def test_sectors_client_news_fixture():
    client = SectorsClient(api_key="", cache_dir=TEST_CACHE_DIR, use_fixtures_fallback=True)
    news = await client.get_company_news("ADRO")
    assert len(news) > 0
    assert "Adaro" in news[0]["title"]


@pytest.mark.asyncio
async def test_sectors_client_quota_persistence_and_hard_limit():
    # Set limit to 2 calls
    client1 = SectorsClient(api_key="mock_key", cache_dir=TEST_CACHE_DIR, max_credits=2)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"symbol": "TEST", "overview": {"symbol": "TEST"}, "financials": {}}

    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        # 1st call
        await client1.get_company_report("AAA")
        # 2nd call
        await client1.get_company_report("BBB")

    assert client1.api_calls_count == 2
    assert (TEST_CACHE_DIR / "quota.json").exists()

    # Create new client instance pointing to same cache directory (simulating restart)
    client2 = SectorsClient(api_key="mock_key", cache_dir=TEST_CACHE_DIR, max_credits=2, use_fixtures_fallback=False)
    assert client2.api_calls_count == 2
    assert client2.get_quota_stats()["credits_remaining_estimate"] == 0

    # 3rd call should be blocked by hard limit
    with pytest.raises(RuntimeError, match="credit quota of 2 calls exceeded"):
        await client2.get_company_report("CCC")


@pytest.mark.asyncio
async def test_sectors_client_fallback_caching_on_api_error():
    client = SectorsClient(api_key="mock_key", cache_dir=TEST_CACHE_DIR, use_fixtures_fallback=True)

    mock_resp = MagicMock()
    mock_resp.status_code = 500
    mock_resp.raise_for_status.side_effect = Exception("Internal Server Error")

    with patch("httpx.AsyncClient.get", return_value=mock_resp) as mock_get:
        # Initial call fails and falls back to fixture
        report1 = await client.get_company_report("PGEO")
        assert report1["symbol"] == "PGEO"
        assert report1["_source"] == "fixture_fallback"
        assert mock_get.call_count == 1

        # Second call must hit disk cache without re-invoking failing API
        report2 = await client.get_company_report("PGEO")
        assert report2["symbol"] == "PGEO"
        assert mock_get.call_count == 1  # No additional network call!


@pytest.mark.asyncio
async def test_sectors_client_request_deduplication():
    client = SectorsClient(api_key="mock_key", cache_dir=TEST_CACHE_DIR, use_fixtures_fallback=True)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"symbol": "PGEO", "overview": {"symbol": "PGEO"}, "financials": {}}

    async def delayed_get(*args, **kwargs):
        await asyncio.sleep(0.05)
        return mock_resp

    with patch("httpx.AsyncClient.get", side_effect=delayed_get) as mock_get:
        # Launch 5 concurrent calls for the same ticker
        results = await asyncio.gather(*[client.get_company_report("PGEO") for _ in range(5)])
        assert len(results) == 5
        # Only exactly 1 network request must have been triggered
        assert mock_get.call_count == 1
