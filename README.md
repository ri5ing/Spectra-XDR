# SPECTRA-XDR

SPECTRA-XDR is a hybrid, multi-agent Extended Detection and Response (XDR) architecture designed to combine real-time telemetry, threat intelligence, autonomous AI-assisted reasoning, and strict deterministic security controls for enterprise threat detection and incident response.

---

## Current Phase

```text
Phase 1 — Wazuh Foundation
```

This repository is currently at **Phase 1**. It establishes a reliable, read-only telemetry integration between the SPECTRA-XDR FastAPI backend and Wazuh Manager (v4.x) via the official Wazuh API, featuring an asynchronous client, an event normalization engine, REST API routes, and a complete mocked unit testing suite.

---

## Architecture Flow

```text
Windows Endpoint ─┐
Linux Endpoint ───┼──> Wazuh Agents
Kali Endpoint ────┘
                       │
                       ▼
                 Wazuh Manager
                       │
              ┌────────┴────────┐
              ▼                 ▼
        Wazuh Indexer       Wazuh API
                                │
                                ▼
                         SPECTRA FastAPI
                                │
                         Event Normalizer
                                │
                                ▼
                         Normalized Event
```

---

## Development Principles & Security Guidelines

### Core Principle
```text
AI recommends.
Deterministic security controls decide.
Controlled response executes.
```

### Phase 1 Read-Only Security Model
* **Strictly Read-Only Telemetry**: All Wazuh communication is limited to HTTP `GET` queries (plus `POST` for authentication tokens).
* **No Active Response**: No endpoint isolation, process termination, file quarantine, IP blocking, or agent command execution functionality is implemented in this phase.
* **Credential Protection**: Passwords, API tokens, and authorization headers are never logged or exposed in client responses.
* **TLS Security**: SSL certificate verification (`WAZUH_VERIFY_SSL=true`) is enabled by default.

---

## Phase 1 — Wazuh Foundation Details

### Wazuh's Role in SPECTRA-XDR
Wazuh acts as the primary endpoint telemetry and alert ingestion engine. SPECTRA-XDR ingests raw Wazuh alerts, standardizes them into `NormalizedEvent` schemas for AI agents, and preserves raw event payloads as unalterable evidence.

### Application Health vs. Wazuh Integration Health
* **SPECTRA App Health** (`GET /health`): Independent application status check verifying SPECTRA backend readiness.
* **Wazuh Integration Health** (`GET /api/v1/wazuh/health`): Dedicated read-only connectivity check against the external Wazuh API Manager.

### Available Endpoints
| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | SPECTRA-XDR root information |
| `GET` | `/health` | SPECTRA-XDR application health check |
| `GET` | `/api/v1/wazuh/health` | Wazuh API connectivity & authentication status |
| `GET` | `/api/v1/wazuh/agents` | Read-only inventory of registered Wazuh agents |
| `GET` | `/api/v1/wazuh/alerts` | Read-only raw telemetry alerts from Wazuh |
| `GET` | `/api/v1/events` | Standardized `NormalizedEvent` telemetry feed |

---

## Environment Configuration

Configure `.env` using `.env.example`:
```env
# Application Settings
APP_NAME=SPECTRA-XDR
APP_ENV=development
DEBUG=True
HOST=0.0.0.0
PORT=8000

# Wazuh Integration Settings
WAZUH_API_URL=https://localhost:55000
WAZUH_USERNAME=wazuh-wui
WAZUH_PASSWORD=wazuh-password
WAZUH_VERIFY_SSL=true
WAZUH_TIMEOUT=10
```

---

## Running Locally & Testing

### 1. Environment & Dependencies
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Testing Without a Live Wazuh Server
All unit and integration tests run offline using mocked Wazuh API responses:
```powershell
pytest -v
```

### 3. Connecting to a Live Wazuh Deployment
To connect SPECTRA to a real Wazuh Manager:
1. Update `.env` with your Wazuh Manager API URL, username, and password.
2. If using self-signed certificates in local testing, set `WAZUH_VERIFY_SSL=false`.
3. Start FastAPI server:
   ```powershell
   uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```
4. Query `/api/v1/wazuh/health` to verify live connectivity.
