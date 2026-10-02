"""Unit tests for SectorsClient caching and quota protection."""

import pytest
import shutil
from pathlib import Path
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
