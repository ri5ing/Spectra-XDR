# SPECTRA-XDR

SPECTRA-XDR is a hybrid, multi-agent Extended Detection and Response (XDR) architecture designed to combine real-time telemetry, threat intelligence, deterministic security controls, and autonomous AI-assisted reasoning for enterprise threat detection and incident response.

---

## Current Phase

```text
Phase 5 — Incident Investigation & Analyst Workflow Foundation
```

This repository is at **Phase 5**. It implements the deterministic incident investigation, aggregation, timeline construction, analyst annotation, and append-only audit trail layer for SPECTRA-XDR. Phase 5 operates 100% deterministically over persisted PostgreSQL events and enrichment records without using AI, LLMs, active response, or external threat intelligence network lookups.

---

## Architecture Flow

```text
Wazuh (v4.14.7 Single-Node Docker)
   ↓ (JWT Auth & Read-Only REST API)
Wazuh API Client (WazuhClient)
   ↓
NormalizedEvent
   ↓
IOC Extraction & Normalization
   ↓
MITRE ATT&CK Mapping
   ↓
Persisted Enriched Event (PostgreSQL)
   ↓
Detection Engine & Correlation Matches (Phase 4)
   ↓
[Phase 5 Incident Investigation Layer]
   ├── Detailed Incident Aggregation (Summary, Events, Detections, IOCs, MITRE)
   ├── Deterministic Investigation Timeline (Events + Detections + Notes + Audits)
   ├── Analyst Notes & Workflow State Management (OPEN, INVESTIGATING, CONTAINED, RESOLVED, CLOSED)
   └── Immutable Append-Only Audit Log (incident_audit_log)
   ↓
Auditable Incidents & Evidence
```

---

## Development Principles & Security Guidelines

### Core Principle
```text
AI recommends.
Deterministic security controls decide.
Controlled response executes.
```

### Deterministic Security Rules (Phase 5 Boundary)
* **Zero AI / LLM Calls**: All incident detail assembly, event/detection/IOC/MITRE aggregation, timeline construction, status transition validation, and audit logging are 100% deterministic and reproducible. Zero AI agents, LLM calls, risk scoring heuristics, active response, or dynamic code execution (`eval()`).
* **Zero External Intel Network Lookups**: Extracted IOCs and incidents are analyzed strictly against persisted PostgreSQL telemetry. Zero external WHOIS, VirusTotal, AbuseIPDB, or DNS network requests.
* **Extracted IOC & Incident Safeguards**: Detections, IOCs, and incidents are treated strictly as data. The system will **NEVER** make network requests to extracted URLs, resolve extracted domains, scan extracted IPs, or execute extracted strings.

---

## API Endpoints Reference

| Category | Method | Endpoint | Description |
| :--- | :--- | :--- | :--- |
| **System** | `GET` | `/` | SPECTRA-XDR root information |
| **System** | `GET` | `/health` | SPECTRA-XDR application health check |
| **Infrastructure** | `GET` | `/api/v1/database/health` | PostgreSQL read-only ping health check |
| **Wazuh** | `GET` | `/api/v1/wazuh/health` | Wazuh API connectivity health check |
| **Wazuh** | `GET` | `/api/v1/wazuh/agents` | Read-only inventory of registered Wazuh agents |
| **Wazuh** | `GET` | `/api/v1/wazuh/alerts` | Read-only raw telemetry alerts from Wazuh |
| **Events** | `GET` | `/api/v1/events` | Query persisted normalized security events |
| **Events** | `POST` | `/api/v1/events` | Ingest a `NormalizedEvent` into PostgreSQL |
| **Incidents** | `GET` | `/api/v1/incidents` | List security incidents with filters |
| **Incidents** | `POST` | `/api/v1/incidents` | Create a new security incident (`INC-XXXXXX`) |
| **Incidents** | `GET` | `/api/v1/incidents/{id}` | Retrieve incident details by UUID or `INC-XXXXXX` |
| **Incidents** | `PATCH` | `/api/v1/incidents/{id}` | Update incident status/assignee with atomic audit log |
| **Incidents** | `POST` | `/api/v1/incidents/{id}/events/{event_id}` | Associate an event with an incident |
| **Investigation** | `GET` | `/api/v1/incidents/{id}/summary` | Get deterministic summary statistics for an incident |
| **Investigation** | `GET` | `/api/v1/incidents/{id}/events` | Get associated persisted events with filters |
| **Investigation** | `GET` | `/api/v1/incidents/{id}/detections` | Get detection matches contributing to an incident |
| **Investigation** | `GET` | `/api/v1/incidents/{id}/iocs` | Get deduplicated extracted IOCs for an incident |
| **Investigation** | `GET` | `/api/v1/incidents/{id}/mitre` | Get deduplicated MITRE ATT&CK techniques for an incident |
| **Investigation** | `GET` | `/api/v1/incidents/{id}/timeline` | Get deterministic investigation timeline |
| **Investigation** | `GET` | `/api/v1/incidents/{id}/evidence` | List all auditable evidence items for an incident |
| **Investigation** | `POST` | `/api/v1/incidents/{id}/notes` | Add an analyst note to an incident |
| **Investigation** | `GET` | `/api/v1/incidents/{id}/notes` | List analyst notes for an incident |
| **Investigation** | `PATCH` | `/api/v1/incidents/{id}/notes/{note_id}` | Update an analyst note |
| **Investigation** | `DELETE` | `/api/v1/incidents/{id}/notes/{note_id}` | Delete an analyst note |
| **Investigation** | `GET` | `/api/v1/incidents/{id}/audit` | Get immutable append-only audit trail for an incident |

---

## Validated Status Workflow

| Current Status | Allowed Target Transitions |
| :--- | :--- |
| `open` | `investigating`, `contained`, `resolved` |
| `investigating` | `contained`, `resolved` |
| `contained` | `investigating`, `resolved` |
| `resolved` | `closed` |
| `closed` | *(Terminal state)* |

---

## Migration & Execution Guide

### 1. Database Migrations (Alembic)
To apply database schema migrations (including `004_incident_investigation`):
```powershell
alembic upgrade head
```

### 2. Automated Test Suite

#### Offline Pytest Suite (Default CI mode)
Runs unit tests offline without requiring a live Wazuh server:
```powershell
pytest -v
```

#### Optional Live Integration Test Suite
To run tests against the live Wazuh 4.14.7 server:
```cmd
set WAZUH_INTEGRATION_TESTS=true&& pytest -v tests/test_wazuh_live_integration.py
```
