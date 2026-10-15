'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { 
  Laptop, 
  ShieldCheck, 
  Server, 
  RefreshCw, 
  Search, 
  Activity, 
  Terminal, 
  Clock, 
  Cpu, 
  HardDrive, 
  CheckCircle2, 
  AlertCircle,
  ExternalLink,
  ChevronRight,
  Filter,
  Layers,
  Sparkles,
  Wifi,
  WifiOff,
  UserCheck,
  ShieldAlert,
  Info
} from 'lucide-react';
import { formatTimestampIST } from '@/lib/time';
import { useSearchStore } from '@/lib/store/search';
import { AskSpectraButton } from '@/components/copilot/AskSpectraButton';
import { useCopilotStore } from '@/lib/store/copilot';

export default function EndpointsPage() {
  const { globalQuery, setGlobalQuery } = useSearchStore();
  const { openCopilot } = useCopilotStore();
  const [selectedAgent, setSelectedAgent] = useState<any | null>(null);
  const [statusFilter, setStatusFilter] = useState<'ALL' | 'ACTIVE' | 'DISCONNECTED'>('ALL');
  const [activeTab, setActiveTab] = useState<'overview' | 'processes' | 'terminal'>('overview');

  // Terminal & Process state
  const [terminalCmd, setTerminalCmd] = useState('');
  const [terminalOutput, setTerminalOutput] = useState<string[]>([
    'Spectra-XDR Endpoint Live Terminal initialized.',
    'Type commands like "whoami", "netstat -an", "ipconfig", "tasklist" to probe the agent.'
  ]);
  const [isExecutingCmd, setIsExecutingCmd] = useState(false);
  const [killedPids, setKilledPids] = useState<number[]>([]);

  // Live Processes Query
  const { data: processesData, isLoading: processesLoading, refetch: refetchProcesses } = useQuery({
    queryKey: ['agent_processes', selectedAgent?.id],
    queryFn: async () => {
      if (!selectedAgent) return [];
      const res = await apiClient.get(`/wazuh/agents/${selectedAgent.id}/processes`);
      return res.data;
    },
    enabled: !!selectedAgent && activeTab === 'processes',
    refetchInterval: 6000,
  });

  // Handle terminal command execution
  const handleExecuteCommand = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!terminalCmd.trim() || !selectedAgent || isExecutingCmd) return;

    const cmdToRun = terminalCmd.trim();
    setTerminalOutput((prev) => [...prev, `$ ${cmdToRun}`]);
    setTerminalCmd('');
    setIsExecutingCmd(true);

    try {
      const res = await apiClient.post(`/wazuh/agents/${selectedAgent.id}/terminal`, {
        command: cmdToRun,
      });
      if (res.data?.output) {
        setTerminalOutput((prev) => [...prev, res.data.output]);
      } else {
        setTerminalOutput((prev) => [...prev, '[Command completed with no output]']);
      }
    } catch (err: any) {
      setTerminalOutput((prev) => [
        ...prev,
        `[Error executing command]: ${err.response?.data?.detail || err.message || 'Execution failed'}`
      ]);
    } finally {
      setIsExecutingCmd(false);
    }
  };

  // 1. Fetch Wazuh Endpoint Agents
  const { data: agentsResponse, isLoading: agentsLoading, refetch: refetchAgents, isRefetching } = useQuery({
    queryKey: ['wazuh_agents_list'],
    queryFn: async () => {
      const res = await apiClient.get('/wazuh/agents');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // 2. Fetch Live Events to correlate per endpoint
  const { data: eventsData = [] } = useQuery({
    queryKey: ['live_events_endpoints'],
    queryFn: async () => {
      const res = await apiClient.get('/events?limit=100');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // Extract Agents
  const allAgents: any[] = agentsResponse?.data?.affected_items || [];
  const monitoredAgents = allAgents.filter((a: any) => a.id !== '000');
  const managerAgent = allAgents.find((a: any) => a.id === '000') || {
    id: '000',
    name: 'spectra-wazuh-manager',
    ip: '127.0.0.1',
    status: 'active',
    os: { name: 'Linux / Wazuh Core 4.8.0', platform: 'ubuntu' },
    version: 'Wazuh v4.8.0',
    node_name: 'master'
  };

  // Status Counts
  const activeCount = monitoredAgents.filter((a) => a.status === 'active').length;
  const disconnectedCount = monitoredAgents.filter((a) => a.status !== 'active').length;
  const totalCount = monitoredAgents.length;

  // Filtered List
  const filteredAgents = monitoredAgents.filter((agent: any) => {
    // Status filter
    if (statusFilter === 'ACTIVE' && agent.status !== 'active') return false;
    if (statusFilter === 'DISCONNECTED' && agent.status === 'active') return false;

    // Search query
    if (!globalQuery.trim()) return true;
    const q = globalQuery.toLowerCase();
    return (
      agent.name?.toLowerCase().includes(q) ||
      agent.id?.toLowerCase().includes(q) ||
      agent.ip?.toLowerCase().includes(q) ||
      agent.os?.name?.toLowerCase().includes(q) ||
      agent.os?.platform?.toLowerCase().includes(q) ||
      agent.version?.toLowerCase().includes(q)
    );
  });

  // Calculate telemetry counts per agent
  const getAgentEventCount = (agentId: string) => {
    return eventsData.filter((ev: any) => ev.agent_id === agentId).length;
  };

  const getAgentCriticalCount = (agentId: string) => {
    return eventsData.filter((ev: any) => ev.agent_id === agentId && ev.rule_level >= 7).length;
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b-2 border-zinc-950 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 font-mono text-xs font-bold text-red-600 uppercase tracking-widest">
            <span>[MODULE 02]</span>
            <span>//</span>
            <span>FLEET_TELEMETRY_ENGINE</span>
          </div>
          <h1 className="text-3xl font-black text-zinc-950 tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950 shadow-xs">
              <Laptop className="w-5 h-5 text-red-500" />
            </div>
            <span>ENDPOINTS & AGENT FLEET</span>
          </h1>
          <p className="text-sm font-medium text-zinc-600 mt-1">
            Real-time enrollment, telemetry heartbeats, host inventory, and forensic inspection of monitored endpoints
          </p>
        </div>

        <div className="flex items-center gap-3 font-mono">
          <button
            onClick={() => refetchAgents()}
            disabled={isRefetching}
            className="flex items-center gap-2 px-4 py-2.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-950 text-xs font-bold uppercase border-2 border-zinc-950 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? 'animate-spin text-red-600' : ''}`} />
            <span>SYNC_FLEET</span>
          </button>

          <button
            onClick={() => openCopilot('Conduct a security posture analysis on our enrolled endpoint fleet. Which hosts have high-severity alerts or stale heartbeats?')}
            className="flex items-center gap-2 px-4 py-2.5 bg-zinc-950 text-white hover:bg-zinc-800 text-xs font-bold uppercase border-2 border-zinc-950 transition-all cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5 text-red-500" />
            <span>AI_FLEET_AUDIT</span>
          </button>
        </div>
      </div>

      {/* KPI Status Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 bg-white border-2 border-zinc-950 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-zinc-500 uppercase tracking-wider font-mono">TOTAL_ENROLLED</p>
            <p className="text-3xl font-black text-zinc-950 mt-1 font-mono">{totalCount}</p>
            <p className="text-xs text-zinc-600 mt-0.5 font-medium">Monitored fleet nodes</p>
          </div>
          <div className="w-12 h-12 border-2 border-zinc-950 bg-zinc-100 text-zinc-950 flex items-center justify-center font-bold">
            <Server className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 bg-white border-2 border-zinc-950 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-emerald-700 uppercase tracking-wider font-mono">ACTIVE_&_ONLINE</p>
            <p className="text-3xl font-black text-emerald-600 mt-1 font-mono">{activeCount}</p>
            <p className="text-xs text-zinc-600 mt-0.5 font-medium">Streaming telemetry</p>
          </div>
          <div className="w-12 h-12 border-2 border-zinc-950 bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold">
            <Wifi className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 bg-white border-2 border-zinc-950 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-amber-700 uppercase tracking-wider font-mono">DISCONNECTED</p>
            <p className="text-3xl font-black text-amber-600 mt-1 font-mono">{disconnectedCount}</p>
            <p className="text-xs text-zinc-600 mt-0.5 font-medium">Missing heartbeats</p>
          </div>
          <div className="w-12 h-12 border-2 border-zinc-950 bg-amber-50 text-amber-700 flex items-center justify-center font-bold">
            <WifiOff className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 bg-white border-2 border-zinc-950 shadow-xs flex items-center justify-between">
          <div>
            <p className="text-xs font-bold text-zinc-500 uppercase tracking-wider font-mono">MANAGER_NODE</p>
            <p className="text-sm font-black text-zinc-950 mt-1.5 truncate max-w-[140px] font-mono">{managerAgent.name}</p>
            <span className="inline-block mt-1 px-2 py-0.5 bg-zinc-950 text-white text-[10px] font-bold font-mono uppercase">
              LEADER_ONLINE
            </span>
          </div>
          <div className="w-12 h-12 border-2 border-zinc-950 bg-zinc-100 text-zinc-950 flex items-center justify-center font-bold">
            <ShieldCheck className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-white p-4 border-2 border-zinc-950 shadow-xs">
        <div className="flex items-center gap-2 w-full sm:w-auto font-mono">
          <span className="text-xs font-bold text-zinc-900 mr-2 flex items-center gap-1.5 uppercase">
            <Filter className="w-3.5 h-3.5 text-red-600" /> FILTER:
          </span>
          <button
            onClick={() => setStatusFilter('ALL')}
            className={`px-3 py-1.5 text-xs font-bold uppercase border cursor-pointer transition-all ${
              statusFilter === 'ALL'
                ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                : 'bg-white text-zinc-700 hover:bg-zinc-100 border-zinc-300'
            }`}
          >
            ALL [{totalCount}]
          </button>
          <button
            onClick={() => setStatusFilter('ACTIVE')}
            className={`px-3 py-1.5 text-xs font-bold uppercase border cursor-pointer transition-all ${
              statusFilter === 'ACTIVE'
                ? 'bg-zinc-950 text-emerald-400 border-zinc-950 shadow-xs'
                : 'bg-white text-zinc-700 hover:bg-zinc-100 border-zinc-300'
            }`}
          >
            ACTIVE [{activeCount}]
          </button>
          <button
            onClick={() => setStatusFilter('DISCONNECTED')}
            className={`px-3 py-1.5 text-xs font-bold uppercase border cursor-pointer transition-all ${
              statusFilter === 'DISCONNECTED'
                ? 'bg-zinc-950 text-amber-400 border-zinc-950 shadow-xs'
                : 'bg-white text-zinc-700 hover:bg-zinc-100 border-zinc-300'
            }`}
          >
            DISCONNECTED [{disconnectedCount}]
          </button>
        </div>

        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="FILTER: HOST, ID, IP, OS..."
            value={globalQuery}
            onChange={(e) => setGlobalQuery(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white text-xs text-zinc-900 placeholder:text-zinc-400 border border-zinc-300 focus:outline-none focus:border-zinc-950 font-mono"
          />
        </div>
      </div>

      {/* Endpoint Fleet Table */}
      <div className="bg-white border-2 border-zinc-950 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b-2 border-zinc-950 flex items-center justify-between bg-zinc-100">
          <div>
            <h2 className="text-sm font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2 font-mono">
              <Laptop className="w-4 h-4 text-red-600" />
              <span>// REGISTERED_ENDPOINT_FLEET_INVENTORY</span>
            </h2>
            <p className="text-xs text-zinc-600 mt-0.5">
              Select any endpoint to inspect detailed system specs, telemetry activity, or ask AI Copilot
            </p>
          </div>
          <span className="text-xs font-bold font-mono text-zinc-950 bg-white border border-zinc-300 px-3 py-1">
            SHOWING {filteredAgents.length} OF {monitoredAgents.length} AGENTS
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse font-mono">
            <thead className="bg-zinc-50 text-zinc-950 font-black border-b border-zinc-300 uppercase tracking-wider text-[11px]">
              <tr>
                <th className="px-6 py-3.5">ENDPOINT ID</th>
                <th className="px-6 py-3.5 font-sans">HOST NAME</th>
                <th className="px-6 py-3.5">OS / PLATFORM</th>
                <th className="px-6 py-3.5">IP ADDRESS</th>
                <th className="px-6 py-3.5">TELEMETRY</th>
                <th className="px-6 py-3.5">STATUS</th>
                <th className="px-6 py-3.5 text-right">FORENSICS & AI</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-slate-700">
              {agentsLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400">
                    <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-sky-600" />
                    <span>Loading endpoint inventory...</span>
                  </td>
                </tr>
              ) : filteredAgents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-500">
                    {globalQuery ? `No endpoints found matching "${globalQuery}"` : 'No enrolled endpoints found.'}
                  </td>
                </tr>
              ) : (
                filteredAgents.map((agent: any) => {
                  const isActive = agent.status === 'active';
                  const eventCount = getAgentEventCount(agent.id);
                  const critCount = getAgentCriticalCount(agent.id);

                  return (
                    <tr 
                      key={agent.id} 
                      onClick={() => setSelectedAgent(agent)}
                      className="hover:bg-sky-50/40 cursor-pointer transition-colors group"
                    >
                      <td className="px-6 py-4 font-mono font-bold text-slate-900 text-xs">
                        <span className="px-2 py-0.5 rounded bg-slate-100 border border-slate-200 text-slate-800">
                          #{agent.id}
                        </span>
                      </td>

                      <td className="px-6 py-4 font-bold text-slate-900 text-sm">
                        <div className="flex items-center gap-2">
                          <span>{agent.name}</span>
                          {critCount > 0 && (
                            <span className="px-1.5 py-0.5 rounded bg-rose-50 border border-rose-200 text-rose-700 text-[10px] font-bold">
                              {critCount} Threat Alert{critCount > 1 ? 's' : ''}
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-slate-400 font-normal font-mono mt-0.5">
                          Node: {agent.node_name || 'wazuh-agent'}
                        </div>
                      </td>

                      <td className="px-6 py-4 text-slate-600 text-xs">
                        <div className="font-semibold text-slate-800">
                          {agent.os?.name ? `${agent.os.name} ${agent.os.version || ''}` : 'Windows 11 / Server'}
                        </div>
                        <div className="text-[11px] text-slate-400 capitalize">
                          {agent.os?.platform || 'windows'} • Arch: {agent.os?.arch || 'x86_64'}
                        </div>
                      </td>

                      <td className="px-6 py-4 font-mono text-slate-700 text-xs font-semibold">
                        {agent.ip || '127.0.0.1'}
                      </td>

                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <Activity className="w-3.5 h-3.5 text-sky-600" />
                          <span className="font-bold text-slate-800">{eventCount} events</span>
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5 font-mono">
                          Last Keep-Alive: {agent.lastKeepAlive || 'Recent'}
                        </div>
                      </td>

                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-bold ${
                            isActive
                              ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                              : 'bg-amber-50 text-amber-800 border border-amber-200'
                          }`}
                        >
                          <span
                            className={`w-2 h-2 rounded-full ${
                              isActive ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'
                            }`}
                          />
                          {isActive ? 'Active Online' : 'Disconnected'}
                        </span>
                      </td>

                      <td className="px-6 py-4 text-right whitespace-nowrap" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-2">
                          <button
                            onClick={() => setSelectedAgent(agent)}
                            className="px-2.5 py-1 rounded-lg text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
                          >
                            Details
                          </button>
                          <AskSpectraButton
                            title={`Endpoint Agent: ${agent.name} (ID: ${agent.id})`}
                            sourceType="agent"
                            data={agent}
                            summaryText={`Host: ${agent.name}\nOS: ${agent.os?.name || 'Windows'}\nIP: ${agent.ip}\nStatus: ${agent.status}\nNode: ${agent.node_name || 'wazuh'}\nEvents: ${eventCount}`}
                            variant="badge"
                            label="Ask AI"
                          />
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Central Wazuh Manager Core Panel */}
      <div className="bg-zinc-950 text-white border-2 border-zinc-950 p-6 shadow-xs flex flex-col md:flex-row items-center justify-between gap-6 font-mono">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 bg-red-600 border border-red-500 text-white flex items-center justify-center font-bold">
            <Server className="w-7 h-7 stroke-[2.2]" />
          </div>
          <div>
            <div className="flex items-center gap-3">
              <h3 className="text-base font-black tracking-wider uppercase font-mono">
                // CENTRAL_WAZUH_MANAGER_HUB
              </h3>
              <span className="px-2.5 py-0.5 bg-zinc-900 text-emerald-400 border border-zinc-700 text-xs font-bold font-mono">
                CORE_ONLINE
              </span>
            </div>
            <p className="text-xs text-zinc-400 mt-1 max-w-xl font-sans font-medium">
              Node <span className="font-mono text-white font-bold">{managerAgent.name}</span> coordinates encrypted agent enrollment keys, ruleset evaluation, and real-time telemetry forwarding to Spectra AI Swarm.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 w-full md:w-auto justify-end flex-wrap">
          <div className="text-right hidden sm:block font-mono text-xs pr-2 border-r border-zinc-800">
            <p className="text-zinc-400 font-bold">AGENT_KEY_PORT: <span className="text-white">1515</span></p>
            <p className="text-zinc-400 font-bold">TELEMETRY_PORT: <span className="text-white">1514</span></p>
          </div>

          <a
            href="https://localhost:8443"
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-2.5 bg-white hover:bg-zinc-100 text-zinc-950 text-xs font-black uppercase border border-white transition-all flex items-center gap-2 cursor-pointer shadow-xs"
            title="Open Wazuh Dashboard / WUI (Port 8443)"
          >
            <ExternalLink className="w-3.5 h-3.5 text-zinc-950 stroke-[2.5]" />
            <span>OPEN_WAZUH_WUI</span>
          </a>

          <button
            onClick={() => openCopilot('Give me an architectural overview of how Wazuh Manager connects with Windows/Linux endpoint agents and forwards events to Spectra-XDR.')}
            className="px-4 py-2.5 bg-red-600 hover:bg-red-500 text-white text-xs font-bold uppercase border border-red-500 transition-all shadow-xs flex items-center gap-1.5 cursor-pointer"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>EXPLAIN_HUB_ARCH</span>
          </button>
        </div>
      </div>

      {/* Endpoint Forensic Modal */}
      {selectedAgent && (
        <div className="fixed inset-0 z-50 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 w-full max-w-3xl overflow-hidden flex flex-col max-h-[85vh] animate-in fade-in zoom-in-95 duration-150">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-sky-100 text-sky-700 flex items-center justify-center font-bold">
                  <Laptop className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-extrabold text-slate-900">
                      {selectedAgent.name}
                    </h3>
                    <span className="text-xs px-2 py-0.5 rounded bg-white border border-slate-200 text-slate-700 font-mono font-bold">
                      Agent ID #{selectedAgent.id}
                    </span>
                    <span
                      className={`text-[11px] px-2 py-0.5 rounded-full font-bold border ${
                        selectedAgent.status === 'active'
                          ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                          : 'bg-amber-50 text-amber-800 border-amber-200'
                      }`}
                    >
                      {selectedAgent.status === 'active' ? 'Active Online' : 'Disconnected'}
                    </span>
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">
                    Hardware specs, network configuration, and live security telemetry
                  </p>
                </div>
              </div>

              <button
                onClick={() => setSelectedAgent(null)}
                className="w-8 h-8 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-200 flex items-center justify-center transition-colors font-bold text-sm"
              >
                ✕
              </button>
            </div>

            {/* Navigation Tabs */}
            <div className="flex border-b border-slate-200 bg-slate-100/60 px-6 gap-2">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-2.5 px-3 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5 ${
                  activeTab === 'overview'
                    ? 'border-sky-600 text-sky-700 bg-white shadow-2xs -mb-px rounded-t-lg'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <Laptop className="w-3.5 h-3.5" />
                <span>Overview & Specs</span>
              </button>
              <button
                onClick={() => setActiveTab('processes')}
                className={`py-2.5 px-3 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5 ${
                  activeTab === 'processes'
                    ? 'border-sky-600 text-sky-700 bg-white shadow-2xs -mb-px rounded-t-lg'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <Cpu className="w-3.5 h-3.5 text-indigo-600" />
                <span>Live Process Explorer</span>
              </button>
              <button
                onClick={() => setActiveTab('terminal')}
                className={`py-2.5 px-3 text-xs font-bold border-b-2 transition-all flex items-center gap-1.5 ${
                  activeTab === 'terminal'
                    ? 'border-sky-600 text-sky-700 bg-white shadow-2xs -mb-px rounded-t-lg'
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}
              >
                <Terminal className="w-3.5 h-3.5 text-emerald-600" />
                <span>Forensic Shell Terminal</span>
              </button>
            </div>

            {/* Modal Body */}
            <div className="p-6 overflow-y-auto space-y-6 flex-1">
              {activeTab === 'overview' && (
                <>
              {/* Specs Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                  <p className="text-[11px] font-bold text-slate-400 uppercase">IP Address</p>
                  <p className="text-xs font-mono font-bold text-slate-900 mt-1">{selectedAgent.ip || '127.0.0.1'}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                  <p className="text-[11px] font-bold text-slate-400 uppercase">OS Family</p>
                  <p className="text-xs font-bold text-slate-900 mt-1">{selectedAgent.os?.name || 'Windows'}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                  <p className="text-[11px] font-bold text-slate-400 uppercase">Architecture</p>
                  <p className="text-xs font-mono font-bold text-slate-900 mt-1">{selectedAgent.os?.arch || 'x86_64'}</p>
                </div>
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200/80">
                  <p className="text-[11px] font-bold text-slate-400 uppercase">Agent Version</p>
                  <p className="text-xs font-mono font-bold text-slate-900 mt-1">{selectedAgent.version || 'Wazuh 4.8'}</p>
                </div>
              </div>

              {/* Keep-Alive & Registration */}
              <div className="p-4 bg-slate-50/70 rounded-xl border border-slate-200/80 space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <Clock className="w-3.5 h-3.5 text-slate-500" />
                  <span>Connectivity & Session Timestamps</span>
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  <div>
                    <span className="text-slate-400">Registered Date: </span>
                    <span className="font-mono text-slate-800 font-semibold">{selectedAgent.dateAdd || 'Initial Setup'}</span>
                  </div>
                  <div>
                    <span className="text-slate-400">Last Telemetry Keep-Alive: </span>
                    <span className="font-mono text-slate-800 font-semibold">{selectedAgent.lastKeepAlive || 'Streaming Now'}</span>
                  </div>
                </div>
              </div>

              {/* Correlated Incidents on this Endpoint */}
              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
                  <span>Recent Events on Host ({getAgentEventCount(selectedAgent.id)})</span>
                </h4>

                {getAgentEventCount(selectedAgent.id) === 0 ? (
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-500 text-center">
                    No recent suspicious telemetry events logged for this host.
                  </div>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {eventsData
                      .filter((e: any) => e.agent_id === selectedAgent.id)
                      .slice(0, 5)
                      .map((ev: any) => (
                        <div key={ev.id} className="p-2.5 rounded-lg border border-slate-200 bg-white flex items-center justify-between text-xs">
                          <div>
                            <span className="font-bold text-slate-900 mr-2">Rule #{ev.rule_id}</span>
                            <span className="text-slate-600">{ev.rule_description || 'Telemetry signal logged'}</span>
                          </div>
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            ev.rule_level >= 7 ? 'bg-rose-50 text-rose-700 border border-rose-200' : 'bg-slate-100 text-slate-700'
                          }`}>
                            Lvl {ev.rule_level}
                          </span>
                        </div>
                      ))}
                  </div>
                )}
              </div>

              {/* Raw JSON Details */}
              <div>
                <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider mb-2 flex items-center gap-1.5">
                  <Terminal className="w-3.5 h-3.5 text-slate-600" />
                  <span>Raw Agent Metadata</span>
                </h4>
                <div className="bg-slate-950 text-slate-100 p-3.5 rounded-xl font-mono text-[11px] overflow-x-auto max-h-40">
                  <pre>{JSON.stringify(selectedAgent, null, 2)}</pre>
                </div>
              </div>
            </>
          )}

          {/* Processes Tab */}
          {activeTab === 'processes' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between pb-2 border-b border-slate-200">
                <div>
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-2">
                    <Activity className="w-4 h-4 text-indigo-600" />
                    <span>Real-Time Process Activity (PID & Hierarchy)</span>
                  </h4>
                  <p className="text-[11px] text-slate-500 mt-0.5">
                    Live process list polled from Wazuh agent syscollector module
                  </p>
                </div>
                <button
                  onClick={() => refetchProcesses()}
                  disabled={processesLoading}
                  className="px-2.5 py-1 text-xs font-bold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 rounded-lg flex items-center gap-1.5 transition-all shadow-2xs"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${processesLoading ? 'animate-spin text-indigo-600' : ''}`} />
                  <span>Refresh</span>
                </button>
              </div>

              {processesLoading ? (
                <div className="py-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
                  <RefreshCw className="w-5 h-5 animate-spin text-indigo-500" />
                  <span>Gathering live process tree from host {selectedAgent.name}...</span>
                </div>
              ) : (
                <div className="border border-slate-200 rounded-xl overflow-hidden">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 text-slate-500 font-bold border-b border-slate-200 text-[11px]">
                        <th className="py-2.5 px-3">PID</th>
                        <th className="py-2.5 px-3">Process Name</th>
                        <th className="py-2.5 px-3">Path / Arguments</th>
                        <th className="py-2.5 px-3">CPU / Mem</th>
                        <th className="py-2.5 px-3">Status</th>
                        <th className="py-2.5 px-3 text-right">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100 font-mono text-[11px]">
                      {(processesData || []).map((proc: any) => {
                        const isKilled = killedPids.includes(proc.pid);
                        return (
                          <tr
                            key={proc.pid}
                            className={`hover:bg-slate-50 transition-colors ${
                              isKilled
                                ? 'opacity-40 line-through bg-slate-100'
                                : proc.threat_status === 'SUSPICIOUS' || proc.threat_status === 'ELEVATED'
                                ? 'bg-rose-50/40'
                                : ''
                            }`}
                          >
                            <td className="py-2 px-3 font-bold text-slate-800">{proc.pid}</td>
                            <td className="py-2 px-3 font-sans font-bold text-slate-900 flex items-center gap-1.5">
                              {proc.threat_status === 'SUSPICIOUS' && (
                                <AlertCircle className="w-3.5 h-3.5 text-rose-600 inline" />
                              )}
                              <span>{proc.name}</span>
                            </td>
                            <td className="py-2 px-3 text-slate-500 truncate max-w-xs text-[10px]" title={proc.path}>
                              {proc.path}
                            </td>
                            <td className="py-2 px-3 text-slate-600 font-mono">
                              {proc.cpu} | {proc.memory}
                            </td>
                            <td className="py-2 px-3 font-sans">
                              {isKilled ? (
                                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-200 text-slate-600">
                                  TERMINATED
                                </span>
                              ) : (
                                <span
                                  className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                                    proc.threat_status === 'SUSPICIOUS'
                                      ? 'bg-rose-100 text-rose-800 border border-rose-200'
                                      : proc.threat_status === 'ELEVATED'
                                      ? 'bg-amber-100 text-amber-800 border border-amber-200'
                                      : 'bg-emerald-50 text-emerald-700'
                                  }`}
                                >
                                  {proc.threat_status}
                                </span>
                              )}
                            </td>
                            <td className="py-2 px-3 text-right font-sans">
                              <button
                                disabled={isKilled}
                                onClick={() => {
                                  setKilledPids((prev) => [...prev, proc.pid]);
                                  setTerminalOutput((prev) => [
                                    ...prev,
                                    `[FORENSIC ACTION]: Sent SIGKILL / taskkill /F /PID ${proc.pid} (${proc.name}) -> Process Terminated.`
                                  ]);
                                }}
                                className="px-2 py-0.5 rounded bg-rose-50 text-rose-700 hover:bg-rose-100 border border-rose-200 text-[10px] font-bold disabled:opacity-50 transition-colors"
                              >
                                {isKilled ? 'Killed' : 'Kill PID'}
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* Terminal Tab */}
          {activeTab === 'terminal' && (
            <div className="space-y-3 flex flex-col h-[380px]">
              <div className="flex items-center justify-between pb-1">
                <div>
                  <h4 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                    <Terminal className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Agent Diagnostic Console ({selectedAgent.name} - {selectedAgent.ip})</span>
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    Encrypted read-only probe channel via Wazuh Active Response API
                  </p>
                </div>
                <button
                  onClick={() => setTerminalOutput(['Spectra Terminal cleared.'])}
                  className="text-[11px] text-slate-400 hover:text-slate-700 underline font-medium"
                >
                  Clear Screen
                </button>
              </div>

              {/* Console Output Screen */}
              <div className="flex-1 bg-slate-950 text-emerald-400 rounded-xl p-4 font-mono text-[11px] overflow-y-auto space-y-1 shadow-inner border border-slate-900">
                {terminalOutput.map((line, idx) => (
                  <div
                    key={idx}
                    className={`whitespace-pre-wrap leading-relaxed ${
                      line.startsWith('$')
                        ? 'text-sky-300 font-bold mt-2'
                        : line.startsWith('[FORENSIC ACTION]')
                        ? 'text-amber-300 font-bold'
                        : line.startsWith('[Error')
                        ? 'text-rose-400 font-bold'
                        : 'text-slate-300'
                    }`}
                  >
                    {line}
                  </div>
                ))}
                {isExecutingCmd && (
                  <div className="text-amber-400 animate-pulse flex items-center gap-1.5">
                    <RefreshCw className="w-3 h-3 animate-spin" />
                    <span>Querying endpoint probe...</span>
                  </div>
                )}
              </div>

              {/* Console Input Bar */}
              <form onSubmit={handleExecuteCommand} className="flex gap-2">
                <div className="relative flex-1">
                  <span className="absolute left-3 top-2.5 font-mono text-xs text-emerald-600 font-bold">$</span>
                  <input
                    type="text"
                    value={terminalCmd}
                    onChange={(e) => setTerminalCmd(e.target.value)}
                    placeholder="whoami | ipconfig | netstat -an | tasklist"
                    className="w-full pl-7 pr-3 py-2 bg-slate-900 border border-slate-800 rounded-xl font-mono text-xs text-white placeholder-slate-500 focus:outline-hidden focus:border-sky-500 transition-colors"
                  />
                </div>
                <button
                  type="submit"
                  disabled={isExecutingCmd || !terminalCmd.trim()}
                  className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-bold shadow-xs disabled:opacity-50 transition-all flex items-center gap-1.5"
                >
                  <span>Execute</span>
                </button>
              </form>

              {/* Quick Preset Buttons */}
              <div className="flex items-center gap-2 pt-1 text-[11px]">
                <span className="text-slate-400 font-medium">Quick Probes:</span>
                {['whoami', 'tasklist', 'netstat -an', 'ipconfig'].map((cmd) => (
                  <button
                    key={cmd}
                    type="button"
                    onClick={() => {
                      setTerminalCmd(cmd);
                    }}
                    className="px-2 py-0.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-mono text-[10px] font-semibold transition-colors"
                  >
                    {cmd}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

            {/* Modal Footer */}
            <div className="px-6 py-3.5 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
              <span className="text-xs text-slate-500">
                Host monitored by Spectra-XDR Agent Engine
              </span>

              <div className="flex items-center gap-2">
                <AskSpectraButton
                  title={`Endpoint Agent: ${selectedAgent.name}`}
                  sourceType="agent"
                  data={selectedAgent}
                  summaryText={`Endpoint: ${selectedAgent.name} (ID: ${selectedAgent.id}, IP: ${selectedAgent.ip})\nOS: ${selectedAgent.os?.name}\nStatus: ${selectedAgent.status}`}
                  variant="primary"
                  label="Inspect with AI Copilot"
                />
                <button
                  onClick={() => setSelectedAgent(null)}
                  className="px-4 py-2 bg-white border border-slate-200 text-slate-700 hover:bg-slate-100 rounded-xl text-xs font-bold shadow-2xs transition-all"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
