# SPECTRA-XDR: Swarm-Powered Predictive Event Correlation & Threat Response Architecture
> **Comprehensive Technical Architecture, System Engineering, and Term-1 Project Report**  
> *Extended Detection and Response (XDR) | Security Information & Event Management (SIEM) | Endpoint Detection & Response (EDR) | Network Telemetry (NDR) | Autonomous SOAR Governance*

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [Literature Survey](#2-literature-survey)
3. [Problem Statement](#3-problem-statement)
4. [Research Objectives](#4-research-objectives)
5. [Frameworks and Algorithms](#5-frameworks-and-algorithms)
6. [Design Details and Architecture](#6-design-details-and-architecture)
7. [Methodology & Internal Logic Workflow](#7-methodology--internal-logic-workflow)
8. [Software Setup & System Requirements](#8-software-setup--system-requirements)
9. [Implementation Plan for Next Phase (Phase 7 / Term 2)](#9-implementation-for-next-plan)
10. [Timeline Chart for Term 1](#10-timeline-chart-for-term-1)
11. [Conclusion](#11-conclusion)
12. [Future Scope](#12-future-scope)
13. [References](#13-references)

---

## 1. Introduction

Modern enterprise attack surfaces have expanded exponentially across distributed endpoints, cloud infrastructure, hybrid operational networks, and virtualized workloads. Advanced Persistent Threats (APTs), zero-day exploits, ransomware campaigns, and fileless memory-only attacks consistently evade isolated perimeter defenses.

Traditional cybersecurity operations face significant challenges:
- **Disjointed Security Silos:** Organizations maintain separate tools for Endpoint Detection and Response (EDR), Network Detection and Response (NDR), and Security Information and Event Management (SIEM). These tools fail to share context in real time.
- **Alert Fatigue in the SOC:** Modern Security Operations Centers (SOCs) are overwhelmed with thousands of alerts daily, leading to analyst burnout, delayed triage, and missed indicators of compromise (IOCs).
- **Uncontrolled or Fragile Automation:** Traditional Security Orchestration, Automation, and Response (SOAR) playbooks often rely on fragile static scripts or unconstrained AI prompts that risk operational disruption on false positives.

**SPECTRA-XDR** (**S**warm-**P**owered **E**vent **C**orrelation & **T**hreat **R**esponse **A**rchitecture) is an open-source, hybrid Extended Detection and Response (XDR) and autonomous SOAR platform. Built on **Wazuh**, **MITRE ATT&CK Enterprise Matrix v14**, **LangGraph**, **Ollama**, and **Gemini Flash LLM**, Spectra unifies endpoint telemetry, network visibility, multi-agent AI threat reasoning, deterministic risk scoring, and cryptographically verified Human-in-the-Loop (HITL) response actions into a single operational command center.

---

## 2. Literature Survey

The development of unified detection and response architectures has evolved across several paradigms:

| Domain / Paradigm | Classical Implementation | Inherent Limitations | Spectra-XDR Architectural Enhancement |
| :--- | :--- | :--- | :--- |
| **SIEM (Security Information & Event Management)** | Splunk, IBM QRadar, ELK Stack | Ingests huge log volumes; high storage costs; rule-based correlation lacks multi-step attack reasoning; reactive querying. | Uses OpenSearch/Wazuh Indexer + PostgreSQL with unified normalized schemas (`telemetry_events`), real-time ingestion, and automatic agent triage. |
| **EDR (Endpoint Detection & Response)** | CrowdStrike Falcon, Microsoft Defender for Endpoint, SentinelOne | Proprietary agent lock-in; high licensing costs; high cloud dependency; limited local autonomous remediation. | Leverages open-source Wazuh agents (Sysmon & Auditd telemetry) with bidirectional active response sockets and local endpoint isolation. |
| **NDR (Network Detection & Response)** | Zeek, Snort, Suricata, Darktrace | High packet capture volumes; blind to encrypted traffic without endpoint-level correlation; lacks automated endpoint-side process termination. | Endpoint socket-to-process binding correlates outbound beaconing directly with parent process trees and MITRE C2 technique mapping. |
| **SOAR (Orchestration, Automation & Response)** | Palo Alto Cortex XSOAR, Splunk Phantom | Static, brittle playbooks; maintenance overhead; risk of network disruption without strict human guardrails. | Introduces a **Dual-Layer Governance Engine**: AI swarm formulates playbooks, but a **Deterministic Policy Engine** enforces strict mathematical gates and HITL cryptographic approvals. |
| **AI in Cybersecurity** | Single-prompt LLM wrappers, ChatGPT SOC assistants | Hallucinations; prompt injection vulnerabilities; data leakage of confidential tokens/IPs to cloud LLMs. | Implements a **Hierarchical LangGraph Multi-Agent Swarm** with an automated **Telemetry Sanitizer** and round-robin multi-key failover to offline local models (Ollama). |

---

## 3. Problem Statement

### 3.1 The Visibility & Correlation Gap
Enterprise security tools generate high volumes of isolated signals. Endpoint agents record process execution; network taps record IP connections; authentication logs capture login anomalies. Correlating these events across time, hosts, and networks requires manual human intervention, creating a critical visibility gap during lateral movement.

### 3.2 The Alert Triage Bottleneck
Tier-1 SOC analysts spend over 75% of their working hours manually investigating low-fidelity alerts, evaluating false positives, and cross-referencing external threat feeds. This high Mean Time to Detect (MTTD) and Mean Time to Respond (MTTR) provides adversaries an operational window of hours to days.

### 3.3 The Automation Dilemma: Hallucination vs. Inaction
Fully autonomous response systems risk taking mission-critical servers offline due to false positives or AI hallucinations. Conversely, purely manual approval pipelines fail to mitigate automated ransomware encrypting thousands of files per minute. 

**Spectra-XDR resolves this dilemma** by implementing a deterministic mathematical safety boundary that allows autonomous mitigation for low/medium non-disruptive threats while enforcing strict Human-in-the-Loop authorization for high/critical disruptive actions.

---

## 4. Research Objectives

1. **Unified Cross-Layer Telemetry Ingestion:** Develop an ingestion pipeline integrating Wazuh agents, Sysmon, Auditd, and network socket telemetry into a normalized security event schema.
2. **Multi-Agent AI Swarm Reasoning:** Design and deploy a 3-phase, 7-agent hierarchical LangGraph swarm (Detection, MITRE, Threat Intel, Correlation, Investigation, Response, and Reporting) capable of sub-second parallel analysis.
3. **Resilient Hybrid Model Routing & Privacy Preservation:** Build an intelligent model router with automated PII/credential sanitization, multi-key round-robin failover, and local offline LLM (Ollama) fallback.
4. **Deterministic Multi-Factor Risk Scoring:** Formulate an explainable, deterministic mathematical model calculating risk scores ($0 - 100$) derived from severity, MITRE tactics, IOC reputation, attack chain depth, and asset criticality.
5. **Safe, Policy-Guarded SOAR Execution:** Implement an active response framework enforcing Human-in-the-Loop (HITL) approval gates for disruptive actions (process termination, host quarantine, account disabling) while automating non-disruptive remediations.
6. **Real-Time SOC Command Center:** Build a high-performance web dashboard providing real-time telemetry streaming, incident lifecycle management, interactive swarm execution inspection, and an integrated AI Copilot.

---

## 5. Frameworks and Algorithms

### 5.1 Deterministic Multi-Factor Risk Scoring Formula
Spectra-XDR eliminates arbitrary LLM score hallucination by computing incident risk through a deterministic weighted formulation:

$$\text{Risk Score} = \min\left(100, \; w_1 S_{\text{severity}} + w_2 S_{\text{mitre}} + w_3 S_{\text{ioc}} + w_4 S_{\text{chain}} + w_5 S_{\text{asset}}\right)$$

Where:
- $S_{\text{severity}} \in [0, 100]$: Normalized Wazuh alert rule level ($0 - 16 \rightarrow 0 - 100$).
- $S_{\text{mitre}} \in [0, 100]$: Weight assigned based on MITRE tactic stage (Initial Access = $30$, Execution = $50$, Privilege Escalation = $70$, Lateral Movement = $85$, Impact/Exfiltration = $100$).
- $S_{\text{ioc}} \in [0, 100]$: Aggregated reputation score of extracted IP, domain, and file hash indicators.
- $S_{\text{chain}} \in [0, 100]$: Attack graph depth and count of correlated multi-host events over a 24-hour sliding window.
- $S_{\text{asset}} \in [0, 100]$: Criticality factor of target host (Workstation = $40$, Internal Server = $70$, Domain Controller / Crown Jewel = $100$).
- Weights configured by policy: $w_1 = 0.30, \; w_2 = 0.25, \; w_3 = 0.20, \; w_4 = 0.15, \; w_5 = 0.10$.

### 5.2 Deterministic Risk Matrix & Action Boundaries

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

### 6.1 High-Level Platform Architecture

```text
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                ENDPOINT FLEET LAYER                                    │
│    [Windows 11 Client]          [Ubuntu Server]           [Kali Linux Adversary VM]    │
│    Wazuh Agent + Sysmon        Wazuh Agent + Auditd       Simulated ATT&CK Emulation   │
└────────────────────────────────────────┬───────────────────────────────────────────────┘
                                         │ Encrypted Telemetry (Port 1514/1515 TCP)
                                         ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                 WAZUH SECURITY CORE                                    │
│   ┌────────────────────────┐  ┌─────────────────────────┐  ┌────────────────────────┐  │
│   │     Wazuh Manager      │  │      Wazuh Indexer      │  │    Wazuh Dashboard     │  │
│   │   Analysis Engine      ├──┤    OpenSearch Cluster   ├──┤   Web GUI (Port 8443)  │  │
│   │   Active Response      │  │  Normalized Telemetry   │  │   Compliance Views     │  │
│   └───────────┬────────────┘  └─────────────────────────┘  └────────────────────────┘  │
└───────────────┼────────────────────────────────────────────────────────────────────────┘
                │ REST API Telemetry Pull (Port 55000)
                ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             SPECTRA-XDR CONTROL PLANE                                  │
│                                                                                        │
│   ┌────────────────────────────────────────────────────────────────────────────────┐   │
│   │                     FastAPI Unified Gateway (:8000)                            │   │
│   │   - Incident Management      - Telemetry Ingestion      - SOAR Dispatcher      │   │
│   └───────────────────────┬────────────────────────────────┬───────────────────────┘   │
│                           │                                │                           │
│   ┌───────────────────────▼───────┐        ┌───────────────▼───────────────────────┐   │
│   │      PERSISTENCE LAYER        │        │        AI MODEL ROUTER MATRIX         │   │
│   │  - PostgreSQL 16 (Forensics)  │        │  - Gemini Flash (Multi-Key Ring)      │   │
│   │  - Redis 7.2 (Queue/Cache)    │        │  - Ollama Local (Offline Fallback)    │   │
│   │  - SQLAlchemy 2.0 Async ORM   │        │  - Regex PII Telemetry Sanitizer      │   │
│   └───────────────────────┬───────┘        └───────────────┬───────────────────────┘   │
│                           │                                │                           │
│   ┌───────────────────────▼────────────────────────────────▼───────────────────────┐   │
│   │               LANGGRAPH MULTI-AGENT SWARM ORCHESTRATOR                         │   │
│   │   [Detection Agent]  ──> [MITRE Agent] + [Intel Agent] + [Correlation Agent]  │   │
│   │                          ──> [Investigation Agent] ──> [SOAR Response Agent]   │   │
│   └────────────────────────────────────────┬───────────────────────────────────────┘   │
│                                            │                                           │
│   ┌────────────────────────────────────────▼───────────────────────────────────────┐   │
│   │                   DETERMINISTIC SAFETY & POLICY ENGINE                         │   │
│   │   - Mathematical Risk Score: S = w1*Sev + w2*Mitre + w3*Ioc + w4*Chain + w5*Ass │   │
│   │   - Human-in-the-Loop (HITL) Gate: Cryptographic Token Approval Barrier        │   │
│   └────────────────────────────────────────┬───────────────────────────────────────┘   │
└────────────────────────────────────────────┼───────────────────────────────────────────┘
                                             │
                         Active Response API │ Action Feedback Loop
                                             ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                             SOC ANALYST COMMAND CENTER                                 │
│    Next.js 15 + React 19 + Tailwind CSS + Lucide Icons + TanStack React Query v5       │
│    [Dashboard]   [Endpoints]   [Alerts/Incidents]   [SOAR Queue]   [AI Swarm Live]     │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Methodology & Internal Logic Workflow

Spectra-XDR follows a strict 6-stage lifecycle for every event traversing the platform:

```text
[1. TELEMETRY INGESTION]  -->  [2. AGENT ENRICHMENT]  -->  [3. SWARM CONSENSUS]
          │                                                       │
          ▼                                                       ▼
[6. ACTIVE REMEDIATION]   <--  [5. HITL POLICY GATE]   <--  [4. RISK CALCULATION]
```

### Stage 1: Ingestion & Normalization
- Endpoints send real-time system calls (Sysmon event IDs 1, 3, 7, 11; Linux auditd syscalls) to the Wazuh Manager.
- The Spectra backend polls alerts via the authenticated Wazuh REST API, maps them into unified schemas, and persists them into PostgreSQL.

### Stage 2: Feature Extraction & Sanitization
- File paths, hashes, IP addresses, command arguments, and user accounts are extracted.
- The `Telemetry Sanitizer` scrubs sensitive environment variables, authorization headers, and private key strings using regex boundaries before any AI analysis.

### Stage 3: LangGraph Swarm Consensus
- The incident is dispatched to the multi-agent graph.
- Agents execute their specialized prompts, recording their structured chain of thought into the database.
- Multi-key rotation ensures high uptime across free-tier and enterprise cloud LLM quotas.

### Stage 4: Deterministic Risk Scoring
- The outputs of the MITRE mapping, IOC scores, and historical incident correlation are fed into `risk/scoring.py`.
- The final score ($0 - 100$) and severity level are deterministically locked.

### Stage 5: Policy Evaluation & HITL Boundary
- The action engine checks `risk/policies.py`:
  - If the risk is $< 60$ and the playbook is non-disruptive $\rightarrow$ Status: `AUTO_APPROVED`.
  - If the risk is $\ge 60$ or action is disruptive (e.g., `isolate_endpoint`, `kill_process`) $\rightarrow$ Status: `PENDING_APPROVAL`.
- The action is held in the SOAR queue until an authenticated analyst reviews the AI summary and clicks **Approve**.

### Stage 6: Controlled Active Response Execution
- Approved actions are translated into Wazuh Active Response commands (`wazuh-control active-response`).
- The agent terminates the process or drops the socket on the target endpoint.
- Execution results are returned to Spectra, updating the incident state to `RESOLVED` with an immutable forensic audit log.

---

## 8. Software Setup & System Requirements

### 8.1 System Prerequisites
- **Operating System:** Windows 10/11 (64-bit with WSL2), Ubuntu 22.04/24.04 LTS, or macOS (Apple Silicon / Intel).
- **CPU:** Minimum 4 Cores (8 Cores recommended for local Ollama inference).
- **Memory (RAM):** 16 GB minimum (32 GB recommended if running Wazuh Indexer + Local LLM simultaneously).
- **Disk Storage:** 50 GB free SSD storage.
- **Virtualization:** Docker Desktop with Docker Compose v2.20+.

### 8.2 Technology Stack

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Core** | Python / FastAPI | 3.12+ / 0.115+ | High-performance async microservice gateway |
| **Orchestration** | LangGraph / LangChain | 0.2+ / 0.3+ | State graph execution for AI swarm |
| **Databases** | PostgreSQL / Redis | 16-alpine / 7.2 | Persistent transactional storage & hot task queues |
| **SIEM / EDR Core**| Wazuh Manager / Indexer | 4.8.0 / 2.13.0 | Telemetry collection, rules engine & OpenSearch |
| **Frontend UI** | Next.js / React | 15.0+ / 19.0+ | Modern Server/Client component SOC interface |
| **Styling & State**| Tailwind CSS / TanStack | 3.4+ / Query v5 | Design system & real-time telemetry polling |
| **LLM Tier 1** | Google Gemini API | Flash 2.5 / 1.5 | High-speed cloud reasoning and attack graph synthesis |
| **LLM Tier 2** | Ollama | 0.3+ (Mistral 7B)| Privacy-preserving, offline fallback inference |

### 8.3 Step-by-Step Installation

#### 1. Repository Setup & Virtual Environment
```bash
git clone https://github.com/ri5ing/Spectra-XDR.git
cd Spectra-XDR
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

#### 2. Environment Configuration
Copy `.env.example` to `.env` and configure your API keys and endpoints:
```ini
# PostgreSQL & Redis Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/spectra_xdr
REDIS_URL=redis://localhost:6379/0

# Wazuh Integration
WAZUH_API_URL=https://localhost:55000
WAZUH_API_USER=wazuh-wui
WAZUH_API_PASSWORD=YourWazuhPasswordHere
WAZUH_VERIFY_SSL=False

# AI Model Configuration
GEMINI_API_KEY=AIzaSy...YourPrimaryGeminiKey
GEMINI_KEY_2=AIzaSy...YourBackupGeminiKey
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral:7b
DEFAULT_MODEL_TIER=gemini_cloud
```

#### 3. Database Migration
```bash
alembic upgrade head
```

#### 4. Launch Infrastructure via Docker
```bash
docker compose up -d postgres redis wazuh-indexer wazuh-manager
```

#### 5. Launch Full Stack Development Servers
```bash
# Terminal 1: Backend API Gateway
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Next.js Frontend Console
cd frontend
npm install
npm run dev
```

---

## 9. Implementation Plan for Next Phase (Phase 7 / Term 2)

Building on the Term 1 foundation, the next development phase focuses on enterprise scale and automated threat hunting:

1. **Autonomous Threat Hunting Engine:** Implement schedule-based proactive queries hunting for unindexed persistence indicators across historical Sysmon logs.
2. **eBPF (Extended Berkeley Packet Filter) Kernel Sensor:** Add high-frequency kernel-level network and syscall monitoring for Linux workloads without agent overhead.
3. **Automated Dynamic Sandbox Integration:** Integrate Cuckoo Sandbox / CAPEv2 to automatically submit suspicious binaries extracted from endpoints for detonation analysis.
4. **Decentralized SIEM Streaming (Kafka / Vector):** Transition from periodic polling to an event-driven streaming architecture capable of handling 50,000+ events per second.
5. **Cryptographic Multi-Signature HITL Approvals:** Require m-of-n quorum approval from multiple authorized analysts for mission-critical enterprise isolation commands.

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

Spectra-XDR successfully bridges the operational divide separating isolated EDR, SIEM, and NDR tools by introducing a **cohesive, open-source, AI-governed XDR platform**. 

Key technical achievements demonstrated in Term 1 include:
- Unifying real-world Wazuh endpoint telemetry with sub-second backend ingestion.
- Eliminating AI hallucinations in critical response paths via a **Deterministic Mathematical Risk Formula**.
- Developing a resilient, privacy-preserving **Hybrid Multi-Agent Swarm** utilizing dynamic key rings, telemetry sanitization, and local offline fallbacks.
- Enforcing strict **Human-in-the-Loop cryptographic safety boundaries** for high-impact endpoint isolation and process mitigation.

The platform provides small-to-medium enterprises and academic institutions with a practical, cost-effective alternative to costly enterprise XDR suites without sacrificing security rigor or operational safety.

---

## 12. Future Scope

1. **Cross-Tenant Federated Learning:** Enable multiple decentralized Spectra-XDR nodes to exchange threat intelligence models without sharing sensitive raw telemetry.
2. **Native Cloud-Trail & Kubernetes Audit Connectors:** Extend detection beyond endpoints to AWS CloudTrail, Google Cloud Audit, and Kubernetes cluster control planes.
3. **Adversarial Attack Simulation Engine:** Automate built-in Caldera / Atomic Red Team adversary emulation directly within the dashboard to benchmark defense postures continuously.
4. **Zero-Knowledge Proofs for SOAR Actions:** Implement zero-knowledge cryptographic proofs verifying that an analyst had valid credentials before executing an endpoint kill command.

---

## 13. References

1. **Wazuh Open Source Security Platform:** Documentation and Architecture Manual, Wazuh Inc., 2024. [https://documentation.wazuh.com/](https://documentation.wazuh.com/)
2. **MITRE ATT&CK® Enterprise Matrix:** Design and Tactics Specification (v14), The MITRE Corporation, 2023. [https://attack.mitre.org/](https://attack.mitre.org/)
3. **LangGraph & LangChain Documentation:** Multi-Agent State Graph Orchestration, Harrison Chase et al., 2024. [https://langchain-ai.github.io/langgraph/](https://langchain-ai.github.io/langgraph/)
4. **NIST Special Publication 800-61 Rev. 2:** Computer Security Incident Handling Guide, National Institute of Standards and Technology, U.S. Department of Commerce.
5. **CISA Best Practices for SOAR & Incident Response:** Cybersecurity and Infrastructure Security Agency, 2023.
6. **Sysinternals Sysmon Technical Reference:** Windows System and Network Monitoring, Microsoft Learn, Mark Russinovich et al.
7. **FastAPI & Starlette High-Performance Asynchronous Framework:** Sebastián Ramírez, 2024. [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
8. **Google Gemini LLM Technical Report:** Gemini Flash Architecture and Multimodal Reasoning Capabilities, Google DeepMind, 2024.
