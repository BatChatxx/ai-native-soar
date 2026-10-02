# AI-Native SOAR - Implementation Summary

## Current State

The AI-Native SOAR platform is a working end-to-end system deployed via Docker Compose, featuring:

- **Dashboard** with live statistics and visualizations
- **Incident management** (CRUD + detail page + timeline + comments)
- **Alert management** (CRUD + detail page + promote-to-incident workflow)
- **Observable (IOC) extraction** from descriptions (IP, domain, URL, hashes, Ethereum contracts, Arweave)
- **Threat intel enrichment** with malicious scoring
- **Interactive AI analysis** (summaries + custom Q&A with context-aware answers)
- **Token-budget management** to prevent context overflow on long reports
- **LLM profile management** (multiple configurable models, switchable at runtime)
- **Authentication** (default admin account + login + password change)
- **Client-side routing** with browser back/forward support

## Project Structure

```
ai-native-soar/
├── .env                        # Environment configuration (gitignored)
├── docker-compose.yml          # Docker orchestration
├── README.md                   # Project overview
├── ARCHITECTURE.md             # Detailed architecture documentation
├── IMPLEMENTATION_SUMMARY.md   # This file
│
├── backend/                    # FastAPI backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # Entry point (mounts routers, seeds default admin + LLM profile)
│   ├── data/
│   │   └── threat_intel.json   # Local threat intel feed (demo)
│   ├── models/
│   │   ├── models.py           # Core models (Incident, Alert, Observables, User, LLMProfile…)
│   │   ├── database.py         # Engine/session management
│   │   └── …                   # Other domain models
│   ├── routers/
│   │   ├── incidents_clean.py  # Incident CRUD + events + comments + observables + AI + Q&A
│   │   ├── alerts_clean.py     # Alert CRUD + observables + promote + AI + Q&A
│   │   ├── dashboard_clean.py  # Dashboard aggregate stats
│   │   ├── settings_clean.py   # Health + LLM profile management
│   │   ├── auth_clean.py       # Login + password change + default admin
│   │   └── …                   # (legacy placeholder routers, not mounted)
│   └── utils/
│       ├── observable_extractor.py  # IOC regex extraction
│       ├── enricher.py              # Threat intel enrichment
│       ├── llm_client.py            # LLM client (profiles + token budget + Q&A)
│       ├── auth_utils.py            # PBKDF2 password hashing + JWT
│       └── …                         # Other utilities
│
└── frontend/                   # React + Vite frontend (nginx-served)
    ├── Dockerfile              # Multi-stage: node build → nginx serve
    ├── nginx.conf              # Static serve + /api proxy to backend
    ├── package.json
    └── src/
        ├── main.tsx            # BrowserRouter entry
        ├── App.tsx             # Routes + all views (Dashboard/Incidents/Alerts/Settings/Login)
        └── api/client.ts       # Typed API client (native fetch)
```

## Frontend Routes

Client-side routing uses `react-router-dom` with browser back/forward support:

| Route | View |
|-------|------|
| `/` | Dashboard (stats, severity chart, IOC donut, recent activity) |
| `/incidents` | Incident list (filter, create, edit, delete) |
| `/incidents/:id` | Incident detail (timeline, comments, observables, AI analysis + Q&A) |
| `/alerts` | Alert list (filter, create, edit, delete, promote) |
| `/alerts/:id` | Alert detail (observables, AI analysis + Q&A, promote) |
| `/settings` | Settings (health, LLM profiles, account/password) |
| `/login` | Login (default account admin/admin) |

The nginx config serves static assets and proxies `/api` to the backend service.

## Backend API (working endpoints)

### Incidents (`/api/v1/incidents`)
- `GET /` — list (with severity/status filters)
- `POST /` — create (auto-extracts IOCs, optional auto-enrich)
- `GET /{id}` — detail (includes events, comments, observables, source_alert)
- `PUT /{id}` — update
- `DELETE /{id}` — soft delete
- `GET/POST /{id}/events` — timeline events
- `GET/POST /{id}/comments` — comments
- `GET/POST /{id}/observables` — IOCs
- `POST /{id}/observables/extract` — extract IOCs from description
- `POST /{id}/observables/enrich` — enrich IOCs (threat intel)
- `DELETE /{id}/observables/{oid}` — remove IOC
- `POST /{id}/analyze` — AI analysis summary
- `POST /{id}/ask` — custom AI question (persisted to history)

### Alerts (`/api/v1/alerts`)
- `GET /` — list
- `POST /` — create (auto-extract + optional auto-enrich)
- `GET /{id}` — detail (includes observables)
- `PUT /{id}` — update
- `DELETE /{id}` — soft delete
- `GET/POST /{id}/observables` — IOCs
- `POST /{id}/observables/extract` — extract IOCs
- `POST /{id}/observables/enrich` — enrich IOCs
- `DELETE /{id}/observables/{oid}` — remove IOC
- `POST /{id}/promote` — promote alert to incident (copies observables)
- `POST /{id}/analyze` — AI triage summary
- `POST /{id}/ask` — custom AI question (persisted to history)

### Dashboard (`/api/v1/dashboard`)
- `GET /summary` — aggregate stats (totals, severity/status distribution, IOC reputation, recent items)

### Settings (`/api/v1/settings`)
- `GET /health` — system/database/LLM health + data counts
- `GET /llm` — list LLM profiles (api_key masked)
- `POST /llm` — create profile
- `PUT /llm/{id}` — update profile
- `DELETE /llm/{id}` — delete profile
- `POST /llm/{id}/activate` — activate a profile

### Auth (`/api/v1/auth`)
- `POST /login` — login, returns JWT token
- `POST /change-password` — change admin password
- `GET /me` — current account info

## Observable (IOC) Pipeline

```
Incident/Alert description
        ↓  observable_extractor.py (regex)
IP / domain / URL / MD5 / SHA1 / SHA256
        ↓  enricher.py vs threat_intel.json
malicious / suspicious / clean / unknown + score (0-100)
```

Key behaviors:
- **Auto-extract** on create (no manual step needed)
- **Optional auto-enrich** on create (checkbox in the form)
- **Manual enrich** available in detail pages ("Enrich" button)
- **Promote** copies alert observables (including enrichment) to the new incident

## LLM Integration (multi-provider)

The platform supports **multiple configurable LLM profiles**, switchable at runtime via the Settings page (stored in the local DB, API keys masked in API responses).

- **Local Qwen 3.5 9B** (LM Studio, reasoning model) — `http://host.docker.internal:56987`
- **DeepSeek V4 Flash** (cloud API, non-reasoning) — `https://api.deepseek.com/v1`
- Any other OpenAI-compatible endpoint can be added via the Settings UI or API.

### Reasoning-model handling

- Qwen reasoning models return `content` (final answer) + `reasoning_content` (thinking); the client reads `content` and retries with a larger budget if the model runs out of tokens before emitting content.
- Non-reasoning models (e.g. DeepSeek) return `content` directly.

### Token-budget management

To avoid context overflow on long DFIR reports, `llm_client.py` estimates token usage (CJK ≈ 1 char/token, other ≈ 4 chars/token) and progressively truncates lower-priority context (comments < events < observables < description) to fit within the model's context window.

### AI Analysis (in detail pages)
- **Summary**: one-click "Analyze with AI" for a structured summary
- **Q&A**: ask custom questions using full incident/alert context (with preset questions)
- **History**: Q&A is persisted to the `analysis_questions` table and restored on reload

## Docker Compose Services

| Service | Image | Purpose |
|---------|-------|---------|
| db | postgres:16-alpine | Primary database |
| redis | redis:7-alpine | Cache / messaging |
| backend | python:3.11-slim (custom) | FastAPI on :8000 |
| frontend | node build → nginx:alpine | Static UI on :3000, proxies /api |
| airflow-webserver | apache/airflow (profile) | Optional orchestration |
| airflow-scheduler | apache/airflow (profile) | Optional orchestration |
| llm-server | lmstudio-server (profile) | Optional (external LLM used instead) |

## Getting Started

```bash
cd ai-native-soar

# Build and start core services (db, redis, backend, frontend)
docker-compose up -d --build db redis backend frontend

# Access the UI
http://localhost:3000

# Access the API docs
http://localhost:8000/docs
```

### Environment Variables (`.env`)

```bash
# Database
DB_PASSWORD=soar_password_2026!

# CORS / debug
CORS_ORIGINS=http://localhost:3000
DEBUG=true

# LLM (initial seed profile; can be overridden via Settings UI at runtime)
LLM_API_KEY=            # your LLM API key (kept out of git via .gitignore)
LLM_BASE_URL=http://host.docker.internal:56987
LLM_MODEL=qwen/qwen3.5-9b
LLM_CONTEXT_WINDOW=40000

# Default admin account (created on first startup)
SOAR_ADMIN_PASSWORD=admin
```

> **Security note**: `.env` is gitignored. The `LLM_API_KEY` shown here is a placeholder — never commit real keys.

## Authentication

- Default account: **admin / admin** (password configurable via `SOAR_ADMIN_PASSWORD`, changeable in Settings)
- Passwords hashed with PBKDF2 (stdlib, no bcrypt/passlib dependency issues)
- Login returns a JWT; the frontend stores it in localStorage

## Known Limitations

- Legacy placeholder routers (`incidents_router.py`, `evidence_router.py`, etc.) remain in `backend/routers/` but are **not mounted** (the clean `*_clean.py` routers are used instead)
- `init_db.py` references stale modules and needs updating
- The threat intel feed is a static demo JSON (`data/threat_intel.json`); production should use VirusTotal / AbuseIPDB / MISP
- Authentication is single-account (one admin); no multi-user RBAC yet
- Airflow and bundled `llm-server` are optional profiles (external LM Studio is used)

---

*Last Updated: 2026*
*Version: 1.1.0*
