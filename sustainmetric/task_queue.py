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
    """Manages asynchronous audit tasks with SQLite persistence, startup recovery, and partial-failure resilience."""

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
        self._running_tasks: dict[str, asyncio.Task] = {}
        self._init_db()
        self.recover_interrupted_tasks()

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

    def recover_interrupted_tasks(self) -> list[str]:
        """Recover tasks left in QUEUED or PROCESSING across process restarts."""
        conn = self._get_connection()
        recovered_ids: list[str] = []
        try:
            cursor = conn.execute(
                "SELECT task_id, tickers, status FROM audit_tasks WHERE status IN ('QUEUED', 'PROCESSING')"
            )
            pending = cursor.fetchall()
        finally:
            conn.close()

        for tid, tickers_raw, old_status in pending:
            try:
                tickers = json.loads(tickers_raw)
                logger.info(f"Recovering task {tid} (previous status: {old_status}) with {len(tickers)} tickers.")
                self._spawn_worker(tid, tickers)
                recovered_ids.append(tid)
            except Exception as e:
                logger.warning(f"Could not recover task {tid}: {e}")
                self._update_status(tid, "FAILED", error=f"Recovery failed: {str(e)}")

        return recovered_ids

    def _spawn_worker(self, task_id: str, tickers: list[str]) -> None:
        """Spawn worker task on current running loop or synchronous fallback."""
        try:
            loop = asyncio.get_running_loop()
            task = loop.create_task(self._execute_audit(task_id, tickers))
            self._running_tasks[task_id] = task
        except RuntimeError:
            try:
                asyncio.run(self._execute_audit(task_id, tickers))
            except Exception as e:
                logger.error(f"Failed synchronous execution for task {task_id}: {e}")

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

        self._spawn_worker(task_id, clean_tickers)
        return task_id

    def cancel_task(self, task_id: str) -> dict[str, Any]:
        """Cancel an in-progress or queued audit task."""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT status FROM audit_tasks WHERE task_id = ?", (task_id,))
            row = cursor.fetchone()
        finally:
            conn.close()

        if not row:
            return {"task_id": task_id, "status": "NOT_FOUND", "message": f"Task '{task_id}' not found."}

        current_status = row[0]
        if current_status in ["COMPLETED", "FAILED", "CANCELLED"]:
            return {"task_id": task_id, "status": current_status, "message": f"Task already in terminal state '{current_status}'."}

        if task_id in self._running_tasks:
            t = self._running_tasks[task_id]
            if not t.done():
                t.cancel()

        self._update_status(task_id, "CANCELLED", error="Task cancelled by user or agent.")
        return {"task_id": task_id, "status": "CANCELLED", "message": f"Task '{task_id}' successfully cancelled."}

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
            failed_tickers = [r for r in (results or []) if r.get("status") == "FAILED"]
            if failed_tickers:
                response["partial_failures"] = failed_tickers
        elif status in ["FAILED", "CANCELLED"]:
            response["error"] = error
            if results:
                response["results"] = results

        return response

    async def _execute_audit(self, task_id: str, tickers: list[str]) -> None:
        """Background worker executing fundamental and TKBI 2024 green audit with ticker-level resilience."""
        self._update_status(task_id, "PROCESSING")
        results = []

        try:
            for ticker in tickers:
                # Check for cancellation before each ticker
                task_info = self.get_task_status(task_id)
                if task_info and task_info.get("status") == "CANCELLED":
                    logger.info(f"Task {task_id} was cancelled; stopping audit worker.")
                    return

                # Per-ticker retry loop with exponential backoff
                report = None
                news = None
                last_err = None
                for attempt in range(2):
                    try:
                        report = await self.sectors_client.get_company_report(ticker)
                        news = await self.sectors_client.get_company_news(ticker)
                        break
                    except Exception as exc:
                        last_err = exc
                        await asyncio.sleep(0.1 * (2 ** attempt))

                if report is None or last_err is not None and news is None:
                    logger.warning(f"Ticker audit failed for {ticker} in task {task_id}: {last_err}")
                    results.append({
                        "ticker": ticker,
                        "status": "FAILED",
                        "error": str(last_err),
                    })
                    continue

                try:
                    overview = report.get("overview", {})
                    financials = report.get("financials", {})

                    # Semantic search in TKBI 2024 database
                    news_titles = " ".join([n.get("title", "") for n in news[:3]]) if news else ""
                    query_context = f"{ticker} {overview.get('company_name', '')} {overview.get('industry', '')} {overview.get('subsector', '')} {overview.get('description', '')} {news_titles}".strip()
                    tkbi_matches = self.vector_store.search(query_context, top_k=2)

                    # Quantitative evaluation
                    eval_data = ScoringEngine.evaluate(overview, financials, news, tkbi_matches)

                    results.append({
                        "ticker": ticker,
                        "status": "SUCCESS",
                        "company_name": overview.get("company_name", ticker),
                        "subsector": overview.get("subsector", "N/A"),
                        **eval_data,
                    })
                except Exception as eval_err:
                    logger.warning(f"Evaluation failed for ticker {ticker}: {eval_err}")
                    results.append({
                        "ticker": ticker,
                        "status": "FAILED",
                        "error": str(eval_err),
                    })

            # Check if all failed or partial
            all_failed = results and all(r.get("status") == "FAILED" for r in results)
            if all_failed:
                self._update_status(task_id, "FAILED", results=results, error="All tickers in batch failed audit.")
            else:
                self._update_status(task_id, "COMPLETED", results=results)

        except asyncio.CancelledError:
            logger.info(f"Audit task {task_id} coroutine cancelled.")
            self._update_status(task_id, "CANCELLED", results=results, error="Worker cancelled.")
            raise
        except Exception as e:
            logger.exception(f"Audit task {task_id} crashed: {e}")
            self._update_status(task_id, "FAILED", results=results, error=str(e))
        finally:
            self._running_tasks.pop(task_id, None)

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
