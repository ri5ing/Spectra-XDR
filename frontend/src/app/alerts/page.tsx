'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import { AlertTriangle, ShieldAlert, Filter, Search, RefreshCw, Zap } from 'lucide-react';
import { useState } from 'react';
import { formatTimestampIST } from '@/lib/time';
import { useSearchStore } from '@/lib/store/search';
import { AskSpectraButton } from '@/components/copilot/AskSpectraButton';

export default function AlertsPage() {
  const { globalQuery, setGlobalQuery } = useSearchStore();

  const { data: events = [], isLoading, refetch, isRefetching } = useQuery({
    queryKey: ['alerts_correlation'],
    queryFn: async () => {
      const res = await apiClient.get('/events?limit=50');
      return res.data;
    },
    refetchInterval: 5000,
  });

  const filteredEvents = events.filter((e: any) => {
    if (!globalQuery.trim()) return true;
    const term = globalQuery.toLowerCase();
    return (
      e.agent_name?.toLowerCase().includes(term) ||
      e.rule_description?.toLowerCase().includes(term) ||
      e.raw_event?.description?.toLowerCase().includes(term) ||
      e.source?.toLowerCase().includes(term) ||
      e.rule_id?.toLowerCase().includes(term) ||
      e.agent_ip?.toLowerCase().includes(term)
    );
  });

  return (
    <div className="space-y-6 pb-16">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b-2 border-zinc-950 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 font-mono text-xs font-bold text-red-600 uppercase tracking-widest">
            <span>[MODULE 03]</span>
            <span>//</span>
            <span>CORRELATED_TELEMETRY_ENGINE</span>
          </div>
          <h1 className="text-3xl font-black text-zinc-950 tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950 shadow-xs">
              <AlertTriangle className="w-5 h-5 text-red-500" />
            </div>
            <span>ALERTS & TELEMETRY STREAM</span>
          </h1>
          <p className="text-sm font-medium text-zinc-600 mt-1">
            Real-time correlated telemetry events and detection alerts from Windows & Linux endpoints
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => refetch()}
            disabled={isRefetching}
            className="flex items-center gap-2 px-4 py-2.5 bg-zinc-950 text-white hover:bg-zinc-800 text-xs font-bold font-mono uppercase border border-zinc-950 transition-all cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefetching ? 'animate-spin text-red-400' : ''}`} />
            <span>FORCE_SYNC</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="swiss-card p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-zinc-400" />
          <input
            type="text"
            placeholder="FILTER: RULE, AGENT, DESCRIPTION, RULE ID, IP..."
            value={globalQuery}
            onChange={(e) => setGlobalQuery(e.target.value)}
            className="w-full h-10 border border-zinc-300 bg-white pl-10 pr-4 text-xs font-mono text-zinc-900 placeholder:text-zinc-400 focus:outline-none focus:border-zinc-950"
          />
        </div>
        <div className="flex items-center gap-3 w-full sm:w-auto font-mono text-xs">
          <span className="text-zinc-500 uppercase font-semibold">MATCHED_EVENTS:</span>
          <span className="px-3 py-1 bg-zinc-950 text-white font-bold">
            {filteredEvents.length}
          </span>
        </div>
      </div>

      {/* Events Table Container */}
      <div className="swiss-card overflow-hidden">
        <div className="px-4 py-2.5 bg-zinc-100 border-b border-zinc-200 flex items-center justify-between">
          <span className="text-xs font-mono font-bold text-zinc-800 uppercase tracking-wider">
            // TELEMETRY_INGESTION_LOGS
          </span>
          <span className="text-[11px] font-mono text-zinc-500">
            AUTO_POLL: 5000MS
          </span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-zinc-50 text-zinc-900 font-bold border-b border-zinc-300 uppercase tracking-wider text-[11px]">
              <tr>
                <th className="px-5 py-3">SEVERITY</th>
                <th className="px-5 py-3">TIMESTAMP (IST)</th>
                <th className="px-5 py-3">ENDPOINT / HOST</th>
                <th className="px-5 py-3 font-sans">RULE & EVENT SPECIFICATION</th>
                <th className="px-5 py-3">SOURCE</th>
                <th className="px-5 py-3 text-right">RULE ID</th>
                <th className="px-4 py-3 text-center">COPILOT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-200 text-zinc-800">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-zinc-500 font-bold">
                    STREAMING ALERTS AND TELEMETRY...
                  </td>
                </tr>
              ) : filteredEvents.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-10 text-center text-zinc-500 font-bold">
                    NO MATCHING SECURITY TELEMETRY FOUND.
                  </td>
                </tr>
              ) : (
                filteredEvents.map((ev: any) => {
                  const level = Number(ev.rule_level || ev.level || 3);
                  const isCritical = level >= 12;
                  const isHigh = level >= 8 && level < 12;
                  const isMed = level >= 4 && level < 8;

                  return (
                    <tr key={ev.id || Math.random()} className="hover:bg-zinc-50 transition-colors">
                      <td className="px-5 py-3.5">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 text-[11px] font-black border ${
                            isCritical
                              ? 'bg-red-50 text-red-700 border-red-300'
                              : isHigh
                              ? 'bg-amber-50 text-amber-800 border-amber-300'
                              : isMed
                              ? 'bg-blue-50 text-blue-800 border-blue-300'
                              : 'bg-zinc-100 text-zinc-800 border-zinc-300'
                          }`}
                        >
                          LVL_{level}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-zinc-600 text-[11px] whitespace-nowrap">
                        {formatTimestampIST(ev.timestamp)}
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="font-bold text-zinc-950 font-sans text-xs">
                          {ev.agent_name || ev.agent_id || 'Endpoint'}
                        </div>
                        {ev.agent_ip && (
                          <div className="text-[10px] text-zinc-400 font-mono">{ev.agent_ip}</div>
                        )}
                      </td>
                      <td className="px-5 py-3.5">
                        <div className="font-semibold text-zinc-950 font-sans text-xs">
                          {ev.rule_description || ev.raw_event?.description || 'Security Event Detected'}
                        </div>
                      </td>
                      <td className="px-5 py-3.5">
                        <span className="px-2 py-0.5 bg-zinc-100 border border-zinc-300 text-zinc-700 text-[10px] uppercase font-bold">
                          {ev.source || 'Wazuh EDR'}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-right text-red-600 text-xs font-bold">
                        #{ev.rule_id || '0000'}
                      </td>
                      <td className="px-4 py-3.5 text-center">
                        <AskSpectraButton
                          title={`Alert #${ev.rule_id}: ${ev.rule_description}`}
                          sourceType="alert"
                          data={ev}
                          summaryText={`Alert Rule ID: ${ev.rule_id}\nDescription: ${ev.rule_description}\nSeverity: Level ${ev.rule_level}\nHost: ${ev.agent_name || 'Lazasus'} (${ev.agent_ip || 'Local'})`}
                          variant="badge"
                          label="Ask AI"
                        />
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
