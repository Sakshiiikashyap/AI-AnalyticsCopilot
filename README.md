# AI Analytics Copilot

An AI-powered data analyst assistant. Upload a CSV or Excel file and get automated data profiling, AI-grounded chat, machine-learning forecasting, anomaly detection, and AI-generated executive insight reports — all backed by real computation, not hallucinated numbers.

**This is a copilot for analysts, not a replacement.** Every AI-generated answer is grounded in actual statistics computed from your data; the LLM explains and narrates, it never invents.

---

## Live Demo

- Frontend: [your-deployed-frontend-url]
- API docs: [your-deployed-backend-url]/docs

---

## Why this project

Manual exploratory data analysis (EDA) is repetitive: checking for missing values, duplicates, outliers, correlations, writing summaries, building forecasts. This project automates the repetitive analytical work while keeping a human analyst in control of the interpretation and decisions.

## Features

- **Dataset Upload** — CSV/XLSX, with defensive parsing for messy real-world files (inconsistent date formats, placeholder null values, encoding quirks)
- **Automated Profiling** — missing values, duplicate detection, IQR-based outlier detection, correlation analysis
- **AI Chat With Data (RAG-grounded)** — ask questions in plain English; a query engine first attempts a real pandas computation, then an LLM (Gemini) explains the result. The LLM is never shown raw data and is instructed to answer only from computed context.
- **Forecasting** — XGBoost-based time-series forecasting with engineered lag/rolling/calendar features, recursive multi-step prediction, and **backtest validation** (MAE/RMSE on held-out historical data) so forecast accuracy is measurable, not a black box.
- **Anomaly Detection** — Isolation Forest (multivariate, contamination-tunable) and DBSCAN (density-based, data-driven eps estimation), independently cross-validated against each other.
- **AI Insight Engine** — proactively synthesizes profile + anomaly + forecast results into a structured executive summary (key findings, risks, opportunities, recommendations).
- **PDF Executive Reports** — one-click downloadable report combining all of the above.
- **Auth** — JWT-based signup/login/refresh, rate-limited against brute force, password reset flow.

## Tech Stack

**Backend:** Python, FastAPI, SQLAlchemy, PostgreSQL (Neon), Pandas, NumPy, scikit-learn, XGBoost, Google Gemini API, ReportLab

**Frontend:** Next.js (App Router), TypeScript, Tailwind CSS, Framer Motion, Recharts

**Architecture:** Feature-based clean architecture (each domain — auth, datasets, profiling, chat, forecasting, anomaly, insights, reports — is a self-contained module with its own models/schemas/service/routes). LLM provider is abstracted behind an interface so the underlying model (currently Gemini) can be swapped without touching calling code.

## Architecture Overview

Browser (Next.js)

|

FastAPI (versioned REST API, JWT auth, rate limiting)

|

+---+---+---+---+---+

|   |   |   |   |   |

Auth Data Prof Chat  ML Reports

|   |   |   |   |   |

+---+---+---+---+---+

|

PostgreSQL (Neon) + local/object file storage

Each ML feature (forecasting, anomaly detection) fits a fresh model per request on the user's specific data — there is no single pre-trained model; computation happens on demand and results are persisted for reuse (dashboard stats, PDF reports).

## Key Engineering Decisions

- **RAG grounding over free-form generation**: every AI response (chat, insights) is built from a prompt containing only real, precomputed statistics — never raw rows. This eliminates hallucinated numbers, at the cost of requiring a query-translation layer for chat.
- **Backtest-validated forecasting**: rather than presenting a forecast as ground truth, the system holds out recent real data, predicts it, and reports actual MAE/RMSE — so forecast confidence is measurable.
- **Two independent anomaly detection methods**: Isolation Forest and DBSCAN use fundamentally different approaches (isolation depth vs. density). Cross-checking that both agree on the most extreme cases increases confidence those are genuine anomalies, not algorithm-specific artifacts.
- **Provider-agnostic LLM layer**: the LLM is accessed through an abstract interface; swapping providers (e.g. to OpenAI) requires implementing one class, not refactoring callers.

## Local Development Setup

### Backend
```bash
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
# Create .env with DATABASE_URL, JWT_SECRET_KEY, GEMINI_API_KEY (see .env.example)
python scripts/create_tables.py
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
# Create .env.local with NEXT_PUBLIC_API_URL=http://localhost:8000
npm run dev
```

## Environment Variables

See `backend/.env.example` for the full list. Required: `DATABASE_URL` (PostgreSQL), `JWT_SECRET_KEY`, `GEMINI_API_KEY`.

## Project Structure

backend/

app/

core/           - config, database, security, rate limiting

api/v1/         - route definitions (thin, delegate to services)

features/       - one folder per domain (auth, datasets, profiling,

chat, forecasting, anomaly, insights, reports)

llm/            - provider-agnostic LLM interface + Gemini implementation

scripts/          - one-off scripts (table creation)
frontend/

src/

app/            - Next.js App Router pages

lib/            - typed API client + per-feature helper functions

## License

This project is a personal portfolio project built for educational and demonstration purposes.