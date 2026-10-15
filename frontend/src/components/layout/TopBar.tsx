'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Search, Laptop, ShieldCheck, Clock, Menu, Cpu, Sparkles } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { useSearchStore } from '@/lib/store/search';
import { useSidebarStore } from '@/lib/store/sidebar';
import { useCopilotStore } from '@/lib/store/copilot';
import { ModelSelectorPopover } from '@/components/copilot/ModelSelectorPopover';

export function TopBar() {
  const [istTime, setIstTime] = useState<string>('');
  const [modelPopoverOpen, setModelPopoverOpen] = useState(false);
  const { openCopilot } = useCopilotStore();

  useEffect(() => {
    let animId: number;
    const updateTime = () => {
      const now = new Date();
      const formatter = new Intl.DateTimeFormat('en-IN', {
        timeZone: 'Asia/Kolkata',
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true,
      });

      const parts = formatter.formatToParts(now);
      const day = parts.find((p) => p.type === 'day')?.value || '';
      const month = parts.find((p) => p.type === 'month')?.value || '';
      const year = parts.find((p) => p.type === 'year')?.value || '';
      const hour = parts.find((p) => p.type === 'hour')?.value || '00';
      const minute = parts.find((p) => p.type === 'minute')?.value || '00';
      const second = parts.find((p) => p.type === 'second')?.value || '00';
      const dayPeriod = parts.find((p) => p.type === 'dayPeriod')?.value || 'AM';
      const ms = String(now.getMilliseconds()).padStart(3, '0');

      setIstTime(`${day} ${month} ${year}, ${hour}:${minute}:${second}.${ms} ${dayPeriod}`);
      animId = requestAnimationFrame(updateTime);
    };

    animId = requestAnimationFrame(updateTime);
    return () => cancelAnimationFrame(animId);
  }, []);

  const { isSuccess } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const res = await apiClient.get('/health');
      return res.data;
    },
    refetchInterval: 5000,
  });

  const { data: agentsData } = useQuery({
    queryKey: ['wazuh_agents_count'],
    queryFn: async () => {
      const res = await apiClient.get('/wazuh/agents');
      return res.data;
    },
    refetchInterval: 5000,
  });

  const activeAgentsCount = agentsData?.data?.affected_items?.filter(
    (a: any) => a.status === 'active' && a.id !== '000'
  ).length || 0;

  // Active AI Model Status Query
  const { data: aiStatus } = useQuery({
    queryKey: ['ai_model_status'],
    queryFn: async () => {
      const res = await apiClient.get('/ai/status');
      return res.data;
    },
    refetchInterval: 5000,
  });

  const activeModelDisplay = aiStatus?.active_backend === 'gemini_cloud'
    ? (aiStatus?.gemini_cloud?.display_name || 'Gemini 3.5 Flash')
    : aiStatus?.active_backend === 'ollama_local'
    ? `Ollama (${aiStatus?.ollama_local?.model || 'llama3'})`
    : 'Deterministic Fallback';

  const { globalQuery, setGlobalQuery, clearGlobalQuery } = useSearchStore();
  const { toggle: toggleSidebar } = useSidebarStore();

  return (
    <header className="h-16 bg-white border-b-2 border-zinc-950 flex items-center justify-between px-6 flex-shrink-0 z-30 gap-4 select-none">
      <div className="flex items-center gap-3.5 flex-1 min-w-0">
        {/* Hamburger Menu Toggle Button */}
        <button
          onClick={toggleSidebar}
          className="w-10 h-10 hover:bg-zinc-100 text-zinc-900 border-2 border-zinc-950 transition-colors flex items-center justify-center shrink-0 cursor-pointer"
          title="Toggle Navigation Menu"
        >
          <Menu className="w-5 h-5 text-zinc-900 stroke-[2.2]" />
        </button>

        {/* Brand Logo & Name - Clicking opens Spectra AI Copilot */}
        <button
          onClick={() => openCopilot()}
          className="hidden sm:flex items-center gap-3 shrink-0 pr-4 border-r-2 border-zinc-200 hover:opacity-85 transition-opacity text-left cursor-pointer group"
          title="Click to Open Spectra AI Copilot"
        >
          <div className="w-8 h-8 bg-zinc-950 text-white flex items-center justify-center font-mono font-black text-sm tracking-tighter border-2 border-zinc-950 group-hover:bg-red-600 transition-colors">
            SX
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="text-sm font-black tracking-tight text-zinc-950 font-mono uppercase block leading-none">
                SPECTRA<span className="text-red-600">/</span>XDR
              </span>
              <Sparkles className="w-3.5 h-3.5 text-red-500 group-hover:rotate-12 transition-transform" />
            </div>
            <span className="text-[10px] font-mono text-zinc-400 uppercase tracking-wider block leading-none mt-1 group-hover:text-red-600 transition-colors">
              SEC_OS // COPILOT
            </span>
          </div>
        </button>

        {/* Swiss Modernist Search Bar */}
        <div className="relative w-80 md:w-96">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-zinc-400" />
          <input
            type="text"
            value={globalQuery}
            onChange={(e) => setGlobalQuery(e.target.value)}
            placeholder="QUERY: IP, RULE_ID, HASH, HOST..."
            className="w-full h-10 pl-10 pr-8 bg-zinc-50 border-2 border-zinc-950 text-xs md:text-sm font-mono text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:bg-white transition-all uppercase font-bold"
          />
          {globalQuery && (
            <button
              onClick={clearGlobalQuery}
              className="absolute right-3 top-2.5 text-zinc-400 hover:text-zinc-900 text-sm font-mono font-bold"
              title="Clear search"
            >
              &times;
            </button>
          )}
        </div>
        {globalQuery && (
          <span className="hidden xl:inline-block font-mono text-xs font-bold text-zinc-900 bg-zinc-100 border-2 border-zinc-950 px-2.5 py-1 shrink-0 truncate uppercase">
            FILTER: &quot;{globalQuery}&quot;
          </span>
        )}
      </div>

      <div className="flex items-center gap-3">
        {/* Live IST Clock */}
        <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 bg-zinc-50 border-2 border-zinc-950 font-mono text-sm text-zinc-900">
          <div className="w-2 h-2 rounded-full bg-red-600 animate-pulse" />
          <span className="font-bold tracking-tight">{istTime || 'SYNCING IST...'}</span>
          <span className="text-[10px] bg-zinc-950 text-white px-1.5 py-0.5 font-bold uppercase tracking-wider">
            IST
          </span>
        </div>

        {/* Endpoints Counter */}
        <Link 
          href="/endpoints"
          className="flex items-center gap-2 px-3 py-1.5 bg-white hover:bg-zinc-50 border-2 border-zinc-950 font-mono text-xs md:text-sm text-zinc-900 transition-colors"
          title="Open Endpoints & Fleet Management"
        >
          <Laptop className="w-4 h-4 text-zinc-700" />
          <span className="text-xs text-zinc-500 uppercase font-semibold">FLEET:</span>
          <span className="font-bold text-zinc-950">
            {activeAgentsCount} ONLINE
          </span>
        </Link>

        {/* Backend API Status */}
        <div className="flex items-center gap-2 px-2.5 py-1.5 bg-white border-2 border-zinc-950 font-mono text-xs">
          <span
            className={`w-2 h-2 rounded-full ${
              isSuccess ? 'bg-emerald-500' : 'bg-red-600'
            }`}
          />
          <span className="font-bold uppercase text-zinc-800">
            {isSuccess ? 'CORE:OK' : 'CORE:ERR'}
          </span>
        </div>

        {/* Active AI Model Badge with Split Click Actions:
            1. Clicking 'AI' or Chip Icon: Opens Spectra AI Copilot
            2. Clicking Model Name: Opens Model Selector Popover
        */}
        <div className="relative">
          <div className="flex items-center border-2 border-zinc-950 bg-zinc-950 text-white font-mono text-xs shadow-xs">
            {/* Click on AI / Chip icon -> Opens Spectra AI Copilot */}
            <button
              onClick={() => openCopilot()}
              className="flex items-center gap-1.5 px-3 py-1.5 hover:bg-red-600 transition-colors border-r border-zinc-800 cursor-pointer group"
              title="Click AI to Open SPECTRA-AI Copilot"
            >
              <Cpu className="w-4 h-4 text-zinc-300 group-hover:text-white" />
              <span className="text-red-500 group-hover:text-white font-black uppercase text-xs">
                AI:
              </span>
            </button>

            {/* Click on Model Name -> Opens Model Selector Popover */}
            <button
              onClick={() => setModelPopoverOpen((prev) => !prev)}
              className="px-3 py-1.5 hover:bg-zinc-800 transition-colors flex items-center gap-1.5 cursor-pointer max-w-[190px]"
              title="Click Model Name to Change Model or Open Model Router"
            >
              <span className="font-bold truncate text-white">
                {activeModelDisplay}
              </span>
              <span className="text-[10px] text-zinc-400">▼</span>
            </button>
          </div>

          {/* Model Selector Popover */}
          <ModelSelectorPopover
            isOpen={modelPopoverOpen}
            onClose={() => setModelPopoverOpen(false)}
            onOpenCopilot={() => openCopilot()}
          />
        </div>
      </div>
    </header>
  );
}
