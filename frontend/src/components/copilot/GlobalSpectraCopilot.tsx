'use client';

import React, { useState } from 'react';
import { useCopilotStore } from '@/lib/store/copilot';
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import {
  Sparkles,
  X,
  Send,
  Trash2,
  ChevronRight,
  ShieldCheck,
  Cpu,
  Layers,
  Terminal,
  FileText
} from 'lucide-react';

export function GlobalSpectraCopilot() {
  const {
    isOpen,
    closeCopilot,
    messages,
    addMessage,
    clearMessages,
    suggestedQuestions,
    setSuggestedQuestions,
    activeContext
  } = useCopilotStore();

  const [inputPrompt, setInputPrompt] = useState('');

  // Fetch AI Router status for active badge
  const { data: aiStatus } = useQuery({
    queryKey: ['ai_model_status'],
    queryFn: async () => {
      const res = await apiClient.get('/ai/status');
      return res.data;
    },
    refetchInterval: 5000,
  });

  // AI Chat Mutation with automatic context injection
  const chatMutation = useMutation({
    mutationFn: async (queryText: string) => {
      let contextStr = '';
      if (activeContext) {
        contextStr = `Active Context: [${activeContext.title || 'Screen Item'}] (${activeContext.sourceType || 'telemetry'})\n${
          activeContext.summaryText || JSON.stringify(activeContext.data || {}, null, 2)
        }`;
      }

      const res = await apiClient.post('/ai/chat', {
        query: queryText,
        incident_context: contextStr || undefined
      });
      return res.data;
    },
    onSuccess: (data) => {
      addMessage({
        id: `ai-${Date.now()}`,
        sender: 'ai',
        text: data.reply,
        model: data.model
      });
      if (data.suggested_questions && data.suggested_questions.length > 0) {
        setSuggestedQuestions(data.suggested_questions);
      }
    },
    onError: () => {
      addMessage({
        id: `err-${Date.now()}`,
        sender: 'ai',
        text: 'Error communicating with SPECTRA-AI. Please check router status.',
        model: 'Error'
      });
    }
  });

  const handleSend = (e?: React.FormEvent, customQuery?: string) => {
    if (e) e.preventDefault();
    const q = (customQuery || inputPrompt).trim();
    if (!q || chatMutation.isPending) return;

    addMessage({
      id: `user-${Date.now()}`,
      sender: 'user',
      text: q
    });
    setInputPrompt('');
    chatMutation.mutate(q);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-white border-l-2 border-zinc-950 shadow-2xl flex flex-col font-mono animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="h-16 px-5 border-b-2 border-zinc-950 flex items-center justify-between bg-zinc-950 text-white">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-red-600 text-white flex items-center justify-center border border-white">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h2 className="text-xs font-black uppercase tracking-wider flex items-center gap-1.5 font-mono">
              <span>SPECTRA-AI GLOBAL COPILOT</span>
            </h2>
            <span className="text-[11px] font-mono text-zinc-300 font-bold block">
              {aiStatus?.active_backend === 'gemini_cloud'
                ? `⚡ ${aiStatus?.gemini_cloud?.model?.toUpperCase() || 'GEMINI 3.5 FLASH'} [CLOUD]`
                : aiStatus?.active_backend === 'ollama_local'
                ? '🔒 LOCAL OLLAMA LLAMA 3'
                : '🛡️ SOC RULE ENGINE'}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={clearMessages}
            title="Clear Chat History"
            className="p-1.5 text-zinc-400 hover:text-white transition-colors cursor-pointer"
          >
            <Trash2 className="w-4 h-4" />
          </button>
          <button
            onClick={closeCopilot}
            className="p-1.5 text-zinc-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Active Context Banner if injected */}
      {activeContext && (
        <div className="px-5 py-2.5 bg-zinc-100 border-b-2 border-zinc-950 flex items-center justify-between text-xs">
          <div className="truncate pr-2 font-mono">
            <span className="font-black text-zinc-950 block truncate uppercase">
              🎯 CONTEXT: {activeContext.title || 'Screen Item'}
            </span>
            <span className="text-[10px] text-zinc-600 block truncate font-bold">
              SOURCE: {activeContext.sourceType?.toUpperCase()}
            </span>
          </div>
          <span className="text-[10px] font-black text-white bg-zinc-950 border border-zinc-950 px-2 py-0.5 font-mono uppercase">
            ATTACHED
          </span>
        </div>
      )}

      {/* Messages Scroll Area */}
      <div className="flex-1 overflow-y-auto p-5 space-y-4 bg-zinc-50 font-mono">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`p-4 border-2 text-xs leading-relaxed ${
              m.sender === 'user'
                ? 'bg-zinc-950 text-white border-zinc-950 ml-6 shadow-xs font-bold'
                : 'bg-white border-zinc-950 text-zinc-950 mr-4 shadow-xs font-medium'
            }`}
          >
            <div className="whitespace-pre-wrap font-sans text-xs font-semibold">{m.text}</div>
            {m.model && m.sender === 'ai' && (
              <div className="text-[10px] text-zinc-500 mt-3 pt-2 border-t-2 border-zinc-200 font-mono flex items-center justify-between font-bold uppercase">
                <span>{m.model}</span>
                <span className="text-red-600 font-black">[VERIFIED]</span>
              </div>
            )}
          </div>
        ))}

        {chatMutation.isPending && (
          <div className="text-xs text-zinc-950 font-bold py-2.5 flex items-center gap-2 bg-white px-4 border-2 border-zinc-950 animate-pulse font-mono">
            <Sparkles className="w-4 h-4 text-red-600" />
            <span>SPECTRA-AI IS REASONING ON LIVE CONTEXT...</span>
          </div>
        )}
      </div>

      {/* Suggested Questions Section */}
      <div className="p-4 border-t-2 border-zinc-950 bg-white space-y-3 font-mono">
        <div className="flex items-center justify-between text-[11px] font-black text-zinc-950 uppercase tracking-wider">
          <span className="flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-red-600" />
            <span>// SUGGESTED_QUESTIONS:</span>
          </span>
          <span className="text-[10px] text-zinc-500 font-bold uppercase">CLICK TO SEND</span>
        </div>

        <div className="flex flex-wrap gap-2 max-h-[100px] overflow-y-auto">
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              type="button"
              disabled={chatMutation.isPending}
              onClick={() => handleSend(undefined, q)}
              className="text-left text-xs font-bold text-zinc-950 bg-white hover:bg-zinc-950 hover:text-white border-2 border-zinc-950 px-3 py-1.5 transition-all cursor-pointer disabled:opacity-50 flex items-center gap-1.5 uppercase"
            >
              <span className="text-red-600 font-black">↳</span>
              <span className="truncate max-w-[340px]">{q}</span>
            </button>
          ))}
        </div>

        {/* Query Input Bar */}
        <form onSubmit={(e) => handleSend(e)} className="flex gap-2 pt-1">
          <input
            type="text"
            value={inputPrompt}
            onChange={(e) => setInputPrompt(e.target.value)}
            placeholder="Ask SPECTRA-AI anything about this screen..."
            className="flex-1 h-10 px-3 text-xs font-mono font-bold text-zinc-950 bg-white border-2 border-zinc-950 placeholder-zinc-400 focus:outline-none focus:ring-0"
          />
          <button
            type="submit"
            disabled={chatMutation.isPending || !inputPrompt.trim()}
            className="px-4 h-10 bg-zinc-950 hover:bg-zinc-800 disabled:opacity-50 text-white text-xs font-black uppercase tracking-wider border-2 border-zinc-950 transition-all flex items-center gap-1.5 cursor-pointer shadow-xs"
          >
            <Send className="w-3.5 h-3.5 text-red-500" />
            <span>ASK</span>
          </button>
        </form>
      </div>
    </div>
  );
}
