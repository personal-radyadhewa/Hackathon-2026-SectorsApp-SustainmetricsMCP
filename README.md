# SustainMetric IDX: The Algorithmic Green Auditor

Production-grade FastMCP Server auditing Indonesia Stock Exchange (IDX) equities against greenwashing risks using OJK TKBI 2024 sustainable taxonomy and empirical fundamental financial metrics.

## Features
- **FastMCP Protocol**: Operates over standard I/O (`stdio`) and Server-Sent Events (`SSE`).
- **Durable Task Queue**: Async background worker with SQLite state persistence prevents agent protocol timeouts.
- **Embedded TKBI 2024 Vector Store**: Technical Screening Criteria (TSC) semantic retrieval across Geothermal, Coal Transition, Renewables, and Banking.
- **Sectors API v2 Integration**: Resilient client with SHA-256 disk cache and 1,000 credit quota protection shield.
- **4-Quadrant Classifier**: Maps companies on Consistency Score (0-100) vs Fundamental Viability Score (0-100).
