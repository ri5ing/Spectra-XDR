# SPECTRA-XDR: Swarm-Powered Predictive Event Correlation & Threat Response Architecture
> **Comprehensive System Engineering Report, Architecture Specification & Operator Manual**  
> *Extended Detection and Response (XDR) | Security Information & Event Management (SIEM) | Endpoint Detection & Response (EDR) | Network Telemetry (NDR) | Autonomous SOAR Governance*

[![Build & Test](https://img.shields.io/badge/Pytest-61%20Passed-emerald.svg)](#8-software-setup--system-requirements)
[![Architecture](https://img.shields.io/badge/Architecture-LangGraph%20Swarm%20%2B%20Wazuh-blue.svg)](#6-design-details-and-architecture)
[![License](https://img.shields.io/badge/License-Apache%202.0-zinc.svg)](#11-conclusion)

---

## 📑 Table of Contents
1. [Introduction](#1-introduction)
2. [Literature Survey](#2-literature-survey)
3. [Problem Statement](#3-problem-statement)
4. [Research Objectives](#4-research-objectives)
5. [Frameworks and Algorithms](#5-frameworks-and-algorithms)
6. [Design Details and Architecture](#6-design-details-and-architecture)
7. [Methodology & Internal Logic Workflow](#7-methodology--internal-logic-workflow)
8. [Software Setup & System Requirements](#8-software-setup--system-requirements)
9. [Implementation Plan for Next Phase (Phase 7 / Term 2)](#9-implementation-plan-for-next-phase)
10. [Timeline Chart for Term 1](#10-timeline-chart-for-term-1)
11. [Conclusion](#11-conclusion)
12. [Future Scope](#12-future-scope)
13. [References](#13-references)

---

## 1. Introduction

Modern cybersecurity defense environments face unprecedented challenges as enterprise attack surfaces expand across distributed hybrid endpoints, cloud instances, and virtual networks. Advanced Persistent Threats (APTs), zero-day memory attacks, ransomware, and credential-stuffing campaigns systematically evade traditional isolated defenses.

### The Operational Challenge:
- **Fragmented Tooling:** Organizations typically maintain separate silos for **EDR** (host-level telemetry), **NDR** (network flow telemetry), and **SIEM** (central log indexing). These components do not share unified context in real time.
- **Alert Fatigue in Security Operations (SOC):** Analysts are inundated with thousands of raw alerts daily, leading to analyst burnout, delayed triage, and missed high-criticality threats.
- **The Automation Dilemma:** Static SOAR scripts often break, while unconstrained LLM agents pose severe operational risks (e.g., hallucinated or erroneous server shutdowns).

### The SPECTRA-XDR Solution:
**SPECTRA-XDR** (**S**warm-**P**owered **E**vent **C**orrelation & **T**hreat **R**esponse **A**rchitecture) is an open-source, hybrid Extended Detection and Response (XDR) and autonomous SOAR platform. It integrates:
- **Wazuh EDR & SIEM Core:** Real-time event auditing across Windows (Sysmon) and Linux (Auditd) endpoints.
- **LangGraph Multi-Agent AI Swarm:** A 3-phase, 7-agent consensus pipeline that triages, extracts MITRE ATT&CK techniques, audits IOCs, and reconstructs attack chains in sub-second latency.
- **Deterministic Risk & Policy Engine:** Strict mathematical scoring ($0-100$) and cryptographically verified **Human-in-the-Loop (HITL)** approval gates.
- **SOC Command Center:** A Next.js 15 / React 19 operational cockpit providing real-time fleet health, interactive attack chains, and an embedded conversational security copilot.

---

## 2. Literature Survey

The architecture of Spectra-XDR builds upon and addresses the limitations of existing enterprise and academic security paradigms:

| Domain / Paradigm | Industry Standard Examples | Inherent Limitations | Spectra-XDR Architectural Advancement |
| :--- | :--- | :--- | :--- |
| **SIEM** (Log & Event Management) | Splunk, IBM QRadar, Elastic SIEM | High ingest storage costs; rule-based correlation lacks multi-step attack reasoning; static querying. | Implements unified normalized PostgreSQL schemas (`telemetry_events`) with real-time asynchronous polling and automatic agent triage. |
| **EDR** (Endpoint Detection & Response) | CrowdStrike Falcon, Microsoft Defender for Endpoint | Proprietary agent lock-in; high per-seat licensing costs; cloud dependency prevents air-gapped protection. | Uses open-source Wazuh agents (Sysmon/Auditd) with native active-response execution sockets and host isolation. |
| **NDR** (Network Detection & Response) | Zeek, Suricata, Darktrace | High packet capture volumes; blind to encrypted payloads without endpoint context; no host-side process termination. | Correlates network socket connections directly with parent process trees and MITRE Command & Control (C2) techniques. |
| **SOAR** (Orchestration & Response) | Palo Alto Cortex XSOAR, Splunk Phantom | Static playbooks require continuous script maintenance; unguided automation risks enterprise downtime. | Implements a **Dual-Layer Governance Model**: AI swarms propose playbooks, but a deterministic mathematical policy engine enforces strict HITL gates. |
| **AI in Cybersecurity** | Single-prompt LLM wrappers, ChatGPT SOC plugins | High hallucination rates; prompt injection vulnerabilities; credential leakage to external cloud endpoints. | Hierarchical LangGraph Multi-Agent Swarm with automated **Telemetry Sanitizer** and round-robin multi-key failover to local offline LLMs (Ollama). |

---

## 3. Problem Statement

### 3.1 The Visibility & Correlation Gap
Enterprise security tools generate high volumes of isolated signals. Endpoint agents record process execution; network sensors capture external IP handshakes; authentication logs track user sessions. Reconstructing multi-stage lateral movement across these silos currently requires tedious manual correlation, creating prolonged adversary dwell time.

### 3.2 The Alert Triage Bottleneck
Tier-1 SOC analysts spend over 75% of their time manually reviewing low-fidelity alerts, evaluating false positives, and cross-referencing external threat intelligence feeds. This causes critical alert fatigue and delays the containment of active ransomware campaigns.

### 3.3 The Automation Dilemma: Hallucination vs. Inaction
Unrestricted autonomous response systems risk taking critical domain controllers or production databases offline due to false alarms. Conversely, requiring manual approval for every low-level alert creates bottlenecks. 

**Spectra-XDR resolves this dilemma** by implementing a deterministic mathematical safety boundary that allows autonomous mitigation for low/medium non-disruptive threats while enforcing strict Human-in-the-Loop authorization for high/critical disruptive actions.

---

## 4. Research Objectives

1. **Unified Cross-Layer Telemetry Ingestion:** Ingest and normalize security telemetry from Wazuh agents, Windows Sysmon, Linux Auditd, and network socket tables into a cohesive event model.
2. **Multi-Agent AI Swarm Reasoning:** Deploy a 3-phase, 7-agent hierarchical LangGraph state graph (Detection, MITRE, Threat Intel, Correlation, Investigation, Response, and Reporting) capable of parallel attack chain synthesis.
3. **Resilient Hybrid Model Routing & Privacy Preservation:** Build an intelligent model router with automated PII/credential sanitization, multi-key round-robin failover, and local offline LLM (Ollama) fallback.
4. **Deterministic Multi-Factor Risk Scoring:** Formulate an explainable, deterministic mathematical model calculating risk scores ($0 - 100$) derived from severity, MITRE tactics, IOC reputation, attack chain depth, and asset criticality.
5. **Safe, Policy-Guarded SOAR Execution:** Implement an active response framework enforcing Human-in-the-Loop (HITL) approval gates for disruptive actions (process termination, host quarantine, account disabling) while automating non-disruptive remediations.
6. **Real-Time SOC Command Center:** Build a high-performance web dashboard providing real-time telemetry streaming, incident lifecycle management, interactive swarm execution inspection, and an integrated AI Copilot.

---

## 5. Frameworks and Algorithms

### 5.1 Deterministic Multi-Factor Risk Scoring Formula (`risk/scoring.py`)
To prevent hallucinations in threat evaluation, Spectra-XDR computes incident risk using an explainable, weighted formula:

$$\text{Risk Score} = \min\left(100, \; w_1 S_{\text{severity}} + w_2 S_{\text{mitre}} + w_3 S_{\text{ioc}} + w_4 S_{\text{chain}} + w_5 S_{\text{asset}}\right)$$

#### Component Breakdown:
- $S_{\text{severity}} \in [0, 100]$: Normalized Wazuh alert rule level ($0 - 16 \rightarrow 0 - 100$).
- $S_{\text{mitre}} \in [0, 100]$: Weight assigned based on MITRE tactic stage (Initial Access = $30$, Execution = $50$, Privilege Escalation = $70$, Lateral Movement = $85$, Impact/Exfiltration = $100$).
- $S_{\text{ioc}} \in [0, 100]$: Aggregated reputation score of extracted IP, domain, and file hash indicators.
- $S_{\text{chain}} \in [0, 100]$: Attack graph depth and count of correlated multi-host events over a 24-hour sliding window.
- $S_{\text{asset}} \in [0, 100]$: Criticality factor of target host (Workstation = $40$, Internal Server = $70$, Domain Controller / Crown Jewel = $100$).
- **Configured Weights:** $w_1 = 0.30, \; w_2 = 0.25, \; w_3 = 0.20, \; w_4 = 0.15, \; w_5 = 0.10$.

### 5.2 Deterministic Risk Matrix & Action Boundaries (`risk/policies.py`)

| Risk Score | Threat Level | Operational Classification | SOAR Execution Policy |
| :--- | :--- | :--- | :--- |
| **$0.0 - 29.9$** | `LOW` | Benign Anomaly / Noise | **Autonomous Execution:** Passive log retention, Syscheck baseline audit. |
| **$30.0 - 59.9$** | `MEDIUM` | Suspicious Activity | **Autonomous Execution:** Perimeter firewall IP block, elevated process monitoring. |
| **$60.0 - 79.9$** | `HIGH` | Verified Lateral Threat | **HITL Enforced:** Requires Tier-2 Analyst approval for host containment. |
| **$80.0 - 100.0$** | `CRITICAL` | Imminent Breach / Ransomware | **HITL Enforced:** Requires Cryptographic Analyst Approval for endpoint isolation/kill. |

### 5.3 LangGraph Hierarchical Multi-Agent Graph Algorithm
The AI reasoning engine uses a directed acyclic graph (DAG) execution model:
- **Phase 1 (Ingestion & Triage):** The `Detection Agent` normalizes incoming Wazuh JSON alerts and discards known false positives.
- **Phase 2 (Concurrent Analysis):** 4 specialized agents run in parallel:
  - `MITRE ATT&CK Agent`: Maps behavioral telemetry to STIX 2.1 Enterprise techniques.
  - `Threat Intel Agent`: Queries IOC reputation and extracts threat actor attribution.
  - `Correlation Agent`: Traverses graph edges to link prior incidents with matching host/user context.
  - `Investigation Agent`: Simulates DFIR artifact queries across historical process trees.
- **Phase 3 (Arbitration & SOAR Formulation):**
  - `Response Agent`: Synthesizes outputs into concrete containment playbooks.
  - `Reporting Agent`: Produces an executive incident briefing.

### 5.4 Secret Key Ring Round-Robin & Offline Failover Algorithm
```text
function ROUTE_MODEL_REQUEST(prompt, telemetry):
    sanitized_prompt = Sanitizer.redact_credentials_and_tokens(prompt, telemetry)
    
    // Attempt 1: Cloud High-Reasoning Tier with Multi-Key Pool
    for key in CloudKeyRing.getActiveKeys():
        try:
            return GeminiCloud.generate(sanitized_prompt, key, timeout=5000ms)
        catch RateLimitException or NetworkTimeout:
            CloudKeyRing.markDegraded(key)
            continue
            
    // Attempt 2: Local Offline Inference Tier
    if OllamaLocal.isHealthy():
        return OllamaLocal.generate(sanitized_prompt, model="mistral:7b")
        
    // Attempt 3: Zero-Downtime Deterministic Fallback
    return DeterministicRuleEngine.evaluate(telemetry)
```

---

## 6. Design Details and Architecture

### 6.1 Complete Architecture Diagram

```text
                               SPECTRA-XDR ENTERPRISE TOPOLOGY

  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                                 ENDPOINT FLEET LAYER                                   │
  │    [Windows 11 Client]            [Ubuntu Server]            [Kali Linux Adversary VM] │
  │    Wazuh Agent + Sysmon          Wazuh Agent + Auditd        Simulated ATT&CK Attacks  │
  └───────────────────────────────────────────┬────────────────────────────────────────────┘
                                              │ Encrypted Telemetry (Port 1514/1515 TCP)
                                              ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                                  WAZUH SECURITY CORE                                   │
  │   ┌─────────────────────────┐  ┌───────────────────────────┐  ┌────────────────────┐   │
  │   │      Wazuh Manager      │  │       Wazuh Indexer       │  │  Wazuh Dashboard   │   │
  │   │     Analysis Engine     ├──┤    OpenSearch Cluster     ├──┤   Port 8443 (GUI)  │   │
  │   │  Active Response Daemon │  │    Normalized Storage     │  │  Compliance Engine │   │
  │   └────────────┬────────────┘  └───────────────────────────┘  └────────────────────┘   │
  └────────────────┼───────────────────────────────────────────────────────────────────────┘
                   │ REST API Telemetry Pull (Port 55000 JWT)
                   ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                              SPECTRA-XDR CONTROL PLANE                                 │
  │                                                                                        │
  │   ┌────────────────────────────────────────────────────────────────────────────────┐   │
  │   │                      FastAPI Unified Gateway (:8000)                           │   │
  │   │   - Incident Management      - Telemetry Ingestion      - SOAR Dispatcher      │   │
  │   └────────────────────────┬────────────────────────────────┬──────────────────────┘   │
  │                            │                                │                          │
  │   ┌────────────────────────▼───────┐        ┌───────────────▼──────────────────────┐   │
  │   │       PERSISTENCE LAYER        │        │        AI MODEL ROUTER MATRIX        │   │
  │   │   - PostgreSQL 16 (Forensics)  │        │   - Gemini Flash (Multi-Key Ring)    │   │
  │   │   - Redis 7.2 (Queue/Cache)    │        │   - Ollama Local (Offline Fallback)  │   │
  │   │   - SQLAlchemy 2.0 Async ORM   │        │   - Regex PII Telemetry Sanitizer    │   │
  │   └────────────────────────┬───────┘        └───────────────┬──────────────────────┘   │
  │                            │                                │                          │
  │   ┌────────────────────────▼────────────────────────────────▼──────────────────────┐   │
  │   │                LANGGRAPH MULTI-AGENT SWARM ORCHESTRATOR                        │   │
  │   │   [Detection Agent]  ──> [MITRE Agent] + [Intel Agent] + [Correlation Agent]   │   │
  │   │                          ──> [Investigation Agent] ──> [SOAR Response Agent]    │   │
  │   └────────────────────────────────────────┬───────────────────────────────────────┘   │
  │                                            │                                           │
  │   ┌────────────────────────────────────────▼───────────────────────────────────────┐   │
  │   │                    DETERMINISTIC SAFETY & POLICY ENGINE                        │   │
  │   │   - Mathematical Risk Score: S = w1*Sev + w2*Mitre + w3*Ioc + w4*Chain + w5*Ass│   │
  │   │   - Human-in-the-Loop (HITL) Gate: Cryptographic Token Approval Barrier         │   │
  │   └────────────────────────────────────────┬───────────────────────────────────────┘   │
  └────────────────────────────────────────────┼───────────────────────────────────────────┘
                                               │
                           Active Response API │ Action Feedback Loop
                                               ▼
  ┌────────────────────────────────────────────────────────────────────────────────────────┐
  │                              SOC ANALYST COMMAND CENTER                                │
  │     Next.js 15 + React 19 + Tailwind CSS + Lucide Icons + TanStack React Query v5      │
  │     [Dashboard]   [Endpoints]   [Alerts/Incidents]   [SOAR Queue]   [AI Swarm Live]    │
  └────────────────────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Key Frontend Console Views (`/frontend/src/app`)

| Route | Page Name | Primary Technical Responsibility |
| :--- | :--- | :--- |
| `/` | **Command Center** | High-level defense posture, real-time sync across microservices, KPI metric cards, and SOAR severity distribution. |
| `/endpoints` | **Fleet Inventory** | Registered Wazuh agents live audit, OS detection, IP addresses, agent connection status, and active response sockets. |
| `/incidents` | **Incident Management** | Normalized security incidents, multi-factor risk scores, severity badges, and quick-access threat analysis triggers. |
| `/risk` | **SOAR Governance** | Human-in-the-Loop (HITL) quarantine queue, action approvals/rejections, and deterministic policy guardrail breakdowns. |
| `/swarm` | **Multi-Agent Cockpit** | Live visual graph of LangGraph swarm execution, agent thoughts, sub-second latency monitors, and MITRE correlations. |
| `/mitre` | **MITRE ATT&CK Matrix** | Full STIX 2.1 taxonomy catalog (14 Enterprise tactics, techniques, adversary playbooks, and mitigation procedures). |
| `/ai-router` | **Model Router Matrix** | Round-robin key ring pool health, active cloud model, Ollama offline readiness, and latency telemetry. |
| `/database` | **Storage Hub** | Telemetry indices overview, PostgreSQL audit trail volumes, and Wazuh OpenSearch cluster storage health. |

---

## 7. Methodology & Internal Logic Workflow

```text
[1. TELEMETRY INGESTION]  -->  [2. AGENT ENRICHMENT]  -->  [3. SWARM CONSENSUS]
          │                                                       │
          ▼                                                       ▼
[6. ACTIVE REMEDIATION]   <--  [5. HITL POLICY GATE]   <--  [4. RISK CALCULATION]
```

1. **Telemetry Ingestion:** Endpoints emit Sysmon/Auditd alerts $\rightarrow$ Wazuh Manager processes rules $\rightarrow$ Spectra-XDR async worker extracts normalized JSON.
2. **Sanitization & Feature Extraction:** IPs, hashes, usernames, and command arguments are extracted. Passwords, bearer tokens, and private keys are redacted.
3. **LangGraph Swarm Consensus:** 
   - Detection Agent assesses true-positive probability.
   - MITRE Agent matches techniques (e.g. `T1059.001 - PowerShell`).
   - Threat Intel Agent scores IP/hash reputation.
   - Correlation Agent tracks historical lateral connections.
   - Response Agent drafts mitigation commands.
4. **Deterministic Risk Calculation:** `risk/scoring.py` evaluates the 5-part weighted formula and locks the mathematical score ($0-100$).
5. **HITL Policy Enforcement:** High/Critical risk actions are marked `PENDING_APPROVAL` and held in the SOAR queue. Non-disruptive actions are auto-approved.
6. **Active Response Dispatch:** Approved commands are pushed to the Wazuh Manager API (`wazuh-control active-response`), executing endpoint host isolation or process termination with verified feedback.

---

## 8. Software Setup & System Requirements

### 8.1 System Prerequisites
- **Hardware:** Minimum 4 CPU Cores, 16 GB RAM (32 GB recommended for local Ollama), 50 GB free SSD storage.
- **Operating Systems:** Windows 10/11 (WSL2), Ubuntu 22.04/24.04 LTS, macOS (Apple Silicon / Intel).
- **Dependencies:** Docker Desktop & Docker Compose v2.20+, Python 3.12+, Node.js 20+.

### 8.2 Technology Stack Reference

| Component | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Core** | FastAPI / Python | 0.115+ / 3.12+ | Async REST API & incident orchestration engine |
| **AI Orchestrator**| LangGraph / LangChain | 0.2+ / 0.3+ | Multi-agent DAG state graph consensus |
| **Databases** | PostgreSQL / Redis | 16 / 7.2 | Immutable forensic records & async worker task queue |
| **EDR / SIEM** | Wazuh Manager / Indexer | 4.8.0 / 2.13.0 | Real-time endpoint telemetry & OpenSearch storage |
| **Frontend UI** | Next.js / React | 15.0+ / 19.0+ | Modern high-performance SOC dashboard |
| **Styling & State**| Tailwind CSS / TanStack | 3.4+ / Query v5 | Design system & real-time telemetry polling |
| **Cloud LLM** | Google Gemini API | Flash 2.5 / 1.5 | High-speed cloud reasoning & attack chain analysis |
| **Local LLM** | Ollama | 0.3+ (Mistral 7B)| Privacy-preserving, offline fallback inference |

### 8.3 Single-Command Quickstart

#### Option A: Docker Compose (Cross-Platform)
```powershell
docker compose up --build -d
```

#### Option B: Windows Native Launcher
```cmd
.\start.bat
```

#### Option C: Manual Development Run
```bash
# 1. Activate Python virtual environment & run migrations
.\.venv\Scripts\activate
alembic upgrade head

# 2. Start FastAPI Backend Gateway
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start Next.js Frontend Console
cd frontend
npm install
npm run dev
```

---

## 9. Implementation Plan for Next Phase (Phase 7 / Term 2)

1. **Autonomous Threat Hunting Engine:** Schedule background threat hunting jobs scanning unindexed historical Sysmon telemetry for APT persistence mechanisms.
2. **Kernel-Level eBPF Telemetry Sensor:** Deploy lightweight eBPF probes on Linux hosts to capture raw socket syscalls without userspace agent overhead.
3. **Automated Malware Sandboxing:** Integrate CAPEv2 / Cuckoo Sandbox connectors to automatically isolate and detonate suspicious binaries identified on endpoints.
4. **High-Throughput Streaming Pipeline:** Integrate Apache Kafka / Vector for distributed log ingestion exceeding 50,000 EPS (events per second).
5. **Multi-Party Cryptographic HITL Sign-off:** Enforce m-of-n multi-analyst signature verification before enterprise-wide isolation actions can execute.

---

## 10. Timeline Chart for Term 1

```text
┌────────────────────────────────────────┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐
│ Milestone / Task                       │W01│W02│W03│W04│W05│W06│W07│W08│W09│W10│W11│W12│
├────────────────────────────────────────┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┼───┤
│ Literature Review & Threat Modeling    │███│███│   │   │   │   │   │   │   │   │   │   │
│ Wazuh EDR & Telemetry Ingestion Setup  │   │███│███│███│   │   │   │   │   │   │   │   │
│ Database Schema & Async API Gateway    │   │   │   │███│███│   │   │   │   │   │   │   │
│ LangGraph Multi-Agent Swarm Logic      │   │   │   │   │███│███│███│   │   │   │   │   │
│ Model Router, Sanitizer & Ollama Fall  │   │   │   │   │   │   │███│███│   │   │   │   │
│ Deterministic Risk & Policy Engines    │   │   │   │   │   │   │   │███│███│   │   │   │
│ Next.js SOC Dashboard & HITL Interface │   │   │   │   │   │   │   │   │███│███│███│   │
│ Integration Testing & Pytest Suite (61)│   │   │   │   │   │   │   │   │   │   │███│███│
└────────────────────────────────────────┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘
```

---

## 11. Conclusion

Spectra-XDR bridges the operational divide separating isolated EDR, SIEM, and NDR products by introducing an **open-source, AI-governed Extended Detection and Response platform**.

### Key Technical Achievements Demonstrated:
- Ingestion and correlation of live endpoint telemetry across Windows and Linux fleets.
- Sub-second threat reasoning via a **3-phase LangGraph multi-agent swarm**.
- Complete elimination of automated response hallucinations through an explainable, **deterministic risk scoring formula**.
- Strict **Human-in-the-Loop safety boundaries** ensuring that high-impact remediations require authenticated human consent.
- Resilient model routing supporting cloud LLMs, multi-key pools, and offline Ollama fallbacks.

Spectra-XDR provides enterprise-grade detection and automated response capabilities with complete transparency, deterministic safety, and open-source flexibility.

---

## 12. Future Scope

1. **Cross-Tenant Federated Threat Intelligence:** Enable peer-to-peer sharing of IOC models between Spectra nodes without exposing raw telemetry.
2. **Cloud-Native Audit Connectors:** Extend detection coverage to AWS CloudTrail, Google Cloud Audit, and Kubernetes API logs.
3. **Automated Adversary Emulation:** Integrate Caldera and Atomic Red Team directly into the dashboard for one-click defense validation.
4. **Zero-Knowledge Action Verification:** Provide cryptographic proof verifying that an analyst possessed valid authorization before executing disruptive endpoint commands.

---

## 13. References

1. **Wazuh Open Source Security Platform:** Documentation and Architecture Manual, Wazuh Inc., 2024. [https://documentation.wazuh.com/](https://documentation.wazuh.com/)
2. **MITRE ATT&CK® Enterprise Matrix:** Design and Tactics Specification (v14), The MITRE Corporation, 2023. [https://attack.mitre.org/](https://attack.mitre.org/)
3. **LangGraph & LangChain Documentation:** Multi-Agent State Graph Orchestration, Harrison Chase et al., 2024. [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
4. **NIST Special Publication 800-61 Rev. 2:** Computer Security Incident Handling Guide, National Institute of Standards and Technology.
5. **CISA Best Practices for SOAR & Incident Response:** Cybersecurity and Infrastructure Security Agency, 2023.
6. **Sysinternals Sysmon Technical Reference:** Windows System and Network Monitoring, Microsoft Learn, Mark Russinovich et al.
7. **FastAPI Asynchronous Framework:** Sebastián Ramírez, 2024. [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
8. **Google Gemini LLM Technical Report:** Gemini Flash Architecture and Multimodal Reasoning Capabilities, Google DeepMind, 2024.
