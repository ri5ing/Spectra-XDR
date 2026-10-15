'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { 
  Play, 
  ArrowRight, 
  CheckCircle2, 
  Cpu, 
  ShieldAlert, 
  Layers, 
  Search, 
  GitBranch, 
  Terminal, 
  UserCheck,
  AlertCircle,
  Clock,
  Sparkles,
  X,
  Activity,
  ChevronRight,
  Filter,
  Check,
  Zap,
  Info,
  Radio,
  Share2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';
import { useCopilotStore } from '@/lib/store/copilot';
import { formatTimestampIST } from '@/lib/time';

export default function SwarmPage() {
  const queryClient = useQueryClient();
  const { openCopilot } = useCopilotStore();

  const [selectedIncidentId, setSelectedIncidentId] = useState<string>('');
  const [filterSeverity, setFilterSeverity] = useState<string>('all');
  
  // Modals
  const [activeModalEvent, setActiveModalEvent] = useState<any | null>(null);
  const [activeModalAgent, setActiveModalAgent] = useState<any | null>(null);

  // 1. Fetch live incidents / events queue list
  const { data: incidents = [], isLoading: incLoading } = useQuery({
    queryKey: ['incidents_list'],
    queryFn: async () => {
      const res = await apiClient.get('/incidents?limit=25');
      return res.data;
    },
    refetchInterval: 4000,
  });

  const activeIncId = selectedIncidentId || (incidents[0]?.id ?? '');
  const activeIncident = incidents.find((i: any) => i.id === activeIncId) || incidents[0];

  // 2. Fetch live latest swarm run for active incident
  const { data: swarmRun, isLoading: runLoading } = useQuery({
    queryKey: ['swarm_run', activeIncId],
    queryFn: async () => {
      if (!activeIncId) return null;
      try {
        const res = await apiClient.get(`/swarm/runs/${activeIncId}`);
        if (res.data?.status === 'not_analyzed' && !runSwarmMutation.isPending) {
          runSwarmMutation.mutate(activeIncId);
        }
        return res.data;
      } catch (err) {
        return null;
      }
    },
    enabled: Boolean(activeIncId),
    refetchInterval: 3000,
  });

  // 3. Trigger swarm mutation
  const runSwarmMutation = useMutation({
    mutationFn: async (incId: string) => {
      const res = await apiClient.post(`/swarm/analyze/${incId}`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['swarm_run', activeIncId] });
      queryClient.invalidateQueries({ queryKey: ['incidents_list'] });
    },
  });

  const completedAgents = swarmRun?.completed_agents || [];

  // 3-Phase Multi-Agent Architecture Structure
  const phase1Agent = {
    step: 1,
    role: 'detection_agent',
    name: 'Detection Agent',
    short: 'Ingestion & Triage',
    icon: Search,
    color: 'blue',
    mission: 'Alert ingestion, anomaly detection, threat severity scoring, and initial SOC triage classification.',
    roleDesc: 'Analyzes raw incoming telemetry, filters benign system noise, and isolates attack signals.'
  };

  const phase2Agents = [
    {
      step: 2,
      role: 'mitre_agent',
      name: 'MITRE Intel Agent',
      short: 'ATT&CK Mapping',
      icon: Layers,
      color: 'purple',
      mission: 'ATT&CK matrix mapping, tactic & technique correlation, mitigation info, and STIX/TAXII enrichment.',
      roleDesc: 'Translates raw endpoint events into MITRE ATT&CK tactics, techniques, and adversary behaviors.'
    },
    {
      step: 3,
      role: 'threat_intel_agent',
      name: 'Threat Intel Agent',
      short: 'IOC Enrichment',
      icon: ShieldAlert,
      color: 'amber',
      mission: 'IOC enrichment, reputation scoring, external threat intelligence lookup, and malware signature analysis.',
      roleDesc: 'Scores external IPs, domains, and file hashes against threat reputation feeds.'
    },
    {
      step: 4,
      role: 'investigation_agent',
      name: 'Investigation Agent',
      short: 'Deep Forensics',
      icon: Terminal,
      color: 'cyan',
      mission: 'Deep read-only forensics, process tree audit, host/user context enrichment, and evidence compilation.',
      roleDesc: 'Conducts read-only forensic audits on endpoints, inspecting users, processes, and parent trees.'
    },
    {
      step: 5,
      role: 'correlation_agent',
      name: 'Correlation Agent',
      short: 'Attack Chain Building',
      icon: GitBranch,
      color: 'indigo',
      mission: 'Multi-event correlation, attack chain building, temporal analysis, and cross-entity clustering.',
      roleDesc: 'Correlates concurrent telemetry streams into chronological attack progressions.'
    }
  ];

  const phase3Agents = [
    {
      step: 6,
      role: 'response_agent',
      name: 'Response Agent',
      short: 'SOAR Containment',
      icon: UserCheck,
      color: 'emerald',
      mission: 'Action recommendation, SOAR playbook automation, containment isolation, and active response dispatch.',
      roleDesc: 'Formulates controlled mitigation playbooks, host isolation commands, and network quarantine measures.'
    },
    {
      step: 7,
      role: 'supervisor',
      name: 'Executive Supervisor',
      short: 'Synthesis & Brief',
      icon: Cpu,
      color: 'blue',
      mission: 'Executive briefing, overall incident posture synthesis, and human approval policy checks.',
      roleDesc: 'Compiles multi-agent forensic evidence into executive summaries and containment audits.'
    }
  ];

  // Helper to determine status for each node
  const getNodeStatus = (role: string) => {
    if (completedAgents.includes(role)) {
      return { status: 'DONE', label: 'Done', color: 'emerald' };
    }
    if (runSwarmMutation.isPending) {
      // Phase 1
      if (role === 'detection_agent') {
        return { status: 'IN_PROGRESS', label: 'Triage Working', color: 'blue' };
      }
      // Phase 2: If Phase 1 done and Phase 2 not all done
      const phase1Done = completedAgents.includes('detection_agent');
      if (phase1Done && ['mitre_agent', 'threat_intel_agent', 'investigation_agent', 'correlation_agent'].includes(role)) {
        return { status: 'IN_PROGRESS', label: 'Parallel Working', color: 'blue' };
      }
      // Phase 3
      const phase2Done = ['mitre_agent', 'threat_intel_agent', 'investigation_agent', 'correlation_agent'].every(r => completedAgents.includes(r));
      if (phase2Done && ['response_agent', 'supervisor'].includes(role)) {
        return { status: 'IN_PROGRESS', label: 'Convergence', color: 'blue' };
      }
      return { status: 'IN_QUEUE', label: 'In Queue', color: 'amber' };
    }
    return { status: 'STANDBY', label: 'Standby', color: 'slate' };
  };

  const isPhase1Active = runSwarmMutation.isPending && !completedAgents.includes('detection_agent');
  const isPhase1Done = completedAgents.includes('detection_agent');

  const isPhase2Active = runSwarmMutation.isPending && isPhase1Done && !phase2Agents.every(a => completedAgents.includes(a.role));
  const isPhase2Done = phase2Agents.every(a => completedAgents.includes(a.role));

  const isPhase3Active = runSwarmMutation.isPending && isPhase2Done && !phase3Agents.every(a => completedAgents.includes(a.role));
  const isPhase3Done = phase3Agents.every(a => completedAgents.includes(a.role));

  const filteredIncidents = incidents.filter((inc: any) => {
    if (filterSeverity === 'all') return true;
    return String(inc.severity || '').toLowerCase() === filterSeverity.toLowerCase();
  });

  return (
    <div className="space-y-6 pb-20 max-w-[1600px] mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b-2 border-zinc-950 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 font-mono text-xs font-bold text-red-600 uppercase tracking-widest">
            <span>[MODULE 05]</span>
            <span>//</span>
            <span>MULTI_AGENT_SWARM_ORCHESTRATOR</span>
          </div>
          <h1 className="text-3xl font-black text-zinc-950 tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950 shadow-xs">
              <Cpu className="w-5 h-5 text-red-500" />
            </div>
            <span>AI SWARM ENGINE</span>
          </h1>
          <p className="text-sm font-medium text-zinc-600 mt-1">
            3-Phase Asynchronous Swarm Architecture: Alert triage, parallel intelligence execution, and SOAR response convergence.
          </p>
        </div>

        <div className="flex items-center gap-3 font-mono">
          <button
            disabled={!activeIncId || runSwarmMutation.isPending}
            onClick={() => runSwarmMutation.mutate(activeIncId)}
            className="flex items-center gap-2 px-5 py-2.5 bg-zinc-950 hover:bg-zinc-800 text-white text-xs font-bold uppercase border-2 border-zinc-950 shadow-xs transition-all disabled:opacity-50 cursor-pointer"
          >
            {runSwarmMutation.isPending ? (
              <>
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
                  <Cpu className="w-4 h-4 text-red-500" />
                </motion.div>
                <span>EXECUTING_SWARM...</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-red-500 text-red-500" />
                <span>TRIGGER_SWARM_RUN</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 1. HORIZONTAL 3-PHASE DATA FLOW DIAGRAM WITH PARALLEL ARROWS & ANIMATION */}
      {/* ========================================================================= */}
      <div className="bg-white border-2 border-zinc-950 p-6 shadow-xs overflow-hidden">
        {/* Header Strip */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 mb-6 border-b-2 border-zinc-950">
          <div className="flex items-center gap-3">
            <div className="w-3 h-3 bg-red-600 animate-pulse" />
            <h3 className="text-sm font-black text-zinc-950 uppercase tracking-wider font-mono">
              // LIVE_SWARM_EXECUTION_GRAPH
            </h3>
            {activeIncident && (
              <span className="text-xs font-mono font-bold px-2.5 py-1 bg-zinc-100 border border-zinc-300 text-zinc-950">
                INCIDENT_TARGET: {activeIncident.incident_id || activeIncident.id.substring(0, 8)}
              </span>
            )}
          </div>
          <div className="flex items-center gap-4 text-xs font-mono font-bold text-zinc-700">
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-emerald-500" /> DONE</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-red-500 animate-pulse" /> WORKING</span>
            <span className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-zinc-400" /> STANDBY</span>
          </div>
        </div>

        {/* 3-PHASE HORIZONTAL GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-center">
          
          {/* ---------------------------------------------------- */}
          {/* PHASE 1: ALERT INGESTION & DETECTION TRIAGE (3 Cols) */}
          {/* ---------------------------------------------------- */}
          <div className="lg:col-span-3 flex flex-col justify-between h-full bg-zinc-50 p-4 border-2 border-zinc-950 shadow-xs relative">
            <div className="flex items-center justify-between pb-2 mb-3 border-b-2 border-zinc-200">
              <span className="text-xs font-black font-mono uppercase tracking-wider px-2 py-0.5 bg-zinc-950 text-white">
                // PHASE 01: INGESTION
              </span>
              <span className="text-xs font-mono font-bold text-zinc-500 uppercase">SEQUENTIAL</span>
            </div>

            {/* Single Detection Agent Card */}
            {(() => {
              const node = phase1Agent;
              const statusInfo = getNodeStatus(node.role);
              const thought = swarmRun?.thoughts?.find((t: any) => t.agent_role === node.role);

              return (
                <button
                  onClick={() => setActiveModalAgent({ ...node, thought })}
                  className={cn(
                    'w-full text-left p-4 border-2 transition-all relative group shadow-xs cursor-pointer',
                    statusInfo.status === 'DONE'
                      ? 'bg-zinc-950 text-white border-zinc-950'
                      : statusInfo.status === 'IN_PROGRESS'
                      ? 'bg-zinc-950 text-white border-red-600 shadow-md translate-x-1'
                      : 'bg-white text-zinc-950 border-zinc-300 hover:border-zinc-950'
                  )}
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className={cn(
                      'w-8 h-8 flex items-center justify-center font-bold border',
                      statusInfo.status === 'DONE' || statusInfo.status === 'IN_PROGRESS'
                        ? 'bg-red-600 border-red-500 text-white'
                        : 'bg-zinc-100 border-zinc-300 text-zinc-950'
                    )}>
                      <node.icon className="w-4 h-4 stroke-[2.2]" />
                    </div>
                    {statusInfo.status === 'DONE' ? (
                      <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                    ) : statusInfo.status === 'IN_PROGRESS' ? (
                      <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: 'linear' }}>
                        <Cpu className="w-5 h-5 text-red-500" />
                      </motion.div>
                    ) : (
                      <Clock className="w-4 h-4 text-zinc-400" />
                    )}
                  </div>

                  <h4 className="text-sm font-black tracking-tight font-sans">
                    {node.name}
                  </h4>
                  <p className={cn(
                    'text-xs font-mono mt-1',
                    statusInfo.status === 'DONE' || statusInfo.status === 'IN_PROGRESS' ? 'text-zinc-300' : 'text-zinc-600'
                  )}>
                    {node.short}
                  </p>

                  <div className="mt-4 pt-2.5 border-t border-zinc-700/40 flex items-center justify-between font-mono">
                    <span
                      className={cn(
                        'text-[10px] font-black px-2 py-0.5 uppercase tracking-wider',
                        statusInfo.status === 'DONE'
                          ? 'bg-emerald-500 text-zinc-950'
                          : statusInfo.status === 'IN_PROGRESS'
                          ? 'bg-red-600 text-white animate-pulse'
                          : 'bg-zinc-200 text-zinc-800'
                      )}
                    >
                      [{statusInfo.label.toUpperCase()}]
                    </span>
                    <span className="text-xs font-bold text-red-400 group-hover:translate-x-1 transition-transform">
                      INSPECT &rarr;
                    </span>
                  </div>
                </button>
              );
            })()}

            <p className="text-xs text-zinc-500 font-mono mt-3 text-center uppercase">
              Normalizes telemetry & filters noise
            </p>
          </div>

          {/* CONNECTOR ARROW 1 -> 2 (Forks into 4 Parallel Streams) */}
          <div className="hidden lg:flex lg:col-span-1 flex-col items-center justify-center relative font-mono">
            <div className="text-[10px] font-black uppercase text-zinc-950 bg-white border-2 border-zinc-950 px-2 py-0.5 mb-2 shadow-xs whitespace-nowrap">
              FORKS 4X
            </div>
            {/* Animated Flow Arrow */}
            <div className="relative w-full flex items-center justify-center">
              <div className="w-full h-1 bg-zinc-300 overflow-hidden">
                <motion.div
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }}
                  className={cn(
                    'w-1/2 h-full',
                    isPhase1Done ? 'bg-red-600' : 'bg-zinc-400'
                  )}
                />
              </div>
              <ArrowRight className={cn(
                'w-4 h-4 shrink-0 -ml-1',
                isPhase1Done ? 'text-red-600' : 'text-zinc-400'
              )} />
            </div>
          </div>

          {/* ---------------------------------------------------- */}
          {/* PHASE 2: PARALLEL SWARM REASONING (4 AGENTS) (4 Cols) */}
          {/* ---------------------------------------------------- */}
          <div className="lg:col-span-4 bg-zinc-50 p-4 border-2 border-zinc-950 shadow-xs relative">
            <div className="flex items-center justify-between pb-2 mb-3 border-b-2 border-zinc-200">
              <span className="text-xs font-black font-mono uppercase tracking-wider px-2 py-0.5 bg-zinc-950 text-white">
                // PHASE 02: PARALLEL_SWARM
              </span>
              <span className="text-xs font-mono font-bold text-zinc-900 bg-zinc-200 px-2 py-0.5">
                SIMULTANEOUS 4X
              </span>
            </div>

            {/* 2x2 Grid of Parallel Agents */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {phase2Agents.map((node) => {
                const statusInfo = getNodeStatus(node.role);
                const thought = swarmRun?.thoughts?.find((t: any) => t.agent_role === node.role);

                return (
                  <button
                    key={node.role}
                    onClick={() => setActiveModalAgent({ ...node, thought })}
                    className={cn(
                      'text-left p-3.5 border-2 transition-all relative group shadow-xs cursor-pointer',
                      statusInfo.status === 'DONE'
                        ? 'bg-zinc-950 text-white border-zinc-950'
                        : statusInfo.status === 'IN_PROGRESS'
                        ? 'bg-zinc-950 text-white border-red-600 shadow-md'
                        : 'bg-white text-zinc-950 border-zinc-300 hover:border-zinc-950'
                    )}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className={cn(
                        'w-7 h-7 flex items-center justify-center font-bold border',
                        statusInfo.status === 'DONE' || statusInfo.status === 'IN_PROGRESS'
                          ? 'bg-red-600 border-red-500 text-white'
                          : 'bg-zinc-100 border-zinc-300 text-zinc-950'
                      )}>
                        <node.icon className="w-3.5 h-3.5 stroke-[2.2]" />
                      </div>
                      {statusInfo.status === 'DONE' ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : statusInfo.status === 'IN_PROGRESS' ? (
                        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.2, ease: 'linear' }}>
                          <Cpu className="w-4 h-4 text-red-500" />
                        </motion.div>
                      ) : (
                        <Clock className="w-4 h-4 text-zinc-400" />
                      )}
                    </div>

                    <h4 className="text-xs font-black tracking-tight font-sans truncate">
                      {node.name}
                    </h4>
                    <p className={cn(
                      'text-[11px] font-mono truncate mt-0.5',
                      statusInfo.status === 'DONE' || statusInfo.status === 'IN_PROGRESS' ? 'text-zinc-300' : 'text-zinc-600'
                    )}>
                      {node.short}
                    </p>

                    <div className="mt-3 pt-2 border-t border-zinc-700/40 flex items-center justify-between font-mono">
                      <span
                        className={cn(
                          'text-[9px] font-black px-1.5 py-0.5 uppercase',
                          statusInfo.status === 'DONE'
                            ? 'bg-emerald-500 text-zinc-950'
                            : statusInfo.status === 'IN_PROGRESS'
                            ? 'bg-red-600 text-white animate-pulse'
                            : 'bg-zinc-200 text-zinc-800'
                        )}
                      >
                        [{statusInfo.label.toUpperCase()}]
                      </span>
                      <span className="text-[10px] font-bold text-red-400 group-hover:translate-x-1 transition-transform">
                        &rarr;
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            <p className="text-xs text-zinc-500 font-mono mt-3 text-center uppercase">
              MITRE, IOCs, Forensics & Attack Chain run concurrently
            </p>
          </div>

          {/* CONNECTOR ARROW 2 -> 3 (Converges 4 into 1 Stream) */}
          <div className="hidden lg:flex lg:col-span-1 flex-col items-center justify-center relative font-mono">
            <div className="text-[10px] font-black uppercase text-zinc-950 bg-white border-2 border-zinc-950 px-2 py-0.5 mb-2 shadow-xs whitespace-nowrap">
              CONVERGES
            </div>
            {/* Animated Flow Arrow */}
            <div className="relative w-full flex items-center justify-center">
              <div className="w-full h-1 bg-zinc-300 overflow-hidden">
                <motion.div
                  animate={{ x: ['-100%', '100%'] }}
                  transition={{ repeat: Infinity, duration: 1.5, ease: 'linear' }}
                  className={cn(
                    'w-1/2 h-full',
                    isPhase2Done ? 'bg-red-600' : 'bg-zinc-400'
                  )}
                />
              </div>
              <ArrowRight className={cn(
                'w-4 h-4 shrink-0 -ml-1',
                isPhase2Done ? 'text-red-600' : 'text-zinc-400'
              )} />
            </div>
          </div>

          {/* ---------------------------------------------------- */}
          {/* PHASE 3: RISK SYNTHESIS & SOAR CONTAINMENT (3 Cols)  */}
          {/* ---------------------------------------------------- */}
          <div className="lg:col-span-3 bg-zinc-50 p-4 border-2 border-zinc-950 shadow-xs relative">
            <div className="flex items-center justify-between pb-2 mb-3 border-b-2 border-zinc-200">
              <span className="text-xs font-black font-mono uppercase tracking-wider px-2 py-0.5 bg-zinc-950 text-white">
                // PHASE 03: DECISION_SOAR
              </span>
              <span className="text-xs font-mono font-bold text-zinc-500 uppercase">CONTAINMENT</span>
            </div>

            {/* Vertical Stack: Response Agent + Supervisor Summary */}
            <div className="space-y-3">
              {phase3Agents.map((node) => {
                const statusInfo = getNodeStatus(node.role);
                const thought = swarmRun?.thoughts?.find((t: any) => t.agent_role === node.role);

                return (
                  <button
                    key={node.role}
                    onClick={() => setActiveModalAgent({ ...node, thought })}
                    className={cn(
                      'w-full text-left p-3.5 border-2 transition-all relative group shadow-xs cursor-pointer',
                      statusInfo.status === 'DONE'
                        ? 'bg-zinc-950 text-white border-zinc-950'
                        : statusInfo.status === 'IN_PROGRESS'
                        ? 'bg-zinc-950 text-white border-red-600 shadow-md translate-x-1'
                        : 'bg-white text-zinc-950 border-zinc-300 hover:border-zinc-950'
                    )}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className={cn(
                        'w-7 h-7 flex items-center justify-center font-bold border',
                        statusInfo.status === 'DONE' || statusInfo.status === 'IN_PROGRESS'
                          ? 'bg-red-600 border-red-500 text-white'
                          : 'bg-zinc-100 border-zinc-300 text-zinc-950'
                      )}>
                        <node.icon className="w-3.5 h-3.5 stroke-[2.2]" />
                      </div>
                      {statusInfo.status === 'DONE' ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                      ) : statusInfo.status === 'IN_PROGRESS' ? (
                        <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1.2, ease: 'linear' }}>
                          <Cpu className="w-4 h-4 text-red-500" />
                        </motion.div>
                      ) : (
                        <Clock className="w-4 h-4 text-zinc-400" />
                      )}
                    </div>

                    <h4 className="text-xs font-black tracking-tight font-sans truncate">
                      {node.name}
                    </h4>
                    <p className={cn(
                      'text-[11px] font-mono truncate mt-0.5',
                      statusInfo.status === 'DONE' || statusInfo.status === 'IN_PROGRESS' ? 'text-zinc-300' : 'text-zinc-600'
                    )}>
                      {node.short}
                    </p>

                    <div className="mt-3 pt-2 border-t border-zinc-700/40 flex items-center justify-between font-mono">
                      <span
                        className={cn(
                          'text-[9px] font-black px-1.5 py-0.5 uppercase',
                          statusInfo.status === 'DONE'
                            ? 'bg-emerald-500 text-zinc-950'
                            : statusInfo.status === 'IN_PROGRESS'
                            ? 'bg-red-600 text-white animate-pulse'
                            : 'bg-zinc-200 text-zinc-800'
                        )}
                      >
                        [{statusInfo.label.toUpperCase()}]
                      </span>
                      <span className="text-xs font-bold text-red-400 group-hover:translate-x-1 transition-transform">
                        INSPECT &rarr;
                      </span>
                    </div>
                  </button>
                );
              })}
            </div>

            <p className="text-xs text-zinc-500 font-mono mt-3 text-center uppercase">
              Evaluates Risk, Playbooks & Human Guardrail
            </p>
          </div>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* 2. REAL-TIME LOGS & EVENTS QUEUE TABLE */}
      {/* ========================================================================= */}
      <div className="bg-white border-2 border-zinc-950 shadow-xs overflow-hidden">
        {/* Table Header & Controls */}
        <div className="p-5 border-b-2 border-zinc-950 bg-zinc-100 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-red-600" />
              <h3 className="text-sm font-black text-zinc-950 uppercase tracking-wider font-mono">
                // TELEMETRY_EVENTS_&_SECURITY_LOGS_QUEUE [{filteredIncidents.length}]
              </h3>
            </div>
            <p className="text-xs text-zinc-600 mt-0.5">
              Select any event to inspect full forensic summary, or trigger the Swarm pipeline. Click a row to load telemetry.
            </p>
          </div>

          <div className="flex items-center gap-2 font-mono flex-wrap">
            <Filter className="w-3.5 h-3.5 text-red-600" />
            <span className="text-xs font-bold text-zinc-900 uppercase tracking-wider">SEVERITY:</span>
            {['all', 'critical', 'high', 'medium', 'low'].map((sev) => (
              <button
                key={sev}
                onClick={() => setFilterSeverity(sev)}
                className={cn(
                  'px-3 py-1 text-xs font-bold uppercase border cursor-pointer transition-all',
                  filterSeverity === sev
                    ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                    : 'bg-white text-zinc-700 hover:bg-zinc-200 border-zinc-300'
                )}
              >
                {sev}
              </button>
            ))}
          </div>
        </div>

        {/* The List of Events */}
        {incLoading ? (
          <div className="py-16 text-center text-xs font-mono font-bold text-zinc-500">
            STREAMING REAL-TIME SECURITY EVENTS QUEUE...
          </div>
        ) : filteredIncidents.length === 0 ? (
          <div className="py-16 text-center text-xs font-mono font-bold text-zinc-500">
            NO TELEMETRY EVENTS FOUND MATCHING SEVERITY FILTER.
          </div>
        ) : (
          <div className="divide-y-2 divide-zinc-200">
            {filteredIncidents.map((inc: any) => {
              const isSelected = activeIncId === inc.id;
              const sev = String(inc.severity || 'medium').toLowerCase();

              return (
                <div
                  key={inc.id}
                  onClick={() => setSelectedIncidentId(inc.id)}
                  className={cn(
                    'p-4 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 cursor-pointer',
                    isSelected
                      ? 'bg-zinc-100 border-l-4 border-l-red-600 shadow-inner'
                      : 'hover:bg-zinc-50 border-l-4 border-l-transparent'
                  )}
                >
                  {/* Left: Event Details */}
                  <div className="flex items-start gap-3.5 flex-1 min-w-0">
                    <div className={cn(
                      'w-8 h-8 flex items-center justify-center shrink-0 mt-0.5 border',
                      isSelected
                        ? 'bg-red-600 border-red-500 text-white'
                        : 'bg-zinc-100 border-zinc-300 text-zinc-900'
                    )}>
                      <Zap className="w-4 h-4 stroke-[2.2]" />
                    </div>

                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-center gap-2 mb-1">
                        <span className="font-mono text-xs font-black text-zinc-950">
                          [{inc.incident_id || inc.id.substring(0, 8)}]
                        </span>
                        <span
                          className={cn(
                            'text-[10px] font-black font-mono px-2 py-0.5 uppercase border',
                            sev === 'critical'
                              ? 'bg-red-100 text-red-900 border-red-300'
                              : sev === 'high'
                              ? 'bg-orange-100 text-orange-900 border-orange-300'
                              : sev === 'medium'
                              ? 'bg-amber-100 text-amber-900 border-amber-300'
                              : 'bg-emerald-100 text-emerald-900 border-emerald-300'
                          )}
                        >
                          {inc.severity}
                        </span>
                        <span className="text-[11px] font-mono font-medium text-zinc-500">
                          • {formatTimestampIST(inc.created_at)}
                        </span>
                      </div>

                      <h4 className="text-xs font-black text-zinc-950 truncate font-sans">
                        {inc.title}
                      </h4>
                      <p className="text-xs text-zinc-600 line-clamp-1 mt-0.5 font-mono">
                        {inc.description}
                      </p>
                    </div>
                  </div>

                  {/* Right: Actions */}
                  <div className="flex items-center gap-2 shrink-0 font-mono" onClick={(e) => e.stopPropagation()}>
                    {/* View Details Pop-up */}
                    <button
                      onClick={() => setActiveModalEvent(inc)}
                      className="px-3.5 py-2 bg-white hover:bg-zinc-100 text-zinc-950 text-xs font-bold uppercase border border-zinc-300 transition-all flex items-center gap-1.5 cursor-pointer shadow-xs"
                    >
                      <Info className="w-3.5 h-3.5 text-zinc-700" />
                      <span>SUMMARY</span>
                    </button>

                    {/* Run Swarm for this specific event */}
                    <button
                      onClick={() => {
                        setSelectedIncidentId(inc.id);
                        runSwarmMutation.mutate(inc.id);
                      }}
                      disabled={runSwarmMutation.isPending && isSelected}
                      className={cn(
                        'px-4 py-2 text-xs font-bold uppercase border transition-all flex items-center gap-1.5 cursor-pointer shadow-xs',
                        isSelected
                          ? 'bg-red-600 hover:bg-red-500 text-white border-red-600'
                          : 'bg-zinc-950 hover:bg-zinc-800 text-white border-zinc-950'
                      )}
                    >
                      <Play className="w-3 h-3 fill-current" />
                      <span>{runSwarmMutation.isPending && isSelected ? 'ANALYZING...' : 'RUN_SWARM'}</span>
                    </button>

                    {/* Ask Spectra AI Copilot */}
                    <button
                      onClick={() => {
                        openCopilot({
                          title: `Event ${inc.incident_id}: ${inc.title}`,
                          sourceType: 'alert',
                          data: inc,
                          summaryText: `Event ID: ${inc.incident_id}\nSeverity: ${inc.severity}\nDescription: ${inc.description}`
                        });
                      }}
                      className="p-2 bg-zinc-100 hover:bg-zinc-200 text-zinc-950 border border-zinc-300 transition-all shadow-xs cursor-pointer"
                      title="Ask SPECTRA-AI about this event"
                    >
                      <Sparkles className="w-4 h-4 text-red-600" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ========================================================================= */}
      {/* MODAL 1: EVENT SUMMARY POP-UP */}
      {/* ========================================================================= */}
      <AnimatePresence>
        {activeModalEvent && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/70 backdrop-blur-xs">
            <motion.div
              initial={{ scale: 0.96, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.96, opacity: 0 }}
              className="bg-white border-2 border-zinc-950 shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden flex flex-col font-mono"
            >
              {/* Modal Header */}
              <div className="p-5 border-b-2 border-zinc-950 flex items-center justify-between bg-zinc-950 text-white">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-red-600 text-white flex items-center justify-center font-bold">
                    <Activity className="w-4 h-4 stroke-[2.2]" />
                  </div>
                  <div>
                    <h3 className="text-sm font-black tracking-wider uppercase">
                      EVENT SUMMARY: [{activeModalEvent.incident_id || activeModalEvent.id.substring(0, 8)}]
                    </h3>
                    <p className="text-xs text-zinc-400 font-mono mt-0.5">
                      RECORDED_AT: {formatTimestampIST(activeModalEvent.created_at)}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => setActiveModalEvent(null)}
                  className="w-8 h-8 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6 overflow-y-auto space-y-5 text-xs bg-white">
                <div>
                  <span className="text-xs font-black text-zinc-500 uppercase tracking-wider block mb-1">
                    // EVENT_TITLE
                  </span>
                  <p className="text-sm font-black text-zinc-950 font-sans leading-snug">
                    {activeModalEvent.title}
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3.5 bg-zinc-50 border-2 border-zinc-200">
                    <span className="text-[11px] font-bold text-zinc-500 uppercase">ASSESSED_SEVERITY</span>
                    <p className="text-base font-black text-red-600 mt-1 uppercase">
                      {activeModalEvent.severity}
                    </p>
                  </div>
                  <div className="p-3.5 bg-zinc-50 border-2 border-zinc-200">
                    <span className="text-[11px] font-bold text-zinc-500 uppercase">STATUS</span>
                    <p className="text-base font-black text-zinc-950 mt-1 uppercase">
                      {activeModalEvent.status}
                    </p>
                  </div>
                </div>

                <div>
                  <span className="text-xs font-black text-zinc-500 uppercase tracking-wider block mb-1.5">
                    // DETAILED_NARRATIVE_TELEMETRY
                  </span>
                  <div className="p-4 bg-zinc-50 border-2 border-zinc-200 text-zinc-900 leading-relaxed font-mono text-xs">
                    {activeModalEvent.description || 'No extended description recorded.'}
                  </div>
                </div>
              </div>

              {/* Modal Footer with AI Q&A Button */}
              <div className="p-4 border-t-2 border-zinc-950 bg-zinc-100 flex items-center justify-between">
                <button
                  onClick={() => {
                    const evt = activeModalEvent;
                    setActiveModalEvent(null);
                    openCopilot({
                      title: `Event: ${evt.title}`,
                      sourceType: 'alert',
                      data: evt,
                      summaryText: `Event ID: ${evt.incident_id}\nSeverity: ${evt.severity}\nDetails: ${evt.description}`
                    });
                  }}
                  className="flex items-center gap-2 px-4 py-2.5 bg-zinc-950 hover:bg-zinc-800 text-white text-xs font-bold uppercase border-2 border-zinc-950 transition-all cursor-pointer shadow-xs"
                >
                  <Sparkles className="w-3.5 h-3.5 text-red-500" />
                  <span>ASK_SPECTRA_AI_COPILOT</span>
                </button>

                <button
                  onClick={() => setActiveModalEvent(null)}
                  className="px-4 py-2.5 bg-white hover:bg-zinc-200 text-zinc-950 border-2 border-zinc-300 text-xs font-bold uppercase transition-all cursor-pointer"
                >
                  CLOSE
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* ========================================================================= */}
      {/* MODAL 2: AGENT WORKING DETAILS POP-UP */}
      {/* ========================================================================= */}
      <AnimatePresence>
        {activeModalAgent && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-zinc-950/70 backdrop-blur-xs">
            <motion.div
              initial={{ scale: 0.96, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.96, opacity: 0 }}
              className="bg-white border-2 border-zinc-950 shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden flex flex-col font-mono"
            >
              {/* Modal Header */}
              <div className="p-5 border-b-2 border-zinc-950 flex items-center justify-between bg-zinc-950 text-white">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-red-600 text-white flex items-center justify-center font-bold text-xs border border-red-500">
                    0{activeModalAgent.step}
                  </div>
                  <div>
                    <h3 className="text-sm font-black tracking-wider uppercase font-sans">
                      {activeModalAgent.name} // WORK_&_REASONING_STATE
                    </h3>
                    <p className="text-xs text-zinc-400 font-mono mt-0.5">
                      {activeModalAgent.short}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => setActiveModalAgent(null)}
                  className="w-8 h-8 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 hover:text-white flex items-center justify-center transition-colors cursor-pointer"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Modal Content */}
              <div className="p-6 overflow-y-auto space-y-5 text-xs bg-white">
                {/* Agent Role Mission */}
                <div className="p-4 bg-zinc-50 border-2 border-zinc-200">
                  <span className="text-[11px] font-black uppercase text-zinc-500 block mb-1">
                    // WHAT_THIS_AGENT_DOES (MISSION)
                  </span>
                  <p className="text-xs text-zinc-900 font-sans leading-relaxed">
                    {activeModalAgent.roleDesc}
                  </p>
                </div>

                {/* Agent Thought / Output if completed */}
                {activeModalAgent.thought ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-black text-zinc-500 uppercase tracking-wider">
                        // LIVE_AI_REASONING_OUTPUT
                      </span>
                      <span className="text-[11px] font-mono font-bold px-2.5 py-0.5 bg-zinc-950 text-emerald-400">
                        ENGINE: {activeModalAgent.thought.model_used?.toUpperCase() || 'GEMINI_CLOUD'}
                      </span>
                    </div>

                    <div className="p-4 bg-zinc-50 border-2 border-zinc-950 text-zinc-950 font-bold leading-relaxed font-sans text-xs">
                      {activeModalAgent.thought.summary}
                    </div>

                    {activeModalAgent.thought.findings && (
                      <div>
                        <span className="text-xs font-black text-zinc-500 uppercase tracking-wider block mb-2">
                          // FORENSIC_FINDINGS [{activeModalAgent.thought.findings.length}]
                        </span>
                        <div className="space-y-2">
                          {activeModalAgent.thought.findings.map((finding: string, i: number) => (
                            <div
                              key={i}
                              className="flex items-start gap-3 p-3 border-2 border-zinc-200 bg-white"
                            >
                              <span className="w-5 h-5 bg-zinc-950 text-white font-mono text-xs font-bold flex items-center justify-center shrink-0 mt-0.5">
                                {i + 1}
                              </span>
                              <span className="font-mono text-xs text-zinc-800 leading-relaxed">
                                {finding}
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="pt-2 flex items-center justify-between text-xs text-zinc-600 font-mono">
                      <span>CONFIDENCE: <strong className="text-zinc-950 font-black">{Math.round((activeModalAgent.thought.confidence || 0.9) * 100)}%</strong></span>
                      <span>RECORDED_UTC: {activeModalAgent.thought.created_at?.substring(11, 19) || 'Active'}</span>
                    </div>
                  </div>
                ) : (
                  <div className="py-10 text-center space-y-2 bg-zinc-50 border-2 border-dashed border-zinc-300">
                    <AlertCircle className="w-8 h-8 text-zinc-400 mx-auto" />
                    <h5 className="text-xs font-black text-zinc-900 uppercase">AGENT IN QUEUE / WAITING FOR EXECUTION</h5>
                    <p className="text-xs text-zinc-500 font-mono max-w-sm mx-auto">
                      This agent will run automatically as part of Phase 2 or 3 when you trigger the swarm run.
                    </p>
                  </div>
                )}
              </div>

              {/* Modal Footer with AI Q&A Button */}
              <div className="p-4 border-t-2 border-zinc-950 bg-zinc-100 flex items-center justify-between">
                <button
                  onClick={() => {
                    const ag = activeModalAgent;
                    setActiveModalAgent(null);
                    openCopilot({
                      title: `Agent: ${ag.name}`,
                      sourceType: 'agent',
                      data: ag,
                      summaryText: `Agent: ${ag.name} (${ag.short})\nMission: ${ag.mission}\nReasoning: ${ag.thought?.summary || 'Pending execution'}`
                    });
                  }}
                  className="flex items-center gap-2 px-4 py-2.5 bg-zinc-950 hover:bg-zinc-800 text-white text-xs font-bold uppercase border-2 border-zinc-950 transition-all cursor-pointer shadow-xs"
                >
                  <Sparkles className="w-3.5 h-3.5 text-red-500" />
                  <span>ASK_SPECTRA_AI_COPILOT</span>
                </button>

                <button
                  onClick={() => setActiveModalAgent(null)}
                  className="px-5 py-2.5 bg-white hover:bg-zinc-200 text-zinc-950 border-2 border-zinc-300 text-xs font-bold uppercase transition-all cursor-pointer"
                >
                  CLOSE
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
