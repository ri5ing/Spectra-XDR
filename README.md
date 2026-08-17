# SPECTRA-XDR

## Swarm-Powered Predictive Event Correlation & Threat Response Architecture — Extended Detection and Response

> **SPECTRA-XDR** is a hybrid, multi-agent, open-source XDR architecture built around **Wazuh**, **MITRE ATT&CK**, **LangGraph**, **Ollama**, and **Gemini API**. It operates across multiple endpoints on a local network, combining real-time security telemetry with autonomous AI-assisted correlation, investigation, threat reasoning, deterministic risk scoring, and controlled response execution.

---

## Current Phase

```text
Phase 6 — Swarm-Powered Multi-Agent Reasoning, Risk Engine & Controlled Response Architecture
```

---

## ⚡ Single-Command Startup

Start the **FULL SPECTRA-XDR & WAZUH PLATFORM** (Wazuh Manager, Wazuh Indexer, Wazuh Dashboard, PostgreSQL, Redis, Ollama, and SPECTRA-XDR Console) with **ONE SINGLE COMMAND**:

### Docker Compose (Cross-Platform)
```powershell
docker compose up --build -d
```

### Windows Launcher
```cmd
.\start.bat
```

### Linux / macOS Launcher
```bash
chmod +x start.sh && ./start.sh
```

---

## 🌐 Platform Service Endpoints

| Component | URL / Endpoint | Credentials / Details |
| :--- | :--- | :--- |
| **Wazuh Web Dashboard** | `https://localhost:8443` | User: `admin` / Password: `admin` |
| **SPECTRA-XDR Analyst Console** | `http://localhost:8000` | Real-time SOC Console Dashboard |
| **SPECTRA-XDR API Documentation** | `http://localhost:8000/docs` | Interactive OpenAPI Swagger UI |
| **Wazuh REST API Engine** | `https://localhost:55000` | JWT Authenticated Management API |
| **Wazuh Agent Enrollment** | `1514 / 1515 TCP` | Endpoint Agent Registration & Telemetry |
| **Ollama Local LLM Engine** | `http://localhost:11434` | Offline Local Model Processing |

---

## 🏗️ Architecture Flow

```text
Telemetry → Detection → Correlation → Threat Context → Investigation
          → Risk Scoring → Policy Decision → Response → Feedback
```

```text
                               SPECTRA-XDR ARCHITECTURE

  subgraph ENDPOINTS ["LOCAL NETWORK / ENDPOINT LAYER"]
      Windows Endpoint | Linux Endpoint | Kali VM | macOS / Other VM
  end

  subgraph WAZUH ["WAZUH XDR & SOAR PLATFORM"]
      Wazuh Agents ──> Wazuh Manager ──> Wazuh Indexer ──> Wazuh Dashboard (Port 8443)
                            │               ▲
                            ▼               │ (Active Response Commands)
                        Wazuh API ──────────┤
                            │               │
  end                       ▼               │
  subgraph SPECTRA ["SPECTRA AI CONTROL PLANE"]
      LangGraph Supervisor Orchestrator
         ├── 1. Detection Agent
         ├── 2. MITRE ATT&CK Agent
         ├── 3. Threat Intelligence Agent
         ├── 4. Correlation Agent
         ├── 5. Investigation Agent
         ├── 6. Response Agent
         └── 7. Reporting Agent
                            │
                            ▼
               Deterministic Risk Engine (0-100)
                            │
                            ▼
               Deterministic Policy Engine
             (Human-in-the-Loop Approval Boundary)
                            │
                            ▼
               Controlled Active Response Execution ──────┘
  end
```

---

## 🤖 Multi-Agent AI Swarm & Hybrid Router

SPECTRA-XDR routes reasoning requests dynamically across local and cloud LLMs while keeping deterministic controls in charge:

1. **Hybrid Model Router (`models/router.py`)**:
   - **Ollama Local (`ollama_local`)**: Fast, private, offline processing for sensitive endpoint telemetry.
   - **Gemini API (`gemini_cloud`)**: High-reasoning cloud LLM for complex attack chain reconstruction.
   - **Deterministic Fallback (`deterministic_fallback`)**: Zero-downtime rule-based reasoning engine if LLMs are offline.
2. **Telemetry Sanitizer (`models/sanitizer.py`)**: Redacts passwords, bearer tokens, and private keys prior to cloud model inference.
3. **Specialized Swarm Agents (`agents/`)**:
   - **Detection Agent**: Alert triage, anomaly detection, false-positive evaluation.
   - **MITRE ATT&CK Agent**: Maps behaviors to MITRE tactics, techniques, and mitigations.
   - **Threat Intel Agent**: Evaluates extracted IOC reputation scores.
   - **Correlation Agent**: Reconstructs multi-stage attack chains across endpoints over time.
   - **Investigation Agent**: Read-only DFIR host investigation and timeline collection.
   - **Response Agent**: Formulates recommended containment playbooks.
   - **Reporting Agent**: Generates executive incident summary reports.

---

## 🛡️ Deterministic Risk Engine & Safety Policy

AI agents generate recommendations; deterministic code decides and enforces security boundaries.

### Deterministic Risk Scoring Formula (`risk/scoring.py`)
$$\text{Risk Score} = w_1 S_{\text{severity}} + w_2 S_{\text{mitre}} + w_3 S_{\text{ioc}} + w_4 S_{\text{chain}} + w_5 S_{\text{asset}}$$

| Risk Score | Threat Level | Default Policy |
| :--- | :--- | :--- |
| **0 – 29.9** | `LOW` | Alert & Monitor |
| **30 – 59.9** | `MEDIUM` | Non-disruptive Monitoring |
| **60 – 79.9** | `HIGH` | Requires Human Approval for Containment |
| **80 – 100** | `CRITICAL` | Requires Human Approval for Disruptive Actions |

### Strict Security Policy Rules (`risk/policies.py`)
* **Zero Arbitrary Shell Execution**: No LLM `eval()` or unvalidated shell execution.
* **Human-in-the-Loop Sign-off**: High-impact actions (`isolate_endpoint`, `block_ip`, `kill_process`, `quarantine_file`, `disable_user_account`) strictly require explicit analyst approval (`PENDING_APPROVAL`) before execution.
* **Immutable Audit Trail**: All actions, approvals, and model thoughts are persisted to PostgreSQL audit logs.

---

## 🔌 API Endpoints Reference

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **System** | `GET` | `/` | Serves SPECTRA-XDR SOC Console Dashboard UI |
| **System** | `GET` | `/health` | Application operational health check |
| **Infrastructure** | `GET` | `/api/v1/database/health` | PostgreSQL read-only health ping |
| **Wazuh** | `GET` | `/api/v1/wazuh/health` | Wazuh API connectivity check |
| **Wazuh** | `GET` | `/api/v1/wazuh/agents` | Read-only inventory of registered Wazuh agents |
| **Wazuh** | `GET` | `/api/v1/wazuh/alerts` | Read-only raw telemetry alerts from Wazuh |
| **Events** | `GET` | `/api/v1/events` | Query persisted normalized security events |
| **Incidents** | `GET` | `/api/v1/incidents` | List security incidents with filters |
| **Incidents** | `GET` | `/api/v1/incidents/{id}` | Retrieve incident details by UUID or `INC-XXXXXX` |
| **Incidents** | `PATCH` | `/api/v1/incidents/{id}` | Update incident status/assignee |
| **AI Swarm** | `POST` | `/api/v1/swarm/analyze/{id}` | Trigger LangGraph Multi-Agent reasoning on incident |
| **AI Swarm** | `GET` | `/api/v1/swarm/runs/{id}` | Retrieve agent thoughts and attack chain execution |
| **Risk Engine** | `GET` | `/api/v1/risk/assessments/{id}`| Retrieve deterministic multi-factor risk score breakdown |
| **Risk Engine** | `POST` | `/api/v1/risk/recalculate/{id}`| Force recalculation of incident risk score |
| **Response** | `GET` | `/api/v1/response/actions/{id}`| List recommended/executed response actions |
| **Response** | `POST` | `/api/v1/response/actions/{id}/approve` | Analyst Human-in-the-Loop approval/rejection |
| **Response** | `POST` | `/api/v1/response/actions/execute` | Trigger controlled Wazuh Active Response execution |
| **AI Router** | `GET` | `/api/v1/ai/status` | Model router health (Ollama, Gemini API, Fallback) |

---

## 🧪 Testing & Execution

Run the complete automated pytest suite:

```powershell
.\.venv\Scripts\python -m pytest -v
```

All 61 unit and integration tests validate model router fallbacks, risk calculations, policy boundaries, response execution, and swarm state graph execution.
