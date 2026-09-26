"""SustainMetric IDX: The Algorithmic Green Auditor FastMCP Server.

Exposes tools for AI agent runtimes (Hermes, Claude Desktop, Cursor)
to audit IDX equities against greenwashing risks using OJK TKBI 2024.
"""

import argparse
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from sustainmetric.sectors_client import SectorsClient
from sustainmetric.task_queue import TaskQueue, DISCLAIMER_TEXT
from sustainmetric.tkbi_vector_store import TKBIVectorStore

# Initialize FastMCP Server
mcp = FastMCP("sustainmetric-idx")

# Initialize shared components
sectors_client = SectorsClient()
vector_store = TKBIVectorStore()
task_queue = TaskQueue(sectors_client=sectors_client, vector_store=vector_store)


@mcp.tool()
async def trigger_green_audit(tickers: list[str]) -> dict[str, Any]:
    """Trigger an asynchronous quantitative green audit for one or more IDX tickers.
    
    Accepts stock tickers (e.g. ['PGEO', 'ADRO', 'BBRI', 'BREN']), creates a durable background task,
    and returns immediately with a task_id to prevent agent protocol timeouts.
    """
    if not tickers:
        return {
            "error": "At least one ticker must be provided.",
            "disclaimer": DISCLAIMER_TEXT,
        }

    clean_tickers = [t.strip().upper() for t in tickers if t.strip()]
    task_id = task_queue.create_task(clean_tickers)

    return {
        "task_id": task_id,
        "status": "QUEUED",
        "tickers": clean_tickers,
        "poll_tool": "get_audit_status",
        "message": f"Audit task queued for {len(clean_tickers)} tickers. Poll get_audit_status with task_id to retrieve matrix results.",
        "disclaimer": DISCLAIMER_TEXT,
    }


@mcp.tool()
def get_audit_status(task_id: str) -> dict[str, Any]:
    """Poll the status and completed results of an audit task using its task_id.
    
    Returns status ('QUEUED', 'PROCESSING', 'COMPLETED', or 'FAILED') along with
    the 4-quadrant matrix coordinates, consistency score, viability score, and audit findings.
    """
    task = task_queue.get_task_status(task_id)
    if not task:
        return {
            "error": f"Task ID '{task_id}' not found.",
            "disclaimer": DISCLAIMER_TEXT,
        }
    return task


@mcp.tool()
def query_tkbi_knowledge_base(query: str, top_k: int = 3) -> dict[str, Any]:
    """Semantically search the official OJK TKBI 2024 Sustainable Finance Taxonomy.
    
    Query specific sector guidelines, Technical Screening Criteria (TSC), Do No Significant Harm (DNSH),
    and Minimum Social Safeguards (MSS) for energy, coal transition, renewables, or banking.
    """
    results = vector_store.search(query, top_k=top_k)
    return {
        "query": query,
        "total_matches": len(results),
        "results": results,
        "disclaimer": DISCLAIMER_TEXT,
    }


@mcp.tool()
async def inspect_ticker_evidence(ticker: str) -> dict[str, Any]:
    """Inspect raw auditable evidence trail for a specific IDX ticker.
    
    Retrieves cached fundamentals (Capex, OCF, Debt), recent disclosures and news snippets,
    green vs brown keyword frequency, and TKBI criteria alignment citations.
    """
    sym = ticker.strip().upper()
    try:
        report = await sectors_client.get_company_report(sym)
        news = await sectors_client.get_company_news(sym)
        matches = vector_store.search(
            f"{sym} {report.get('overview', {}).get('industry', '')} {report.get('overview', {}).get('description', '')}",
            top_k=2,
        )

        return {
            "ticker": sym,
            "company_name": report.get("overview", {}).get("company_name", sym),
            "subsector": report.get("overview", {}).get("subsector", "N/A"),
            "financial_facts": report.get("financials", {}),
            "recent_disclosures_count": len(news),
            "disclosures_sample": news[:3],
            "tkbi_screening_citations": matches,
            "disclaimer": DISCLAIMER_TEXT,
        }
    except Exception as e:
        return {
            "ticker": sym,
            "error": f"Failed to retrieve evidence: {str(e)}",
            "disclaimer": DISCLAIMER_TEXT,
        }


def main():
    """CLI entrypoint supporting stdio and SSE transports."""
    parser = argparse.ArgumentParser(description="SustainMetric IDX FastMCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument("--host", default="0.0.0.0", help="SSE host (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="SSE port (default: 8000)")

    args = parser.parse_args()

    if args.transport == "sse":
        print(f"Starting SustainMetric FastMCP Server over SSE on {args.host}:{args.port}", file=sys.stderr)
        mcp.settings.host = args.host
        mcp.settings.port = args.port
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
