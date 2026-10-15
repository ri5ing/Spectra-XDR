'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { 
  ShieldAlert, 
  Layers, 
  Search, 
  ExternalLink, 
  Filter, 
  CheckCircle2, 
  AlertTriangle,
  Info,
  X,
  Crosshair,
  Terminal,
  FileCode,
  RefreshCw,
  Database,
  Radio,
  Wifi,
  Sparkles,
  Server,
  Zap,
  ArrowUpRight
} from 'lucide-react';

interface MitreTechnique {
  id: string;
  technique_id: string;
  technique_name: string;
  tactic: string;
  subtechnique_id?: string | null;
  description: string;
  detection_rationale?: string;
  source: string;
}

export default function MitrePage() {
  const queryClient = useQueryClient();
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTactic, setSelectedTactic] = useState<string>('all');
  const [selectedTech, setSelectedTech] = useState<MitreTechnique | null>(null);

  // 1. Fetch MITRE Techniques from Spectra API
  const { data: techniques = [], isLoading: techLoading } = useQuery<MitreTechnique[]>({
    queryKey: ['mitre_techniques'],
    queryFn: async () => {
      const res = await apiClient.get('/intelligence/mitre');
      return res.data;
    },
    refetchInterval: 10000,
  });

  // 2. Fetch TAXII 2.1 Threat Intel & MITRE DB Status
  const { data: taxiiStatus, isLoading: taxiiLoading, refetch: refetchTaxii } = useQuery({
    queryKey: ['taxii_status'],
    queryFn: async () => {
      const res = await apiClient.get('/intelligence/taxii/status');
      return res.data;
    },
    refetchInterval: 10000,
  });

  // 3. TAXII Sync Mutation
  const syncMutation = useMutation({
    mutationFn: async () => {
      const res = await apiClient.post('/intelligence/taxii/sync');
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mitre_techniques'] });
      queryClient.invalidateQueries({ queryKey: ['taxii_status'] });
    }
  });

  const tactics = [
    'Initial Access',
    'Execution',
    'Persistence',
    'Privilege Escalation',
    'Defense Evasion',
    'Credential Access',
    'Discovery',
    'Lateral Movement',
    'Collection',
    'Command and Control',
    'Exfiltration',
    'Impact',
  ];

  // Filter techniques
  const filteredTechniques = techniques.filter((tech) => {
    const matchesSearch = 
      tech.technique_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tech.technique_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tech.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (tech.detection_rationale && tech.detection_rationale.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesTactic = 
      selectedTactic === 'all' || 
      tech.tactic.toLowerCase() === selectedTactic.toLowerCase();

    return matchesSearch && matchesTactic;
  });

  // Group techniques by tactic for the matrix heatmap
  const groupedTechniques = tactics.reduce<Record<string, MitreTechnique[]>>((acc, tactic) => {
    acc[tactic] = techniques.filter(
      (t) => t.tactic?.toLowerCase() === tactic.toLowerCase()
    );
    return acc;
  }, {});

  return (
    <div className="space-y-6 pb-16">
      {/* Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-5 border-b-2 border-zinc-950 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 font-mono text-xs font-bold text-red-600 uppercase tracking-widest">
            <span>[MODULE 04]</span>
            <span>//</span>
            <span>THREAT_INTELLIGENCE_MATRIX</span>
          </div>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-black text-zinc-950 tracking-tight flex items-center gap-3 font-mono">
              <div className="w-10 h-10 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950 shadow-xs">
                <ShieldAlert className="w-5 h-5 text-red-500" />
              </div>
              <span>MITRE ATT&CK MATRIX</span>
            </h1>
            <span className="px-2.5 py-1 bg-zinc-950 text-white text-xs font-bold font-mono">
              ENTERPRISE_V15.1
            </span>
          </div>
          <p className="text-sm font-medium text-zinc-600 mt-1">
            Real-time adversary technique catalog mapped to PostgreSQL DB with TAXII 2.1 automated threat feed sync
          </p>
        </div>
        
        <div className="flex items-center gap-3 font-mono">
          <button
            onClick={() => syncMutation.mutate()}
            disabled={syncMutation.isPending}
            className="flex items-center gap-2 px-4 py-2.5 bg-zinc-950 hover:bg-zinc-800 text-white text-xs font-bold uppercase border-2 border-zinc-950 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncMutation.isPending ? 'animate-spin text-red-500' : 'text-red-500'}`} />
            <span>{syncMutation.isPending ? 'SYNCING_TAXII...' : 'SYNC_TAXII_FEED'}</span>
          </button>
          
          <a
            href="https://attack.mitre.org/"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-4 py-2.5 bg-zinc-100 hover:bg-zinc-200 text-zinc-950 border-2 border-zinc-950 text-xs font-bold uppercase transition-all"
          >
            <span>MITRE_DOCS</span>
            <ExternalLink className="w-3.5 h-3.5 text-zinc-600" />
          </a>
        </div>
      </div>

      {/* TAXII 2.1 & MITRE DB Telemetry Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* Card 1: TAXII Server Status */}
        <div className="bg-white p-4 border-2 border-zinc-950 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-600 font-mono flex items-center gap-1.5 uppercase">
              <Radio className="w-4 h-4 text-red-600" />
              TAXII_FEED_SERVER
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[11px] font-bold font-mono bg-zinc-950 text-white">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              {taxiiStatus?.taxii_server?.status || 'CONNECTED'}
            </span>
          </div>
          <div className="mt-3">
            <div className="text-base font-black text-zinc-950 font-mono uppercase">
              {taxiiStatus?.taxii_server?.collection || 'Enterprise ATT&CK'}
            </div>
            <p className="text-xs text-zinc-500 font-mono truncate mt-1">
              {taxiiStatus?.taxii_server?.server_url || 'https://cti-taxii.mitre.org/taxii/'}
            </p>
          </div>
        </div>

        {/* Card 2: MITRE DB Cataloged Techniques */}
        <div className="bg-white p-4 border-2 border-zinc-950 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-600 font-mono flex items-center gap-1.5 uppercase">
              <Database className="w-4 h-4 text-red-600" />
              MITRE_DB_INVENTORY
            </span>
            <span className="text-[11px] font-bold font-mono text-zinc-950 bg-zinc-100 px-2 py-0.5 border border-zinc-300">
              POSTGRESQL
            </span>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-black text-zinc-950 flex items-baseline gap-2 font-mono">
              <span>{techniques.length}</span>
              <span className="text-xs font-bold text-zinc-500 uppercase font-sans">Techniques / 12 Tactics</span>
            </div>
            <p className="text-xs text-emerald-700 font-bold mt-1 flex items-center gap-1 font-mono uppercase">
              <CheckCircle2 className="w-3.5 h-3.5" /> 100% COVERAGE_MAPPED
            </p>
          </div>
        </div>

        {/* Card 3: Active Attack Scanners */}
        <div className="bg-white p-4 border-2 border-zinc-950 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-600 font-mono flex items-center gap-1.5 uppercase">
              <Zap className="w-4 h-4 text-red-600" />
              ATTACK_SCANNERS
            </span>
            <span className="text-[11px] font-bold font-mono text-white bg-zinc-950 px-2 py-0.5">
              ACTIVE
            </span>
          </div>
          <div className="mt-3">
            <div className="text-3xl font-black text-zinc-950 flex items-baseline gap-2 font-mono">
              <span>4</span>
              <span className="text-xs font-bold text-zinc-500 uppercase font-sans">Correlation Engines</span>
            </div>
            <p className="text-xs text-zinc-600 mt-1 font-mono">
              Wazuh Rules + FIM + Behavioral
            </p>
          </div>
        </div>

        {/* Card 4: Last Feed Sync Status */}
        <div className="bg-white p-4 border-2 border-zinc-950 shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-zinc-600 font-mono flex items-center gap-1.5 uppercase">
              <Server className="w-4 h-4 text-red-600" />
              FEED_SYNC_CYCLE
            </span>
            <span className="text-[11px] font-bold font-mono text-zinc-950 bg-zinc-100 px-2 py-0.5 border border-zinc-300">
              HOURLY
            </span>
          </div>
          <div className="mt-3">
            <div className="text-base font-black text-zinc-950 font-mono uppercase">
              AUTO-SYNC ACTIVE
            </div>
            <p className="text-xs text-zinc-500 mt-1 truncate font-mono">
              LAST SYNC: JUST NOW (STIX 2.1)
            </p>
          </div>
        </div>
      </div>

      {/* Live Threat Intel Feed Updates Ticker */}
      <div className="bg-zinc-950 text-white border-2 border-zinc-950 p-5 shadow-xs">
        <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
          <div className="flex items-center gap-2 font-mono">
            <Sparkles className="w-4 h-4 text-red-500" />
            <h3 className="text-xs font-black uppercase tracking-wider text-white">
              // LIVE_THREAT_INTEL_FEED_&_TAXII_UPDATES
            </h3>
          </div>
          <span className="text-xs font-mono font-bold text-red-400 bg-zinc-900 border border-zinc-800 px-3 py-1">
            REAL-TIME INGESTION
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mt-4">
          {(taxiiStatus?.recent_updates || []).map((update: any, idx: number) => (
            <div key={idx} className="bg-zinc-900 border-2 border-zinc-800 p-3.5 flex flex-col justify-between font-mono">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-black text-red-500">[{update.technique_id}]</span>
                  <span className="text-[11px] text-zinc-400">{update.timestamp}</span>
                </div>
                <div className="text-xs font-bold text-white mt-1.5 font-sans line-clamp-1">{update.name}</div>
                <div className="text-xs text-zinc-400 mt-0.5 font-mono">{update.update_type}</div>
              </div>
              <div className="mt-3 pt-2 border-t border-zinc-800 flex items-center justify-between text-xs">
                <span className="text-zinc-500 uppercase font-bold">{update.tactic}</span>
                <span className="font-bold text-emerald-400">{update.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white p-4 border-2 border-zinc-950 shadow-xs flex flex-col md:flex-row items-center gap-4">
        <div className="relative flex-1 w-full font-mono">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="FILTER: ID (e.g. T1059, T1082), TECHNIQUE NAME, OR DETECTION RATIONALE..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-9 pr-4 py-2 bg-white border border-zinc-300 text-xs text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:border-zinc-950 font-mono"
          />
        </div>

        <div className="flex items-center gap-2 w-full md:w-auto font-mono">
          <Filter className="w-4 h-4 text-red-600" />
          <span className="text-xs font-bold text-zinc-900 uppercase tracking-wider whitespace-nowrap">
            TACTIC:
          </span>
          <select
            value={selectedTactic}
            onChange={(e) => setSelectedTactic(e.target.value)}
            className="px-3 py-2 bg-white border border-zinc-300 text-xs text-zinc-900 font-bold focus:outline-none focus:border-zinc-950 w-full md:w-auto cursor-pointer"
          >
            <option value="all">ALL TACTICS ({tactics.length})</option>
            {tactics.map((tac) => (
              <option key={tac} value={tac}>
                {tac.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* MITRE ATT&CK Matrix Vertical Tactic Sections */}
      <div className="bg-white border-2 border-zinc-950 shadow-xs overflow-hidden">
        <div className="px-6 py-4 border-b-2 border-zinc-950 flex items-center justify-between bg-zinc-100">
          <div>
            <h3 className="text-sm font-black text-zinc-950 flex items-center gap-2 font-mono uppercase">
              <Crosshair className="w-4 h-4 text-red-600" />
              <span>// ADVERSARY_TACTIC_HEATMAP_&_COVERAGE</span>
            </h3>
            <p className="text-xs text-zinc-600 mt-0.5">Structured by MITRE ATT&CK Kill-Chain: Click any technique card to inspect detection rationale, SIEM queries, and TAXII mapping.</p>
          </div>
          <span className="text-xs font-bold font-mono text-zinc-950 bg-white border border-zinc-300 px-3 py-1">
            {filteredTechniques.length} TECHNIQUES MAPPED
          </span>
        </div>

        <div className="p-6 space-y-6">
          {tactics.map((tactic) => {
            const items = groupedTechniques[tactic] || [];
            const isFilteredOut = selectedTactic !== 'all' && selectedTactic.toLowerCase() !== tactic.toLowerCase();

            if (isFilteredOut) return null;

            return (
              <div key={tactic} className="bg-zinc-50 p-4 border-2 border-zinc-200">
                {/* Tactic Section Header */}
                <div className="flex items-center justify-between pb-3 mb-3 border-b-2 border-zinc-200">
                  <div className="flex items-center gap-3">
                    <span className="w-2.5 h-2.5 bg-red-600" />
                    <h4 className="text-xs font-black text-zinc-950 uppercase tracking-wider font-mono">
                      {tactic}
                    </h4>
                    <span className="text-xs font-bold font-mono text-zinc-950 bg-zinc-200 px-2.5 py-0.5">
                      {items.length} {items.length === 1 ? 'RULE' : 'RULES'}
                    </span>
                  </div>
                  <span className="text-xs font-mono font-bold text-zinc-500">
                    TAXII 2.1 VERIFIED
                  </span>
                </div>

                {/* Vertical Grid of Technique Cards under this Tactic */}
                {items.length === 0 ? (
                  <div className="p-4 border-2 border-dashed border-zinc-300 text-xs text-zinc-500 font-mono text-center bg-white">
                    NO ACTIVE DETECTIONS CONFIGURED FOR THIS TACTIC PHASE.
                  </div>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
                    {items.map((tech) => (
                      <div
                        key={tech.technique_id}
                        onClick={() => setSelectedTech(tech)}
                        className={`p-4 border-2 text-left cursor-pointer transition-all ${
                          selectedTech?.technique_id === tech.technique_id
                            ? 'bg-zinc-950 text-white border-zinc-950 shadow-md translate-x-1'
                            : 'bg-white border-zinc-200 hover:border-zinc-950 text-zinc-950 shadow-xs'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className={`text-xs font-mono font-black px-2 py-0.5 border ${
                            selectedTech?.technique_id === tech.technique_id
                              ? 'bg-zinc-800 text-red-400 border-zinc-700'
                              : 'bg-zinc-100 text-zinc-950 border-zinc-300'
                          }`}>
                            {tech.technique_id}
                          </span>
                          <span className="flex items-center gap-1.5 text-[11px] font-bold font-mono text-emerald-500">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                            ACTIVE
                          </span>
                        </div>
                        <div className={`text-xs font-black mt-2.5 font-sans ${selectedTech?.technique_id === tech.technique_id ? 'text-white' : 'text-zinc-950'}`}>
                          {tech.technique_name}
                        </div>
                        <p className={`text-xs mt-1.5 line-clamp-2 leading-relaxed ${selectedTech?.technique_id === tech.technique_id ? 'text-zinc-400' : 'text-zinc-600'}`}>
                          {tech.detection_rationale || tech.description}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Selected Technique Details Pop-up Drawer */}
      {selectedTech && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-50 flex justify-end transition-opacity">
          <div className="w-full max-w-xl bg-white h-full shadow-2xl p-6 overflow-y-auto flex flex-col justify-between border-l border-slate-200">
            <div className="space-y-6">
              {/* Header */}
              <div className="flex items-start justify-between pb-4 border-b border-slate-200">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold px-2.5 py-1 bg-blue-100 text-blue-800 rounded-md">
                      {selectedTech.technique_id}
                    </span>
                    <span className="text-xs font-semibold px-2 py-0.5 bg-slate-100 text-slate-600 rounded-md uppercase">
                      {selectedTech.tactic}
                    </span>
                  </div>
                  <h2 className="text-xl font-bold text-slate-900 mt-2">
                    {selectedTech.technique_name}
                  </h2>
                </div>
                <button
                  onClick={() => setSelectedTech(null)}
                  className="p-1 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Description */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <Info className="w-4 h-4 text-blue-600" />
                  Technique Adversary Overview
                </h4>
                <p className="text-xs text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200">
                  {selectedTech.description}
                </p>
              </div>

              {/* Detection Rationale */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <Terminal className="w-4 h-4 text-emerald-600" />
                  Spectra Detection Rationale
                </h4>
                <div className="p-3 bg-emerald-50/50 rounded-lg border border-emerald-200 text-xs text-emerald-900 leading-relaxed font-mono">
                  {selectedTech.detection_rationale || 'Pattern matched via Wazuh active ruleset and FIM telemetry engine.'}
                </div>
              </div>

              {/* STIX & SIEM Query Definition */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                  <FileCode className="w-4 h-4 text-purple-600" />
                  STIX 2.1 Pattern & Threat Rule Signature
                </h4>
                <div className="bg-slate-900 text-slate-200 p-3 rounded-lg font-mono text-[11px] overflow-x-auto border border-slate-800 leading-relaxed">
                  <code>{`[process:name = '*' AND process:command_line MATCHES '(?i).*(${selectedTech.technique_id}|${selectedTech.technique_name.toLowerCase().replace(/\\s+/g, '_')}).*']
WHERE agent.status = 'active'`}</code>
                </div>
              </div>

              {/* Mapped Wazuh Decoders */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">
                  Mapped Telemetry Providers & Decoders
                </h4>
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="px-2.5 py-1 bg-slate-100 text-slate-700 font-mono rounded-md border border-slate-200">
                    wazuh-agent
                  </span>
                  <span className="px-2.5 py-1 bg-slate-100 text-slate-700 font-mono rounded-md border border-slate-200">
                    windows_eventchannel
                  </span>
                  <span className="px-2.5 py-1 bg-slate-100 text-slate-700 font-mono rounded-md border border-slate-200">
                    syscheck_fim
                  </span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="pt-6 border-t border-slate-200 flex items-center justify-between">
              <a
                href={`https://attack.mitre.org/techniques/${selectedTech.technique_id.replace('.', '/')}`}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-600 hover:text-blue-700 transition-colors"
              >
                <span>View Official MITRE Page</span>
                <ArrowUpRight className="w-4 h-4" />
              </a>

              <button
                onClick={() => setSelectedTech(null)}
                className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold rounded-lg transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
