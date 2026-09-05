TRACK_ID=PS03

# Retail Sales & Inventory Copilot — NexusTiQ24 (PS03)

An intelligent, grounded retail store-manager operational command center and natural-language reasoning copilot designed for **NexusTiQ24 Track PS03 — Retail: Sales and Inventory Copilot**.

---

## 1. Executive Summary & Problem Understanding

Store managers face complex daily operational decisions regarding stock replenishment, excess inventory management, and demand anomaly response. The **Retail Sales & Inventory Copilot** bridges numerical analytics and natural-language decision support:

1. **Operational Command Center (Dashboard)**: Provides real-time visual breakdown of stockout risks, overstocked items, low stock warnings, sales volume spikes/drops, and an operational attention panel prioritized by severity.
2. **Reasoning Copilot**: A natural-language assistant grounded strictly in Python deterministic analytics and local retail business rules using official Google Gemini models.

---

## 2. Key Capabilities

- **Stock-Out Risk Identification**: Detects depleted products (0 stock) and critical stockout risks (< 7.0 days coverage) based on recent sales velocity.
- **Overstock & Slow-Moving Detection**: Identifies excess stock (>= 2.0x target levels) and stagnant products (<= 0.25 units/day).
- **Sales Trend Anomaly Detection**: Highlights sales volume spikes (>= 1.8x baseline ratio) and sales drops (<= 0.4x baseline ratio).
- **Product & Store Performance**: Computes unit volumes, revenue totals, average daily sales velocity, and period-over-period percentage growth.
- **Natural-Language Understanding**: Maps manager questions across broad phrasing, synonyms, informal wording, and retail abbreviations to core analytics intents.
- **Grounding & Refusals**: Deterministically rejects out-of-scope queries (weather, non-retail technical tasks), external market factors (competitor pricing), and non-existent products (*PlayStation 7*) before LLM reasoning.

---

## 3. Architecture

```text
               python app.py
                    │
            FastAPI / Uvicorn (:8000)
                    │
   ┌────────────────┼────────────────┐
   ▼                ▼                ▼
/api/*       frontend/dist      Gemini API
Backend      Production UI     (gemini-3.5-flash-lite)
Endpoints    (Served on /)     (gemini-embedding-001)
```

- **Backend**: Python 3.11 + FastAPI + Uvicorn + Pandas + NumPy.
- **Frontend**: React + Vite pre-compiled production bundle (`frontend/dist`), served directly by FastAPI on port 8000.
- **AI Layer**: `gemini-3.5-flash-lite` (LLM reasoning) & `gemini-embedding-001` (RAG rule embeddings).
- **Local RAG**: In-memory cosine similarity retrieval over pre-computed rule embeddings (`data/rules/embeddings_cache.json`).

---

## 4. Retail Dataset Overview

Grounding data is stored in standard CSV files (`data/`):
- `data/stores.csv`: 3 active retail stores (Flagship, Superstore, Express formats).
- `data/products.csv`: 25 active SKUs across Electronics, Home & Kitchen, Office Supplies, Groceries, and Apparel.
- `data/sales.csv`: 6,398 point-of-sale transactions.
- `data/inventory.csv`: 6,750 daily inventory snapshots.
- **Data Coverage**: June 1, 2026 through August 29, 2026 (90 days).

---

## 5. Judge Quickstart & Application Startup

### Prerequisites
- Python 3.11+
- `GEMINI_API_KEY` set in environment or `.env` file in repository root.

### One-Command Judge Startup

```bash
# 1. Install runtime dependencies
pip install -r requirements.txt

# 2. Launch application (Single Port 8000)
python app.py
```

### Access Points
- **Web Command Center & Copilot**: [http://localhost:8000](http://localhost:8000)
- **API Health Endpoint**: [http://localhost:8000/api/health](http://localhost:8000/api/health)

> **Note for Judges**: The pre-built React production frontend (`frontend/dist`) is committed and served directly by FastAPI on port `8000`. You do **NOT** need to run `npm`, Vite, or any secondary server commands.

---

## 6. Development Setup (Optional / Contributor Only)

If modifying frontend source code (`frontend/src/`):

```bash
cd frontend
npm install
npm run dev      # Launches Vite dev server on http://localhost:3000 (proxies /api to :8000)
npm run build    # Rebuilds production bundle into frontend/dist
```

---

## 7. Natural-Language Copilot Query Examples

- **Stock-Out Risk**: *"Which products are at risk?"* or *"Anything I should reorder?"*
- **Overstock**: *"What do we have too much of?"* or *"Which items are sitting around?"*
- **Slow Moving**: *"Which products aren't moving?"*
- **Sales Trends**: *"What products suddenly started selling more?"* or *"Which products are losing sales?"*
- **Product Performance**: *"How did Wireless Ergonomic Mouse perform this month?"* or *"How is the mouse doing?"*
- **Store & Catalog Info**: *"What stores do we have?"* or *"What do we sell?"*
- **Refusal / Out-of-Scope**: *"Did competitor pricing cause the sales drop?"* or *"What is the weather today?"*

---

## 8. Security & Environment Configuration

- **API Keys**: Configured via `GEMINI_API_KEY` environment variable. Zero credentials committed to Git.
- **Ignored Artifacts**: `.env`, `.venv`, and `node_modules` are excluded in `.gitignore`.

