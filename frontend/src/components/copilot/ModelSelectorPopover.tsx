'use client';

import React, { useRef, useEffect } from 'react';
import Link from 'next/link';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { 
  Sparkles, 
  Cpu, 
  Server, 
  Globe, 
  Check, 
  ExternalLink, 
  ChevronRight, 
  X,
  Zap,
  RotateCw
} from 'lucide-react';

interface ModelOption {
  id: string;
  name: string;
  category: 'cloud' | 'local';
  badge: string;
  rpm?: string;
  rpd?: string;
}

const AVAILABLE_MODELS: ModelOption[] = [
  {
    id: 'gemini-3.5-flash',
    name: 'Google Gemini 3.5 Flash',
    category: 'cloud',
    badge: '100% Free • Recommended',
    rpm: '15 RPM',
    rpd: '1,500 RPD'
  },
  {
    id: 'gemini-3.1-flash-lite',
    name: 'Google Gemini 3.1 Flash-Lite',
    category: 'cloud',
    badge: 'Highest RPM (30 RPM)',
    rpm: '30 RPM',
    rpd: '1,500 RPD'
  },
  {
    id: 'gemini-3.5-flash-lite',
    name: 'Google Gemini 3.5 Flash-Lite',
    category: 'cloud',
    badge: 'Latest Free Lite',
    rpm: '15 RPM',
    rpd: '1,500 RPD'
  },
  {
    id: 'llama3:latest',
    name: 'Ollama Llama 3 (8B)',
    category: 'local',
    badge: 'Local • Air-Gapped Port 11434'
  }
];

interface ModelSelectorPopoverProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenCopilot: () => void;
}

export function ModelSelectorPopover({ isOpen, onClose, onOpenCopilot }: ModelSelectorPopoverProps) {
  const queryClient = useQueryClient();
  const popoverRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (popoverRef.current && !popoverRef.current.contains(e.target as Node)) {
        onClose();
      }
    }
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, onClose]);

  // Fetch status
  const { data: statusData, isLoading } = useQuery({
    queryKey: ['ai_model_status'],
    queryFn: async () => {
      const res = await apiClient.get('/ai/status');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // Switch Model Mutation
  const modelMutation = useMutation({
    mutationFn: async (model: string) => {
      const res = await apiClient.post('/ai/config/model', { model });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai_model_status'] });
    }
  });

  // Switch Router Mode Mutation
  const modeMutation = useMutation({
    mutationFn: async (mode: string) => {
      const res = await apiClient.post('/ai/config/mode', { mode });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['ai_model_status'] });
    }
  });

  if (!isOpen) return null;

  const activeBackend = statusData?.active_backend || 'ollama_local';
  const routerMode = statusData?.router_mode || 'auto';
  const currentGeminiModel = statusData?.gemini_cloud?.model || 'gemini-3.5-flash';
  const currentOllamaModel = statusData?.ollama_local?.model || 'llama3';

  const isModelSelected = (m: ModelOption) => {
    if (m.category === 'cloud') {
      return activeBackend === 'gemini_cloud' && currentGeminiModel === m.id;
    }
    return activeBackend === 'ollama_local';
  };

  const handleSelectModel = (m: ModelOption) => {
    if (m.category === 'cloud') {
      modelMutation.mutate(m.id);
      if (routerMode === 'ollama') {
        modeMutation.mutate('gemini');
      }
    } else {
      modeMutation.mutate('ollama');
    }
  };

  return (
    <div
      ref={popoverRef}
      className="absolute right-0 top-12 z-50 w-96 bg-white border-2 border-zinc-950 shadow-2xl p-4 font-mono select-none animate-in fade-in zoom-in-95 duration-100"
    >
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b-2 border-zinc-950">
        <div className="flex items-center gap-2">
          <div className="w-6 h-6 bg-red-600 text-white flex items-center justify-center font-bold">
            <Cpu className="w-3.5 h-3.5" />
          </div>
          <span className="text-xs font-black text-zinc-950 uppercase tracking-wider">
            // ACTIVE_AI_MODELS
          </span>
        </div>
        <button
          onClick={onClose}
          className="text-zinc-500 hover:text-zinc-950 font-bold p-1 transition-colors cursor-pointer"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Quick Launch Copilot */}
      <button
        onClick={() => {
          onClose();
          onOpenCopilot();
        }}
        className="w-full mt-3 p-2.5 bg-zinc-950 hover:bg-zinc-800 text-white border-2 border-zinc-950 flex items-center justify-between transition-all cursor-pointer shadow-xs group"
      >
        <span className="text-xs font-black uppercase flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-red-500 group-hover:rotate-12 transition-transform" />
          LAUNCH SPECTRA AI COPILOT
        </span>
        <ChevronRight className="w-4 h-4 text-zinc-400 group-hover:translate-x-0.5 transition-transform" />
      </button>

      {/* Available Models List */}
      <div className="mt-3.5 space-y-2">
        <span className="text-[10px] font-black text-zinc-500 uppercase tracking-wider block">
          SWITCH ACTIVE INFERENCE MODEL:
        </span>

        {AVAILABLE_MODELS.map((m) => {
          const selected = isModelSelected(m);
          return (
            <button
              key={m.id}
              onClick={() => handleSelectModel(m)}
              disabled={modelMutation.isPending || modeMutation.isPending}
              className={`w-full text-left p-2.5 border-2 transition-all cursor-pointer flex items-center justify-between ${
                selected
                  ? 'bg-zinc-100 border-zinc-950 shadow-xs'
                  : 'bg-white border-zinc-200 hover:border-zinc-950 hover:bg-zinc-50'
              }`}
            >
              <div className="truncate pr-2">
                <div className="flex items-center gap-1.5">
                  {m.category === 'cloud' ? (
                    <Globe className="w-3.5 h-3.5 text-zinc-700 shrink-0" />
                  ) : (
                    <Server className="w-3.5 h-3.5 text-zinc-700 shrink-0" />
                  )}
                  <span className="text-xs font-bold text-zinc-950 truncate">
                    {m.name}
                  </span>
                </div>
                <span className="text-[10px] font-medium text-zinc-500 block mt-0.5 truncate font-sans">
                  {m.badge}
                </span>
              </div>

              {selected ? (
                <div className="w-5 h-5 bg-zinc-950 text-white flex items-center justify-center shrink-0">
                  <Check className="w-3.5 h-3.5 text-red-500 stroke-[3]" />
                </div>
              ) : (
                <span className="text-[10px] font-bold text-zinc-400 uppercase">
                  SWITCH
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Footer link to full router */}
      <div className="mt-4 pt-3 border-t-2 border-zinc-950 flex items-center justify-between text-xs">
        <Link
          href="/ai-router"
          onClick={onClose}
          className="text-xs font-black uppercase text-zinc-950 hover:text-red-600 flex items-center gap-1.5 transition-colors"
        >
          <span>OPEN MODEL ROUTER</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </Link>
        <span className="text-[10px] font-mono text-zinc-500 uppercase">
          MODE: {routerMode.toUpperCase()}
        </span>
      </div>
    </div>
  );
}
