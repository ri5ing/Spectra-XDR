'use client';

import React, { useState } from 'react';
import { useCopilotStore } from '@/lib/store/copilot';
import { Sparkles } from 'lucide-react';

interface AskSpectraButtonProps {
  title?: string;
  sourceType?: 'event' | 'alert' | 'agent' | 'mitre' | 'risk' | 'swarm' | 'database' | 'page';
  data?: any;
  summaryText?: string;
  variant?: 'button' | 'badge' | 'icon' | 'link';
  className?: string;
  label?: string;
}

export function AskSpectraButton({
  title,
  sourceType = 'event',
  data,
  summaryText,
  variant = 'button',
  className = '',
  label = 'Ask SPECTRA-AI'
}: AskSpectraButtonProps) {
  const { openCopilot } = useCopilotStore();

  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    openCopilot({
      title: title || 'Context Item',
      sourceType,
      data,
      summaryText: summaryText || (data ? JSON.stringify(data, null, 2) : undefined)
    });
  };

  if (variant === 'icon') {
    return (
      <button
        type="button"
        onClick={handleClick}
        title="Ask SPECTRA-AI about this item"
        className={`p-1 hover:bg-sky-50 text-sky-600 hover:text-sky-700 rounded transition-colors ${className}`}
      >
        <Sparkles className="w-3.5 h-3.5" />
      </button>
    );
  }

  if (variant === 'badge') {
    return (
      <button
        type="button"
        onClick={handleClick}
        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold bg-sky-50 text-sky-700 hover:bg-sky-100 border border-sky-200 transition-colors shadow-2xs ${className}`}
      >
        <Sparkles className="w-3 h-3 text-sky-600" />
        <span>{label}</span>
      </button>
    );
  }

  if (variant === 'link') {
    return (
      <button
        type="button"
        onClick={handleClick}
        className={`text-sky-600 hover:text-sky-800 text-xs font-semibold flex items-center gap-1 transition-colors ${className}`}
      >
        <Sparkles className="w-3 h-3" />
        <span>{label}</span>
      </button>
    );
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 bg-white hover:bg-sky-50 border border-slate-200 hover:border-sky-300 text-slate-700 hover:text-sky-800 rounded-md text-xs font-semibold transition-all shadow-2xs ${className}`}
    >
      <Sparkles className="w-3.5 h-3.5 text-sky-600" />
      <span>{label}</span>
    </button>
  );
}
