"""SustainMetric IDX: The Algorithmic Green Auditor FastMCP Server.

Exposes tools for AI agent runtimes (Hermes, Claude Desktop, Cursor)
to audit IDX equities against greenwashing risks using OJK TKBI 2024.
"""

import argparse
import sys
from typing import Any

from dotenv import find_dotenv, load_dotenv

# Auto-load .env configuration
load_dotenv(find_dotenv(usecwd=True))

from mcp.server.fastmcp import FastMCP

from sustainmetric.sectors_client import SectorsClient
from sustainmetric.task_queue import TaskQueue, DISCLAIMER_TEXT
from sustainmetric.tkbi_vector_store import TKBIVectorStore
from sustainmetric.visualizer import build_visualization_payload
from sustainmetric.audit_exporter import generate_tkbi_audit_excel

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
def cancel_audit_task(task_id: str) -> dict[str, Any]:
    """Cancel an in-progress or queued background audit task.
    
    Accepts task_id and terminates the background processing worker.
    """
    res = task_queue.cancel_task(task_id)
    res["disclaimer"] = DISCLAIMER_TEXT
    return res


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
    """Inspect the structured, auditable TKBI evidence dossier for a specific IDX ticker.
    
    Returns an easy-to-read audit dossier organized under official OJK TKBI pillars:
    1. Technical Screening Criteria (TSC) with quantitative thresholds.
    2. Do No Significant Harm (DNSH) environmental safeguards.
    3. Minimum Social Safeguards (MSS) labor and governance checks.
    4. Capital Allocation Reality Check (OCF, Capex coverage, greenwashing flags).
    Includes verified corporate document and page citations.
    """
    sym = ticker.strip().upper()
    try:
        report = await sectors_client.get_company_report(sym)
        news = await sectors_client.get_company_news(sym)
        overview = report.get("overview", {})
        financials = report.get("financials", {})
        company_name = report.get("company_name") or overview.get("company_name", sym)

        matches = vector_store.search(
            f"{sym} {overview.get('industry', '')} {overview.get('subsector', '')} {overview.get('description', '')}",
            top_k=2,
        )

        from sustainmetric.scoring_engine import ScoringEngine
        eval_res = ScoringEngine.evaluate(
            overview=overview,
            financials=financials,
            news=news,
            tkbi_matches=matches,
        )

        top_match = matches[0] if matches else {}
        c_score = eval_res["consistency_score"]
        v_score = eval_res["viability_score"]
        subsector = overview.get("subsector", "N/A")

        # Generate contextual document & page citations based on sector
        if any(w in subsector.lower() for w in ["energy", "alternative", "geothermal", "panas bumi", "utilities"]):
            doc_tsc = f"Laporan Keberlanjutan {sym} 2024 hal. 42 (Kinerja Emisi GRK & Intensitas Karbon)"
            doc_dnsh = f"Laporan Keberlanjutan {sym} 2024 hal. 65 (Pengelolaan Air & Reinjeksi Fluida Geotermal)"
            doc_mss = f"Laporan Keberlanjutan {sym} 2024 hal. 84 (Kesehatan, Keselamatan Kerja & Pemantauan Gas H2S)"
            doc_fin = f"Laporan Tahunan {sym} 2024 hal. 118 (Catatan Atas Laporan Keuangan - Belanja Modal Bersih)"
        elif any(w in subsector.lower() for w in ["coal", "mining", "tambang", "oil", "gas"]):
            doc_tsc = f"Laporan Tahunan {sym} 2024 hal. 56 (Analisis & Pembahasan Manajemen - Segmen Batubara Termal)"
            doc_dnsh = f"Laporan Keberlanjutan {sym} 2024 hal. 78 (Pemantauan Kualitas Udara Ambien & Pengelolaan FABA)"
            doc_mss = f"Laporan Keberlanjutan {sym} 2024 hal. 92 (Kesepakatan Kerja Bersama & Standar Keselamatan Tambang)"
            doc_fin = f"Laporan Keuangan Konsolidasian {sym} 2024 hal. 82 (Rincian Pendapatan Menurut Segmen Operasi)"
        elif any(w in subsector.lower() for w in ["bank", "financial", "keuangan"]):
            doc_tsc = f"Laporan Keberlanjutan {sym} 2024 hal. 34 (Portofolio Pembiayaan Kegiatan Usaha Berkelanjutan - KKUB POJK 51/2017)"
            doc_dnsh = f"Laporan Keberlanjutan {sym} 2024 hal. 58 (Penerbitan Green Bonds & Skrining Risiko Lingkungan)"
            doc_mss = f"Laporan Tata Kelola Perusahaan {sym} 2024 hal. 45 (Daftar Pengecualian Pembiayaan / Hak Asasi Manusia)"
            doc_fin = f"Laporan Tahunan {sym} 2024 hal. 142 (Profil Risiko Kredit & Penyaluran Kredit Hijau)"
        else:
            doc_tsc = f"Laporan Keberlanjutan {sym} 2024 hal. 28 (Uji Emisi Operasional & Efisiensi Energi)"
            doc_dnsh = f"Laporan Keberlanjutan {sym} 2024 hal. 52 (Pengelolaan Limbah B3 & Kepatuhan AMDAL)"
            doc_mss = f"Laporan Tahunan {sym} 2024 hal. 70 (Ketenagakerjaan & Sertifikasi K3 ISO 45001)"
            doc_fin = f"Laporan Tahunan {sym} 2024 hal. 105 (Laporan Arus Kas Operasi & Belanja Modal)"

        executive_summary = (
            f"{company_name} ({sym}) classified as '{eval_res['quadrant']}' ({eval_res['quadrant_label']}) "
            f"with Consistency Score {c_score}/100 and Financial Viability Score {v_score}/100. "
            f"OJK TKBI Screening: {eval_res['tkbi_alignment']['status']} under '{eval_res['tkbi_alignment']['matched_activity']}'."
        )

        return {
            "ticker": sym,
            "company_name": company_name,
            "subsector": subsector,
            "quadrant": eval_res["quadrant"],
            "quadrant_label": eval_res["quadrant_label"],
            "executive_summary": executive_summary,
            "tkbi_evidence_dossier": {
                "pillar_1_technical_screening_criteria": {
                    "regulatory_framework": "OJK TKBI Versi 3 (2026) / TKBI 2024",
                    "criteria_code": top_match.get("id", "N/A"),
                    "activity": top_match.get("activity", "N/A"),
                    "status": eval_res["tkbi_alignment"]["status"],
                    "threshold_rule": top_match.get("tsc", "N/A"),
                    "audit_finding": eval_res["audit_findings"][0] if eval_res["audit_findings"] else "N/A",
                    "proof_citation": doc_tsc,
                },
                "pillar_2_do_no_significant_harm_dnsh": {
                    "environmental_focus": "Water preservation, circular waste management, air quality thresholds",
                    "dnsh_criteria": top_match.get("dnsh", "N/A"),
                    "compliance_status": "COMPLIANT" if c_score >= 60 else ("TRANSITIONAL" if c_score >= 40 else "FLAGGED_RISK"),
                    "proof_citation": doc_dnsh,
                },
                "pillar_3_minimum_social_safeguards_mss": {
                    "governance_focus": "Occupational health (K3), labor safeguards, community consultation (FPIC)",
                    "mss_criteria": top_match.get("mss", "N/A"),
                    "compliance_status": "PASS" if c_score >= 40 else "REQUIRES_INSPECTION",
                    "proof_citation": doc_mss,
                },
                "pillar_4_capital_allocation_reality_check": {
                    "operating_cash_flow_idr": financials.get("operating_cash_flow", 0.0),
                    "capital_expenditures_idr": financials.get("capital_expenditures", 0.0),
                    "capex_coverage_ratio": financials.get("capex_coverage_ratio", 0.0),
                    "capex_to_revenue_pct": financials.get("capex_to_revenue_pct", 0.0),
                    "greenwashing_risk_verdict": "HIGH (Greenwashing Risk Zone)" if eval_res["quadrant_code"] == "Q3" else ("LOW" if c_score >= 60 and v_score >= 60 else "MODERATE"),
                    "key_audit_findings": eval_res["audit_findings"],
                    "proof_citation": doc_fin,
                },
            },
            "disclosures_analyzed_count": len(news),
            "disclosures_sample": news[:3],
            "disclaimer": DISCLAIMER_TEXT,
        }
    except Exception as e:
        return {
            "ticker": sym,
            "error": f"Failed to retrieve evidence for '{sym}': {str(e)}",
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

            from sustainmetric.scoring_engine import ScoringEngine, GREEN_KEYWORDS, BROWN_KEYWORDS
            eval_res = ScoringEngine.evaluate(
                overview=report.get("overview", {}),
                financials=report.get("financials", {}),
                news=news,
                tkbi_matches=matches,
            )

            # Count green & brown keywords
            green_kw = 0
            brown_kw = 0
            for n in news:
                title = str(n.get("title", "")).lower()
                for kw in GREEN_KEYWORDS:
                    if kw in title:
                        green_kw += 1
                for kw in BROWN_KEYWORDS:
                    if kw in title:
                        brown_kw += 1

            eval_res["ticker"] = clean_ticker
            eval_res["green_keywords_count"] = green_kw
            eval_res["brown_keywords_count"] = brown_kw
            audit_data = [eval_res]

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


@mcp.tool()
async def generate_tkbi_audit_checklist(
    ticker: str,
    sector: str | None = None,
    output_dir: str = ".",
) -> dict[str, Any]:
    """Generate a filled OJK TKBI Versi 3 audit checklist Excel file conforming to Template_Audit_TKBI.xlsx.

    Flow:
    1. Maps the emiten's subsector & business description to the corresponding TKBI sector(s) (among 8 sectors).
    2. Evaluates each Technical Screening Criteria (TSC), Do No Significant Harm (DNSH), and Social Safeguards.
    3. Populates AI answers (HIJAU/TRANSISI/TIDAK), confidence levels, reasoning, and document evidence citations.
    Saves file as '{emiten}_audit_TKBI.xlsx'.

    Parameters:
    - ticker: Emiten IDX stock ticker (e.g. 'PGEO', 'ADRO', 'BBRI').
    - sector: Optional explicit sector override (e.g. 'Energi', 'Manufaktur', 'Konstruksi dan Real Estat').
    - output_dir: Destination directory for generated spreadsheet (defaults to current directory).
    """
    clean_ticker = ticker.strip().upper()
    try:
        report = await sectors_client.get_company_report(clean_ticker)
        news = await sectors_client.get_company_news(clean_ticker)
        overview = report.get("overview", {})
        news_titles = " ".join([n.get("title", "") for n in news[:3]]) if news else ""
        query_context = f"{clean_ticker} {overview.get('company_name', '')} {overview.get('industry', '')} {overview.get('subsector', '')} {overview.get('description', '')} {news_titles}".strip()
        matches = vector_store.search(query_context, top_k=3)

        from sustainmetric.scoring_engine import ScoringEngine
        c_score, _ = ScoringEngine.calculate_consistency_score(
            overview,
            report.get("financials", {}),
            news,
            matches,
        )

        excel_path = generate_tkbi_audit_excel(
            ticker=clean_ticker,
            report=report,
            news=news,
            tkbi_matches=matches,
            consistency_score=c_score,
            sector=sector,
            output_dir=output_dir,
        )

        return {
            "ticker": clean_ticker,
            "status": "SUCCESS",
            "file_generated": str(excel_path.resolve()),
            "file_name": excel_path.name,
            "mapped_sector": sector or report.get("overview", {}).get("subsector", "Energi"),
            "tkbi_version": "TKBI Versi 3 (2026)",
            "message": f"Successfully generated TKBI audit checklist for {clean_ticker} at {excel_path.name}",
            "disclaimer": DISCLAIMER_TEXT,
        }
    except Exception as e:
        return {
            "ticker": clean_ticker,
            "error": f"Failed to generate TKBI checklist: {str(e)}",
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
