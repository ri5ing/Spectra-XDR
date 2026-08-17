# SPECTRA-XDR

SPECTRA-XDR is a hybrid, multi-agent Extended Detection and Response (XDR) architecture designed to combine real-time telemetry, threat intelligence, deterministic security controls, and autonomous AI-assisted reasoning for enterprise threat detection and incident response.

---

## Current Phase

```text
Phase 4 — Deterministic Detection & Incident Correlation Foundation
```

This repository is at **Phase 4**. It implements the deterministic security detection engine, threshold correlation, evidence auditability, and incident correlation layer for SPECTRA-XDR. Phase 4 operates 100% deterministically over persisted PostgreSQL events and enrichment records without using AI, LLMs, active response, or network reputation lookups.

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
[Phase 4 Pipeline]
   ├── Detection Engine (SINGLE_EVENT, THRESHOLD, SAME_SOURCE_THRESHOLD, IOC_MATCH, MITRE_TECHNIQUE_MATCH, COMBINATION)
   ├── Built-in Rules Catalog (DET-001 through DET-005)
   ├── Incident Correlation & Severity Precedence (critical > high > medium > low)
   └── Auditable Incident Evidence Logging (detection_matches, incident_evidence)
   ↓
Auditable Incidents & Evidence
   ↓
Future SPECTRA AI Control Plane (Phase 5)
```

---

## Development Principles & Security Guidelines

### Core Principle
```text
AI recommends.
Deterministic security controls decide.
Controlled response executes.
```

### Deterministic Security Rules (Phase 4 Boundary)
* **Zero AI / LLM Calls**: All detection rule evaluation, threshold correlation, severity assignment, and evidence logging logic is 100% deterministic and reproducible. Zero AI agents, LLM calls, risk scoring heuristics, active response, or dynamic code execution (`eval()`).
* **Phase 5 Scope Note**: Phase 5 will introduce AI-assisted security analysis as a separate reasoning layer consuming Phase 4 evidence.
* **Extracted IOC & Detection Safeguards**: Extracted IOCs (IPs, domains, URLs) and detections are treated strictly as data. The system will **NEVER** make network requests to extracted URLs, resolve extracted domains, scan extracted IPs, or execute extracted strings.

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
| **Incidents** | `PATCH` | `/api/v1/incidents/{id}` | Update incident status or severity |
| **Incidents** | `POST` | `/api/v1/incidents/{id}/events/{event_id}` | Associate an event with an incident |
| **Incidents** | `GET` | `/api/v1/incidents/{id}/evidence` | List all auditable evidence items for an incident |
| **Intelligence** | `GET` | `/api/v1/intelligence/iocs` | List extracted and normalized IOC records |
| **Intelligence** | `GET` | `/api/v1/intelligence/iocs/{ioc_id}` | Get detailed IOC record by UUID |
| **Intelligence** | `GET` | `/api/v1/intelligence/mitre` | List MITRE ATT&CK catalog techniques |
| **Intelligence** | `GET` | `/api/v1/intelligence/mitre/{technique_id}` | Get MITRE technique details by ID (e.g. `T1059`) |
| **Intelligence** | `GET` | `/api/v1/intelligence/events/{event_id}` | Get enriched intelligence for a persisted event |
| **Intelligence** | `POST` | `/api/v1/intelligence/events/{event_id}/enrich` | Explicitly trigger deterministic event enrichment |
| **Detections** | `GET` | `/api/v1/detections/rules` | List deterministic detection rules |
| **Detections** | `GET` | `/api/v1/detections/rules/{rule_id}` | Get detection rule details by rule_id (e.g. `DET-001`) |
| **Detections** | `POST` | `/api/v1/detections/run` | Execute deterministic detection engine over events |
| **Detections** | `GET` | `/api/v1/detections/matches` | List generated detection matches |
| **Detections** | `GET` | `/api/v1/detections/matches/{match_id}` | Get detection match details by UUID |

---

## Built-In Detection Rules Catalog

| Rule ID | Rule Name | Condition Type | Severity | MITRE Technique | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `DET-001` | Repeated Authentication Failures | `SAME_SOURCE_THRESHOLD` (5 events / 5 min) | `medium` | `T1110` | Triggers when 5 or more authentication failures occur on same agent within 5 minutes. |
| `DET-002` | Brute Force Threshold Violation | `THRESHOLD` (10 events / 10 min) | `high` | `T1110` | Triggers when 10 or more failed login attempts occur within 10 minutes. |
| `DET-003` | PowerShell Script Execution | `MITRE_TECHNIQUE_MATCH` (`T1059.001`) | `medium` | `T1059.001` | Triggers when telemetry is mapped to MITRE T1059.001. |
| `DET-004` | OS Credential Dumping Activity | `MITRE_TECHNIQUE_MATCH` (`T1003`) | `high` | `T1003` | Triggers when telemetry matches MITRE T1003. |
| `DET-005` | Privilege Escalation Exploitation | `MITRE_TECHNIQUE_MATCH` (`T1068`) | `high` | `T1068` | Triggers when telemetry matches MITRE T1068. |

---

## Migration & Execution Guide

### 1. Database Migrations (Alembic)
To apply database schema migrations (including `003_detection_and_correlation`):
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
