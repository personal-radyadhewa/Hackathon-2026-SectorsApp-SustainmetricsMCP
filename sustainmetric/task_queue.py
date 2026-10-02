"""Durable background audit task queue backed by SQLite.

Prevents LLM client stdio/SSE connection drops by decoupling audit triggering
from result retrieval via asynchronous background workers.
"""

import asyncio
import json
import logging
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Optional

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

from sustainmetric.scoring_engine import ScoringEngine
from sustainmetric.sectors_client import SectorsClient
from sustainmetric.tkbi_vector_store import TKBIVectorStore

logger = logging.getLogger("sustainmetric.task_queue")

DB_PATH_DEFAULT = Path(".cache/tasks.db")
DISCLAIMER_TEXT = "Information & Analysis Tool Only. Not Financial Advice or Investment Recommendation."


class TaskQueue:
    """Manages asynchronous audit tasks with SQLite persistence."""

    def __init__(
        self,
        db_path: Optional[Path] = None,
        sectors_client: Optional[SectorsClient] = None,
        vector_store: Optional[TKBIVectorStore] = None,
    ):
        self.db_path = db_path or DB_PATH_DEFAULT
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.sectors_client = sectors_client or SectorsClient()
        self.vector_store = vector_store or TKBIVectorStore()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _init_db(self) -> None:
        conn = self._get_connection()
        try:
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
            conn.commit()
        finally:
            conn.close()

    def create_task(self, tickers: list[str]) -> str:
        """Create new queued audit task and persist in SQLite."""
        task_id = str(uuid.uuid4())
        clean_tickers = [t.strip().upper() for t in tickers if t.strip()]
        now = time.time()

        conn = self._get_connection()
        try:
            conn.execute(
                """
                INSERT INTO audit_tasks (task_id, tickers, status, created_at, updated_at, results, error)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (task_id, json.dumps(clean_tickers), "QUEUED", now, now, None, None),
            )
            conn.commit()
        finally:
            conn.close()

        # Spawn background execution
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._execute_audit(task_id, clean_tickers))
        except RuntimeError:
            # If no running loop in current thread, execute sync or spawn thread
            asyncio.run(self._execute_audit(task_id, clean_tickers))

        return task_id

    def get_task_status(self, task_id: str) -> Optional[dict[str, Any]]:
        """Retrieve task state and results if completed."""
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "SELECT task_id, tickers, status, created_at, updated_at, results, error FROM audit_tasks WHERE task_id = ?",
                (task_id,),
            )
            row = cursor.fetchone()
        finally:
            conn.close()

        if not row:
            return None

        tid, tickers_raw, status, created_at, updated_at, results_raw, error = row
        tickers = json.loads(tickers_raw)
        results = json.loads(results_raw) if results_raw else None

        response = {
            "task_id": tid,
            "status": status,
            "tickers": tickers,
            "created_at": created_at,
            "updated_at": updated_at,
            "disclaimer": DISCLAIMER_TEXT,
        }

        if status == "COMPLETED":
            response["results"] = results
        elif status == "FAILED":
            response["error"] = error

        return response

    async def _execute_audit(self, task_id: str, tickers: list[str]) -> None:
        """Background worker executing fundamental and TKBI 2024 green audit."""
        self._update_status(task_id, "PROCESSING")
        results = []

        try:
            for ticker in tickers:
                report = await self.sectors_client.get_company_report(ticker)
                news = await self.sectors_client.get_company_news(ticker)

                overview = report.get("overview", {})
                financials = report.get("financials", {})

                # Semantic search in TKBI 2024 database
                query_context = f"{ticker} {overview.get('industry', '')} {overview.get('subsector', '')} {overview.get('description', '')}"
                tkbi_matches = self.vector_store.search(query_context, top_k=2)

                # Quantitative evaluation
                eval_data = ScoringEngine.evaluate(overview, financials, news, tkbi_matches)

                results.append({
                    "ticker": ticker,
                    "company_name": overview.get("company_name", ticker),
                    "subsector": overview.get("subsector", "N/A"),
                    **eval_data,
                })

            self._update_status(task_id, "COMPLETED", results=results)
        except Exception as e:
            logger.exception(f"Audit task {task_id} failed: {e}")
            self._update_status(task_id, "FAILED", error=str(e))

    def _update_status(
        self,
        task_id: str,
        status: str,
        results: Optional[list[dict[str, Any]]] = None,
        error: Optional[str] = None,
    ) -> None:
        now = time.time()
        results_str = json.dumps(results) if results is not None else None

        conn = self._get_connection()
        try:
            conn.execute(
                """
                UPDATE audit_tasks
                SET status = ?, updated_at = ?, results = coalesce(?, results), error = ?
                WHERE task_id = ?
                """,
                (status, now, results_str, error, task_id),
            )
            conn.commit()
        finally:
            conn.close()
