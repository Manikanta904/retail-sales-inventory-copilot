TRACK_ID=PS03

# Retail Sales & Inventory Copilot — NexusTiQ24 (PS03)

An intelligent, grounded retail store-manager operational command center and natural-language reasoning copilot designed for **NexusTiQ24 Track PS03 — Retail: Sales and Inventory Copilot**. The application enables store managers to monitor operational KPIs, evaluate stock-out risks, manage excess inventory, analyze sales anomalies, and query retail data through natural language with grounded, evidence-backed answers with validation and refusal when data is insufficient.

## Demo Video

[WATCH DEMO VIDEO](https://youtu.be/hw3csGNWxZc)

## Quick Start

To launch the application from the repository root:

1. **Install runtime dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application**:
   ```bash
   python app.py
   ```

3. **Access the application in your browser**:
   - **Application URL**: [http://localhost:8000](http://localhost:8000)
   - **Health Check Endpoint**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

> **Important Note for Judges**:
> - **No `npm` command is required** for judging.
> - **No Vite dev server is required** for judging.
> - **No second terminal is required**.
> - **No separate frontend build step is required**.
> - The pre-compiled production build in `frontend/dist` is committed to the repository and served directly by the Python FastAPI application on port `8000`.

---

## What the Project Does

Retail store managers face constant operational decisions: reordering inventory before stockouts occur, liquidating overstocked items, and responding to sudden sales volume spikes or drops. The **Retail Sales & Inventory Copilot** provides an intuitive decision-support system:

- **Operational Command Center (Dashboard)**: Visual indicators for active stores, product catalog size, revenue, out-of-stock items, critical coverage risks, low-stock warnings, overstock alerts, and sales volume anomalies.
- **Attention Summary Panel**: Priority-ranked operational issues (HIGH, MEDIUM, LOW severity) with direct numerical evidence.
- **Reasoning Copilot**: Natural-language assistant that parses manager questions, maps them to deterministic Python analytics, retrieves relevant retail rules, and generates grounded explanations with recommendations and explicit assumptions.
- **Strict Grounding & Deterministic Refusal**: When questions fall outside the available retail dataset (e.g., competitor pricing, weather data, or non-existent products like *PlayStation 7*), the system explicitly refuses to guess and explains what data is missing.

> **Architecture Principle**: Python performs all critical mathematical calculations deterministically (stock coverage, daily sales velocity, spike/drop ratios, revenue totals). Google Gemini is used solely for natural-language intent mapping, contextual reasoning, and user-facing explanation—never as the source of truth for numerical calculations.

---

## Key Capabilities

- **Stock-Out Risk Detection**: Flags depleted products (0 stock) and critical stockout risks (< 7.0 days of coverage based on recent sales velocity).
- **Overstock & Slow-Moving Analysis**: Identifies inventory exceeding 2.0x target levels combined with stagnant daily sales (<= 0.25 units/day).
- **Sales Spike & Drop Identification**: Pinpoints demand anomalies using 1.8x baseline spike and 0.4x baseline drop threshold ratios.
- **Product & Store Performance**: Calculates unit volumes, revenue totals, average daily sales velocity, and period-over-period growth rates.
- **Natural-Language Flexibility**: Supports diverse manager phrasing, informal wording, synonyms, and product abbreviations.
- **Structured Decision Evidence**: Responses provide relevant key metrics, structured evidence, grounded recommendations, assumptions, and source tags when applicable.

---

## How It Works / Architecture

```text
                                python app.py
                                      │
                              FastAPI / Uvicorn (:8000)
                                      │
                 ┌────────────────────┼────────────────────┐
                 ▼                    ▼                    ▼
             /api/*              frontend/dist        Gemini API
         Backend Endpoints     Production React UI  (gemini-3.5-flash-lite)
         (Python Analytics)    (Served on /)        (gemini-embedding-001)
```

1. **Frontend**: React application bundled with Vite (`frontend/dist`), providing an executive dashboard and interactive copilot interface.
2. **Backend**: FastAPI web server running on Uvicorn, exposing REST APIs for data, analytics, attention items, and copilot reasoning.
3. **Deterministic Core**: Python + Pandas + NumPy engine computing daily sales velocity, stock coverage days, spike/drop ratios, and store/product metrics.
4. **Local Retrieval (RAG)**: In-memory cosine similarity search over cached rule embeddings (`data/rules/embeddings_cache.json`) to fetch relevant retail management guidelines.
5. **AI Reasoning**: `gemini-3.5-flash-lite` handles query parsing and structured synthesis; `gemini-embedding-001` generates rule vector embeddings.
6. **Validation Engine**: Validates LLM responses against backend analytics evidence before rendering to guarantee consistency.

> **Technology Stack**: Python 3.11, FastAPI, Uvicorn, Pandas, NumPy, React, Vite (dev only), `google-genai` SDK. No FAISS, Chroma, SQLite, or external vector databases are used.

---

## Data and Documents

Grounding data and domain knowledge rules reside in the `data/` directory:

- `data/stores.csv`: 3 retail store locations (Flagship Store, Superstore, Express Store).
- `data/products.csv`: 25 active SKUs across Electronics, Home & Kitchen, Office Supplies, Groceries, and Apparel.
- `data/sales.csv`: 6,398 point-of-sale transaction records.
- `data/inventory.csv`: 6,750 daily store inventory snapshots.
- **Date Coverage**: June 1, 2026 through August 29, 2026 (90 days).
- **Business Rule Documents**:
  - `data/rules/inventory_rules.md`: Rules for stock coverage, reorder points, and overstock definitions.
  - `data/rules/sales_rules.md`: Rules for sales spikes, sales drops, and period comparison calculations.
  - `data/rules/recommendation_rules.md`: Guidelines for actionable inventory replenishment and liquidation.
  - `data/rules/embeddings_cache.json`: Pre-computed vector embeddings using `gemini-embedding-001`.

---

## Deterministic Analytics & Thresholds

Critical business logic and numerical calculations are centralized in `backend/services/analytics.py` and `backend/core/config.py`:

- **Stock Coverage Days**: `stock_on_hand / avg_daily_sales`
- **Critical Stock-Out Risk Threshold**: `< 7.0 days` of coverage (`CRITICAL_STOCK_DAYS_THRESHOLD = 7.0`)
- **Overstock Threshold**: `>= 2.0x` target stock level (`OVERSTOCK_MULTIPLIER_THRESHOLD = 2.0`)
- **Slow-Moving Sales Threshold**: `<= 0.25 units/day` (`SLOW_MOVING_DAILY_SALES_THRESHOLD = 0.25`)
- **Sales Spike Ratio**: `>= 1.8x` baseline sales (`SPIKE_RATIO_THRESHOLD = 1.8`)
- **Sales Drop Ratio**: `<= 0.4x` baseline sales (`DROP_RATIO_THRESHOLD = 0.4`)

---

## Grounded GenAI & Copilot Pipeline

When a store manager submits a query to `POST /api/copilot/query`:

1. **Intent Classification & Scope Guard**: Checks query intent and validates whether required entities (product, store) exist in the database.
2. **Deterministic Refusal**: If out-of-scope (e.g., competitor pricing, external market trends, weather) or referencing non-existent SKUs (e.g., *PlayStation 7*), returns an `insufficient_data` refusal payload immediately.
3. **Analytics Evidence Extraction**: Python computes exact numbers for the target intent (e.g., affected SKUs, coverage days, revenue totals).
4. **Local Rule Retrieval**: Retrieves matching rules from `data/rules/` using pre-computed `gemini-embedding-001` embeddings.
5. **Gemini Synthesis**: `gemini-3.5-flash-lite` formats the evidence into natural text, recommendations, and assumptions using strict JSON schema enforcement.
6. **Schema Validation**: Ensures all response fields match backend evidence before returning to the UI.

---

## Copilot Query Examples

### Supported Manager Questions
- **Stock-Out Risks**: *"Which products are at risk?"* or *"Anything I should reorder?"*
- **Overstock & Excess**: *"What do we have too much of?"* or *"Which items are sitting around?"*
- **Slow-Moving Inventory**: *"Which products aren't moving?"*
- **Sales Trends**: *"Which products suddenly started selling more?"* or *"Which items are losing sales?"*
- **Product Performance**: *"How did Wireless Ergonomic Mouse perform this month?"* or *"How is the mouse doing?"*
- **Store & Catalog Information**: *"What stores do we have?"* or *"What do we sell?"*

### Insufficient-Data Refusal Example
- **Query**: *"Did competitor pricing cause the sales drop?"*
- **Response Status**: `insufficient_data`
- **Explanation**: The system explains that sales drop data is available, but competitor pricing data is not present in the store dataset, refusing to generate unsupported assumptions.

---

## API Endpoints

- `GET /api/health` — Application health check and status (`{"status": "ok", "message": "Service is healthy"}`).
- `GET /api/dashboard` — High-level retail KPIs (total stores, products, transactions, YTD revenue, units sold, out-of-stock count, critical risk count, low stock warnings, overstocked items count, sales spikes, sales drops, date range).
- `GET /api/attention` — Priority-ranked operational attention items (HIGH, MEDIUM, LOW severity) with supporting evidence.
- `GET /api/products` — Complete product catalog with product ID, product name, category, cost price, unit price, reorder point, and target stock level.
- `GET /api/stores` — Store directory with store ID, store name, location (city/state), geographic region, and store format type.
- `POST /api/copilot/query` — Primary natural-language reasoning endpoint. Accepts `CopilotQueryRequest` (`question`, optional filters) and returns structured response containing answer, findings, evidence, assumptions, recommendations, structured items, summary metrics, and data sources.

---

## Judge Setup & Configuration

### Prerequisites
- **Python 3.11+**
- `GEMINI_API_KEY` environment variable set.

### Environment Variable Setup
Set your API key prior to launching:

```bash
# Linux/macOS
export GEMINI_API_KEY="your-gemini-api-key"

# Windows PowerShell
$env:GEMINI_API_KEY="your-gemini-api-key"

# Windows Command Prompt
set GEMINI_API_KEY=your-gemini-api-key
```

Alternatively, place `GEMINI_API_KEY=your-gemini-api-key` inside a `.env` file in the repository root.

### Launch Command
```bash
pip install -r requirements.txt
python app.py
```
Access at [http://localhost:8000](http://localhost:8000).

---

## Development Setup (Optional / Contributor Only)

If modifying frontend source code in `frontend/src/`:

```bash
cd frontend
npm install
npm run dev      # Runs Vite dev server on http://localhost:3000 (proxies /api to :8000)
npm run build    # Compiles production bundle into frontend/dist
```

> **Note**: This workflow is strictly optional for developers modifying React source code and is **not required for hackathon judging**.

---

## Security & Configuration

- **Zero Credentials Committed**: Secrets are read exclusively from environment variables or local uncommitted `.env` files.
- **Git Ignored Artifacts**: `.env`, `.venv`, `node_modules`, and cache directories are excluded via `.gitignore`.

---

## Project Structure

```text
retail-sales-inventory-copilot/
├── app.py                      # Root FastAPI production entry point (Port 8000)
├── requirements.txt            # Python dependencies
├── README.md                   # Submission documentation
├── .env.example                # Example environment file
├── backend/
│   ├── api/
│   │   └── routes.py           # FastAPI REST endpoints
│   ├── core/
│   │   └── config.py           # Application config & analytics thresholds
│   ├── models/
│   │   └── schemas.py          # Pydantic request/response schemas
│   └── services/
│       ├── analytics.py        # Deterministic retail math & anomaly detection
│       ├── copilot.py          # Copilot orchestration engine
│       ├── data_service.py     # CSV data loader & indexing
│       ├── gemini_service.py   # Gemini API integration & schema validation
│       ├── intent.py           # Query intent parser & scope validator
│       └── retrieval.py        # Local cosine similarity RAG engine
├── data/
│   ├── stores.csv              # Store catalog (3 stores)
│   ├── products.csv            # Product catalog (25 products)
│   ├── sales.csv               # Point-of-sale transaction data (6,398 rows)
│   ├── inventory.csv           # Daily inventory snapshots (6,750 rows)
│   └── rules/                  # Domain business rules & embedding cache
└── frontend/
    ├── src/                    # React UI source code
    └── dist/                   # Pre-built production frontend (served by FastAPI)
```

---

## Demo Flow

For a 2-minute judge walkthrough:

1. **Dashboard Overview**: Open [http://localhost:8000](http://localhost:8000). View executive KPIs, out-of-stock counts, critical risks, and the prioritized Attention Panel.
2. **Stock-Out Query**: Click *Reasoning Copilot* or *Open Retail Copilot*. Ask: *"Which products are at risk?"*. Review the numerical metrics, evidence table, actionable reorder recommendations, and assumptions.
3. **Product Performance**: Ask: *"How did Wireless Ergonomic Mouse perform this month?"*. Review unit volume (392 units), total revenue ($19,596.08), percentage growth (+3.16%), and performance breakdown.
4. **Grounded Refusal**: Ask: *"Did competitor pricing cause the sales drop?"*. Observe the system's explicit refusal to guess due to unavailable competitor pricing data.

---

## Hackathon Alignment (PS03)

- **Numerical Grounding**: Every claim is backed by deterministic Python calculations on actual CSV sales/inventory data.
- **Dual AI Synergy**: Combines fast local vector retrieval (`gemini-embedding-001`) with structured reasoning (`gemini-3.5-flash-lite`).
- **Grounded Decision Support**: Provides evidence, assumptions, recommendations, and source tags for every query.
- **Hallucination Prevention**: Deterministic refusal pipeline prevents AI guessing when required data is missing.
- **Judge Simplicity**: Single command (`python app.py`), single port (`8000`), zero manual build steps.

---

## Data Scope & Coverage

- The included retail dataset covers point-of-sale sales and daily inventory snapshots from **June 1, 2026 to August 29, 2026** (90-day static baseline dataset). All analytical insights, stock coverage calculations, and period comparisons are computed against this defined dataset.
