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
from sustainmetric.visualizer import build_visualization_payload

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


@mcp.tool()
async def visualize_green_audit(
    chart_type: str = "quadrant",
    ticker: str | None = None,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Generate self-contained matplotlib/seaborn code to visualize green audit and transition efforts.

    Enabled on-demand when requested by the user. Suitable for execution in Python environments
    or Agent Code Interpreters.

    Parameters:
    - chart_type: Type of chart. Options:
        * 'quadrant': 4-Quadrant consistency vs viability matrix (default).
        * 'green_effort': Green vs brown discourse and transition share breakdown.
        * 'financial_coverage': Operating cash flow vs green Capex coverage.
        * 'radar': Multi-axis sustainability and fundamental viability radar profile.
    - ticker: Specific IDX ticker to visualize (e.g. 'PGEO', 'ADRO').
    - task_id: Optional completed audit task ID to pull existing multi-ticker matrix results.
    """
    audit_data: Any = []

    # Priority 1: Pull from task_id if provided
    if task_id:
        task = task_queue.get_task_status(task_id)
        if task and "results" in task:
            audit_data = task["results"]
        elif task and "error" in task:
            return {"error": task["error"], "disclaimer": DISCLAIMER_TEXT}

    # Priority 2: Single ticker lookup if no task_id or specific ticker requested
    if not audit_data and ticker:
        clean_ticker = ticker.strip().upper()
        # Fetch report and news to evaluate
        try:
            report = await sectors_client.get_company_report(clean_ticker)
            news = await sectors_client.get_company_news(clean_ticker)
            matches = vector_store.search(clean_ticker, top_k=2)

            from sustainmetric.scoring_engine import ScoringEngine
            v_score, v_metrics = ScoringEngine.calculate_viability_score(report.get("financials", {}))
            c_score, findings = ScoringEngine.calculate_consistency_score(
                report.get("overview", {}),
                report.get("financials", {}),
                news,
                matches,
            )
            quadrant = ScoringEngine.classify_quadrant(v_score, c_score)

            # Count green & brown keywords
            green_kw = 0
            brown_kw = 0
            from sustainmetric.scoring_engine import GREEN_KEYWORDS, BROWN_KEYWORDS
            for n in news:
                title = str(n.get("title", "")).lower()
                for kw in GREEN_KEYWORDS:
                    if kw in title:
                        green_kw += 1
                for kw in BROWN_KEYWORDS:
                    if kw in title:
                        brown_kw += 1

            audit_data = [{
                "ticker": clean_ticker,
                "quadrant": quadrant,
                "consistency_score": c_score,
                "viability_score": v_score,
                "tkbi_alignment": {
                    "status": "HIJAU" if c_score >= 60 else "MERAH",
                    "matched_criteria": matches[0]["rule_name"] if matches else "N/A",
                },
                "financial_summary": {
                    "operating_cash_flow": v_metrics["operating_cash_flow"],
                    "capex": v_metrics["capex"],
                    "capex_coverage_ratio": v_metrics["capex_coverage_ratio"],
                    "roa_pct": v_metrics["roa_pct"],
                },
                "audit_findings": findings,
                "green_keywords_count": green_kw,
                "brown_keywords_count": brown_kw,
            }]
        except Exception as e:
            return {
                "error": f"Failed to retrieve data for ticker '{clean_ticker}': {str(e)}",
                "disclaimer": DISCLAIMER_TEXT,
            }

    if not audit_data:
        # Default placeholder demonstration tickers if nothing specified
        audit_data = [
            {"ticker": "PGEO", "viability_score": 75.0, "consistency_score": 85.0, "quadrant": "Transisi Tangguh"},
            {"ticker": "ADRO", "viability_score": 78.0, "consistency_score": 42.0, "quadrant": "Sumber Kas Konvensional"},
            {"ticker": "BREN", "viability_score": 48.0, "consistency_score": 72.0, "quadrant": "Dampak Spekulatif"},
            {"ticker": "BUMI", "viability_score": 38.0, "consistency_score": 25.0, "quadrant": "Tertinggal & Red Flag"},
        ]

    payload = build_visualization_payload(chart_type, ticker, audit_data)
    payload["disclaimer"] = DISCLAIMER_TEXT
    return payload



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
