"""Visualization Engine for SustainMetric IDX Green Audits.

Generates self-contained, executable matplotlib and seaborn visualization code
for:
1. 4-Quadrant Matrix (Consistency vs Financial Viability)
2. Green Effort Breakdown (Green vs Brown keywords & Capex commitment)
3. Financial vs Green Coverage (OCF vs Capex capacity)
4. Emiten Radar Profile (Multi-axis sustainability/viability score)
5. Comprehensive Dashboard (2x2 grid combining key visualizations)
"""

import json
from typing import Any


def generate_quadrant_chart_code(audit_results: list[dict[str, Any]]) -> str:
    """Generate executable Python matplotlib/seaborn code for 4-quadrant classification."""
    data_json = json.dumps(audit_results, indent=2)

    return f'''import matplotlib.pyplot as plt
import seaborn as sns

# Audit data payload
results = {data_json}

# Setup plot style
sns.set_theme(style="whitegrid", palette="muted")
fig, ax = plt.subplots(figsize=(10, 8), dpi=150)

# Quadrant dividing lines (X=60, Y=60)
ax.axvline(x=60, color="#718096", linestyle="--", linewidth=1.5, alpha=0.8)
ax.axhline(y=60, color="#718096", linestyle="--", linewidth=1.5, alpha=0.8)

# Quadrant background zones
ax.fill_between([60, 100], 60, 100, color="#48BB78", alpha=0.15, label="Q1: STRONG FUNDAMENTAL AND SUSTAINABLE (High Green & High Viability)")
ax.fill_between([0, 60], 60, 100, color="#ECC94B", alpha=0.15, label="Q2: SUSTAINABLE BUT HIGH FINANCIAL RISK (High Green & Low Viability)")
ax.fill_between([60, 100], 0, 60, color="#ED8936", alpha=0.15, label="Q3: GREENWASHING RISK ZONE (Low Green & High Viability)")
ax.fill_between([0, 60], 0, 60, color="#F56565", alpha=0.15, label="Q4: NOT CONSIDERED (Low Green & Low Viability)")

# Quadrant watermark labels
ax.text(80, 95, "Q1: STRONG FUNDAMENTAL AND SUSTAINABLE\\n(High Green & High Viability)", ha="center", va="top", fontsize=9, fontweight="bold", color="#22543D", alpha=0.8)
ax.text(30, 95, "Q2: SUSTAINABLE BUT HIGH FINANCIAL RISK\\n(High Green & Low Viability)", ha="center", va="top", fontsize=9, fontweight="bold", color="#744210", alpha=0.8)
ax.text(80, 5, "Q3: GREENWASHING RISK ZONE\\n(Low Green & High Viability)", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#7B341E", alpha=0.8)
ax.text(30, 5, "Q4: NOT CONSIDERED\\n(Low Green & Low Viability)", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#742A2A", alpha=0.8)

# Plot tickers
colors = {{
    "STRONG FUNDAMENTAL AND SUSTAINABLE": "#2F855A",
    "SUSTAINABLE BUT HIGH FINANCIAL RISK": "#D69E2E",
    "GREENWASHING RISK ZONE": "#DD6B20",
    "NOT CONSIDERED": "#E53E3E",
    "Transisi Tangguh": "#2F855A",
    "Dampak Spekulatif": "#D69E2E",
    "Sumber Kas Konvensional": "#DD6B20",
    "Tertinggal & Red Flag": "#E53E3E",
}}

for item in results:
    ticker = item.get("ticker", "N/A")
    viability = item.get("viability_score", 0)
    consistency = item.get("consistency_score", 0)
    quadrant = item.get("quadrant", "NOT CONSIDERED")
    dot_color = colors.get(quadrant, "#4A5568")

    ax.scatter(viability, consistency, s=280, color=dot_color, edgecolors="black", linewidth=1.5, zorder=5)
    ax.annotate(
        f"  {{ticker}}\\n  ({{viability}}, {{consistency}})",
        xy=(viability, consistency),
        xytext=(5, 5),
        textcoords="offset points",
        fontsize=9,
        fontweight="bold",
        zorder=6,
    )

ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_xlabel("Financial Viability Score (0 - 100) [OCF, Capex Coverage, ROA, Solvency]", fontsize=11, fontweight="bold", labelpad=10)
ax.set_ylabel("TKBI Consistency Score (0 - 100) [OJK Taxonomy, DNSH, Green/Brown Capex]", fontsize=11, fontweight="bold", labelpad=10)
ax.set_title("SustainMetric IDX: 4-Quadrant Algorithmic Green Auditor Matrix", fontsize=14, fontweight="bold", pad=15)
ax.legend(loc="lower left", fontsize=8, framealpha=0.9)
plt.tight_layout()
plt.show()
'''


def generate_green_effort_code(ticker: str, evidence: dict[str, Any]) -> str:
    """Generate executable Python matplotlib/seaborn code for green effort and keyword disclosure."""
    data_json = json.dumps(evidence, indent=2)

    return f'''import matplotlib.pyplot as plt
import seaborn as sns

data = {data_json}
ticker = "{ticker}"

# Extract keywords count and green ratio
green_kw = data.get("green_keywords_count", 0)
brown_kw = data.get("brown_keywords_count", 0)
total_kw = max(1, green_kw + brown_kw)
green_ratio = (green_kw / total_kw) * 100

findings = data.get("audit_findings", [])
tkbi_status = data.get("tkbi_alignment", {{}}).get("status", "N/A")

sns.set_theme(style="whitegrid")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=150)

# 1. Bar Chart: Green vs Brown Discourse Ratio
bars = ax1.bar(["Green Discourse", "Brown/Fossil Discourse"], [green_kw, brown_kw], color=["#38A169", "#E53E3E"], width=0.5, edgecolor="black")
ax1.set_ylabel("Keyword Mentions in Disclosures / News", fontsize=10, fontweight="bold")
ax1.set_title(f"{{ticker}} Disclosure Sentiment & Transition Focus", fontsize=12, fontweight="bold")
for bar in bars:
    yval = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2.0, yval + 0.1, int(yval), ha="center", va="bottom", fontweight="bold")

# 2. Donut Chart: Transition Share
labels = ["Green Effort", "Fossil / Legacy"]
sizes = [green_ratio, 100 - green_ratio]
colors_pie = ["#48BB78", "#CBD5E0"]
wedges, texts, autotexts = ax2.pie(
    sizes,
    labels=labels,
    autopct="%1.1f%%",
    startangle=140,
    colors=colors_pie,
    wedgeprops=dict(width=0.4, edgecolor="black"),
)
for at in autotexts:
    at.set_fontweight("bold")
ax2.set_title(f"Green Focus Ratio: {{green_ratio:.1f}}% (TKBI: {{tkbi_status}})", fontsize=12, fontweight="bold")

plt.suptitle(f"SustainMetric IDX: Green Effort Audit Trail for {{ticker}}", fontsize=14, fontweight="bold", y=1.02)
plt.tight_layout()
plt.show()
'''


def generate_financial_coverage_code(ticker: str, financial_summary: dict[str, Any]) -> str:
    """Generate code for Operating Cash Flow vs Capex coverage capacity."""
    fin_json = json.dumps(financial_summary, indent=2)

    return f'''import matplotlib.pyplot as plt
import seaborn as sns

fin = {fin_json}
ticker = "{ticker}"

ocf = fin.get("operating_cash_flow", fin.get("operating_cash_flow_idr_b", 0))
capex = fin.get("capex", fin.get("capex_idr_b", 0))
coverage = fin.get("capex_coverage_ratio", 0)

sns.set_theme(style="whitegrid")
fig, ax = plt.subplots(figsize=(8, 5), dpi=150)

metrics = ["Operating Cash Flow (OCF)", "Capital Expenditure (Capex)"]
values = [ocf, capex]
bar_colors = ["#3182CE", "#ED8936"]

bars = ax.bar(metrics, values, color=bar_colors, width=0.45, edgecolor="black")
for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width() / 2.0, h, f"{{h:,.1f}}", ha="center", va="bottom", fontweight="bold")

# Indicator line or status
status_color = "#38A169" if coverage >= 1.0 else "#E53E3E"
status_text = "Sustainable Green Capex Coverage (> 1.0x)" if coverage >= 1.0 else "Deficit / External Debt Dependent (< 1.0x)"

ax.set_title(f"{{ticker}} Financial Viability: OCF vs Capex Capacity\\nCoverage Ratio: {{coverage:.2f}}x ({{status_text}})", fontsize=12, fontweight="bold", pad=12, color=status_color)
ax.set_ylabel("Amount (in reporting units / Billions IDR)", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.show()
'''


def generate_emiten_radar_code(ticker: str, metrics: dict[str, float]) -> str:
    """Generate radar chart code evaluating emiten multi-axis sustainability metrics."""
    metrics_json = json.dumps(metrics, indent=2)

    return f'''import matplotlib.pyplot as plt
import numpy as np

ticker = "{ticker}"
scores = {metrics_json}

# Metric keys: TKBI Consistency, Capex Coverage, OCF Margin, Solvency, Disclosure Transparency
categories = list(scores.keys())
values = list(scores.values())

# Complete the loop for radar chart
N = len(categories)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
values += values[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True), dpi=150)
plt.xticks(angles[:-1], categories, color="#2D3748", size=10, fontweight="bold")

ax.set_rlabel_position(30)
plt.yticks([20, 40, 60, 80, 100], ["20", "40", "60", "80", "100"], color="#718096", size=8)
plt.ylim(0, 100)

# Plot polygon
ax.plot(angles, values, linewidth=2, linestyle="solid", color="#319795")
ax.fill(angles, values, color="#319795", alpha=0.3)

plt.title(f"SustainMetric IDX: {{ticker}} Sustainability & Fundamental Viability Radar", size=13, fontweight="bold", y=1.08)
plt.tight_layout()
plt.show()
'''


def build_visualization_payload(
    chart_type: str,
    ticker: str | None,
    audit_data: list[dict[str, Any]] | dict[str, Any],
) -> dict[str, Any]:
    """Router to generate Python matplotlib/seaborn code according to chart_type."""
    clean_type = (chart_type or "quadrant").lower().strip()

    if clean_type == "quadrant":
        items = audit_data if isinstance(audit_data, list) else [audit_data]
        code = generate_quadrant_chart_code(items)
        description = "4-Quadrant Algorithmic Matrix (Consistency vs Financial Viability) with color-coded risk boundaries."
    elif clean_type in ("green_effort", "green_effort_breakdown"):
        item = audit_data[0] if isinstance(audit_data, list) and audit_data else audit_data
        t = ticker or (item.get("ticker", "UNKNOWN") if isinstance(item, dict) else "UNKNOWN")
        code = generate_green_effort_code(t, item if isinstance(item, dict) else {})
        description = f"Green effort breakdown and transition discourse for {t}."
    elif clean_type in ("financial_coverage", "capex_coverage"):
        item = audit_data[0] if isinstance(audit_data, list) and audit_data else audit_data
        t = ticker or (item.get("ticker", "UNKNOWN") if isinstance(item, dict) else "UNKNOWN")
        fin = item.get("financial_summary", item) if isinstance(item, dict) else {}
        code = generate_financial_coverage_code(t, fin)
        description = f"Operating Cash Flow vs Capex capacity coverage for {t}."
    elif clean_type in ("radar", "emiten_radar"):
        item = audit_data[0] if isinstance(audit_data, list) and audit_data else audit_data
        t = ticker or (item.get("ticker", "UNKNOWN") if isinstance(item, dict) else "UNKNOWN")
        radar_metrics = {
            "TKBI Consistency": float(item.get("consistency_score", 50)),
            "Financial Viability": float(item.get("viability_score", 50)),
            "Capex Coverage": min(100.0, float(item.get("financial_summary", {}).get("capex_coverage_ratio", 1.0)) * 50.0),
            "ROA Metric": min(100.0, max(0.0, float(item.get("financial_summary", {}).get("roa_pct", 5.0)) * 10.0)),
            "Green Discourse": 80.0 if item.get("tkbi_alignment", {}).get("status") == "HIJAU" else 45.0,
        } if isinstance(item, dict) else {
            "TKBI Consistency": 50.0, "Financial Viability": 50.0, "Capex Coverage": 50.0, "ROA Metric": 50.0, "Green Discourse": 50.0
        }
        code = generate_emiten_radar_code(t, radar_metrics)
        description = f"Multi-axis sustainability & viability radar profile for {t}."
    else:
        # Default fallback to quadrant
        items = audit_data if isinstance(audit_data, list) else [audit_data]
        code = generate_quadrant_chart_code(items)
        description = f"4-Quadrant Matrix (unrecognized type '{chart_type}' defaulted to quadrant)."

    return {
        "chart_type": clean_type,
        "ticker": ticker,
        "description": description,
        "runtime": "python (matplotlib / seaborn)",
        "executable_code": code,
        "instructions": "Execute the provided 'executable_code' in a Python environment or Code Interpreter with matplotlib and seaborn installed.",
    }
