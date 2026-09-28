# AGENTS.md - SustainMetric IDX: The Algorithmic Green Auditor

System specification and operational directives for AI agents operating on or consuming the SustainMetric IDX FastMCP server.

---

## 1. System Identity & Mission

- **Name**: SustainMetric IDX (`sustainmetric-idx`)
- **Role**: Algorithmic Greenwashing Auditor & Fundamental Viability Evaluator for Indonesia Stock Exchange (IDX) listed equities.
- **Protocol**: FastMCP (Model Context Protocol) over `stdio` and `SSE`.
- **Target Runtimes**: Hermes, Claude Desktop, Cursor, Antigravity, Open-source LLM agent loops.
- **Mandatory Guardrail**: Strictly an information, audit, and data intelligence tool. Zero automated trading, zero financial advice.
- **Audit Disclaimer**: `"Information & Analysis Tool Only. Not Financial Advice or Investment Recommendation."` (Mandatory in every tool payload).

---

## 2. System Architecture & Topology

```
                  ┌───────────────────────────────────────────────┐
                  │           Agent Runtime (Client)             │
                  │       (Hermes / Claude / Cursor / CLI)        │
                  └───────────────────────┬───────────────────────┘
                                          │ FastMCP (stdio / SSE)
                                          ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│ SustainMetric FastMCP Server (`server.py`)                                      │
│                                                                                 │
│ ┌─────────────────────────┐  ┌────────────────────────────────────────────────┐ │
│ │ Tool Dispatcher         │  │ Durable Background Task Queue (`task_queue.py`)│ │
│ │ - trigger_green_audit   │  │ - UUID Tracking (QUEUED → RUNNING → DONE)      │ │
│ │ - get_audit_status      │  │ - SQLite / JSON Task State Persistence         │ │
│ │ - query_tkbi_kb         │  │ - Prevents Agent Protocol Timeout              │ │
│ │ - inspect_ticker_evidence│ └───────────────────────┬────────────────────────┘ │
│ └─────────────────────────┘                          │                          │
│                                                      ▼                          │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │ Quantitative Scoring Engine (`scoring_engine.py`)                           │ │
│ │                                                                             │ │
│ │ ┌─────────────────────────────┐         ┌─────────────────────────────────┐ │ │
│ │ │ TKBI Consistency Engine     │         │ Financial Viability Engine      │ │ │
│ │ │ - Qualitative claims parsing│         │ - Operating Cash Flow (OCF)     │ │ │
│ │ │ - TKBI 2024 alignment score │         │ - Capex / OCF Coverage Ratio    │ │ │
│ │ │ - Capex green/brown check   │         │ - ROA, Net Debt / EBITDA        │ │ │
│ │ └──────────────┬──────────────┘         └────────────────┬────────────────┘ │ │
│ │                │                                         │                  │ │
│ │                ▼                                         ▼                  │ │
│ │         [ Consistency Score: 0-100 ]            [ Viability Score: 0-100 ]  │ │
│ │                                ╲                     ╱                      │ │
│ │                                 ▼                   ▼                       │ │
│ │                           4-Quadrant Matrix Classifier                      │ │
│ └──────────────────────────────────────┬──────────────────────────────────────┘ │
│                                        │                                        │
│                 ┌──────────────────────┴──────────────────────┐                 │
│                 ▼                                             ▼                 │
│ ┌───────────────────────────────┐           ┌─────────────────────────────────┐ │
│ │ TKBI Vector Store             │           │ Sectors API Client              │ │
│ │ (`tkbi_vector_store.py`)      │           │ (`sectors_client.py`)           │ │
│ │ - OJK TKBI 2024 Taxonomy DB   │           │ - Sectors Financial API v2      │ │
│ │ - TSC, DNSH, MSS Criteria     │           │ - Strict File Cache (SHA-256)   │ │
│ │ - Key Sectors: Geothermal,    │           │ - 1,000 Credit Protection Shield│ │
│ │   Coal Transition, Renewables,│           │ - Fallback & Mock Data Fixtures │ │
│ │   Banking GAR                 │           └─────────────────────────────────┘ │
│ └───────────────────────────────┘                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Four-Quadrant Classification Framework

Coordinates: `(Viability Score X ∈ [0, 100], Consistency Score Y ∈ [0, 100])`

| Quadrant | Name | Criteria | Definition & Audit Verdict |
| :--- | :--- | :--- | :--- |
| **Q1** | **Transisi Tangguh** | `Consistency ≥ 60` ∧ `Viability ≥ 60` | High green alignment backed by robust cash flow and Capex. True sustainable compounders. |
| **Q2** | **Dampak Spekulatif** | `Consistency ≥ 60` ∧ `Viability < 60` | High green narrative/alignment but fragile fundamentals (cash burn, high leverage). Execution risk. |
| **Q3** | **Sumber Kas Konvensional** | `Consistency < 60` ∧ `Viability ≥ 60` | High cash generation with legacy/fossil profile and low TKBI alignment. High greenwashing vulnerability if claiming green status. |
| **Q4** | **Tertinggal & Red Flag** | `Consistency < 60` ∧ `Viability < 60` | Low green alignment + deteriorative fundamentals. High obsolescence and default risk. |

---

## 4. MCP Tools Specification

### 4.1. `trigger_green_audit`
- **Signature**: `trigger_green_audit(tickers: list[str]) -> dict`
- **Behavior**: Validates tickers, assigns `task_id` (UUIDv4), persists task state as `QUEUED`, spawns background worker, returns immediately (< 500ms).
- **Response**:
  ```json
  {
    "task_id": "7f8b9a12-e34b-4a56-8c7d-9912a5df6781",
    "status": "QUEUED",
    "tickers": ["PGEO", "ADRO", "BBRI"],
    "poll_tool": "get_audit_status",
    "disclaimer": "Information & Analysis Tool Only. Not Financial Advice or Investment Recommendation."
  }
  ```

### 4.2. `get_audit_status`
- **Signature**: `get_audit_status(task_id: str) -> dict`
- **Behavior**: Retrieves task state (`QUEUED`, `PROCESSING`, `COMPLETED`, `FAILED`).
- **Response (`COMPLETED`)**:
  ```json
  {
    "task_id": "7f8b9a12-e34b-4a56-8c7d-9912a5df6781",
    "status": "COMPLETED",
    "results": [
      {
        "ticker": "PGEO",
        "quadrant": "Transisi Tangguh",
        "consistency_score": 88.5,
        "viability_score": 76.2,
        "tkbi_alignment": {
          "status": "HIJAU",
          "matched_criteria": "TKBI 2024 §4.1.2 - Geothermal Power Generation GHG < 100g CO2e/kWh",
          "dnsh_compliance": true
        },
        "financial_summary": {
          "operating_cash_flow_idr_b": 3450.2,
          "capex_idr_b": 2100.0,
          "roa_pct": 6.8,
          "capex_coverage_ratio": 1.64
        },
        "audit_findings": [
          "Capex is 85% allocated to geothermal expansion (capacity addition).",
          "Operating cash flow comfortably covers planned green capital expenditure."
        ]
      }
    ],
    "disclaimer": "Information & Analysis Tool Only. Not Financial Advice or Investment Recommendation."
  }
  ```

### 4.3. `query_tkbi_knowledge_base`
- **Signature**: `query_tkbi_knowledge_base(query: str, top_k: int = 3) -> list[dict]`
- **Behavior**: Semantic similarity search against embedded OJK TKBI 2024 database.
- **Response**: List of chunks containing `sector`, `code`, `criteria_level` (`Hijau`/`Transisi`/`Merah`), `threshold_rule`, `citation`, and `similarity_score`.

### 4.4. `inspect_ticker_evidence`
- **Signature**: `inspect_ticker_evidence(ticker: str) -> dict`
- **Behavior**: Retrieves raw cached audit trail: qualitative news claims vs Capex line items, discrepancies, and TKBI rule matches.

### 4.5. `visualize_green_audit`
- **Signature**: `visualize_green_audit(chart_type: str = "quadrant", ticker: str | None = None, task_id: str | None = None) -> dict`
- **Behavior**: Enabled on-demand when requested by the user. Generates ready-to-execute Python matplotlib/seaborn code for Code Interpreter execution.
- **Chart Types**:
  - `quadrant`: 4-Quadrant consistency vs viability classification matrix with risk zones.
  - `green_effort`: Green vs brown transition discourse and disclosure breakdown.
  - `financial_coverage`: Operating Cash Flow (OCF) vs green Capex capacity.
  - `radar`: Multi-axis sustainability and fundamental viability radar profile.
- **Response**:
  ```json
  {
    "chart_type": "green_effort",
    "ticker": "PGEO",
    "description": "Green effort breakdown and transition discourse for PGEO.",
    "runtime": "python (matplotlib / seaborn)",
    "executable_code": "import matplotlib.pyplot as plt...",
    "instructions": "Execute the provided 'executable_code' in a Python environment or Code Interpreter with matplotlib and seaborn installed.",
    "disclaimer": "Information & Analysis Tool Only. Not Financial Advice or Investment Recommendation."
  }
### 4.6. `generate_tkbi_audit_checklist`
- **Signature**: `generate_tkbi_audit_checklist(ticker: str, sector: str | None = None, output_dir: str = ".") -> dict`
- **Behavior**: Maps emiten to the 8 TKBI Versi 3 focus & enabling sectors, evaluates Technical Screening Criteria (TSC) and DNSH/social safeguards, and generates standard Excel checklist `{emiten}_audit_TKBI.xlsx` conforming to `Template_Audit_TKBI.xlsx`.
- **Response**:
  ```json
  {
    "ticker": "PGEO",
    "status": "SUCCESS",
    "file_generated": "/path/to/PGEO_audit_TKBI.xlsx",
    "file_name": "PGEO_audit_TKBI.xlsx",
    "mapped_sector": "Energi",
    "tkbi_version": "TKBI Versi 3 (2026)",
    "message": "Successfully generated TKBI audit checklist for PGEO at PGEO_audit_TKBI.xlsx",
    "disclaimer": "Information & Analysis Tool Only. Not Financial Advice or Investment Recommendation."
  }
  ```

---



## 5. Data Invariants & Quota Protection

1. **Strict 1,000 API Credit Quota**:
   - Every Sectors API HTTP call is checked against disk cache (`.cache/sectors/{sha256}.json`).
   - Default Cache TTL: 7 days for financials, 24 hours for news.
   - Offline fallback mode: If API credits exhausted or key absent, load local mock fixtures (`fixtures/{ticker}.json`).
2. **Platform Portability (Windows ARM64 / x86_64 / Linux)**:
   - Vector Store implementation must support native execution without native C++ compilation failures.
   - Recommended engine: LanceDB or embedded SQLite + cosine similarity (using numpy/fastembed/OpenAI).
3. **No Financial Advice Rule**:
   - Every response payload must include `disclaimer`.
   - Never output buy/sell/hold ratings or price targets.
