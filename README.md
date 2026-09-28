# SustainMetric IDX: The Algorithmic Green Auditor

Production-grade FastMCP Server auditing Indonesia Stock Exchange (IDX) equities against greenwashing risks using OJK TKBI 2024 (Taksonomi Keuangan Berkelanjutan Indonesia) and empirical fundamental financial metrics.

---

## 1. Core Architecture & Features

- **Protocol**: FastMCP over `stdio` (local agent clients) and `SSE` (networked agents).
- **Durable Task Queue**: Decoupled async worker with SQLite task persistence (`QUEUED` → `PROCESSING` → `COMPLETED`), eliminating agent connection timeouts.
- **Embedded TKBI 2024 Vector Store**: Zero C++ dependency vector store utilizing SQLite and NumPy cosine similarity for fast semantic retrieval of Technical Screening Criteria (TSC), Do No Significant Harm (DNSH), and Minimum Social Safeguards (MSS).
- **Sectors API v2 Client**: Robust HTTP client with SHA-256 disk cache (7-day financials TTL, 24h news TTL) and offline fixture fallback to preserve the 1,000 credit budget.
- **4-Quadrant Matrix Classifier**: Maps tickers on Consistency Score (0–100) vs Fundamental Viability Score (0–100):
  - **Q1 - Transisi Tangguh**: High green alignment + robust cash flow.
  - **Q2 - Dampak Spekulatif**: High green narrative + fragile fundamentals / high leverage.
  - **Q3 - Sumber Kas Konvensional**: High cash generation + legacy fossil operations.
  - **Q4 - Tertinggal & Red Flag**: Low green alignment + deteriorative fundamentals.

---

## 2. Quickstart & Installation

### Requirements
- Python 3.11+ (Python 3.12 recommended)
- `uv` package manager (or standard `pip`)

```powershell
# Create virtual environment
uv venv --python 3.12
.\.venv\Scripts\activate

# Install editable package with dev dependencies
uv pip install -e ".[dev]"
```

### Environment Configuration
Copy `.env.example` to `.env` and set your Sectors API key (optional during testing; server automatically falls back to bundled fixtures `PGEO`, `ADRO`, `BBRI`, `BREN`, `BUMI`):

```bash
cp .env.example .env
```

---

## 3. Running the Server

### Standard I/O Mode (Claude Desktop, Cursor, Hermes)
```powershell
python -m sustainmetric.server
```

### Server-Sent Events (SSE) Mode
```powershell
python -m sustainmetric.server --transport sse --host 0.0.0.0 --port 8000
```

---

## 4. Client Integration

### Claude Desktop Configuration
Add to `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "sustainmetric-idx": {
      "command": "C:\\Users\\radyadhewa\\Storage\\code\\personal\\Hackathon-SectorsApp-SustainmetricsMCPServer\\.venv\\Scripts\\python.exe",
      "args": ["-m", "sustainmetric.server"],
      "env": {
        "SECTORS_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Cursor Configuration
Add to Cursor MCP settings:
- **Type**: `command`
- **Command**: `.\.venv\Scripts\python.exe -m sustainmetric.server`

---

## 5. FastMCP Tools Reference

1. `trigger_green_audit(tickers: list[str]) -> dict`:
   Accepts ticker list, returns immediate `task_id` and `status: "QUEUED"`.
2. `get_audit_status(task_id: str) -> dict`:
   Polls task state and retrieves full 4-quadrant matrix results and audit findings.
3. `query_tkbi_knowledge_base(query: str, top_k: int = 3) -> dict`:
   Queries OJK TKBI 2024 database for sector rules, TSC, DNSH, and MSS.
4. `inspect_ticker_evidence(ticker: str) -> dict`:
   Inspects raw financials, news claims, and TKBI citations for a single ticker.
5. `visualize_green_audit(chart_type: str = "quadrant", ticker: str = None, task_id: str = None) -> dict`:
   Generates executable matplotlib/seaborn code on-demand for Code Interpreters (`quadrant`, `green_effort`, `financial_coverage`, `radar`).

---


## 6. Running Tests

```powershell
.\.venv\Scripts\pytest.exe tests/ -v
```

All 12 automated unit and integration tests verify cache hits, semantic search accuracy, scoring invariants, and end-to-end task worker completion.
