"""Integration tests for FastMCP tools and async task worker."""

import pytest
import shutil
import asyncio
from pathlib import Path
from sustainmetric.sectors_client import SectorsClient
from sustainmetric.tkbi_vector_store import TKBIVectorStore
from sustainmetric.task_queue import TaskQueue, DISCLAIMER_TEXT
from sustainmetric.server import (
    trigger_green_audit,
    get_audit_status,
    query_tkbi_knowledge_base,
    inspect_ticker_evidence,
)

TEST_DIR = Path(".cache/test_server_env")

@pytest.fixture(autouse=True)
def setup_test_env():
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR, ignore_errors=True)
    TEST_DIR.mkdir(parents=True, exist_ok=True)
    yield
    if TEST_DIR.exists():
        shutil.rmtree(TEST_DIR, ignore_errors=True)

@pytest.mark.asyncio
async def test_tkbi_query_tool():
    res = query_tkbi_knowledge_base(query="geothermal energy PLTP", top_k=2)
    assert res["total_matches"] == 2
    assert res["disclaimer"] == DISCLAIMER_TEXT
    assert "Geothermal" in res["results"][0]["subsector"]

@pytest.mark.asyncio
async def test_inspect_ticker_evidence_tool():
    res = await inspect_ticker_evidence("PGEO")
    assert res["ticker"] == "PGEO"
    assert "financial_facts" in res
    assert res["disclaimer"] == DISCLAIMER_TEXT
    assert len(res["tkbi_screening_citations"]) > 0

@pytest.mark.asyncio
async def test_trigger_green_audit_end_to_end():
    # 1. Trigger audit for PGEO and ADRO
    trigger_res = await trigger_green_audit(["PGEO", "ADRO"])
    assert trigger_res["status"] == "QUEUED"
    assert "task_id" in trigger_res
    assert trigger_res["disclaimer"] == DISCLAIMER_TEXT
    task_id = trigger_res["task_id"]

    # 2. Wait for background worker to process
    for _ in range(15):
        await asyncio.sleep(0.3)
        status_res = get_audit_status(task_id)
        if status_res and status_res.get("status") == "COMPLETED":
            break

    assert status_res["status"] == "COMPLETED"
    assert len(status_res["results"]) == 2

    # Check PGEO results (Q1 Transisi Tangguh)
    pgeo_res = next(r for r in status_res["results"] if r["ticker"] == "PGEO")
    assert pgeo_res["quadrant_code"] == "Q1"
    assert pgeo_res["consistency_score"] >= 60.0
    assert pgeo_res["viability_score"] >= 60.0

    # Check ADRO results (Q3 Sumber Kas Konvensional)
    adro_res = next(r for r in status_res["results"] if r["ticker"] == "ADRO")
    assert adro_res["quadrant_code"] == "Q3"
    assert adro_res["consistency_score"] < 60.0
    assert adro_res["viability_score"] >= 60.0
