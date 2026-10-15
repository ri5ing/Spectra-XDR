'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { 
  Cpu, 
  Sparkles, 
  Globe, 
  Key, 
  ShieldCheck, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  Wifi, 
  WifiOff, 
  Server, 
  Activity, 
  Zap, 
  Plus,
  Trash2,
  Layers,
  Clock,
  Gauge,
  RotateCw,
  ExternalLink,
  Lock,
  Radio
} from 'lucide-react';

interface GeminiModelOption {
  id: string;
  name: string;
  badge: string;
  badgeColor: string;
  contextWindow: string;
  rpm: string;
  rpd: string;
  tpm: string;
  bestFor: string;
  latency: string;
}

const GEMINI_MODELS: GeminiModelOption[] = [
  {
    id: 'gemini-3.5-flash',
    name: 'Gemini 3.5 Flash',
    badge: '100% Free Tier • Recommended',
    badgeColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    contextWindow: '1,048,576 Tokens (~1M)',
    rpm: '15 RPM',
    rpd: '1,500 RPD (Free)',
    tpm: '1,000,000 TPM',
    bestFor: 'Real-time alert triage, threat correlation, sub-second SOC reasoning',
    latency: '~200-350 ms',
  },
  {
    id: 'gemini-3.1-flash-lite',
    name: 'Gemini 3.1 Flash-Lite',
    badge: 'Highest Free RPM • Ultra Fast',
    badgeColor: 'bg-purple-50 text-purple-700 border-purple-200',
    contextWindow: '1,048,576 Tokens (~1M)',
    rpm: '30 RPM (Highest)',
    rpd: '1,500 RPD (Free)',
    tpm: '1,000,000 TPM',
    bestFor: 'Resource-efficient micro-triaging, highest rate limits without 429 quota exhaustion',
    latency: '~120-220 ms',
  },
  {
    id: 'gemini-3.5-flash-lite',
    name: 'Gemini 3.5 Flash-Lite',
    badge: 'Latest Free Lite',
    badgeColor: 'bg-sky-50 text-sky-700 border-sky-200',
    contextWindow: '1,048,576 Tokens (~1M)',
    rpm: '15 RPM',
    rpd: '1,500 RPD (Free)',
    tpm: '1,000,000 TPM',
    bestFor: 'Ultra low latency Sysmon log parsing & rapid IOC classification',
    latency: '~150-280 ms',
  }
];

export default function AiRouterPage() {
  const queryClient = useQueryClient();
  const [apiKeyInput, setApiKeyInput] = useState('');
  const [keyNameInput, setKeyNameInput] = useState('');
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const [saveSuccessMsg, setSaveSuccessMsg] = useState('');
  const [saveErrMsg, setSaveErrMsg] = useState('');

  // 1. Fetch AI Router Status
  const { data: statusData, refetch, isRefetching } = useQuery({
    queryKey: ['ai_model_status'],
    queryFn: async () => {
      const res = await apiClient.get('/ai/status');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // 2. Mutation to Add Key
  const addKeyMutation = useMutation({
    mutationFn: async ({ key, name, model }: { key: string; name?: string; model: string }) => {
      const res = await apiClient.post('/ai/keys/add', {
        api_key: key,
        name: name || undefined,
        model: model
      });
      return res.data;
    },
    onSuccess: (data) => {
      setSaveSuccessMsg(data.message || 'Key added to rotation pool successfully!');
      setSaveErrMsg('');
      setApiKeyInput('');
      setKeyNameInput('');
      queryClient.invalidateQueries({ queryKey: ['ai_model_status'] });
      setTimeout(() => setSaveSuccessMsg(''), 5000);
    },
    onError: (err: any) => {
      setSaveErrMsg(err.response?.data?.detail || 'Failed to add Gemini API Key.');
      setSaveSuccessMsg('');
    }
  });

  // 3. Mutation to Select Active Key
  const selectKeyMutation = useMutation({
    mutationFn: async (keyId: string) => {
      const res = await apiClient.post('/ai/keys/select', { key_id: keyId });
      return res.data;
    },
    onSuccess: (data) => {
      setSaveSuccessMsg(data.message || 'Active key switched successfully!');
      queryClient.invalidateQueries({ queryKey: ['ai_model_status'] });
      setTimeout(() => setSaveSuccessMsg(''), 4000);
    }
  });

  // 4. Mutation to Delete Key
  const deleteKeyMutation = useMutation({
    mutationFn: async (keyId: string) => {
      const res = await apiClient.delete(`/ai/keys/${keyId}`);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai_model_status'] });
    }
  });

  // 5. Mutation to Switch Model
  const modelMutation = useMutation({
    mutationFn: async (model: string) => {
      const res = await apiClient.post('/ai/config/model', { model });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai_model_status'] });
    }
  });

  // 6. Mutation to Switch Router Mode (auto, gemini, ollama)
  const modeMutation = useMutation({
    mutationFn: async (mode: string) => {
      const res = await apiClient.post('/ai/config/mode', { mode });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai_model_status'] });
    }
  });

  const handleAddKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiKeyInput.trim()) return;
    addKeyMutation.mutate({ 
      key: apiKeyInput.trim(), 
      name: keyNameInput.trim() || undefined,
      model: selectedModel 
    });
  };

  const routerMode = statusData?.router_mode || 'auto';
  const activeBackend = statusData?.active_backend || 'ollama_local';
  const gemini = statusData?.gemini_cloud || {};
  const ollama = statusData?.ollama_local || {};
  const stats = gemini?.stats || {};
  const keysList = gemini?.keys || [];
  const isInternetConnected = statusData?.internet_connected || false;

  return (
    <div className="space-y-6 pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b-2 border-zinc-950 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 font-mono text-xs font-bold text-red-600 uppercase tracking-widest">
            <span>[MODULE 06]</span>
            <span>//</span>
            <span>DUAL_STACK_LLM_ORCHESTRATOR</span>
          </div>
          <h1 className="text-3xl font-black text-zinc-950 tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950 shadow-xs">
              <Cpu className="w-5 h-5 text-red-500" />
            </div>
            <span>AI MODEL ROUTER & FAILOVER HUB</span>
          </h1>
          <p className="text-sm font-medium text-zinc-600 mt-1">
            Smart Dual-Stack LLM: Circular multi-key quota failover for Gemini Cloud + zero-packet offline fallback to local Ollama Llama 3
          </p>
        </div>
        <div className="flex items-center gap-3 font-mono">
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="flex items-center gap-2 px-4 py-2.5 bg-zinc-950 hover:bg-zinc-800 text-white text-xs font-bold uppercase border-2 border-zinc-950 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? 'animate-spin text-red-500' : 'text-red-500'}`} />
            <span>REFRESH_HEALTH</span>
          </button>
        </div>
      </div>

      {/* Router Routing Strategy Controller */}
      {/* Router Routing Strategy Controller */}
      <div className="bg-white border-2 border-zinc-950 p-5 shadow-xs font-mono">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b-2 border-zinc-950">
          <div>
            <h2 className="text-sm font-black text-zinc-950 uppercase tracking-wider">
              // ACTIVE_ROUTING_STRATEGY
            </h2>
            <p className="text-xs text-zinc-600 font-sans mt-0.5">
              Configure how the SOC reasoning pipeline dispatches queries between Cloud and Local inference
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-zinc-500 uppercase">CURRENTLY_EXECUTING:</span>
            <span className="px-3 py-1 text-xs font-black bg-zinc-950 text-white border border-zinc-950">
              {activeBackend === 'gemini_cloud' ? `⚡ GOOGLE ${gemini.model?.toUpperCase() || 'GEMINI'} (CLOUD)` : activeBackend === 'ollama_local' ? '🔒 OLLAMA LLAMA 3 (LOCAL)' : '🛡️ RULE ENGINE FALLBACK'}
            </span>
          </div>
        </div>

        {/* 3 Strategy Buttons */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
          <button
            type="button"
            onClick={() => modeMutation.mutate('auto')}
            className={`p-4 border-2 text-left transition-all cursor-pointer ${
              routerMode === 'auto'
                ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                : 'bg-white text-zinc-900 border-zinc-950 hover:bg-zinc-100'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5 font-mono">
                <Sparkles className={`w-4 h-4 ${routerMode === 'auto' ? 'text-red-500' : 'text-zinc-950'}`} />
                SMART AUTO SWITCH [RECOMMENDED]
              </span>
              {routerMode === 'auto' && (
                <span className="w-2.5 h-2.5 bg-red-600 border border-white" />
              )}
            </div>
            <p className={`text-xs mt-2 font-mono ${routerMode === 'auto' ? 'text-zinc-300' : 'text-zinc-600'}`}>
              Checks internet & Gemini key pool: Auto-rotates across keys on 429 quota exhaustion, and seamlessly falls back to Ollama if offline.
            </p>
          </button>

          <button
            type="button"
            onClick={() => modeMutation.mutate('gemini')}
            className={`p-4 border-2 text-left transition-all cursor-pointer ${
              routerMode === 'gemini'
                ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                : 'bg-white text-zinc-900 border-zinc-950 hover:bg-zinc-100'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5 font-mono">
                <Globe className={`w-4 h-4 ${routerMode === 'gemini' ? 'text-red-500' : 'text-zinc-950'}`} />
                FORCE GOOGLE GEMINI [CLOUD ONLY]
              </span>
              {routerMode === 'gemini' && (
                <span className="w-2.5 h-2.5 bg-red-600 border border-white" />
              )}
            </div>
            <p className={`text-xs mt-2 font-mono ${routerMode === 'gemini' ? 'text-zinc-300' : 'text-zinc-600'}`}>
              Strictly routes 100% of reasoning to Google Cloud Gemini. Rotates across your saved keys if one exhausts.
            </p>
          </button>

          <button
            type="button"
            onClick={() => modeMutation.mutate('ollama')}
            className={`p-4 border-2 text-left transition-all cursor-pointer ${
              routerMode === 'ollama'
                ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                : 'bg-white text-zinc-900 border-zinc-950 hover:bg-zinc-100'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5 font-mono">
                <Server className={`w-4 h-4 ${routerMode === 'ollama' ? 'text-red-500' : 'text-zinc-950'}`} />
                FORCE LOCAL OLLAMA [AIR-GAPPED ONLY]
              </span>
              {routerMode === 'ollama' && (
                <span className="w-2.5 h-2.5 bg-red-600 border border-white" />
              )}
            </div>
            <p className={`text-xs mt-2 font-mono ${routerMode === 'ollama' ? 'text-zinc-300' : 'text-zinc-600'}`}>
              Strictly restricts all reasoning to local Ollama Llama 3 on port 11434. Zero cloud traffic.
            </p>
          </button>
        </div>
      </div>

      {/* Multi-Key Pool & Circular Failover Manager */}
      <div className="bg-white border-2 border-zinc-950 p-5 shadow-xs font-mono">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-zinc-950 gap-3">
          <div>
            <h2 className="text-sm font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2">
              <Key className="w-4 h-4 text-red-600" />
              <span>// GEMINI_MULTI_KEY_FAILOVER_POOL_&_SMART_ROTATION</span>
            </h2>
            <p className="text-xs text-zinc-600 font-sans mt-0.5">
              Save multiple API keys. When one key exhausts its quota (HTTP 429), the router automatically flips to the next healthy key in a complete round-robin cycle.
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-black text-zinc-950 bg-zinc-100 border-2 border-zinc-950 px-3 py-1">
              {keysList.length} KEYS IN POOL
            </span>
            <span className="text-xs font-black text-white bg-zinc-950 border-2 border-zinc-950 px-3 py-1 flex items-center gap-1.5">
              <RotateCw className="w-3.5 h-3.5 text-red-500" />
              <span>{stats.key_exhaustion_cycles || 0} AUTO-SWITCHES</span>
            </span>
          </div>
        </div>

        {/* Keys Table */}
        <div className="overflow-x-auto mt-4 border-2 border-zinc-950">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-zinc-950 text-white font-extrabold uppercase border-b-2 border-zinc-950">
              <tr>
                <th className="px-4 py-3 tracking-wider w-16">Active</th>
                <th className="px-4 py-3 tracking-wider">Key Name / Label</th>
                <th className="px-4 py-3 tracking-wider">Masked API Key</th>
                <th className="px-4 py-3 tracking-wider">Health Status</th>
                <th className="px-4 py-3 tracking-wider">Requests Made</th>
                <th className="px-4 py-3 tracking-wider">Tokens Used</th>
                <th className="px-4 py-3 tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y-2 divide-zinc-950 text-zinc-900 bg-white">
              {keysList.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-zinc-500 font-bold uppercase">
                    No API keys in pool. Add one below to enable Gemini Cloud reasoning.
                  </td>
                </tr>
              ) : (
                keysList.map((k: any) => {
                  const isActive = k.is_active;
                  const isHealthy = k.status === 'HEALTHY';
                  const isExhausted = k.status === 'EXHAUSTED';

                  return (
                    <tr key={k.id} className={`transition-colors ${isActive ? 'bg-zinc-100 font-bold' : 'hover:bg-zinc-50'}`}>
                      <td className="px-4 py-3.5">
                        <input
                          type="radio"
                          name="active_key_radio"
                          checked={isActive}
                          onChange={() => selectKeyMutation.mutate(k.id)}
                          className="h-4 w-4 text-red-600 focus:ring-red-600 cursor-pointer accent-red-600"
                          title="Set as active key"
                        />
                      </td>
                      <td className="px-4 py-3.5 font-black text-zinc-950">
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{k.name}</span>
                          {isActive && (
                            <span className="text-[10px] bg-red-600 text-white px-2 py-0.5 font-mono font-black uppercase tracking-wider">
                              ACTIVE
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3.5 font-mono font-bold text-zinc-700">
                        {k.masked_key}
                      </td>
                      <td className="px-4 py-3.5">
                        <span
                          className={`inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-black uppercase tracking-wider border-2 ${
                            isHealthy
                              ? 'bg-zinc-50 text-emerald-700 border-zinc-950'
                              : isExhausted
                              ? 'bg-amber-100 text-amber-900 border-zinc-950'
                              : 'bg-zinc-100 text-zinc-700 border-zinc-950'
                          }`}
                        >
                          <span className={`w-2 h-2 ${isHealthy ? 'bg-emerald-600' : isExhausted ? 'bg-amber-600' : 'bg-zinc-600'}`} />
                          {k.status}
                        </span>
                      </td>
                      <td className="px-4 py-3.5 font-mono font-bold text-zinc-900">
                        {k.requests_count || 0} reqs
                      </td>
                      <td className="px-4 py-3.5 font-mono font-bold text-zinc-900">
                        {(k.tokens_used || 0).toLocaleString()} tok
                      </td>
                      <td className="px-4 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-2">
                          {!isActive && (
                            <button
                              onClick={() => selectKeyMutation.mutate(k.id)}
                              className="px-3 py-1.5 bg-white hover:bg-zinc-950 hover:text-white border-2 border-zinc-950 text-zinc-950 text-xs font-bold uppercase transition-all cursor-pointer"
                            >
                              SWITCH TO THIS
                            </button>
                          )}
                          <button
                            onClick={() => deleteKeyMutation.mutate(k.id)}
                            className="p-1.5 bg-white hover:bg-red-600 hover:text-white border-2 border-zinc-950 text-zinc-700 transition-all cursor-pointer"
                            title="Delete key from pool"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Add Key Form with Model Selector Dropdown */}
        <div className="mt-6 pt-5 border-t-2 border-zinc-950">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
            <h3 className="text-xs font-black text-zinc-950 uppercase tracking-wider flex items-center gap-1.5">
              <Plus className="w-4 h-4 text-red-600" />
              <span>// ADD_GEMINI_API_KEY_TO_FAILOVER_POOL</span>
            </h3>
            
            {/* Inline Model Selector Dropdown */}
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-zinc-600 uppercase whitespace-nowrap">ACTIVE_MODEL:</span>
              <select
                value={gemini.model || selectedModel}
                onChange={(e) => {
                  setSelectedModel(e.target.value);
                  modelMutation.mutate(e.target.value);
                }}
                className="h-9 px-3 text-xs font-black uppercase text-zinc-950 bg-white border-2 border-zinc-950 shadow-xs focus:ring-0 focus:outline-none cursor-pointer"
              >
                {GEMINI_MODELS.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name} ({m.rpm} • {m.rpd} • {m.latency})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <form onSubmit={handleAddKey} className="grid grid-cols-1 sm:grid-cols-12 gap-3 max-w-5xl">
            <div className="sm:col-span-4">
              <input
                type="text"
                value={keyNameInput}
                onChange={(e) => setKeyNameInput(e.target.value)}
                placeholder="Key Label (e.g. Om-1, Dron-1, Backup Key)"
                className="w-full h-10 px-3 text-xs font-mono font-bold text-zinc-950 bg-white border-2 border-zinc-950 placeholder-zinc-400 focus:outline-none focus:ring-0"
              />
            </div>
            <div className="sm:col-span-5">
              <input
                type="password"
                value={apiKeyInput}
                onChange={(e) => setApiKeyInput(e.target.value)}
                placeholder="Paste Gemini API Key (AIzaSy...)"
                className="w-full h-10 px-3 text-xs font-mono font-bold text-zinc-950 bg-white border-2 border-zinc-950 placeholder-zinc-400 focus:outline-none focus:ring-0"
              />
            </div>
            <div className="sm:col-span-3">
              <button
                type="submit"
                disabled={addKeyMutation.isPending || !apiKeyInput.trim()}
                className="w-full h-10 bg-zinc-950 hover:bg-zinc-800 disabled:opacity-50 text-white text-xs font-black uppercase tracking-wider transition-all border-2 border-zinc-950 flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
              >
                <Plus className="w-4 h-4 text-red-500" />
                <span>{addKeyMutation.isPending ? 'VALIDATING...' : '+ ADD TO POOL'}</span>
              </button>
            </div>
          </form>

          {/* Model info banner right below dropdown */}
          {(() => {
            const currentM = GEMINI_MODELS.find(m => m.id === (gemini.model || selectedModel)) || GEMINI_MODELS[0];
            return (
              <div className="mt-4 p-3.5 bg-zinc-50 border-2 border-zinc-950 text-xs text-zinc-900 flex flex-wrap items-center justify-between gap-3 font-mono">
                <div className="flex items-center gap-2.5">
                  <span className="font-black text-zinc-950">{currentM.name}</span>
                  <span className="text-[10px] font-black px-2 py-0.5 bg-red-600 text-white uppercase">{currentM.badge}</span>
                  <span className="text-zinc-600 hidden md:inline">— {currentM.bestFor}</span>
                </div>
                <div className="flex items-center gap-4 text-xs font-bold text-zinc-950">
                  <span>QUOTA: <strong className="text-red-600">{currentM.rpm}</strong> / <strong className="text-red-600">{currentM.rpd}</strong></span>
                  <span>LATENCY: <strong>{currentM.latency}</strong></span>
                  <span>CONTEXT: <strong>{currentM.contextWindow}</strong></span>
                </div>
              </div>
            );
          })()}

          {saveSuccessMsg && (
            <div className="mt-4 p-3 bg-emerald-50 border-2 border-zinc-950 text-emerald-950 text-xs font-bold flex items-center gap-2 font-mono">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
              <span>{saveSuccessMsg}</span>
            </div>
          )}

          {saveErrMsg && (
            <div className="mt-4 p-3 bg-red-50 border-2 border-zinc-950 text-red-950 text-xs font-bold flex items-center gap-2 font-mono">
              <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0" />
              <span>{saveErrMsg}</span>
            </div>
          )}
        </div>
      </div>

      {/* Gemini Token Usage & Quota Accounting Dashboard */}
      <div className="bg-white border-2 border-zinc-950 p-5 shadow-xs font-mono">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-zinc-950 gap-2">
          <div>
            <h2 className="text-sm font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2">
              <Activity className="w-4 h-4 text-red-600" />
              <span>// CUMULATIVE_TOKEN_ACCOUNTING_&_QUOTA_ANALYTICS</span>
            </h2>
            <p className="text-xs text-zinc-600 font-sans mt-0.5">
              Real-time prompt tokens consumed, response tokens generated across all pooled keys, and auto-failover metrics
            </p>
          </div>
          <span className="text-xs font-black text-white bg-zinc-950 border-2 border-zinc-950 px-3 py-1 uppercase">
            FREE TIER QUOTA TRACKING
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4">
          <div className="p-4 bg-zinc-50 border-2 border-zinc-950">
            <span className="text-xs font-bold text-zinc-500 uppercase block tracking-wider">TOTAL TOKENS USED</span>
            <div className="text-2xl font-black font-mono text-zinc-950 mt-1">
              {(stats.total_tokens_used || 0).toLocaleString()}
            </div>
            <span className="text-[10px] text-zinc-500 font-mono font-semibold uppercase mt-0.5 block">PROMPT + OUTPUT</span>
          </div>

          <div className="p-4 bg-zinc-50 border-2 border-zinc-950">
            <span className="text-xs font-bold text-zinc-500 uppercase block tracking-wider">PROMPT INPUT TOKENS</span>
            <div className="text-2xl font-black font-mono text-zinc-950 mt-1">
              {(stats.prompt_tokens_used || 0).toLocaleString()}
            </div>
            <span className="text-[10px] text-zinc-500 font-mono font-semibold uppercase mt-0.5 block">CONTEXT + TELEMETRY</span>
          </div>

          <div className="p-4 bg-zinc-50 border-2 border-zinc-950">
            <span className="text-xs font-bold text-zinc-500 uppercase block tracking-wider">GENERATED TOKENS</span>
            <div className="text-2xl font-black font-mono text-zinc-950 mt-1">
              {(stats.candidates_tokens_used || 0).toLocaleString()}
            </div>
            <span className="text-[10px] text-zinc-500 font-mono font-semibold uppercase mt-0.5 block">AI ANALYSES & PLAYBOOKS</span>
          </div>

          <div className="p-4 bg-zinc-50 border-2 border-zinc-950">
            <span className="text-xs font-bold text-zinc-500 uppercase block tracking-wider">API CALLS (REQS)</span>
            <div className="text-2xl font-black font-mono text-zinc-950 mt-1">
              {stats.requests_successful || 0}
              <span className="text-xs text-zinc-500 font-mono font-bold ml-1">/ {stats.requests_total || 0}</span>
            </div>
            <span className="text-[10px] text-zinc-500 font-mono font-semibold uppercase mt-0.5 block">{stats.requests_failed || 0} FAILED REQS</span>
          </div>

          <div className="p-4 bg-zinc-50 border-2 border-zinc-950">
            <span className="text-xs font-bold text-zinc-500 uppercase block tracking-wider">AUTO-ROTATIONS</span>
            <div className="text-2xl font-black font-mono text-red-600 mt-1">
              {stats.key_exhaustion_cycles || 0}
            </div>
            <span className="text-[10px] text-zinc-500 font-mono font-semibold uppercase mt-0.5 block">SEAMLESS 429 FAILOVERS</span>
          </div>
        </div>
      </div>
    </div>
  );
}
