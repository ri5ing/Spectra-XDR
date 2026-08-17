# SPECTRA-XDR

SPECTRA-XDR is a hybrid, multi-agent Extended Detection and Response (XDR) architecture designed to combine real-time telemetry, threat intelligence, autonomous AI-assisted reasoning, and strict deterministic security controls for enterprise threat detection and incident response.

---

## Current Phase

```text
Phase 3 — Deterministic Security Intelligence Foundation
```

This repository is at **Phase 3**. It implements the deterministic security intelligence foundation for SPECTRA-XDR, providing offline IOC extraction, canonical indicator normalization, versioned MITRE ATT&CK technique mapping, and event enrichment (`enrichment_version = "1.0.0"`).

---

## Architecture Flow

```text
Wazuh (v4.14.7 Single-Node Docker)
   ↓ (JWT Auth & Read-Only REST API)
Wazuh API Client (WazuhClient)
   ↓
NormalizedEvent
   ↓
Event Service ───> PostgreSQL
   ↓
[Phase 3 Pipeline]
   ├── IOC Extraction (IPv4, IPv6, Domain, URL, MD5, SHA1, SHA256, Username, File Path)
   ├── IOC Normalization (Canonical representation preserving original evidence)
   └── MITRE ATT&CK Mapping (Local versioned catalog matching rule IDs/groups)
   ↓
EnrichedEventData (Version 1.0.0) ───> PostgreSQL (iocs, mitre_techniques, event_iocs, event_mitre_mappings)
   ↓
Future SPECTRA AI Control Plane (Phase 4)
```

---

## Development Principles & Security Guidelines

### Core Principle
```text
AI recommends.
Deterministic security controls decide.
Controlled response executes.
```

### Deterministic Security Rules (Phase 3 Boundary)
* **Zero AI / LLM Calls**: All extraction, normalization, and MITRE mapping logic is 100% deterministic (regular expressions, structured JSON field parsing, static catalog lookup). Zero AI agents, LLM calls, risk scoring, or automated incident creation.
* **Extracted IOC Security Safeguards**: Extracted IOCs (IPs, domains, URLs) are treated strictly as data. The system will **NEVER** make network requests to extracted URLs, resolve extracted domains, scan extracted IPs, or execute extracted strings.
* **Telemetry & Persisted Event Separation**: `/api/v1/wazuh/alerts` remains live/raw Wazuh telemetry, while `/api/v1/events` remains persisted SPECTRA events in PostgreSQL.

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
| **Intelligence** | `GET` | `/api/v1/intelligence/iocs` | List extracted and normalized IOC records |
| **Intelligence** | `GET` | `/api/v1/intelligence/iocs/{ioc_id}` | Get detailed IOC record by UUID |
| **Intelligence** | `GET` | `/api/v1/intelligence/mitre` | List MITRE ATT&CK catalog techniques |
| **Intelligence** | `GET` | `/api/v1/intelligence/mitre/{technique_id}` | Get MITRE technique details by ID (e.g. `T1059`) |
| **Intelligence** | `GET` | `/api/v1/intelligence/events/{event_id}` | Get enriched intelligence for a persisted event |
| **Intelligence** | `POST` | `/api/v1/intelligence/events/{event_id}/enrich` | Explicitly trigger deterministic event enrichment |

---

## Migration & Execution Guide

### 1. Database Migrations (Alembic)
To apply database schema migrations (including `002_intelligence_foundation`):
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
