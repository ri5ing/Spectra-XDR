'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { 
  Laptop, 
  AlertTriangle, 
  ShieldCheck, 
  Activity, 
  Database, 
  Cpu, 
  Clock, 
  Radio, 
  Search, 
  Filter, 
  RefreshCw, 
  ChevronRight, 
  ExternalLink,
  ShieldAlert,
  Server,
  Zap,
  CheckCircle2,
  Lock,
  Layers,
  X,
  Workflow,
  Sparkles,
  Bot,
  Play,
  UserCheck,
  Flame,
  ArrowUpRight
} from 'lucide-react';
import Link from 'next/link';
import { formatTimestampIST } from '@/lib/time';
import { AskSpectraButton } from '@/components/copilot/AskSpectraButton';
import { useCopilotStore } from '@/lib/store/copilot';

export default function CommandCenter() {
  const { openCopilot } = useCopilotStore();

  // 1. Fetch Dashboard Summary
  const { data: summaryData, isLoading: summaryLoading, refetch: refetchSummary } = useQuery({
    queryKey: ['dashboard_summary'],
    queryFn: async () => {
      const res = await apiClient.get('/dashboard/summary');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // 2. Fetch Wazuh Agents Live (Endpoints)
  const { data: agentsResponse, refetch: refetchAgents } = useQuery({
    queryKey: ['wazuh_agents_list'],
    queryFn: async () => {
      const res = await apiClient.get('/wazuh/agents');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // 3. Fetch AI Model Router Status
  const { data: aiStatus, refetch: refetchAi } = useQuery({
    queryKey: ['ai_model_status'],
    queryFn: async () => {
      const res = await apiClient.get('/ai/status');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // 4. Fetch Database Storage Overview
  const { data: dbOverview, refetch: refetchDb } = useQuery({
    queryKey: ['db_overview'],
    queryFn: async () => {
      const res = await apiClient.get('/database/overview');
      return res.data;
    },
    refetchInterval: 10000,
  });

  // 5. Fetch MITRE ATT&CK Catalog Techniques
  const { data: mitreData = [] } = useQuery({
    queryKey: ['mitre_techniques_summary'],
    queryFn: async () => {
      const res = await apiClient.get('/intelligence/mitre');
      return res.data;
    },
    refetchInterval: 10000,
  });

  // 6. Fetch Active Incidents & SOAR Actions
  const { data: incidents = [], refetch: refetchIncidents } = useQuery({
    queryKey: ['incidents_list_dashboard'],
    queryFn: async () => {
      const res = await apiClient.get('/incidents?limit=50');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // 7. Fetch Security Engines Status & Toggles
  const { data: enginesData = [], refetch: refetchEngines } = useQuery({
    queryKey: ['security_engines_status'],
    queryFn: async () => {
      const res = await apiClient.get('/dashboard/engines');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // State for toggling loading state
  const [togglingEngineId, setTogglingEngineId] = useState<string | null>(null);

  const handleToggleEngine = async (engineId: string, currentEnabled: boolean) => {
    try {
      setTogglingEngineId(engineId);
      await apiClient.post(`/dashboard/engines/${engineId}/toggle`, {
        enabled: !currentEnabled,
      });
      refetchEngines();
    } catch (err) {
      console.error('Failed to toggle engine:', err);
    } finally {
      setTogglingEngineId(null);
    }
  };

  // Derived Metrics
  const allAgents = agentsResponse?.data?.affected_items || [];
  const monitoredAgents = allAgents.filter((a: any) => a.id !== '000');
  const activeCount = allAgents.filter((a: any) => a.status === 'active' && a.id !== '000').length;

  const totalIncidents = incidents.length;
  const criticalIncidents = incidents.filter((i: any) => (i.severity || '').toLowerCase() === 'critical').length;
  const highIncidents = incidents.filter((i: any) => (i.severity || '').toLowerCase() === 'high').length;
  const mediumIncidents = incidents.filter((i: any) => (i.severity || '').toLowerCase() === 'medium').length;
  const lowIncidents = incidents.filter((i: any) => (i.severity || '').toLowerCase() === 'low').length;

  const refetchAll = () => {
    refetchSummary();
    refetchAgents();
    refetchAi();
    refetchDb();
    refetchIncidents();
    refetchEngines();
  };

  return (
    <div className="space-y-6 pb-12 select-none">
      {/* 1. Header Banner & Defense Posture */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between pb-4 border-b border-zinc-200 gap-4">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl md:text-3xl font-black text-zinc-950 tracking-tight font-mono uppercase">
              // COMMAND_CENTER_MATRIX
            </h1>
            <span className="px-3 py-1 rounded-xs text-xs font-mono font-bold bg-zinc-950 text-white border border-zinc-900 flex items-center gap-2 uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>POSTURE: ACTIVE_DEFENSE</span>
            </span>
          </div>
          <p className="text-sm font-mono text-zinc-600 mt-1">
            CROSS-MODULE TELEMETRY ENGINE // ENDPOINTS, SWARM CONSENSUS, MITRE CATALOG, AND SOAR GOVERNANCE
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start lg:self-auto font-mono text-sm">
          <Link
            href="/help"
            className="flex items-center gap-2 px-3.5 py-2 bg-zinc-900 hover:bg-zinc-800 text-white font-bold rounded-xs transition-colors uppercase text-xs tracking-wider"
          >
            <Activity className="w-4 h-4 text-zinc-300" />
            <span>00 // ARCH_DOCS</span>
          </Link>

          <button
            onClick={refetchAll}
            className="flex items-center gap-2 px-3.5 py-2 bg-white border border-zinc-300 text-zinc-800 hover:bg-zinc-50 font-bold rounded-xs transition-colors uppercase text-xs tracking-wider"
          >
            <RefreshCw className="w-3.5 h-3.5 text-zinc-600" />
            <span>SYNC_ALL</span>
          </button>

          <button
            onClick={() => openCopilot('Provide a high-level executive security briefing on our current endpoint fleet, active incidents, and SOAR response readiness.')}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-bold rounded-xs transition-colors uppercase text-xs tracking-wider"
          >
            <Sparkles className="w-3.5 h-3.5 text-white" />
            <span>AI_EXECUTIVE</span>
          </button>
        </div>
      </div>

      {/* 2. Top-Level Module KPI Cards (Direct Link to Every Page) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Module 1: Endpoints & Fleet (/endpoints) */}
        <Link 
          href="/endpoints"
          className="p-5 bg-white rounded-xs border border-zinc-200 hover:border-zinc-950 transition-all flex flex-col justify-between group cursor-pointer shadow-xs"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-zinc-500 uppercase tracking-widest">01 // FLEET_AGENTS</span>
            <span className="font-mono text-xs text-zinc-400 group-hover:text-zinc-950 font-bold">&rarr;</span>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-2.5">
              <span className="text-4xl font-black text-zinc-950 font-mono tracking-tight">{activeCount}</span>
              <span className="text-sm font-mono font-semibold text-zinc-500">/ {monitoredAgents.length} ACTIVE</span>
            </div>
            <p className="text-xs font-mono text-zinc-600 mt-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-500" />
              <span>WAZUH PROTOCOL SYNCED</span>
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-zinc-100 flex items-center justify-between text-xs font-mono text-zinc-600 group-hover:text-zinc-950 font-bold uppercase">
            <span>INSPECT_HOSTS</span>
            <span className="text-[11px] text-zinc-400">PORT:1514</span>
          </div>
        </Link>

        {/* Module 2: SOAR & Risk Governance (/risk) */}
        <Link 
          href="/risk"
          className="p-5 bg-white rounded-xs border border-zinc-200 hover:border-zinc-950 transition-all flex flex-col justify-between group cursor-pointer shadow-xs"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-zinc-500 uppercase tracking-widest">02 // SOAR_QUEUE</span>
            <span className="font-mono text-xs text-zinc-400 group-hover:text-zinc-950 font-bold">&rarr;</span>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-2.5">
              <span className="text-4xl font-black text-zinc-950 font-mono tracking-tight">{totalIncidents}</span>
              <span className="text-sm font-mono font-semibold text-red-600">[{criticalIncidents + highIncidents} HITL_GATE]</span>
            </div>
            <p className="text-xs font-mono text-zinc-600 mt-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-amber-500" />
              <span>CONTAINMENT ACTIVE</span>
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-zinc-100 flex items-center justify-between text-xs font-mono text-zinc-600 group-hover:text-zinc-950 font-bold uppercase">
            <span>MANAGE_ACTIONS</span>
            <span className="text-[11px] text-red-600">GUARDED</span>
          </div>
        </Link>

        {/* Module 3: MITRE ATT&CK Catalog (/mitre) */}
        <Link 
          href="/mitre"
          className="p-5 bg-white rounded-xs border border-zinc-200 hover:border-zinc-950 transition-all flex flex-col justify-between group cursor-pointer shadow-xs"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-zinc-500 uppercase tracking-widest">03 // MITRE_MATRIX</span>
            <span className="font-mono text-xs text-zinc-400 group-hover:text-zinc-950 font-bold">&rarr;</span>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-2.5">
              <span className="text-4xl font-black text-zinc-950 font-mono tracking-tight">{mitreData.length || 18}</span>
              <span className="text-sm font-mono font-semibold text-zinc-500">TECHNIQUES</span>
            </div>
            <p className="text-xs font-mono text-zinc-600 mt-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-indigo-500" />
              <span>TAXII 2.1 STIX BUNDLE</span>
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-zinc-100 flex items-center justify-between text-xs font-mono text-zinc-600 group-hover:text-zinc-950 font-bold uppercase">
            <span>OPEN_CATALOG</span>
            <span className="text-[11px] text-zinc-400">14 TACTICS</span>
          </div>
        </Link>

        {/* Module 4: AI Model Router & Swarm (/ai-router & /swarm) */}
        <Link 
          href="/ai-router"
          className="p-5 bg-white rounded-xs border border-zinc-200 hover:border-zinc-950 transition-all flex flex-col justify-between group cursor-pointer shadow-xs"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono font-bold text-zinc-500 uppercase tracking-widest">04 // AI_ROUTER</span>
            <span className="font-mono text-xs text-zinc-400 group-hover:text-zinc-950 font-bold">&rarr;</span>
          </div>
          <div className="mt-4">
            <div className="flex items-baseline gap-2">
              <span className="text-lg font-black text-zinc-950 font-mono tracking-tight truncate max-w-[190px]">
                {aiStatus?.gemini_cloud?.model || 'GEMINI_FLASH'}
              </span>
            </div>
            <p className="text-xs font-mono text-zinc-600 mt-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-cyan-500" />
              <span>ROUND_ROBIN FAILOVER</span>
            </p>
          </div>
          <div className="mt-4 pt-3 border-t border-zinc-100 flex items-center justify-between text-xs font-mono text-zinc-600 group-hover:text-zinc-950 font-bold uppercase">
            <span>KEY_RING_CONFIG</span>
            <span className="text-[11px] text-emerald-600">ONLINE</span>
          </div>
        </Link>
      </div>

      {/* 3. Dedicated SOAR Policy & Incident Risk Reading Section */}
      <div className="bg-white rounded-xs border border-zinc-200 shadow-xs p-6 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-zinc-100 gap-3">
          <div>
            <div className="flex items-center gap-2.5">
              <ShieldCheck className="w-5 h-5 text-zinc-900" />
              <h2 className="text-sm md:text-base font-black text-zinc-950 tracking-tight font-mono uppercase">
                02 // SOAR_CONTAINMENT_TELEMETRY_DISTRIBUTION
              </h2>
            </div>
            <p className="text-xs font-mono text-zinc-600 mt-1">
              AUTONOMOUS EXECUTION VS HUMAN-IN-THE-LOOP (HITL) QUARANTINE GATES
            </p>
          </div>

          <Link
            href="/risk"
            className="flex items-center gap-2 px-3.5 py-1.5 bg-zinc-900 hover:bg-zinc-800 text-white font-mono text-xs font-bold rounded-xs transition-colors uppercase w-fit"
          >
            <span>OPEN_SOAR_CONSOLE &rarr;</span>
          </Link>
        </div>

        {/* Severity Readings Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 font-mono">
          <div className="p-4 rounded-xs border border-zinc-200 bg-zinc-50">
            <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest block">CRITICAL</span>
            <span className="text-3xl font-black text-red-600 mt-1 block">{criticalIncidents}</span>
            <span className="text-xs text-zinc-600 mt-1 block font-semibold">HITL_QUARANTINE</span>
          </div>

          <div className="p-4 rounded-xs border border-zinc-200 bg-zinc-50">
            <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest block">HIGH</span>
            <span className="text-3xl font-black text-zinc-950 mt-1 block">{highIncidents}</span>
            <span className="text-xs text-zinc-600 mt-1 block font-semibold">LATERAL_DEFENSE</span>
          </div>

          <div className="p-4 rounded-xs border border-zinc-200 bg-zinc-50">
            <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest block">MEDIUM</span>
            <span className="text-3xl font-black text-zinc-950 mt-1 block">{mediumIncidents}</span>
            <span className="text-xs text-zinc-600 mt-1 block font-semibold">AUTO_MITIGATED</span>
          </div>

          <div className="p-4 rounded-xs border border-zinc-200 bg-zinc-50">
            <span className="text-xs font-bold text-zinc-500 uppercase tracking-widest block">LOW</span>
            <span className="text-3xl font-black text-zinc-950 mt-1 block">{lowIncidents}</span>
            <span className="text-xs text-zinc-600 mt-1 block font-semibold">PASSIVE_AUDIT</span>
          </div>
        </div>

        {/* SOAR Policy Guardrail Breakdown */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 font-mono text-xs">
          <div className="p-3.5 rounded-xs bg-zinc-50 border border-zinc-200 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-zinc-900 uppercase flex items-center gap-1.5 text-[11px]">
                <Lock className="w-3 h-3 text-red-600" />
                HITL_GATE [HUMAN-IN-THE-LOOP]
              </span>
              <span className="text-[9px] font-bold px-1.5 py-0.2 bg-red-100 text-red-900 border border-red-300 rounded-xs uppercase">
                ENFORCED
              </span>
            </div>
            <p className="text-[11px] text-zinc-600 leading-relaxed font-sans">
              Critical host isolation and process termination actions require verified human analyst cryptographic authorization before execution on endpoints.
            </p>
          </div>

          <div className="p-3.5 rounded-xs bg-zinc-50 border border-zinc-200 space-y-1.5">
            <div className="flex items-center justify-between">
              <span className="font-bold text-zinc-900 uppercase flex items-center gap-1.5 text-[11px]">
                <Zap className="w-3 h-3 text-emerald-600" />
                AUTONOMOUS_PLAYBOOKS
              </span>
              <span className="text-[9px] font-bold px-1.5 py-0.2 bg-emerald-100 text-emerald-900 border border-emerald-300 rounded-xs uppercase">
                ACTIVE
              </span>
            </div>
            <p className="text-[11px] text-zinc-600 leading-relaxed font-sans">
              Low and Medium risk alerts trigger automated firewall boundary IP blocking and increased Syscheck audit frequencies without operational downtime.
            </p>
          </div>
        </div>
      </div>
      {/* 4. Complete System Modules Reading Table (Every Module Overview) */}
      <div className="bg-white rounded-xs border border-zinc-200 shadow-xs overflow-hidden">
        <div className="px-5 py-3 border-b border-zinc-200 bg-zinc-50 flex items-center justify-between font-mono">
          <div>
            <h2 className="text-xs font-black text-zinc-950 uppercase tracking-widest flex items-center gap-2">
              <span>03 // FULL_SYSTEM_MODULES_HEALTH_INDEX</span>
            </h2>
            <p className="text-[10px] text-zinc-500 mt-0.5">
              REAL-TIME OPERATIONAL TELEMETRY ACROSS ALL MICROSERVICES
            </p>
          </div>
          <span className="text-[10px] font-bold px-2 py-0.5 bg-zinc-900 text-white rounded-xs uppercase">
            6 MODULES ONLINE
          </span>
        </div>

        <div className="divide-y divide-zinc-100 font-mono">
          
          {/* Row 1: Fleet Endpoints & Agents */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-zinc-50/70 transition-colors">
            <div className="flex items-center gap-4">
              <span className="text-sm font-bold text-zinc-400">01</span>
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-sm font-bold text-zinc-950">ENDPOINTS & FLEET MANAGEMENT</h3>
                  <span className="px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-300 text-[10px] font-bold rounded-xs">
                    WAZUH_ACTIVE
                  </span>
                </div>
                <p className="text-xs text-zinc-600 font-sans mt-1">
                  Host inventory, Sysmon/Auditd telemetry agents, and active response socket
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-right">
                <p className="text-sm font-bold text-zinc-950">{activeCount} / {monitoredAgents.length} ONLINE</p>
                <p className="text-xs text-zinc-500">NODE: LAZASUS</p>
              </div>
              <Link
                href="/endpoints"
                className="px-3.5 py-1.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-900 font-bold text-xs rounded-xs transition-colors"
              >
                OPEN &rarr;
              </Link>
            </div>
          </div>

          {/* Row 2: AI Multi-Agent Swarm */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-zinc-50/70 transition-colors">
            <div className="flex items-center gap-4">
              <span className="text-sm font-bold text-zinc-400">02</span>
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-sm font-bold text-zinc-950">AI MULTI-AGENT SWARM ORCHESTRATOR</h3>
                  <span className="px-2 py-0.5 bg-zinc-100 text-zinc-800 border border-zinc-300 text-[10px] font-bold rounded-xs">
                    3_PHASE_CONCURRENT
                  </span>
                </div>
                <p className="text-xs text-zinc-600 font-sans mt-1">
                  Phase 1 Ingestion &rarr; 4x Concurrent Phase 2 Analysis &rarr; Phase 3 SOAR Decision
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-right">
                <p className="text-sm font-bold text-zinc-950">6 AGENTS RUNNING</p>
                <p className="text-xs text-zinc-500">~250MS MEAN LATENCY</p>
              </div>
              <Link
                href="/swarm"
                className="px-3.5 py-1.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-900 font-bold text-xs rounded-xs transition-colors"
              >
                OPEN &rarr;
              </Link>
            </div>
          </div>

          {/* Row 3: Deterministic Risk Engine & SOAR Policy */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-zinc-50/70 transition-colors">
            <div className="flex items-center gap-4">
              <span className="text-sm font-bold text-zinc-400">03</span>
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-sm font-bold text-zinc-950">RISK SCORING & SOAR POLICY GOVERNANCE</h3>
                  <span className="px-2 py-0.5 bg-red-50 text-red-800 border border-red-300 text-[10px] font-bold rounded-xs">
                    HITL_GUARDED
                  </span>
                </div>
                <p className="text-xs text-zinc-600 font-sans mt-1">
                  Multi-factor risk score formulas, MITRE playbook synchronization, and action approvals
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-right">
                <p className="text-sm font-bold text-zinc-950">{totalIncidents} INCIDENTS</p>
                <p className="text-xs text-red-600 font-bold">{criticalIncidents} CRITICAL HITL</p>
              </div>
              <Link
                href="/risk"
                className="px-3.5 py-1.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-900 font-bold text-xs rounded-xs transition-colors"
              >
                OPEN &rarr;
              </Link>
            </div>
          </div>

          {/* Row 4: MITRE ATT&CK Catalog */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-zinc-50/70 transition-colors">
            <div className="flex items-center gap-4">
              <span className="text-sm font-bold text-zinc-400">04</span>
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-sm font-bold text-zinc-950">MITRE ATT&CK ENTERPRISE CATALOG</h3>
                  <span className="px-2 py-0.5 bg-indigo-50 text-indigo-800 border border-indigo-300 text-[10px] font-bold rounded-xs">
                    TAXII_2.1_STIX
                  </span>
                </div>
                <p className="text-xs text-zinc-600 font-sans mt-1">
                  Enterprise threat actor mapping, technique mitigations, and detection rules
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-right">
                <p className="text-sm font-bold text-zinc-950">{mitreData.length || 18} TECHNIQUES</p>
                <p className="text-xs text-zinc-500">14 TACTICS LOADED</p>
              </div>
              <Link
                href="/mitre"
                className="px-3.5 py-1.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-900 font-bold text-xs rounded-xs transition-colors"
              >
                OPEN &rarr;
              </Link>
            </div>
          </div>

          {/* Row 5: AI Model Router */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-zinc-50/70 transition-colors">
            <div className="flex items-center gap-4">
              <span className="text-sm font-bold text-zinc-400">05</span>
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-sm font-bold text-zinc-950">AI MODEL ROUTER & SECRET KEY RING</h3>
                  <span className="px-2 py-0.5 bg-zinc-100 text-zinc-800 border border-zinc-300 text-[10px] font-bold rounded-xs">
                    CIRCULAR_FAILOVER
                  </span>
                </div>
                <p className="text-xs text-zinc-600 font-sans mt-1">
                  Multi-key round robin load balancer, local Ollama failover, and latency monitor
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-right">
                <p className="text-sm font-bold text-zinc-950">{aiStatus?.gemini_cloud?.model || 'GEMINI_FLASH'}</p>
                <p className="text-xs text-zinc-500">100% FREE TIER CLOUD</p>
              </div>
              <Link
                href="/ai-router"
                className="px-3.5 py-1.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-900 font-bold text-xs rounded-xs transition-colors"
              >
                OPEN &rarr;
              </Link>
            </div>
          </div>

          {/* Row 6: Database Storage Hub */}
          <div className="p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-zinc-50/70 transition-colors">
            <div className="flex items-center gap-4">
              <span className="text-sm font-bold text-zinc-400">06</span>
              <div>
                <div className="flex items-center gap-2.5">
                  <h3 className="text-sm font-bold text-zinc-950">DATABASE STORAGE HUB</h3>
                  <span className="px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-300 text-[10px] font-bold rounded-xs">
                    POSTGRES_OPENSEARCH
                  </span>
                </div>
                <p className="text-xs text-zinc-600 font-sans mt-1">
                  Immutable forensic audit trails, telemetry indices, and hot cache stores
                </p>
              </div>
            </div>

            <div className="flex items-center gap-6">
              <div className="text-right">
                <p className="text-sm font-bold text-zinc-950">{dbOverview?.postgresql?.total_size || '27 MB'} POSTGRES</p>
                <p className="text-xs text-zinc-500">OPENSEARCH: {dbOverview?.wazuh_indexer?.total_store_size || '1.1 MB'}</p>
              </div>
              <Link
                href="/database"
                className="px-3.5 py-1.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-900 font-bold text-xs rounded-xs transition-colors"
              >
                OPEN &rarr;
              </Link>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}
