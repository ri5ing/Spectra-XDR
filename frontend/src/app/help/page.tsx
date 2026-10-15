'use client';

import { useState } from 'react';
import Link from 'next/link';
import { 
  HelpCircle, 
  ArrowRight, 
  CheckCircle2, 
  ShieldAlert, 
  Laptop, 
  AlertTriangle, 
  ShieldCheck, 
  Activity, 
  Database, 
  Cpu, 
  Workflow, 
  Network, 
  Zap, 
  Layers, 
  Bot, 
  Search, 
  FileText, 
  Lock, 
  Terminal, 
  Share2, 
  RefreshCw,
  Sparkles,
  ChevronDown,
  ChevronRight,
  Server
} from 'lucide-react';
import { AskSpectraButton } from '@/components/copilot/AskSpectraButton';
import { useCopilotStore } from '@/lib/store/copilot';

export default function HelpArchitecturePage() {
  const { openCopilot } = useCopilotStore();
  const [activeTab, setActiveTab] = useState<'flow' | 'pages' | 'engines' | 'faq'>('flow');
  const [expandedFaq, setExpandedFaq] = useState<number | null>(0);

  const toggleFaq = (idx: number) => {
    setExpandedFaq(expandedFaq === idx ? null : idx);
  };

  const pagesInfo = [
    {
      title: 'Unified Command Center (Dashboard)',
      route: '/',
      icon: Layers,
      color: 'sky',
      purpose: 'Central SOC cockpit aggregating fleet-wide metrics, active threats, and master micro-engine power switches.',
      dataInput: 'Real-time rollups from Wazuh Agent Manager, Postgres database, and AI Model Router.',
      dataOutput: 'Executive posture score, quick navigation cards to all microservices, and engine start/stop toggles.',
      keyFeatures: [
        'Master ON/OFF switches for 7 independent security sub-engines',
        'Cross-module telemetry readings (Fleet, Swarm, MITRE, SOAR, Storage)',
        'SOAR containment distribution breakdown (Critical, High, Medium, Low)',
        'One-click deep links to every specialized workspace'
      ]
    },
    {
      title: 'Endpoints & Agent Fleet Management',
      route: '/endpoints',
      icon: Laptop,
      color: 'blue',
      purpose: 'Enrolled host inventory, connection heartbeats, remote live process exploration, and forensic terminal.',
      dataInput: 'Wazuh active-response API and Syscollector telemetry from Windows & Linux agents.',
      dataOutput: 'Per-host IP, OS details, live running processes with PID/CPU/Memory, and command line outputs.',
      keyFeatures: [
        'Live fleet heartbeat status (Active Online vs Disconnected)',
        'Forensic Process Explorer with PID kill actions (`taskkill /F /PID`)',
        'Interactive Encrypted Remote Shell (`whoami`, `netstat`, `ipconfig`, `tasklist`)',
        'Correlated incident drill-down directly linked to the target host'
      ]
    },
    {
      title: 'Alerts & Telemetry Stream',
      route: '/alerts',
      icon: AlertTriangle,
      color: 'amber',
      purpose: 'High-throughput stream of raw Sysmon, Windows Event Logs, and Linux auditd telemetry signals.',
      dataInput: 'Wazuh Log Analysis daemon & OpenSearch indexer indices (`wazuh-alerts-*`).',
      dataOutput: 'Normalized event objects with Rule IDs, Severity Levels (1-15), and agent identification.',
      keyFeatures: [
        'Real-time event filtering by Rule Level, MITRE ID, and Hostname',
        'Sub-second telemetry ingestion and rule level classification',
        'Direct correlation into Security Incident clusters',
        'Raw JSON telemetry viewer for forensic validation'
      ]
    },
    {
      title: 'MITRE ATT&CK Matrix & TAXII Feeds',
      route: '/mitre',
      icon: ShieldAlert,
      color: 'indigo',
      purpose: 'Enterprise threat matrix mapping observed adversary behaviors to standardized tactics and techniques.',
      dataInput: 'Automated TAXII 2.1 STIX threat feed ingestion synced into local PostgreSQL.',
      dataOutput: 'Mapped techniques (T1059, T1055, T1003, etc.), mitigation procedures, and detection logic.',
      keyFeatures: [
        'Enterprise ATT&CK matrix view organized by 14 tactics',
        'Real-time TAXII 2.1 STIX 2.1 sync status and collection inventory',
        'Threat actor attribution and technique mitigation playbooks',
        'Automatic playbook synchronization with SOAR containment policies'
      ]
    },
    {
      title: 'AI Multi-Agent Swarm Orchestrator',
      route: '/swarm',
      icon: Network,
      color: 'cyan',
      purpose: 'Autonomous swarm of 6 specialized AI agents collaborating concurrently to investigate and solve incidents.',
      dataInput: 'Correlated incident dossiers containing events, host context, and IOC hashes.',
      dataOutput: 'Multi-agent consensus reports, confidence scores, threat summaries, and SOAR mitigation plans.',
      keyFeatures: [
        '3-Phase Swarm Architecture (Ingestion → 4x Concurrent Agents → Consensus)',
        'Specialized Agent Roles: Triage, Threat Hunter, Forensic, Intel, and SOAR Supervisor',
        'Visual interactive graph of agent communications and message passes',
        'Sub-second autonomous analysis with LLM fallback routing'
      ]
    },
    {
      title: 'AI Model Router & Key Failover Ring',
      route: '/ai-router',
      icon: Cpu,
      color: 'purple',
      purpose: 'Dynamic AI model load balancing, secret API key failover, and local Ollama offline backup.',
      dataInput: 'Investigation prompts from Swarm Orchestrator and Copilot Assistant.',
      dataOutput: 'Selected inference provider (Gemini 2.5 Flash Cloud vs Local DeepSeek/Llama3).',
      keyFeatures: [
        'Zero-downtime circular key rotation across multiple Google Gemini API keys',
        'Automatic failover to local offline Ollama model if internet or cloud API drops',
        'Live model latency and quota consumption monitoring',
        '100% Free Tier optimization with enterprise resilience'
      ]
    },
    {
      title: 'Database Storage Hub',
      route: '/database',
      icon: Database,
      color: 'emerald',
      purpose: 'Forensic data storage health, table schema records, and OpenSearch index management.',
      dataInput: 'PostgreSQL 15 relational tables and Wazuh OpenSearch cluster metrics.',
      dataOutput: 'Storage consumption bytes, table row counts, and health status indicators.',
      keyFeatures: [
        'Postgres 15 schema breakdown (Incidents, Events, IOCs, Techniques, Audit Logs)',
        'OpenSearch / Wazuh Indexer shard metrics and document volumes',
        'Immutable forensic audit trail preservation',
        'Health check connection latencies for database connection pools'
      ]
    },
    {
      title: 'Risk Scoring & SOAR Policy Governance',
      route: '/risk',
      icon: Activity,
      color: 'rose',
      purpose: 'Deterministic risk calculation (0-100), SOAR playbook execution, and Human-in-the-Loop review.',
      dataInput: 'Incident severity, MITRE weights, asset criticality, and attack chain topology.',
      dataOutput: 'Automated mitigation dispatches, interactive attack graph, PDF report, and webhook alerts.',
      keyFeatures: [
        'Interactive 4-node Attack Chain Graph (Attacker IP → Host → Process → IOC)',
        'Human-in-the-Loop (HITL) gate guarding high blast radius actions (`isolate_host`)',
        'One-Click Executive Forensic PDF Report Generator with print styling',
        'Real-time SOC Webhook integration for Discord, Slack, and Microsoft Teams'
      ]
    }
  ];

  const enginesInfo = [
    {
      id: 'detection',
      name: 'Deterministic Detection Engine',
      purpose: 'Matches real-time endpoint telemetry against pre-compiled Sigma rules, Wazuh rulesets, and known IOC hashes.',
      input: 'Raw Sysmon/Auditd event stream',
      output: 'Validated Security Events & Rule Alerts'
    },
    {
      id: 'risk',
      name: 'Deterministic Risk Scoring Engine',
      purpose: 'Calculates normalized 0-100 risk score factoring severity, host business criticality, MITRE impact, and frequency.',
      input: 'Correlated event groups & asset metadata',
      output: 'Threat Level (LOW, MEDIUM, HIGH, CRITICAL)'
    },
    {
      id: 'swarm',
      name: 'AI Multi-Agent Swarm Orchestrator',
      purpose: 'Coordinates Triage, Threat Hunter, Forensic, Intel, and Supervisor agents in parallel to determine root cause.',
      input: 'Incident evidence dossier',
      output: 'Swarm consensus verdict & recommended remediation'
    },
    {
      id: 'ai_router',
      name: 'AI Model Router & Provider Balancer',
      purpose: 'Routes LLM prompts to the fastest available key or fails over to local Ollama if cloud quotas are exhausted.',
      input: 'Agent prompts & Copilot questions',
      output: 'Synthesized AI analysis response'
    },
    {
      id: 'soar',
      name: 'SOAR Containment Playbook Engine',
      purpose: 'Executes automated low-risk mitigations (`block_ip`) and stages high blast radius actions (`isolate_host`) in HITL queue.',
      input: 'Risk score & response playbook policy',
      output: 'Active quarantine action or HITL approval request'
    },
    {
      id: 'taxii',
      name: 'TAXII 2.1 Threat Intel Ingestion Engine',
      purpose: 'Periodically pulls STIX 2.1 threat intelligence bundles from public and private threat feeds into PostgreSQL.',
      input: 'External TAXII 2.1 threat repositories',
      output: 'Normalized IOC indicators and ATT&CK techniques'
    },
    {
      id: 'wazuh_collector',
      name: 'Wazuh Agent Heartbeat & Telemetry Collector',
      purpose: 'Maintains TLS socket sessions with enrolled Windows/Linux endpoints and parses live OS signals.',
      input: 'Encrypted endpoint heartbeat on port 1514',
      output: 'Decoded Syscollector and auth events'
    }
  ];

  const faqs = [
    {
      q: 'How does Spectra-XDR process a threat from start to finish (Full Data Flow)?',
      a: '1. Wazuh Agent on the endpoint captures suspicious execution (e.g. powershell bypass).\n2. Telemetry is streamed to Wazuh Manager & ingested into Spectra Events API.\n3. Deterministic Detection Engine validates rule thresholds and clusters events into an Incident.\n4. Risk Engine computes asset impact and assigns severity (Low, Medium, High, Critical).\n5. AI Multi-Agent Swarm investigates the attack chain across 3 concurrent phases.\n6. SOAR Policy evaluates blast radius: Low/Medium threats are mitigated autonomously; High/Critical threats trigger Human-in-the-Loop (HITL) review for analyst sign-off.'
    },
    {
      q: 'What is Human-in-the-Loop (HITL) and why is it important?',
      a: 'HITL ensures that high-impact containment actions—such as severing a production server\'s network connection (`isolate_endpoint`) or killing critical system processes (`kill_process`)—cannot be triggered automatically by AI without human verification. This eliminates costly business downtime caused by potential false positives.'
    },
    {
      q: 'How does the AI Model Router prevent API downtime and rate limits?',
      a: 'The router maintains a pool of multiple Google Gemini API keys. If any key encounters a 429 quota exhaustion or network timeout, the router automatically fails over to the next healthy key in milliseconds. If all cloud connections fail, it gracefully switches to an offline local Ollama model (e.g., DeepSeek R1 / Llama 3).'
    },
    {
      q: 'Can I start or stop specific security engines independently?',
      a: 'Yes! On the Unified Command Center (Dashboard `/`), the "Core Security Engines Control Center" provides granular ON/OFF toggle switches for every sub-engine (Detection, Risk Scoring, AI Swarm, Model Router, SOAR Playbooks, TAXII Ingestion, and Wazuh Collector). You can toggle any engine without taking down the rest of the platform.'
    },
    {
      q: 'How do I generate an incident report for executive leadership or audit compliance?',
      a: 'Navigate to Risk & SOAR Policy (`/risk`), locate the incident in the queue or solved list, and click "Export PDF Report". The system generates a forensic dossier with ATT&CK mappings, evidence timeline, and swarm findings, complete with a clean printable layout (`window.print()`).'
    }
  ];

  return (
    <div className="space-y-6 pb-16 max-w-7xl mx-auto select-none">
      {/* Header Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-zinc-200 gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-black text-zinc-950 font-mono tracking-tight uppercase">
              // ARCHITECTURE_&_DATA_FLOW_SPEC
            </h1>
            <span className="px-2.5 py-1 rounded-xs text-[11px] font-mono font-bold bg-zinc-950 text-white uppercase tracking-wider">
              SPEC_V2.4
            </span>
          </div>
          <p className="text-sm font-mono text-zinc-600 mt-1.5">
            EXHAUSTIVE TECHNICAL DOCUMENTATION: 6-STAGE EDR PIPELINE, 9 MODULE DIRECTORIES, AND 7 CORE ENGINES
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => openCopilot('Explain the entire Spectra-XDR data flow from Wazuh endpoint telemetry collection all the way to SOAR containment execution.')}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-mono text-xs font-bold rounded-xs transition-colors uppercase tracking-wider"
          >
            <Sparkles className="w-4 h-4" />
            <span>ASK_AI_ARCHITECT</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex border border-zinc-300 bg-zinc-100 rounded-xs p-1.5 gap-1.5 font-mono text-xs md:text-sm">
        <button
          onClick={() => setActiveTab('flow')}
          className={`flex-1 py-2.5 px-4 rounded-xs font-bold transition-all flex items-center justify-center gap-2 uppercase tracking-wider ${
            activeTab === 'flow'
              ? 'bg-zinc-950 text-white shadow-xs'
              : 'text-zinc-700 hover:text-zinc-950 hover:bg-zinc-200'
          }`}
        >
          <span>01 // EDR_PIPELINE</span>
        </button>

        <button
          onClick={() => setActiveTab('pages')}
          className={`flex-1 py-2.5 px-4 rounded-xs font-bold transition-all flex items-center justify-center gap-2 uppercase tracking-wider ${
            activeTab === 'pages'
              ? 'bg-zinc-950 text-white shadow-xs'
              : 'text-zinc-700 hover:text-zinc-950 hover:bg-zinc-200'
          }`}
        >
          <span>02 // MODULE_DIRECTORY</span>
        </button>

        <button
          onClick={() => setActiveTab('engines')}
          className={`flex-1 py-2.5 px-4 rounded-xs font-bold transition-all flex items-center justify-center gap-2 uppercase tracking-wider ${
            activeTab === 'engines'
              ? 'bg-zinc-950 text-white shadow-xs'
              : 'text-zinc-700 hover:text-zinc-950 hover:bg-zinc-200'
          }`}
        >
          <span>03 // ENGINE_SPECS</span>
        </button>

        <button
          onClick={() => setActiveTab('faq')}
          className={`flex-1 py-2.5 px-4 rounded-xs font-bold transition-all flex items-center justify-center gap-2 uppercase tracking-wider ${
            activeTab === 'faq'
              ? 'bg-zinc-950 text-white shadow-xs'
              : 'text-zinc-700 hover:text-zinc-950 hover:bg-zinc-200'
          }`}
        >
          <span>04 // SOC_RUNBOOKS</span>
        </button>
      </div>

      {/* Tab 1: Full EDR Data Flow */}
      {activeTab === 'flow' && (
        <div className="space-y-6">
          <div className="bg-white rounded-xs border border-zinc-200 shadow-xs p-6 space-y-6">
            <div>
              <h2 className="text-base md:text-lg font-black text-zinc-950 tracking-tight flex items-center gap-2 font-mono uppercase">
                <span>The 6-Stage Autonomous Security Pipeline</span>
                <span className="px-2.5 py-0.5 rounded-xs text-xs font-bold bg-emerald-50 text-emerald-800 border border-emerald-300">
                  REAL-TIME PIPELINE
                </span>
              </h2>
              <p className="text-xs md:text-sm text-zinc-600 font-mono mt-1">
                How an endpoint event transforms into an investigated, AI-analyzed, and mitigated incident
              </p>
            </div>

            {/* Pipeline Stage Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              
              {/* Stage 1 */}
              <div className="p-5 rounded-xs border border-zinc-200 bg-zinc-50 space-y-2.5 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-xs bg-zinc-950 text-white">
                    STAGE 01
                  </span>
                  <Laptop className="w-4 h-4 text-zinc-700" />
                </div>
                <h3 className="text-sm md:text-base font-bold text-zinc-950 font-mono">Endpoint Telemetry Ingestion</h3>
                <p className="text-xs md:text-sm text-zinc-700 leading-relaxed font-sans">
                  Wazuh agent daemon running on Windows/Linux intercepts OS events (process execution, registry modification, network socket binding) and forwards encrypted logs to the Wazuh Manager hub.
                </p>
                <div className="pt-2 border-t border-zinc-200 text-xs text-zinc-500 font-mono">
                  Protocols: Sysmon, Wazuh Agent Protocol (TCP 1514)
                </div>
              </div>

              {/* Stage 2 */}
              <div className="p-5 rounded-xs border border-zinc-200 bg-zinc-50 space-y-2.5 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-xs bg-zinc-950 text-white">
                    STAGE 02
                  </span>
                  <AlertTriangle className="w-4 h-4 text-zinc-700" />
                </div>
                <h3 className="text-sm md:text-base font-bold text-zinc-950 font-mono">Deterministic Rule Matching</h3>
                <p className="text-xs md:text-sm text-zinc-700 leading-relaxed font-sans">
                  Incoming telemetry is parsed by the Detection Engine against Sigma signatures, Wazuh XML rules, and TAXII STIX IOCs. Alerts with Rule Levels &ge; 5 are published to PostgreSQL and OpenSearch.
                </p>
                <div className="pt-2 border-t border-zinc-200 text-xs text-zinc-500 font-mono">
                  Latency: &lt; 15ms | Normalization: ECS Schema
                </div>
              </div>

              {/* Stage 3 */}
              <div className="p-5 rounded-xs border border-zinc-200 bg-zinc-50 space-y-2.5 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-[11px] font-mono font-bold px-2 py-0.5 rounded-xs bg-zinc-950 text-white">
                    STAGE 03
                  </span>
                  <Activity className="w-4 h-4 text-zinc-700" />
                </div>
                <h3 className="text-sm md:text-base font-bold text-zinc-950 font-mono">Risk Scoring & Correlation</h3>
                <p className="text-xs md:text-sm text-zinc-700 leading-relaxed font-sans">
                  Related events on the same host or user within a sliding time window are clustered into a Security Incident. Multi-factor formula computes a 0-100 threat score based on asset criticality and MITRE severity.
                </p>
                <div className="pt-2 border-t border-zinc-200 text-xs text-zinc-500 font-mono">
                  Formula: Severity &times; Asset Weight &times; Blast Factor
                </div>
              </div>

              {/* Stage 4 */}
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-purple-100 text-purple-800">
                    STAGE 04
                  </span>
                  <Network className="w-4 h-4 text-purple-600" />
                </div>
                <h3 className="text-sm font-bold text-slate-900">AI Multi-Agent Swarm Triage</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Incident triggers a 3-phase investigation swarm: Ingestion Agent formats evidence &rarr; Hunter, Forensic, and Intel agents analyze in parallel &rarr; Supervisor Synthesizer builds consensus remediation.
                </p>
                <div className="pt-2 border-t border-slate-200/80 text-[11px] text-slate-500 font-mono">
                  Latency: ~250ms | Key Ring: Circular Gemini / Ollama
                </div>
              </div>

              {/* Stage 5 */}
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-rose-100 text-rose-800">
                    STAGE 05
                  </span>
                  <Lock className="w-4 h-4 text-rose-600" />
                </div>
                <h3 className="text-sm font-bold text-slate-900">SOAR Policy & Blast Radius Gate</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Platform determines whether the proposed response can be safely automated. Safe mitigations (`block_ip`) execute autonomously. High blast actions (`isolate_host`) queue into Human-in-the-Loop (HITL).
                </p>
                <div className="pt-2 border-t border-slate-200/80 text-[11px] text-slate-500 font-mono">
                  Guardrails: Zero Unverified Host Quarantines
                </div>
              </div>

              {/* Stage 6 */}
              <div className="p-4 rounded-xl border border-slate-200 bg-slate-50/50 space-y-2 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-100 text-emerald-800">
                    STAGE 06
                  </span>
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                </div>
                <h3 className="text-sm font-bold text-slate-900">Mitigation & Audit Archival</h3>
                <p className="text-xs text-slate-600 leading-relaxed">
                  Approved actions are dispatched to Wazuh Active Response API. An immutable forensic ledger entry is recorded in PostgreSQL. Webhook notifications trigger alerts in Discord/Slack/Teams.
                </p>
                <div className="pt-2 border-t border-slate-200/80 text-[11px] text-slate-500 font-mono">
                  Audit Integrity: SHA-256 Ledger Record
                </div>
              </div>

            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Modules & Pages Directory */}
      {activeTab === 'pages' && (
        <div className="space-y-4">
          {pagesInfo.map((p) => {
            const Icon = p.icon;
            return (
              <div
                key={p.route}
                className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4 hover:border-slate-300 transition-all"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-slate-900 text-sky-400 flex items-center justify-center font-bold">
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-extrabold text-slate-900">{p.title}</h3>
                      <span className="text-xs font-mono text-slate-400 font-semibold">{p.route}</span>
                    </div>
                  </div>

                  <Link
                    href={p.route}
                    className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-800 rounded-xl text-xs font-bold transition-colors flex items-center gap-1.5 w-fit"
                  >
                    <span>Open Module</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed font-medium">
                  {p.purpose}
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 space-y-1">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Data Input Source</span>
                    <p className="text-xs text-slate-700 font-medium">{p.dataInput}</p>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80 space-y-1">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400">Data Output / Deliverable</span>
                    <p className="text-xs text-slate-700 font-medium">{p.dataOutput}</p>
                  </div>
                </div>

                <div>
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block mb-2">
                    Key Functionalities & Actions
                  </span>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {p.keyFeatures.map((feat, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-xs text-slate-600">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 shrink-0" />
                        <span>{feat}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Tab 3: Security Engines Deep Dive */}
      {activeTab === 'engines' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
            <div>
              <h2 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
                <Zap className="w-5 h-5 text-amber-500" />
                <span>Micro-Engines Powering Spectra-XDR</span>
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Each engine functions as an independent, decoupled microservice that can be toggled on or off from the Unified Command Center
              </p>
            </div>

            <div className="grid grid-cols-1 gap-3.5">
              {enginesInfo.map((eng) => (
                <div
                  key={eng.id}
                  className="p-4 rounded-xl border border-slate-200 bg-white hover:border-slate-300 transition-all space-y-2"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                      <h3 className="text-sm font-bold text-slate-900">{eng.name}</h3>
                    </div>
                    <span className="font-mono text-[11px] text-slate-400 font-bold uppercase">
                      ID: {eng.id}
                    </span>
                  </div>

                  <p className="text-xs text-slate-600 leading-relaxed font-medium">
                    {eng.purpose}
                  </p>

                  <div className="flex flex-col sm:flex-row gap-4 pt-2 border-t border-slate-100 text-[11px]">
                    <div>
                      <span className="font-bold text-slate-400 uppercase">Input: </span>
                      <span className="text-slate-700">{eng.input}</span>
                    </div>
                    <div>
                      <span className="font-bold text-slate-400 uppercase">Output: </span>
                      <span className="text-slate-700">{eng.output}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Platform FAQ & Runbooks */}
      {activeTab === 'faq' && (
        <div className="space-y-4">
          <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-6 space-y-4">
            <div>
              <h2 className="text-base font-extrabold text-slate-900 tracking-tight flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-sky-500" />
                <span>Frequently Asked Questions & SOC Operations</span>
              </h2>
              <p className="text-xs text-slate-500 mt-1">
                Common analyst queries regarding data correlation, AI responses, and platform governance
              </p>
            </div>

            <div className="divide-y divide-slate-100">
              {faqs.map((faq, idx) => {
                const isExpanded = expandedFaq === idx;
                return (
                  <div key={idx} className="py-4">
                    <button
                      onClick={() => toggleFaq(idx)}
                      className="w-full text-left flex items-center justify-between gap-4 font-bold text-xs text-slate-900 hover:text-sky-600 transition-colors"
                    >
                      <span className="text-sm font-bold">{faq.q}</span>
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-slate-400 shrink-0" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-slate-400 shrink-0" />
                      )}
                    </button>

                    {isExpanded && (
                      <div className="mt-3 text-xs text-slate-600 whitespace-pre-line leading-relaxed pl-2 border-l-2 border-sky-400 bg-sky-50/30 p-3 rounded-r-xl">
                        {faq.a}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
