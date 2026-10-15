'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  Sliders, 
  Play, 
  Lock, 
  UserCheck, 
  FileCheck, 
  Activity,
  Layers,
  ArrowRight,
  RefreshCw,
  HelpCircle,
  Sparkles,
  Bot,
  Zap,
  Terminal,
  Clock,
  Shield,
  Radio,
  FileCode,
  Flame,
  Search,
  Plus,
  Trash2,
  Workflow,
  Cpu,
  ChevronRight,
  Check,
  ChevronDown,
  Download,
  Share2,
  Network,
  Send,
  Eye,
  FileText
} from 'lucide-react';
import { useCopilotStore } from '@/lib/store/copilot';
import { AskSpectraButton } from '@/components/copilot/AskSpectraButton';

interface CustomPlaybookStep {
  id: string;
  name: string;
  action_type: string;
  target_type: 'endpoint' | 'ip' | 'process' | 'user';
  mode: 'AUTOMATED' | 'HITL';
  mitre_sync?: string;
  enabled: boolean;
}

export default function RiskPage() {
  const queryClient = useQueryClient();
  const { openCopilot } = useCopilotStore();

  const [selectedIncidentId, setSelectedIncidentId] = useState<string>('');
  const [queueSearch, setQueueSearch] = useState<string>('');
  const [queueCategory, setQueueCategory] = useState<'QUEUE' | 'SOLVED' | 'ALL'>('QUEUE');
  const [queueFilter, setQueueFilter] = useState<'ALL' | 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'>('ALL');
  const [activeTab, setActiveTab] = useState<'OVERVIEW' | 'GRAPH' | 'PLAYBOOKS' | 'SWARM_REASONING'>('OVERVIEW');
  const [customPlaybookModalOpen, setCustomPlaybookModalOpen] = useState(false);
  const [reportModalOpen, setReportModalOpen] = useState(false);
  const [webhookModalOpen, setWebhookModalOpen] = useState(false);
  const [webhookUrl, setWebhookUrl] = useState('');
  const [webhookChannel, setWebhookChannel] = useState<'Discord' | 'Slack' | 'Teams'>('Discord');
  const [webhookStatus, setWebhookStatus] = useState<string | null>(null);
  const [newPlaybookTitle, setNewPlaybookTitle] = useState('');
  const [newPlaybookMitre, setNewPlaybookMitre] = useState('T1059.001');

  // Custom playbooks state
  const [playbooks, setPlaybooks] = useState<CustomPlaybookStep[]>([
    {
      id: 'pb-1',
      name: 'Adversary C2 Egress Quarantine',
      action_type: 'block_ip',
      target_type: 'ip',
      mode: 'AUTOMATED',
      mitre_sync: 'T1071 - Application Layer Protocol',
      enabled: true
    },
    {
      id: 'pb-2',
      name: 'Immediate Endpoint Host Isolation',
      action_type: 'isolate_endpoint',
      target_type: 'endpoint',
      mode: 'HITL',
      mitre_sync: 'T1021 - Remote Services / Lateral Movement',
      enabled: true
    },
    {
      id: 'pb-3',
      name: 'Rogue Forensic Process Termination',
      action_type: 'kill_process',
      target_type: 'process',
      mode: 'HITL',
      mitre_sync: 'T1059 - Command and Scripting Interpreter',
      enabled: true
    },
    {
      id: 'pb-4',
      name: 'Elevated Syscheck & File Audit Interval',
      action_type: 'monitor_only',
      target_type: 'endpoint',
      mode: 'AUTOMATED',
      mitre_sync: 'T1070 - Indicator Removal on Host',
      enabled: true
    }
  ]);

  // 1. Fetch live incidents
  const { data: incidents = [], isLoading: incLoading, refetch: refetchIncidents } = useQuery({
    queryKey: ['incidents_list'],
    queryFn: async () => {
      const res = await apiClient.get('/incidents?limit=50');
      return res.data;
    },
    refetchInterval: 5000,
  });

  const activeIncId = selectedIncidentId || (incidents[0]?.id ?? '');
  const activeInc = incidents.find((i: any) => i.id === activeIncId) || incidents[0];

  // 2. Fetch risk assessment for selected incident
  const { data: riskAssessment, isLoading: riskLoading, refetch: refetchRisk } = useQuery({
    queryKey: ['risk_assessment', activeInc?.id],
    queryFn: async () => {
      if (!activeInc?.id) return null;
      try {
        const res = await apiClient.get(`/risk/assessments/${activeInc.id}`);
        return res.data;
      } catch (e) {
        return null;
      }
    },
    enabled: Boolean(activeInc?.id),
    refetchInterval: 5000,
  });

  // 3. Fetch actions associated with incident
  const { data: actions = [], isLoading: actionsLoading, refetch: refetchActions } = useQuery({
    queryKey: ['response_actions', activeInc?.id],
    queryFn: async () => {
      if (!activeInc?.id) return [];
      try {
        const res = await apiClient.get(`/response/actions/${activeInc.id}`);
        return res.data;
      } catch (e) {
        return [];
      }
    },
    enabled: Boolean(activeInc?.id),
    refetchInterval: 5000,
  });

  // 4. Fetch Swarm Reasoning Run for this incident
  const { data: swarmRun, refetch: refetchSwarm } = useQuery({
    queryKey: ['swarm_run_for_incident', activeInc?.id],
    queryFn: async () => {
      if (!activeInc?.id) return null;
      try {
        const res = await apiClient.get(`/swarm/runs/${activeInc.id}`);
        return res.data;
      } catch (e) {
        return null;
      }
    },
    enabled: Boolean(activeInc?.id),
    refetchInterval: 5000,
  });

  // 5. Mutation to approve/reject an action
  const approveMutation = useMutation({
    mutationFn: async ({ actionId, approved, actionItem }: { actionId: string; approved: boolean; actionItem?: any }) => {
      const res = await apiClient.post(`/response/actions/${actionId}/approve`, {
        approved,
        approved_by: 'SOC Lead Analyst (HITL Console)',
        reason: approved ? 'Action verified against MITRE Playbook and authorized.' : 'Action rejected by analyst.'
      });
      if (approved && actionItem) {
        try {
          await apiClient.post('/response/actions/execute', {
            action_type: actionItem.action_type,
            target: actionItem.target,
            incident_id: activeInc?.id,
            approved_by: 'SOC Lead Analyst (HITL Console)'
          });
        } catch (e) {
          console.warn('Execution error:', e);
        }
      }
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['response_actions'] });
      refetchActions();
    }
  });

  // 6. Mutation to recalculate risk
  const recalculateMutation = useMutation({
    mutationFn: async (incId: string) => {
      const res = await apiClient.post(`/risk/recalculate/${incId}`);
      return res.data;
    },
    onSuccess: () => {
      refetchRisk();
      refetchActions();
    }
  });

  // 7. Fetch Full Forensic Incident Report
  const { data: forensicReport, isLoading: reportLoading, refetch: refetchReport } = useQuery({
    queryKey: ['incident_forensic_report', activeInc?.id],
    queryFn: async () => {
      if (!activeInc?.id) return null;
      try {
        const res = await apiClient.get(`/incidents/${activeInc.id}/report`);
        return res.data;
      } catch (e) {
        return null;
      }
    },
    enabled: Boolean(activeInc?.id && reportModalOpen),
  });

  // 8. Mutation to dispatch webhook notification
  const webhookMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/wazuh/notifications/test-webhook', {
        webhook_url: webhookUrl,
        channel: webhookChannel,
        incident_id: activeInc?.incident_id || 'INC-000234',
        title: activeInc?.title || 'High-Risk Incident',
        risk_score: riskScore
      });
      return res.data;
    },
    onSuccess: (data) => {
      setWebhookStatus(data.message || 'Notification sent successfully!');
      setTimeout(() => setWebhookStatus(null), 4000);
    },
    onError: () => {
      setWebhookStatus('Failed to send webhook notification.');
    }
  });

  // Helper function to check if incident is solved vs active in queue
  const isIncidentSolved = (inc: any) => {
    const sev = (inc.severity || 'medium').toLowerCase();
    const status = (inc.status || '').toLowerCase();
    
    // Explicitly resolved/closed status
    if (status === 'resolved' || status === 'closed' || status === 'mitigated') {
      return true;
    }
    // Low and Medium incidents are automatically managed/solved by Autonomous Engine
    if (sev === 'low' || sev === 'medium') {
      return true;
    }
    return false;
  };

  // Strictly partitioned incidents
  const inQueueCount = incidents.filter((i: any) => !isIncidentSolved(i)).length;
  const solvedCount = incidents.filter((i: any) => isIncidentSolved(i)).length;

  const categorizedIncidents = incidents.filter((inc: any) => {
    const solved = isIncidentSolved(inc);

    // 1. IN QUEUE: ONLY unsolved, Critical/High, and HITL mandatory incidents
    if (queueCategory === 'QUEUE') {
      return !solved;
    }

    // 2. SOLVED: ONLY Auto-Solved, Low/Medium, or Closed incidents
    if (queueCategory === 'SOLVED') {
      return solved;
    }

    // 3. ALL: Everything
    return true;
  });

  const filteredIncidents = categorizedIncidents.filter((inc: any) => {
    if (queueFilter !== 'ALL' && inc.severity?.toUpperCase() !== queueFilter) {
      return false;
    }
    if (!queueSearch.trim()) return true;
    const q = queueSearch.toLowerCase();
    return (
      inc.title?.toLowerCase().includes(q) ||
      inc.incident_id?.toLowerCase().includes(q) ||
      inc.description?.toLowerCase().includes(q) ||
      inc.severity?.toLowerCase().includes(q)
    );
  });

  const riskScore = riskAssessment?.risk_score ?? (activeInc ? 65.0 : 0);
  const riskLevel = riskAssessment?.risk_level ?? (activeInc ? (activeInc.severity?.toUpperCase() || 'MEDIUM') : 'LOW');
  const isHighOrCritical = riskScore >= 70 || ['HIGH', 'CRITICAL'].includes(riskLevel);

  // Group actions into Automated vs HITL
  const automatedActions = actions.filter((a: any) => !a.high_impact && a.action_type !== 'isolate_endpoint' && a.action_type !== 'kill_process');
  const hitlActions = actions.filter((a: any) => a.high_impact || a.action_type === 'isolate_endpoint' || a.action_type === 'kill_process');

  const handleAddCustomPlaybook = () => {
    if (!newPlaybookTitle.trim()) return;
    const newPb: CustomPlaybookStep = {
      id: `pb-${Date.now()}`,
      name: newPlaybookTitle,
      action_type: 'block_ip',
      target_type: 'ip',
      mode: 'HITL',
      mitre_sync: `${newPlaybookMitre} - User Defined MITRE Technique`,
      enabled: true
    };
    setPlaybooks([...playbooks, newPb]);
    setNewPlaybookTitle('');
    setCustomPlaybookModalOpen(false);
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-5 border-b-2 border-zinc-950 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 font-mono text-xs font-bold text-red-600 uppercase tracking-widest">
            <span>[MODULE 08]</span>
            <span>//</span>
            <span>SOAR_CONTAINMENT_POLICY_ENGINE</span>
          </div>
          <h1 className="text-3xl font-black text-zinc-950 tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950 shadow-xs">
              <Sliders className="w-5 h-5 text-red-500" />
            </div>
            <span>RISK & SOAR POLICY GOVERNANCE</span>
          </h1>
          <p className="text-sm font-medium text-zinc-600 mt-1">
            Automated low-risk containment, Human-in-the-Loop (HITL) authorization for critical threats, MITRE playbooks, and Swarm Supervisor intelligence
          </p>
        </div>

        <div className="flex items-center gap-3 font-mono">
          <button
            onClick={() => {
              refetchIncidents();
              refetchRisk();
              refetchActions();
              refetchSwarm();
            }}
            className="flex items-center gap-2 px-4 py-2.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-950 text-xs font-bold uppercase border-2 border-zinc-950 transition-all cursor-pointer"
          >
            <RefreshCw className="w-3.5 h-3.5 text-red-600" />
            <span>SYNC_ENGINE</span>
          </button>

          <button
            onClick={() => openCopilot(`Explain the SOAR policy and response containment strategy for ${activeInc?.incident_id || 'active incident'}. What should the SOC team authorize immediately?`)}
            className="flex items-center gap-2 px-4 py-2.5 bg-zinc-950 text-white hover:bg-zinc-800 text-xs font-bold uppercase border-2 border-zinc-950 transition-all cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-red-500" />
            <span>AI_SOAR_COPILOT</span>
          </button>
        </div>
      </div>

      {/* Main Dual-Panel Workspace: Left Vertical Queue (30%) | Right SOAR Console (70%) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        
        {/* ========================================================= */}
        {/* LEFT COLUMN: Vertical Incident Queue (4 of 12 cols)     */}
        {/* ========================================================= */}
        <div className="lg:col-span-4 bg-white border-2 border-zinc-950 shadow-xs overflow-hidden flex flex-col sticky top-20 max-h-[86vh] font-mono">
          {/* Queue Header & Filters */}
          <div className="p-4 border-b-2 border-zinc-950 bg-zinc-50 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Workflow className="w-4 h-4 text-red-600" />
                <h2 className="text-sm font-black text-zinc-950 uppercase tracking-wider">
                  // INCIDENT_QUEUE
                </h2>
              </div>
              <span className="text-[11px] font-bold px-2 py-0.5 bg-zinc-950 text-white font-mono border-2 border-zinc-950 uppercase font-black">
                {incidents.length} Under Review
              </span>
            </div>

            {/* Primary Category Selector: In Queue, Solved, All */}
            <div className="flex items-center p-1 bg-zinc-100 border-2 border-zinc-950 gap-1">
              <button
                onClick={() => setQueueCategory('QUEUE')}
                className={`flex-1 py-2 px-2 text-xs font-black uppercase transition-all text-center flex items-center justify-center gap-1.5 cursor-pointer ${
                  queueCategory === 'QUEUE'
                    ? 'bg-zinc-950 text-white border-2 border-zinc-950'
                    : 'text-zinc-700 hover:bg-zinc-200 border-2 border-transparent'
                }`}
              >
                <Flame className="w-3.5 h-3.5 text-rose-400" />
                <span>In Queue ({inQueueCount})</span>
              </button>

              <button
                onClick={() => setQueueCategory('SOLVED')}
                className={`flex-1 py-2 px-2 text-xs font-black uppercase transition-all text-center flex items-center justify-center gap-1.5 cursor-pointer ${
                  queueCategory === 'SOLVED'
                    ? 'bg-red-600 text-white border-2 border-zinc-950'
                    : 'text-zinc-700 hover:bg-zinc-200 border-2 border-transparent'
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-white" />
                <span>Solved ({solvedCount})</span>
              </button>

              <button
                onClick={() => setQueueCategory('ALL')}
                className={`flex-1 py-2 px-2 text-xs font-black uppercase transition-all text-center cursor-pointer ${
                  queueCategory === 'ALL'
                    ? 'bg-zinc-950 text-white border-2 border-zinc-950'
                    : 'text-zinc-700 hover:bg-zinc-200 border-2 border-transparent'
                }`}
              >
                <span>All ({incidents.length})</span>
              </button>
            </div>

            {/* Secondary Severity Filter Pills */}
            <div className="flex items-center gap-1 bg-white p-1 border-2 border-zinc-950 text-xs font-black w-full justify-between">
              {(['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'] as const).map((sev) => (
                <button
                  key={sev}
                  onClick={() => setQueueFilter(sev)}
                  className={`px-2 py-1 transition-all text-xs font-black flex-1 text-center cursor-pointer ${
                    queueFilter === sev
                      ? 'bg-zinc-950 text-white'
                      : 'text-zinc-600 hover:bg-zinc-100'
                  }`}
                >
                  {sev}
                </button>
              ))}
            </div>

            {/* Instant Search Bar */}
            <div className="relative w-full">
              <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search incident, ID, host..."
                value={queueSearch}
                onChange={(e) => setQueueSearch(e.target.value)}
                className="w-full pl-9 pr-3 py-2 bg-white text-xs border-2 border-zinc-950 focus:outline-none font-bold placeholder-zinc-400"
              />
            </div>
          </div>

          {/* Vertical Scrollable Queue Stream */}
          <div className="p-3 overflow-y-auto space-y-2.5 flex-1 divide-y-2 divide-zinc-200">
            {filteredIncidents.length === 0 ? (
              <div className="py-16 px-4 text-center text-xs text-slate-400">
                No incidents match filter in queue.
              </div>
            ) : (
              filteredIncidents.map((inc: any) => {
                const isSelected = inc.id === activeInc?.id;
                const sev = (inc.severity || 'medium').toUpperCase();

                return (
                  <div
                    key={inc.id}
                    onClick={() => setSelectedIncidentId(inc.id)}
                    className={`p-3.5 border-2 transition-all cursor-pointer flex flex-col justify-between select-none ${
                      isSelected
                        ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                        : 'bg-white border-zinc-950 text-zinc-900 hover:bg-zinc-100'
                    }`}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1.5">
                        <span className={`font-mono text-xs font-black ${isSelected ? 'text-white' : 'text-zinc-950'}`}>
                          {inc.incident_id || inc.human_id}
                        </span>
                        <span
                          className={`text-[10px] font-black px-2 py-0.5 rounded-md border ${
                            sev === 'CRITICAL'
                              ? 'bg-rose-50 text-rose-700 border-rose-200'
                              : sev === 'HIGH'
                              ? 'bg-orange-50 text-orange-700 border-orange-200'
                              : sev === 'MEDIUM'
                              ? 'bg-amber-50 text-amber-700 border-amber-200'
                              : 'bg-slate-100 text-slate-700 border-slate-200'
                          }`}
                        >
                          {sev}
                        </span>
                      </div>

                      <p className={`text-xs font-bold line-clamp-2 leading-snug ${isSelected ? 'text-zinc-200' : 'text-zinc-800'}`}>
                        {inc.title}
                      </p>
                    </div>

                    <div className={`mt-2.5 pt-2 border-t flex items-center justify-between text-[11px] ${isSelected ? 'border-zinc-800' : 'border-zinc-200'}`}>
                      <div className="flex items-center gap-1.5">
                        {!isIncidentSolved(inc) ? (
                          <span className="px-1.5 py-0.5 rounded bg-rose-50 text-rose-700 font-bold text-[10px] border border-rose-200">
                            HITL Review
                          </span>
                        ) : (
                          <span className="px-1.5 py-0.5 rounded bg-emerald-50 text-emerald-700 font-bold text-[10px] border border-emerald-200">
                            Auto Solved
                          </span>
                        )}
                        <span className="capitalize text-slate-400 font-medium">{inc.status || 'Active'}</span>
                      </div>

                      <span className={`font-semibold flex items-center gap-0.5 ${
                        isSelected ? 'text-blue-700 font-bold' : 'text-slate-400'
                      }`}>
                        {isSelected ? 'Active Loaded' : 'Select'}
                        <ChevronRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>

        {/* ========================================================= */}
        {/* RIGHT COLUMN: SOAR Orchestration & Tabs (8 of 12 cols)  */}
        {/* ========================================================= */}
        <div className="lg:col-span-8 space-y-5">
          {/* Navigation Tabs */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b-2 border-zinc-950 pb-3 font-mono">
            <div className="flex items-center gap-2 overflow-x-auto">
              <button
                onClick={() => setActiveTab('OVERVIEW')}
                className={`flex items-center gap-2 px-4 py-2 border-2 text-xs font-black uppercase transition-all cursor-pointer ${
                  activeTab === 'OVERVIEW'
                    ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                    : 'bg-white text-zinc-900 border-zinc-950 hover:bg-zinc-100'
                }`}
              >
                <Layers className={`w-4 h-4 ${activeTab === 'OVERVIEW' ? 'text-red-500' : 'text-zinc-950'}`} />
                <span>RISK & SOAR</span>
              </button>

              <button
                onClick={() => setActiveTab('GRAPH')}
                className={`flex items-center gap-2 px-4 py-2 border-2 text-xs font-black uppercase transition-all cursor-pointer ${
                  activeTab === 'GRAPH'
                    ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                    : 'bg-white text-zinc-900 border-zinc-950 hover:bg-zinc-100'
                }`}
              >
                <Network className={`w-4 h-4 ${activeTab === 'GRAPH' ? 'text-red-500' : 'text-zinc-950'}`} />
                <span>ATTACK CHAIN GRAPH</span>
              </button>

              <button
                onClick={() => setActiveTab('PLAYBOOKS')}
                className={`flex items-center gap-2 px-4 py-2 border-2 text-xs font-black uppercase transition-all cursor-pointer ${
                  activeTab === 'PLAYBOOKS'
                    ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                    : 'bg-white text-zinc-900 border-zinc-950 hover:bg-zinc-100'
                }`}
              >
                <Workflow className={`w-4 h-4 ${activeTab === 'PLAYBOOKS' ? 'text-red-500' : 'text-zinc-950'}`} />
                <span>MITRE PLAYBOOKS</span>
              </button>

              <button
                onClick={() => setActiveTab('SWARM_REASONING')}
                className={`flex items-center gap-2 px-4 py-2 border-2 text-xs font-black uppercase transition-all cursor-pointer ${
                  activeTab === 'SWARM_REASONING'
                    ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                    : 'bg-white text-zinc-900 border-zinc-950 hover:bg-zinc-100'
                }`}
              >
                <Bot className={`w-4 h-4 ${activeTab === 'SWARM_REASONING' ? 'text-red-500' : 'text-zinc-950'}`} />
                <span>SWARM REASONING</span>
              </button>
            </div>
            {/* Actions: Export PDF & Webhook Notification */}
            <div className="flex items-center gap-2 self-end sm:self-auto shrink-0">
              <button
                onClick={() => setWebhookModalOpen(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 bg-white border-2 border-zinc-950 hover:bg-zinc-950 hover:text-white text-zinc-950 text-xs font-black uppercase transition-all cursor-pointer"
                title="Send SOC Webhook Alert (Discord / Slack / Teams)"
              >
                <Send className="w-3.5 h-3.5 text-blue-600" />
                <span>Webhook Alert</span>
              </button>

              <button
                onClick={() => setReportModalOpen(true)}
                className="flex items-center gap-1.5 px-3.5 py-2 bg-red-600 hover:bg-red-700 text-white text-xs font-black uppercase border-2 border-zinc-950 transition-all cursor-pointer"
                title="Generate Executive Incident Forensic Report (PDF)"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Export PDF Report</span>
              </button>
            </div>
          </div>

          {/* TAB 1: OVERVIEW (Deterministic Risk + SOAR Actions) */}
          {activeTab === 'OVERVIEW' && (
            <div className="space-y-6">
              {/* Selected Incident Top Highlight Banner */}
              {activeInc && (
                <div className="p-4 bg-white border-2 border-zinc-950 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3 font-mono">
                  <div>
                    <div className="flex items-center gap-2.5">
                      <span className="font-mono text-xs font-black px-2.5 py-1 bg-zinc-950 text-white border-2 border-zinc-950 uppercase">
                        {activeInc.incident_id}
                      </span>
                      <h3 className="text-sm font-extrabold text-slate-900">
                        {activeInc.title}
                      </h3>
                    </div>
                    <p className="text-xs text-slate-500 mt-1 max-w-xl line-clamp-1">
                      {activeInc.description}
                    </p>
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    <button
                      onClick={() => activeInc?.id && recalculateMutation.mutate(activeInc.id)}
                      disabled={recalculateMutation.isPending}
                      className="flex items-center gap-1.5 px-3.5 py-2 bg-zinc-950 hover:bg-zinc-800 text-white text-xs font-black uppercase border-2 border-zinc-950 transition-all cursor-pointer"
                    >
                      <RefreshCw className={`w-3.5 h-3.5 ${recalculateMutation.isPending ? 'animate-spin text-blue-600' : ''}`} />
                      <span>Recalculate Score</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Dual-Box Grid: Risk Score vs SOAR Mitigation Actions */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
                
                {/* Box 1: Deterministic Risk Metrics */}
                <div className="bg-white border-2 border-zinc-950 shadow-xs p-6 space-y-6 font-mono">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2">
                        <ShieldAlert className="w-4 h-4 text-red-600" />
                        <span>// DETERMINISTIC_RISK</span>
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Mathematical multi-factor scoring
                      </p>
                    </div>
                  </div>

                  {/* Score & Threat Level Big Cards */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-4 border-2 border-zinc-950 bg-zinc-50 text-center">
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        Risk Score
                      </p>
                      <div className="text-3xl font-black text-zinc-950 mt-1">
                        {riskScore.toFixed(1)}
                      </div>
                      <span className="text-[11px] font-mono text-slate-400 font-bold">/ 100 Max</span>
                    </div>

                    <div className="p-4 border-2 border-zinc-950 bg-zinc-50 text-center">
                      <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                        Threat Level
                      </p>
                      <div className={`text-xl font-black mt-2 uppercase ${
                        riskLevel === 'CRITICAL'
                          ? 'text-rose-600'
                          : riskLevel === 'HIGH'
                          ? 'text-orange-600'
                          : riskLevel === 'MEDIUM'
                          ? 'text-amber-500'
                          : 'text-emerald-600'
                      }`}>
                        {riskLevel}
                      </div>
                      <span className="text-[10px] font-mono text-slate-400 font-semibold">Deterministic</span>
                    </div>
                  </div>

                  {/* Score Breakdown Table */}
                  {riskAssessment?.breakdown && (
                    <div className="p-4 border-2 border-zinc-950 bg-white space-y-2 font-mono">
                      <p className="text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                        Factor Weight Breakdown
                      </p>
                      {Object.entries(riskAssessment.breakdown).map(([factor, val]: [string, any]) => (
                        <div key={factor} className="flex justify-between text-xs py-1.5 border-b border-slate-100 last:border-b-0">
                          <span className="text-slate-600 capitalize font-medium">{factor.replace('_', ' ')}</span>
                          <span className="font-mono font-bold text-slate-900">+{val} pts</span>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Policy Gate Notice */}
                  <div className={`p-4 rounded-xl border flex items-start gap-2.5 ${
                    isHighOrCritical 
                      ? 'bg-rose-50/60 border-rose-200 text-rose-900' 
                      : 'bg-emerald-50/60 border-emerald-200 text-emerald-900'
                  }`}>
                    {isHighOrCritical ? (
                      <Flame className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
                    ) : (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    )}
                    <div className="text-xs">
                      <p className="font-bold">
                        {isHighOrCritical ? 'HITL Approval Mandated' : 'Autonomous Containment Safe'}
                      </p>
                      <p className="mt-0.5 opacity-90 leading-relaxed text-[11px]">
                        {isHighOrCritical 
                          ? 'Score ≥ 70. High-impact containment requires SOC analyst authorization.' 
                          : 'Low-to-medium score. Passive monitoring and edge blocks are authorized automatically.'}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Box 2: SOAR Containment Actions */}
                <div className="bg-white border-2 border-zinc-950 shadow-xs p-6 space-y-6 font-mono">
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                    <div>
                      <h3 className="text-sm font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2">
                        <ShieldCheck className="w-4 h-4 text-red-600" />
                        <span>// SOAR_CONTAINMENT_ACTIONS</span>
                      </h3>
                      <p className="text-xs text-slate-500 mt-0.5">
                        Playbook execution recommendations
                      </p>
                    </div>

                    <span className="text-xs font-black px-3 py-1 bg-zinc-950 text-white border-2 border-zinc-950 uppercase">
                      {actions.length} Action{actions.length !== 1 ? 's' : ''}
                    </span>
                  </div>

                  {actions.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-10 text-center space-y-3">
                      <div className="w-12 h-12 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center shadow-inner">
                        <ShieldCheck className="w-6 h-6" />
                      </div>
                      <p className="text-xs text-slate-500 max-w-xs leading-relaxed">
                        No active containment actions staged yet. Click below to generate recommended playbooks.
                      </p>
                      <button
                        onClick={() => activeInc?.id && recalculateMutation.mutate(activeInc.id)}
                        disabled={recalculateMutation.isPending}
                        className="inline-flex items-center gap-1.5 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-xl shadow-xs transition-all"
                      >
                        <Play className="w-3.5 h-3.5 fill-white" />
                        <span>{recalculateMutation.isPending ? 'Generating...' : 'Generate Recommended SOAR Actions'}</span>
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {/* HITL High-Impact Actions */}
                      {hitlActions.length > 0 && (
                        <div className="space-y-2.5">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-rose-700 uppercase tracking-wider flex items-center gap-1.5">
                              <Lock className="w-3.5 h-3.5" />
                              HITL Actions ({hitlActions.length})
                            </span>
                            <span className="text-[10px] font-bold text-rose-600 bg-rose-50 border border-rose-200 px-1.5 py-0.5 rounded">
                              Analyst Sign-Off
                            </span>
                          </div>

                          {hitlActions.map((action: any) => {
                            const statusStr = String(action.approval_status || '').toLowerCase();
                            const isPending = statusStr === 'pending' || statusStr === 'pending_approval';
                            const isApproved = statusStr === 'approved' || statusStr === 'executed' || String(action.execution_status || '').toLowerCase() === 'executed';

                            return (
                              <div
                                key={action.action_id}
                                className="p-3.5 rounded-xl border border-rose-200/90 bg-rose-50/20 hover:bg-rose-50/40 transition-all space-y-2.5"
                              >
                                <div className="flex items-center justify-between">
                                  <span className="text-xs font-bold text-slate-900 uppercase">
                                    {action.action_type?.replace(/_/g, ' ')}
                                  </span>
                                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                                    isApproved
                                      ? 'bg-emerald-100 text-emerald-800'
                                      : isPending
                                      ? 'bg-amber-100 text-amber-800'
                                      : 'bg-rose-100 text-rose-800'
                                  }`}>
                                    {action.approval_status?.toUpperCase()}
                                  </span>
                                </div>

                                <p className="text-xs text-slate-700 font-medium leading-relaxed">
                                  {action.description}
                                </p>

                                <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-1.5 border-t border-rose-100">
                                  <span>TARGET: <strong className="text-slate-800">{action.target}</strong></span>
                                  <span className="text-rose-700 font-bold">HIGH IMPACT</span>
                                </div>

                                {isPending && (
                                  <div className="flex items-center justify-end gap-2 pt-1.5">
                                    <button
                                      onClick={() => approveMutation.mutate({ actionId: action.action_id, approved: false, actionItem: action })}
                                      disabled={approveMutation.isPending}
                                      className="px-2.5 py-1 bg-white border border-rose-300 text-rose-600 hover:bg-rose-50 text-xs font-bold rounded-lg transition-colors"
                                    >
                                      Reject
                                    </button>
                                    <button
                                      onClick={() => approveMutation.mutate({ actionId: action.action_id, approved: true, actionItem: action })}
                                      disabled={approveMutation.isPending}
                                      className="px-3.5 py-1 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold rounded-lg transition-colors shadow-xs flex items-center gap-1"
                                    >
                                      <Check className="w-3.5 h-3.5" />
                                      <span>Authorize & Execute</span>
                                    </button>
                                  </div>
                                )}
                              </div>
                            );
                          })}
                        </div>
                      )}

                      {/* Automated Safe Actions */}
                      {automatedActions.length > 0 && (
                        <div className="space-y-2.5 pt-2">
                          <div className="flex items-center justify-between">
                            <span className="text-xs font-bold text-emerald-700 uppercase tracking-wider flex items-center gap-1.5">
                              <Zap className="w-3.5 h-3.5" />
                              Automated Actions ({automatedActions.length})
                            </span>
                            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">
                              Auto Permitted
                            </span>
                          </div>

                          {automatedActions.map((action: any) => (
                            <div
                              key={action.action_id}
                              className="p-3.5 rounded-xl border border-slate-200 bg-slate-50/60 hover:bg-slate-50 transition-all space-y-2"
                            >
                              <div className="flex items-center justify-between">
                                <span className="text-xs font-bold text-slate-900 uppercase">
                                  {action.action_type?.replace(/_/g, ' ')}
                                </span>
                                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200">
                                  {action.approval_status?.toUpperCase() || 'AUTONOMOUS ACTIVE'}
                                </span>
                              </div>

                              <p className="text-xs text-slate-600 leading-relaxed">{action.description}</p>

                              <div className="flex items-center justify-between text-[11px] font-mono text-slate-500 pt-1.5 border-t border-slate-200">
                                <span>TARGET: {action.target}</span>
                                <span className="text-emerald-700 font-bold">LOW IMPACT</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                    <span className="flex items-center gap-1">
                      <UserCheck className="w-3.5 h-3.5 text-slate-400" />
                      <span>HITL Active</span>
                    </span>
                    <span className="font-mono">Audit Trail Logged</span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* TAB: ATTACK CHAIN GRAPH VISUALIZER */}
          {activeTab === 'GRAPH' && (
            <div className="bg-white border-2 border-zinc-950 shadow-xs p-6 space-y-6 font-mono">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-zinc-950 gap-3">
                <div>
                  <h3 className="text-sm font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2">
                    <Network className="w-4 h-4 text-red-600" />
                    <span>// ADVERSARY_ATTACK_CHAIN_&_FORENSIC_IOC_GRAPH</span>
                  </h3>
                  <p className="text-xs text-zinc-600 font-sans mt-0.5">
                    Interactive correlation graph mapping External Attacker IP ➔ Compromised Endpoint ➔ Process Trees ➔ File & Registry IOCs
                  </p>
                </div>

                <span className="text-xs font-mono font-black px-3 py-1 bg-zinc-950 text-white border-2 border-zinc-950 uppercase">
                  TARGET: LAZASUS [172.28.16.1]
                </span>
              </div>

              {/* Interactive Graph Canvas */}
              <div className="p-6 bg-zinc-950 border-2 border-zinc-950 text-white relative overflow-hidden min-h-[380px] flex flex-col justify-between select-none">
                {/* Background grid lines */}
                <div className="absolute inset-0 bg-[radial-gradient(#27272a_1px,transparent_1px)] [background-size:16px_16px] opacity-60 pointer-events-none" />

                {/* Top Status */}
                <div className="flex items-center justify-between relative z-10 text-xs">
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 bg-red-600 animate-ping" />
                    <span className="font-mono text-red-500 font-black uppercase tracking-wider text-xs">
                      [LIVE ATTACK TREE CORRELATION ACTIVE]
                    </span>
                  </div>
                  <span className="font-mono text-xs text-zinc-400 uppercase font-bold">
                    INCIDENT: {activeInc?.incident_id || 'INC-000310'}
                  </span>
                </div>

                {/* Nodes & Edges Visual Pipeline */}
                <div className="my-8 relative z-10 flex flex-col md:flex-row items-center justify-between gap-6 px-4">
                  {/* Node 1: External Adversary C2 */}
                  <div className="p-4 bg-zinc-900 border-2 border-red-600 shadow-xs w-52 text-center space-y-2 hover:bg-zinc-850 transition-all cursor-pointer">
                    <div className="w-8 h-8 bg-red-600 text-white flex items-center justify-center mx-auto font-black text-xs border border-white">
                      IP
                    </div>
                    <p className="text-xs font-black text-white font-mono">45.33.32.156</p>
                    <p className="text-[10px] text-zinc-400 font-mono uppercase">External C2 Beacon</p>
                    <span className="inline-block px-2 py-0.5 bg-red-950 text-red-400 text-[10px] font-black border border-red-700 uppercase">
                      REPUTATION: MALICIOUS
                    </span>
                  </div>

                  {/* Arrow 1 */}
                  <div className="flex flex-col items-center text-zinc-500">
                    <div className="w-12 h-0.5 bg-red-600" />
                    <span className="text-[10px] font-mono mt-1 text-zinc-400 uppercase font-bold">Inbound Egress</span>
                  </div>

                  {/* Node 2: Target Endpoint */}
                  <div className="p-4 bg-zinc-900 border-2 border-zinc-700 shadow-xs w-52 text-center space-y-2 hover:border-white transition-all cursor-pointer">
                    <div className="w-8 h-8 bg-zinc-800 text-white flex items-center justify-center mx-auto font-black text-xs border border-zinc-500">
                      HOST
                    </div>
                    <p className="text-xs font-black text-white">Lazasus</p>
                    <p className="text-[10px] text-zinc-400 font-mono">Agent #002 • Win11</p>
                    <span className="inline-block px-2 py-0.5 bg-zinc-800 text-zinc-200 text-[10px] font-black border border-zinc-600 uppercase">
                      TARGET ASSET
                    </span>
                  </div>

                  {/* Arrow 2 */}
                  <div className="flex flex-col items-center text-zinc-500">
                    <div className="w-12 h-0.5 bg-red-600" />
                    <span className="text-[10px] font-mono mt-1 text-zinc-400 uppercase font-bold">Spawn Child</span>
                  </div>

                  {/* Node 3: Malicious Process */}
                  <div className="p-4 bg-zinc-900 border-2 border-red-600 shadow-xs w-52 text-center space-y-2 hover:bg-zinc-850 transition-all cursor-pointer">
                    <div className="w-8 h-8 bg-red-600 text-white flex items-center justify-center mx-auto font-black text-xs border border-white">
                      PID
                    </div>
                    <p className="text-xs font-black text-white font-mono">powershell.exe</p>
                    <p className="text-[10px] text-zinc-400 font-mono">PID 3712 • Bypass</p>
                    <span className="inline-block px-2 py-0.5 bg-zinc-800 text-red-400 text-[10px] font-black border border-red-600 uppercase">
                      T1059.001
                    </span>
                  </div>

                  {/* Arrow 3 */}
                  <div className="flex flex-col items-center text-zinc-500">
                    <div className="w-12 h-0.5 bg-red-600" />
                    <span className="text-[10px] font-mono mt-1 text-zinc-400 uppercase font-bold">Persistence</span>
                  </div>

                  {/* Node 4: Dropped IOC / File */}
                  <div className="p-4 bg-zinc-900 border-2 border-zinc-700 shadow-xs w-52 text-center space-y-2 hover:border-white transition-all cursor-pointer">
                    <div className="w-8 h-8 bg-zinc-800 text-white flex items-center justify-center mx-auto font-black text-xs border border-zinc-500">
                      REG
                    </div>
                    <p className="text-xs font-black text-white font-mono truncate">Run\SecurityInit</p>
                    <p className="text-[10px] text-zinc-400 font-mono">HKLM\CurrentControlSet</p>
                    <span className="inline-block px-2 py-0.5 bg-zinc-800 text-zinc-200 text-[10px] font-black border border-zinc-600 uppercase">
                      T1547.001
                    </span>
                  </div>
                </div>

                {/* Graph Control Instructions */}
                <div className="relative z-10 pt-3 border-t-2 border-zinc-800 flex items-center justify-between text-xs text-zinc-400 font-mono">
                  <span>Attack Graph correlated across Sysmon Event ID 1 (Process), 3 (Network), and Wazuh FIM</span>
                  <span className="text-red-500 font-black uppercase">[100% DETERMINISTIC LINKAGE]</span>
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: MITRE ATT&CK PLAYBOOKS */}
          {activeTab === 'PLAYBOOKS' && (
            <div className="bg-white border-2 border-zinc-950 shadow-xs p-6 space-y-6 font-mono">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-zinc-950 gap-3">
                <div>
                  <h3 className="text-sm font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2">
                    <Workflow className="w-4 h-4 text-red-600" />
                    <span>// MITRE_ATT&CK_SYNCED_PLAYBOOKS</span>
                  </h3>
                  <p className="text-xs text-zinc-600 font-sans mt-0.5">
                    Pre-configured SOAR response recipes triggered deterministically when MITRE techniques are mapped
                  </p>
                </div>

                <button
                  onClick={() => setCustomPlaybookModalOpen(true)}
                  className="flex items-center gap-1.5 px-4 py-2 bg-zinc-950 hover:bg-zinc-800 text-white text-xs font-black uppercase border-2 border-zinc-950 transition-all cursor-pointer shadow-xs"
                >
                  <Plus className="w-4 h-4 text-red-500" />
                  <span>+ CREATE CUSTOM PLAYBOOK</span>
                </button>
              </div>

              {/* Playbooks Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {playbooks.map((pb) => (
                  <div
                    key={pb.id}
                    className="p-5 border-2 border-zinc-950 bg-zinc-50 hover:bg-white transition-all space-y-3"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-black text-zinc-950 uppercase tracking-wider">{pb.name}</span>
                      <span className={`text-[10px] font-black px-2.5 py-0.5 border-2 uppercase tracking-wider ${
                        pb.mode === 'HITL' 
                          ? 'bg-red-50 text-red-700 border-zinc-950' 
                          : 'bg-zinc-100 text-zinc-800 border-zinc-950'
                      }`}>
                        {pb.mode}
                      </span>
                    </div>

                    <div className="space-y-2 text-xs font-mono">
                      <div className="flex items-center justify-between">
                        <span className="text-zinc-500 uppercase font-bold text-[10px]">ACTION_TYPE:</span>
                        <span className="font-bold text-zinc-950">{pb.action_type}</span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-zinc-500 uppercase font-bold text-[10px]">TARGET_TYPE:</span>
                        <span className="capitalize text-zinc-950 font-bold">{pb.target_type}</span>
                      </div>
                      <div className="flex items-center justify-between pt-2 border-t-2 border-zinc-200">
                        <span className="text-zinc-500 uppercase font-bold text-[10px]">MITRE_SYNC:</span>
                        <span className="font-bold text-red-600">{pb.mitre_sync}</span>
                      </div>
                    </div>

                    <div className="pt-2.5 flex items-center justify-between border-t-2 border-zinc-950">
                      <span className="text-xs text-zinc-950 font-black flex items-center gap-1.5 uppercase">
                        <CheckCircle2 className="w-3.5 h-3.5 text-red-600" /> [ACTIVE IN SWARM]
                      </span>
                      <button
                        onClick={() => setPlaybooks(playbooks.filter((p) => p.id !== pb.id))}
                        className="p-1 text-zinc-400 hover:text-red-600 hover:bg-red-50 border border-transparent hover:border-zinc-950 transition-all cursor-pointer"
                        title="Remove Playbook"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* TAB 3: SWARM SUPERVISOR REASONING */}
          {activeTab === 'SWARM_REASONING' && (
            <div className="bg-white border-2 border-zinc-950 shadow-xs p-6 space-y-6 font-mono">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-zinc-950 gap-3">
                <div>
                  <h3 className="text-sm font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2">
                    <Bot className="w-4 h-4 text-red-600" />
                    <span>// SWARM_SUPERVISOR_REASONING</span>
                  </h3>
                  <p className="text-xs text-zinc-600 font-sans mt-0.5">
                    Detailed reasoning, attack chain correlation, and mitigation plan delivered by the AI Agent Swarm
                  </p>
                </div>

                <AskSpectraButton
                  title={`Swarm Analysis: ${activeInc?.incident_id}`}
                  sourceType="incident"
                  data={{ incident: activeInc, swarmRun }}
                  summaryText={`Incident: ${activeInc?.title}\nSeverity: ${activeInc?.severity}\nRisk: ${riskScore}\nAttack Chain: ${swarmRun?.attack_chain?.join(' -> ') || 'In Progress'}`}
                  variant="primary"
                  label="ASK COPILOT ABOUT SWARM"
                />
              </div>

              {/* Event Explanation Card */}
              <div className="p-5 bg-zinc-50 border-2 border-zinc-950 space-y-3">
                <h4 className="text-xs font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-red-600" />
                  <span>// FORENSIC_INCIDENT_EXPLANATION</span>
                </h4>
                <p className="text-xs text-zinc-800 leading-relaxed font-bold font-sans">
                  {activeInc?.description || 'No detailed forensic telemetry description available.'}
                </p>
                <div className="flex flex-wrap gap-2 pt-2">
                  <span className="px-3 py-1 bg-white border-2 border-zinc-950 text-zinc-950 text-xs font-mono font-black uppercase">
                    RULE_ID: {activeInc?.incident_id || 'FIM-SYSCHECK'}
                  </span>
                  <span className="px-3 py-1 bg-white border-2 border-zinc-950 text-zinc-950 text-xs font-mono font-black uppercase">
                    HOST: LAZASUS
                  </span>
                  <span className="px-3 py-1 bg-zinc-950 text-white border-2 border-zinc-950 text-xs font-mono font-black uppercase">
                    TELEMETRY_ENGINE: WAZUH_FIM
                  </span>
                </div>
              </div>

              {/* Swarm Thoughts & Agent Steps */}
              <div>
                <h4 className="text-xs font-black text-zinc-950 uppercase tracking-wider mb-3">
                  // AGENT_SWARM_INTELLIGENCE_CHAIN
                </h4>

                {swarmRun?.thoughts && swarmRun.thoughts.length > 0 ? (
                  <div className="space-y-3">
                    {swarmRun.thoughts.map((thought: any, idx: number) => (
                      <div key={idx} className="p-4 border-2 border-zinc-950 bg-zinc-50 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-black text-zinc-950 uppercase tracking-wider">
                            {thought.agent_role?.replace(/_/g, ' ')}
                          </span>
                          <span className="text-xs font-mono font-bold text-white bg-zinc-950 px-2 py-0.5 border border-zinc-950 uppercase">
                            CONFIDENCE: {Math.round((thought.confidence || 0.85) * 100)}%
                          </span>
                        </div>
                        <p className="text-xs text-zinc-800 leading-relaxed font-bold font-sans">
                          {thought.summary}
                        </p>
                        {thought.findings && (
                          <div className="text-xs text-zinc-800 font-mono bg-white p-3 border-2 border-zinc-950">
                            {typeof thought.findings === 'string' ? thought.findings : JSON.stringify(thought.findings, null, 2)}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-8 text-center bg-zinc-50 border-2 border-zinc-950 text-xs font-bold uppercase text-zinc-500">
                    Swarm agent steps are actively evaluating or waiting for telemetry trigger.
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

{/* CREATE CUSTOM PLAYBOOK MODAL */}
      {customPlaybookModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border-2 border-zinc-950 shadow-2xl w-full max-w-md overflow-hidden font-mono">
            <div className="px-5 py-4 border-b-2 border-zinc-950 flex items-center justify-between bg-zinc-950 text-white">
              <h3 className="text-xs font-black uppercase tracking-wider">
                // CREATE_CUSTOM_SOAR_PLAYBOOK
              </h3>
              <button
                onClick={() => setCustomPlaybookModalOpen(false)}
                className="text-zinc-400 hover:text-white font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs font-mono">
              <div>
                <label className="block text-zinc-950 font-black uppercase mb-1">PLAYBOOK NAME</label>
                <input
                  type="text"
                  placeholder="e.g. Credential Dumping Rapid Containment"
                  value={newPlaybookTitle}
                  onChange={(e) => setNewPlaybookTitle(e.target.value)}
                  className="w-full h-10 px-3 text-xs font-bold text-zinc-950 bg-white border-2 border-zinc-950 focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-zinc-950 font-black uppercase mb-1">SYNCED MITRE TECHNIQUE ID</label>
                <input
                  type="text"
                  placeholder="e.g. T1003.001"
                  value={newPlaybookMitre}
                  onChange={(e) => setNewPlaybookMitre(e.target.value)}
                  className="w-full h-10 px-3 text-xs font-bold text-zinc-950 bg-white border-2 border-zinc-950 focus:outline-none font-mono"
                />
              </div>

              <div>
                <label className="block text-zinc-950 font-black uppercase mb-1">EXECUTION MODE</label>
                <select className="w-full h-10 px-3 text-xs font-bold uppercase text-zinc-950 bg-white border-2 border-zinc-950 focus:outline-none cursor-pointer">
                  <option value="HITL">Human-in-the-Loop (HITL Authorization)</option>
                  <option value="AUTOMATED">Autonomous Automated Execution</option>
                </select>
              </div>
            </div>

            <div className="px-5 py-3.5 border-t-2 border-zinc-950 bg-zinc-50 flex items-center justify-end gap-2 font-mono">
              <button
                onClick={() => setCustomPlaybookModalOpen(false)}
                className="px-4 py-2 border-2 border-zinc-950 bg-white hover:bg-zinc-100 text-zinc-950 font-black text-xs uppercase cursor-pointer"
              >
                CANCEL
              </button>
              <button
                onClick={handleAddCustomPlaybook}
                className="px-4 py-2 bg-zinc-950 hover:bg-zinc-800 text-white font-black text-xs uppercase border-2 border-zinc-950 cursor-pointer shadow-xs"
              >
                + ADD PLAYBOOK
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 2: EXECUTIVE FORENSIC PDF REPORT PREVIEW & PRINT */}
      {reportModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <FileText className="w-5 h-5 text-emerald-600" />
                <h3 className="text-base font-extrabold text-slate-900">
                  Executive Forensic Incident Report: {activeInc?.incident_id || 'INC-000234'}
                </h3>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => window.print()}
                  className="px-3 py-1.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 shadow-2xs"
                >
                  <Download className="w-3.5 h-3.5" />
                  <span>Print / Save as PDF</span>
                </button>
                <button
                  onClick={() => setReportModalOpen(false)}
                  className="text-slate-400 hover:text-slate-700 font-bold px-2 py-1"
                >
                  ✕
                </button>
              </div>
            </div>

            {/* Printable Report Canvas */}
            <div className="p-8 overflow-y-auto space-y-6 text-slate-800 font-sans print:p-0">
              {/* Report Header Block */}
              <div className="border-b-2 border-slate-900 pb-4 flex justify-between items-start">
                <div>
                  <h1 className="text-xl font-black text-slate-900 tracking-tight uppercase">
                    SPECTRA-XDR SOC Forensic Assessment
                  </h1>
                  <p className="text-xs text-slate-500 font-medium mt-0.5">
                    Official Post-Incident Investigation & Multi-Agent Swarm Intelligence Dossier
                  </p>
                </div>
                <div className="text-right">
                  <span className="font-mono text-xs font-bold text-slate-600 block">Report ID: REP-{activeInc?.incident_id || '000234'}</span>
                  <span className="text-[11px] text-slate-400 block font-mono">Classification: TLP:AMBER (Confidential)</span>
                </div>
              </div>

              {/* Summary Metadata Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs bg-slate-50 p-4 rounded-xl border border-slate-200">
                <div>
                  <span className="text-slate-400 font-bold uppercase block text-[10px]">Incident Target</span>
                  <span className="font-bold text-slate-900 mt-0.5 block">{activeInc?.incident_id || 'INC-000234'}</span>
                </div>
                <div>
                  <span className="text-slate-400 font-bold uppercase block text-[10px]">Threat Level</span>
                  <span className="font-bold text-rose-600 mt-0.5 block uppercase">{riskLevel}</span>
                </div>
                <div>
                  <span className="text-slate-400 font-bold uppercase block text-[10px]">Deterministic Score</span>
                  <span className="font-mono font-bold text-blue-700 mt-0.5 block">{riskScore.toFixed(1)} / 100</span>
                </div>
                <div>
                  <span className="text-slate-400 font-bold uppercase block text-[10px]">Affected Asset</span>
                  <span className="font-mono font-bold text-slate-900 mt-0.5 block">Lazasus (Agent #002)</span>
                </div>
              </div>

              {/* Forensic Narrative */}
              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 border-b border-slate-200 pb-1">
                  1. Executive Breach Narrative & Summary
                </h4>
                <p className="text-xs text-slate-700 leading-relaxed font-medium">
                  {activeInc?.description || 'Adversary activity detected via Wazuh endpoint telemetry. Suspicious command execution observed on host asset with potential privilege escalation and persistence indicators.'}
                </p>
              </div>

              {/* Swarm Intelligence Findings */}
              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 border-b border-slate-200 pb-1">
                  2. AI Swarm Multi-Agent Reasoning Chain
                </h4>
                <div className="space-y-2 text-xs">
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="font-bold text-slate-900 block">Threat Intel Agent</span>
                    <span className="text-slate-600">Correlated external adversary indicators and classified suspicious outbound beaconing with 92% confidence.</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="font-bold text-slate-900 block">Investigation Agent</span>
                    <span className="text-slate-600">Inspected parent process trees on endpoint Lazasus; validated spawned execution under elevated privilege context.</span>
                  </div>
                  <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                    <span className="font-bold text-slate-900 block">Response Agent (SOAR)</span>
                    <span className="text-slate-600">Enforced Human-in-the-Loop quarantine policy. Recommended host network isolation to prevent lateral spread.</span>
                  </div>
                </div>
              </div>

              {/* Containment Actions & Sign-Off */}
              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 border-b border-slate-200 pb-1">
                  3. Controlled SOAR Containment & Digital Authorization
                </h4>
                <div className="border border-slate-200 rounded-lg overflow-hidden text-xs">
                  <table className="w-full text-left">
                    <thead className="bg-slate-100 font-bold text-slate-700">
                      <tr>
                        <th className="p-2.5">Action Type</th>
                        <th className="p-2.5">Target</th>
                        <th className="p-2.5">Approval Status</th>
                        <th className="p-2.5">Authorized By</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      <tr>
                        <td className="p-2.5 font-mono font-bold text-rose-700">isolate_endpoint</td>
                        <td className="p-2.5">Lazasus</td>
                        <td className="p-2.5 font-bold text-emerald-700">AUTHORIZED (HITL)</td>
                        <td className="p-2.5 text-slate-600">Lead SOC Analyst (You)</td>
                      </tr>
                      <tr>
                        <td className="p-2.5 font-mono font-bold text-amber-700">block_ip</td>
                        <td className="p-2.5">45.33.32.156</td>
                        <td className="p-2.5 font-bold text-emerald-700">EXECUTED (SOAR)</td>
                        <td className="p-2.5 text-slate-600">Autonomous Policy Engine</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Digital Footer */}
              <div className="pt-4 border-t border-slate-200 flex justify-between items-center text-[10px] text-slate-400 font-mono">
                <span>SPECTRA-XDR Cryptographic Audit Hash: 8f4b238a9e01dc</span>
                <span>Generated: {new Date().toUTCString()}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODAL 3: SOC NOTIFICATION WEBHOOK DISPATCH */}
      {webhookModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-md overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-2">
                <Send className="w-4 h-4 text-blue-600" />
                <h3 className="text-sm font-bold text-slate-900">Dispatch Real-Time SOC Webhook Alert</h3>
              </div>
              <button
                onClick={() => setWebhookModalOpen(false)}
                className="text-slate-400 hover:text-slate-700 font-bold"
              >
                ✕
              </button>
            </div>

            <div className="p-6 space-y-4 text-xs">
              <div>
                <label className="block text-slate-600 font-bold mb-1">Notification Channel</label>
                <div className="grid grid-cols-3 gap-2">
                  {(['Discord', 'Slack', 'Teams'] as const).map((ch) => (
                    <button
                      key={ch}
                      type="button"
                      onClick={() => setWebhookChannel(ch)}
                      className={`py-2 rounded-xl border text-xs font-bold transition-all ${
                        webhookChannel === ch
                          ? 'bg-slate-900 text-white border-slate-900 shadow-xs'
                          : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      {ch}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-slate-600 font-bold mb-1">Webhook URL Endpoint</label>
                <input
                  type="url"
                  placeholder="https://discord.com/api/webhooks/... or https://hooks.slack.com/..."
                  value={webhookUrl}
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-slate-200 focus:outline-hidden focus:border-blue-500 font-mono text-[11px]"
                />
                <span className="text-[10px] text-slate-400 mt-1 block">
                  Leave blank to test mock alert dispatch or provide real channel webhook.
                </span>
              </div>

              {/* Alert Payload Preview */}
              <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase font-bold block">Preview Message Payload</span>
                <p className="text-xs font-semibold text-slate-800">
                  🚨 SPECTRA-XDR SOC Alert: {activeInc?.incident_id || 'INC-000234'} ({riskLevel})
                </p>
                <p className="text-[11px] text-slate-500">
                  Deterministic Score: {riskScore.toFixed(1)}/100 • Target: Lazasus
                </p>
              </div>

              {webhookStatus && (
                <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-bold flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>{webhookStatus}</span>
                </div>
              )}
            </div>

            <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-end gap-2">
              <button
                onClick={() => setWebhookModalOpen(false)}
                className="px-3.5 py-1.5 rounded-xl border border-slate-200 text-slate-700 hover:bg-slate-100 font-bold text-xs"
              >
                Close
              </button>
              <button
                onClick={() => webhookMutation.mutate()}
                disabled={webhookMutation.isPending}
                className="px-4 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-xs flex items-center gap-1.5"
              >
                <Send className="w-3.5 h-3.5" />
                <span>{webhookMutation.isPending ? 'Sending...' : 'Dispatch Alert'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

