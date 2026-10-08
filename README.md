# SustainMetric IDX: The Algorithmic Green Auditor

[![PyPI version](https://img.shields.io/pypi/v/sustainmetric-idx.svg)](https://pypi.org/project/sustainmetric-idx/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SustainMetric IDX** is a production-grade FastMCP (Model Context Protocol) Server for auditing Indonesia Stock Exchange (IDX) listed equities against greenwashing risks. It cross-examines qualitative corporate ESG narratives against empirical financial statements (via [Sectors Financial API v2](https://sectors.app)) and regulatory thresholds established by the **OJK TKBI Versi 3 (Taksonomi Keuangan Berkelanjutan Indonesia)**.

---

## 1. Core Architecture & Highlights

- **Protocol**: FastMCP over `stdio` (local agent clients) and `SSE` (networked agents).
- **Durable Asynchronous Task Queue**: Decoupled worker queue with SQLite persistence (`QUEUED` → `PROCESSING` → `COMPLETED`), eliminating agent connection timeouts during multi-ticker audits.
- **Embedded OJK TKBI Versi 3 Vector Store**: Zero C++ dependency vector store utilizing SQLite and NumPy cosine similarity for fast semantic retrieval of Technical Screening Criteria (TSC), Do No Significant Harm (DNSH), and Minimum Social Safeguards (MSS).
- **Sectors Financial API v2 Integration**: Robust client featuring SHA-256 disk cache (7-day financials TTL, 24h news TTL) and offline fixture fallback to preserve API credit quotas.
- **4-Quadrant Algorithmic Matrix Classifier**:
  - **Q1 - STRONG FUNDAMENTAL AND SUSTAINABLE**: High Green Consistency (≥60) & High Financial Viability (≥60).
  - **Q2 - SUSTAINABLE BUT HIGH FINANCIAL RISK**: High Green Consistency (≥60) & Low Financial Viability (<60).
  - **Q3 - GREENWASHING RISK ZONE**: Low Green Consistency (<60) & High Financial Viability (≥60).
  - **Q4 - NOT CONSIDERED**: Low Green Consistency (<60) & Low Financial Viability (<60).
- **Automated TKBI Audit Spreadsheet Generation**: Produces audit-ready Excel workbooks (`{emiten}_audit_TKBI.xlsx`) mapped directly to OJK TKBI evaluation templates across all 8 taxonomy sectors.
- **On-Demand Visualization Engine**: Emits ready-to-execute Python/matplotlib/seaborn code for Code Interpreters (`quadrant`, `green_effort`, `financial_coverage`, `radar`).

---

## 2. Universal Agent Client Setup (BYOK: Bring Your Own Key)

Anyone can connect `sustainmetric-idx` directly to their favorite agent client without cloning this repository.

### Prerequisites
- Install [`uv`](https://docs.astral.sh/uv/) (recommended) or standard Python 3.11+.
- Obtain your Sectors API key from [sectors.app](https://sectors.app/api).

---

### A. Claude Desktop
Add to `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "sustainmetric-idx": {
      "command": "uvx",
      "args": ["sustainmetric-idx"],
      "env": {
        "SECTORS_API_KEY": "your_sectors_api_key_here"
      }
    }
  }
}
```

---

### B. Cursor
Navigate to **Cursor Settings** → **Features** → **MCP Servers** → **Add New MCP Server**:
- **Name**: `sustainmetric-idx`
- **Type**: `command`
- **Command**: `uvx sustainmetric-idx`
- Add environment variable `SECTORS_API_KEY=your_sectors_api_key_here`.

---

### C. OpenCode
Add to `~/.config/opencode/opencode.json` (or your project's `opencode.jsonc`):

```json
{
  "mcp": {
    "sustainmetric-idx": {
      "type": "local",
      "command": ["uvx", "sustainmetric-idx"],
      "environment": {
        "SECTORS_API_KEY": "your_sectors_api_key_here"
      }
    }
  }
}
```

---

### D. Hermes Agent
Add to Hermes MCP server registry:

```yaml
mcp_servers:
  sustainmetric-idx:
    command: uvx
    args:
      - sustainmetric-idx
    env:
      SECTORS_API_KEY: "your_sectors_api_key_here"
```

---

## 3. Local Installation & Development

If you wish to develop or run directly from source:

```powershell
# Clone the repository
git clone https://github.com/personal-radyadhewa/Hackathon-2026-SectorsApp-SustainmetricsMCP.git
cd Hackathon-2026-SectorsApp-SustainmetricsMCP

# Create and activate environment
uv venv --python 3.12
.\.venv\Scripts\activate

# Install editable package with dev dependencies
uv pip install -e ".[dev]"

# Copy environment template
cp .env.example .env
```

### Running Server Directly

#### Standard I/O (stdio)
```powershell
sustainmetric-idx
# or
python -m sustainmetric.server
```

#### Server-Sent Events (SSE)
```powershell
sustainmetric-idx --transport sse --host 0.0.0.0 --port 8000
```

---

## 4. MCP Tools Reference

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `trigger_green_audit` | `tickers: list[str]` | Initiates asynchronous quantitative green audit for IDX tickers. Returns immediate `task_id` (`QUEUED`). |
| `get_audit_status` | `task_id: str` | Polls audit progress and retrieves 4-quadrant coordinates, scores, and findings. |
| `query_tkbi_knowledge_base` | `query: str`, `top_k: int = 3` | Semantic similarity search against embedded OJK TKBI Versi 3 rules (TSC, DNSH, MSS). |
| `inspect_ticker_evidence` | `ticker: str` | Retrieves raw cached financial data, Capex line items, news claims, and taxonomy citations. |
| `visualize_green_audit` | `chart_type: str`, `ticker: str` | Generates executable Python visualization code (`quadrant`, `green_effort`, `financial_coverage`, `radar`). |
| `generate_tkbi_audit_checklist` | `ticker: str`, `sector: str` | Exports comprehensive audit checklist in Excel (`{emiten}_audit_TKBI.xlsx`) conforming to `Template_Audit_TKBI.xlsx`. |

---

## 5. Automated Tests

Run the test suite to verify scoring invariants, cache integrity, and task queue resilience:

```powershell
pytest tests/ -v
```

---

## 6. Disclaimer

> **Information & Analysis Tool Only. Not Financial Advice or Investment Recommendation.**  
> SustainMetric IDX is an algorithmic audit and compliance research framework. It does not provide financial advice, price targets, or trading recommendations.
