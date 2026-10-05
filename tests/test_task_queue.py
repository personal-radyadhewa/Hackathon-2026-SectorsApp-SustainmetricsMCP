"""Unit tests for TaskQueue resilience, startup recovery, and partial-failure isolation."""

import asyncio
import json
import sqlite3
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock
import pytest
import shutil
from sustainmetric.task_queue import TaskQueue

TEST_DB_PATH = Path(".cache/test_tasks.db")


@pytest.fixture(autouse=True)
def clean_tasks_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    yield
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()


@pytest.mark.asyncio
async def test_task_queue_partial_failure_reporting():
    mock_sectors = MagicMock()
    # PGEO succeeds with mock report
    async def mock_report(ticker):
        if ticker == "BADTICKER":
            raise ValueError("Ticker BADTICKER does not exist in IDX registry")
        return {
            "symbol": ticker,
            "company_name": "Pertamina Geothermal Energy",
            "overview": {"subsector": "Utilities", "industry": "Electric Utilities"},
            "financials": {"operating_cash_flow": 1000, "capital_expenditures": 500, "revenue": 2000},
        }

    mock_sectors.get_company_report = AsyncMock(side_effect=mock_report)
    mock_sectors.get_company_news = AsyncMock(return_value=[])

    mock_vector = MagicMock()
    mock_vector.search = MagicMock(return_value=[{"id": "TKBI-01", "criteria_level": "Hijau", "similarity_score": 0.5}])

    queue = TaskQueue(db_path=TEST_DB_PATH, sectors_client=mock_sectors, vector_store=mock_vector)
    task_id = queue.create_task(["PGEO", "BADTICKER"])

    # Wait for completion
    for _ in range(20):
        await asyncio.sleep(0.1)
        status = queue.get_task_status(task_id)
        if status and status.get("status") in ["COMPLETED", "FAILED"]:
            break

    assert status["status"] == "COMPLETED"
    assert len(status["results"]) == 2

    pgeo_res = next(r for r in status["results"] if r["ticker"] == "PGEO")
    assert pgeo_res["status"] == "SUCCESS"

    bad_res = next(r for r in status["results"] if r["ticker"] == "BADTICKER")
    assert bad_res["status"] == "FAILED"
    assert "does not exist" in bad_res["error"]

    assert "partial_failures" in status
    assert len(status["partial_failures"]) == 1


@pytest.mark.asyncio
async def test_task_queue_cancellation():
    mock_sectors = MagicMock()

    async def slow_report(ticker):
        await asyncio.sleep(1.0)
        return {"symbol": ticker, "overview": {}, "financials": {}}

    mock_sectors.get_company_report = AsyncMock(side_effect=slow_report)
    mock_sectors.get_company_news = AsyncMock(return_value=[])

    queue = TaskQueue(db_path=TEST_DB_PATH, sectors_client=mock_sectors)
    task_id = queue.create_task(["PGEO", "BBRI"])

    await asyncio.sleep(0.05)
    cancel_res = queue.cancel_task(task_id)
    assert cancel_res["status"] == "CANCELLED"

    status = queue.get_task_status(task_id)
    assert status["status"] == "CANCELLED"


@pytest.mark.asyncio
async def test_task_queue_startup_recovery():
    # Insert an interrupted task directly into SQLite
    conn = sqlite3.connect(str(TEST_DB_PATH))
    now = time.time()
    task_id = "interrupted-task-001"
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_tasks (
            task_id TEXT PRIMARY KEY,
            tickers TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at REAL NOT NULL,
            updated_at REAL NOT NULL,
            results TEXT,
            error TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO audit_tasks (task_id, tickers, status, created_at, updated_at, results, error)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (task_id, json.dumps(["PGEO"]), "PROCESSING", now - 100, now - 100, None, None),
    )
    conn.commit()
    conn.close()

    mock_sectors = MagicMock()
    mock_sectors.get_company_report = AsyncMock(return_value={
        "symbol": "PGEO",
        "company_name": "PGEO",
        "overview": {},
        "financials": {},
    })
    mock_sectors.get_company_news = AsyncMock(return_value=[])

    # Instantiating TaskQueue should trigger recovery
    queue = TaskQueue(db_path=TEST_DB_PATH, sectors_client=mock_sectors)

    for _ in range(20):
        await asyncio.sleep(0.1)
        status = queue.get_task_status(task_id)
        if status and status.get("status") == "COMPLETED":
            break

    assert status["status"] == "COMPLETED"
    assert status["results"][0]["ticker"] == "PGEO"
