'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/lib/api/client';
import {
  Database,
  HardDrive,
  Layers,
  Server,
  RefreshCw,
  Plus,
  Trash2,
  Edit2,
  CheckCircle2,
  AlertTriangle,
  Key,
  Table as TableIcon,
  Search,
  ExternalLink,
  Save,
  X,
  FileCode,
  ShieldCheck,
  Activity
} from 'lucide-react';
import { formatTimestampIST } from '@/lib/time';
import { AskSpectraButton } from '@/components/copilot/AskSpectraButton';

export default function DatabaseHubPage() {
  const queryClient = useQueryClient();
  const [selectedTable, setSelectedTable] = useState<string>('system_api_keys');
  const [currentPage, setCurrentPage] = useState<number>(1);
  const [searchTableQuery, setSearchTableQuery] = useState<string>('');

  // Key Store form state
  const [keyService, setKeyService] = useState<string>('gemini');
  const [keyName, setKeyName] = useState<string>('');
  const [apiKeyVal, setApiKeyVal] = useState<string>('');
  const [keySuccess, setKeySuccess] = useState<string>('');
  const [keyError, setKeyError] = useState<string>('');

  // Edit record modal state
  const [editingRecord, setEditingRecord] = useState<any | null>(null);
  const [editFormData, setEditFormData] = useState<Record<string, any>>({});
  const [editStatusMsg, setEditStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // 1. Fetch DB Overview (Sizes, Table Counts, Indexer, Redis)
  const { data: dbOverview, isLoading: overviewLoading, refetch: refetchOverview, isRefetching } = useQuery({
    queryKey: ['db_overview'],
    queryFn: async () => {
      const res = await apiClient.get('/database/overview');
      return res.data;
    },
    refetchInterval: 10000,
  });

  // 2. Fetch Selected Table Rows & Columns
  const { data: tableData, isLoading: tableLoading, refetch: refetchTable } = useQuery({
    queryKey: ['db_table_data', selectedTable, currentPage],
    queryFn: async () => {
      const res = await apiClient.get(`/database/tables/${selectedTable}/data?page=${currentPage}&page_size=20`);
      return res.data;
    },
    refetchInterval: 15000,
  });

  // 3. Mutation to Store New API Key
  const storeKeyMutation = useMutation({
    mutationFn: async (payload: { service: string; name: string; api_key: string }) => {
      const res = await apiClient.post('/database/keys/store', payload);
      return res.data;
    },
    onSuccess: (data) => {
      setKeySuccess(data.message || 'Key safely stored in PostgreSQL.');
      setKeyError('');
      setKeyName('');
      setApiKeyVal('');
      queryClient.invalidateQueries({ queryKey: ['db_overview'] });
      queryClient.invalidateQueries({ queryKey: ['db_table_data', 'system_api_keys'] });
      queryClient.invalidateQueries({ queryKey: ['ai_model_status'] });
      setTimeout(() => setKeySuccess(''), 4000);
    },
    onError: (err: any) => {
      setKeyError(err.response?.data?.detail || 'Failed to persist API key.');
      setKeySuccess('');
    }
  });

  // 4. Mutation to Update Record
  const updateRecordMutation = useMutation({
    mutationFn: async (payload: { table_name: string; primary_key_column: string; primary_key_value: any; data: any }) => {
      const res = await apiClient.put('/database/records/update', payload);
      return res.data;
    },
    onSuccess: (data) => {
      setEditStatusMsg({ type: 'success', text: data.message });
      queryClient.invalidateQueries({ queryKey: ['db_table_data', selectedTable] });
      queryClient.invalidateQueries({ queryKey: ['db_overview'] });
      setTimeout(() => {
        setEditingRecord(null);
        setEditStatusMsg(null);
      }, 1500);
    },
    onError: (err: any) => {
      setEditStatusMsg({ type: 'error', text: err.response?.data?.detail || 'Failed to update record.' });
    }
  });

  // 5. Mutation to Delete Record
  const deleteRecordMutation = useMutation({
    mutationFn: async (payload: { table_name: string; primary_key_column: string; primary_key_value: any }) => {
      const res = await apiClient.delete('/database/records/delete', { data: payload });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['db_table_data', selectedTable] });
      queryClient.invalidateQueries({ queryKey: ['db_overview'] });
      queryClient.invalidateQueries({ queryKey: ['ai_model_status'] });
    }
  });

  const handleCreateKey = (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyName.trim() || !apiKeyVal.trim()) return;
    storeKeyMutation.mutate({
      service: keyService,
      name: keyName.trim(),
      api_key: apiKeyVal.trim()
    });
  };

  const handleStartEdit = (row: any) => {
    setEditingRecord(row);
    // clone data excluding primary key id if desired, or allow editing metadata
    const copy = { ...row };
    delete copy.id;
    delete copy.created_at;
    delete copy.updated_at;
    setEditFormData(copy);
    setEditStatusMsg(null);
  };

  const handleSaveEdit = () => {
    if (!editingRecord) return;
    const pkCol = 'id' in editingRecord ? 'id' : Object.keys(editingRecord)[0];
    const pkVal = editingRecord[pkCol];

    updateRecordMutation.mutate({
      table_name: selectedTable,
      primary_key_column: pkCol,
      primary_key_value: pkVal,
      data: editFormData
    });
  };

  const pg = dbOverview?.postgresql || {};
  const indexer = dbOverview?.wazuh_indexer || {};
  const redis = dbOverview?.redis_cache || {};

  const filteredTables = (pg.tables || []).filter((t: any) =>
    t.table_name.toLowerCase().includes(searchTableQuery.toLowerCase())
  );

  return (
    <div className="space-y-6 pb-16 font-mono">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-5 border-b-2 border-zinc-950 gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1.5 font-mono text-xs font-bold text-red-600 uppercase tracking-widest">
            <span>[MODULE 07]</span>
            <span>//</span>
            <span>DATASTORE_PERSISTENCE_ENGINE</span>
          </div>
          <h1 className="text-3xl font-black text-zinc-950 tracking-tight flex items-center gap-3">
            <div className="w-10 h-10 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950 shadow-xs">
              <Database className="w-5 h-5 text-red-500" />
            </div>
            <span>DATABASE STORAGE & KEY HUB</span>
          </h1>
          <p className="text-sm font-medium text-zinc-600 mt-1 font-sans">
            Real-time storage breakdown across PostgreSQL, Wazuh OpenSearch Indexer, Redis Cache & Live Table Data Manipulation
          </p>
        </div>

        <button
          onClick={() => {
            refetchOverview();
            refetchTable();
          }}
          disabled={isRefetching}
          className="flex items-center gap-2 px-4 py-2.5 bg-zinc-950 hover:bg-zinc-800 text-white text-xs font-bold font-mono uppercase border-2 border-zinc-950 transition-all cursor-pointer self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 text-red-500 ${isRefetching ? 'animate-spin' : ''}`} />
          <span>REFRESH_STATS</span>
        </button>
      </div>

      {/* 3-Engine Data Store Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* PostgreSQL Card */}
        <div className="bg-white border-2 border-zinc-950 p-4 shadow-xs">
          <div className="flex items-center justify-between pb-3 border-b-2 border-zinc-950">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950">
                <Database className="w-4 h-4 text-red-500" />
              </div>
              <div>
                <h3 className="text-xs font-black text-zinc-950 uppercase tracking-wider">PostgreSQL 16</h3>
                <p className="text-[10px] text-zinc-500 font-sans">Relational & State Store</p>
              </div>
            </div>
            <span className="text-xs font-black text-emerald-800 bg-emerald-50 border-2 border-zinc-950 px-2.5 py-0.5 uppercase tracking-wider">
              {pg.status || 'ONLINE'}
            </span>
          </div>

          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 bg-zinc-50 border-2 border-zinc-950">
              <span className="text-[10px] font-bold text-zinc-500 uppercase block tracking-wider">Total Disk Size</span>
              <span className="font-black text-zinc-950 text-base font-mono">{pg.total_size || '0 MB'}</span>
            </div>
            <div className="p-2.5 bg-zinc-50 border-2 border-zinc-950">
              <span className="text-[10px] font-bold text-zinc-500 uppercase block tracking-wider">Managed Tables</span>
              <span className="font-black text-zinc-950 text-base font-mono">{pg.tables_count || 0} Tables</span>
            </div>
          </div>
          <div className="mt-2.5 text-[11px] text-zinc-600 font-sans">
            Stores: Incidents, Alerts, MITRE mappings, Audit logs, Swarm memories & System API Keys.
          </div>
        </div>

        {/* Wazuh OpenSearch Indexer Card */}
        <div className="bg-white border-2 border-zinc-950 p-4 shadow-xs">
          <div className="flex items-center justify-between pb-3 border-b-2 border-zinc-950">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950">
                <HardDrive className="w-4 h-4 text-red-500" />
              </div>
              <div>
                <h3 className="text-xs font-black text-zinc-950 uppercase tracking-wider">Wazuh OpenSearch Indexer</h3>
                <p className="text-[10px] text-zinc-500 font-sans">High-Speed Log Engine (Port 9200)</p>
              </div>
            </div>
            <span className="text-xs font-black text-emerald-800 bg-emerald-50 border-2 border-zinc-950 px-2.5 py-0.5 uppercase tracking-wider">
              {indexer.status || 'ONLINE'}
            </span>
          </div>

          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 bg-zinc-50 border-2 border-zinc-950">
              <span className="text-[10px] font-bold text-zinc-500 uppercase block tracking-wider">Total Indexed Size</span>
              <span className="font-black text-zinc-950 text-base font-mono">{indexer.total_store_size || '0 KB'}</span>
            </div>
            <div className="p-2.5 bg-zinc-50 border-2 border-zinc-950">
              <span className="text-[10px] font-bold text-zinc-500 uppercase block tracking-wider">Indexed Docs</span>
              <span className="font-black text-zinc-950 text-base font-mono">{indexer.total_docs || 0} Docs</span>
            </div>
          </div>
          <div className="mt-2.5 text-[11px] text-zinc-600 font-sans">
            Stores: Endpoint EDR streaming logs, Sysmon events, Wazuh raw security indices.
          </div>
        </div>

        {/* Redis Cache Card */}
        <div className="bg-white border-2 border-zinc-950 p-4 shadow-xs">
          <div className="flex items-center justify-between pb-3 border-b-2 border-zinc-950">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-zinc-950 text-white flex items-center justify-center border-2 border-zinc-950">
                <Server className="w-4 h-4 text-red-500" />
              </div>
              <div>
                <h3 className="text-xs font-black text-zinc-950 uppercase tracking-wider">Redis 7 Cache</h3>
                <p className="text-[10px] text-zinc-500 font-sans">In-Memory Broker (Port 6379)</p>
              </div>
            </div>
            <span className="text-xs font-black text-emerald-800 bg-emerald-50 border-2 border-zinc-950 px-2.5 py-0.5 uppercase tracking-wider">
              {redis.status || 'ONLINE'}
            </span>
          </div>

          <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
            <div className="p-2.5 bg-zinc-50 border-2 border-zinc-950">
              <span className="text-[10px] font-bold text-zinc-500 uppercase block tracking-wider">Memory Used</span>
              <span className="font-black text-zinc-950 text-base font-mono">{redis.used_memory_human || '988 KB'}</span>
            </div>
            <div className="p-2.5 bg-zinc-50 border-2 border-zinc-950">
              <span className="text-[10px] font-bold text-zinc-500 uppercase block tracking-wider">Peak Resident</span>
              <span className="font-black text-zinc-950 text-base font-mono">{redis.peak_memory_human || '1.0 MB'}</span>
            </div>
          </div>
          <div className="mt-2.5 text-[11px] text-zinc-600 font-sans">
            Stores: Real-time telemetry buffering queue, active agent heartbeat state & broker queue.
          </div>
        </div>
      </div>

      {/* API Key Vault Persisted in PostgreSQL */}
      <div className="bg-white border-2 border-zinc-950 p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b-2 border-zinc-950 gap-2">
          <div>
            <h2 className="text-sm font-black text-zinc-950 uppercase tracking-wider flex items-center gap-2">
              <Key className="w-4 h-4 text-red-600" />
              <span>// DATABASE-BACKED_API_KEY_VAULT [system_api_keys]</span>
            </h2>
            <p className="text-xs text-zinc-600 font-sans mt-0.5">
              Persist Gemini API keys, Wazuh credentials, or Threat Intel tokens directly into the PostgreSQL database table.
            </p>
          </div>
          <span className="text-xs font-black text-zinc-950 bg-zinc-100 border-2 border-zinc-950 px-3 py-1 uppercase tracking-wider">
            Auto-Syncs with Model Router
          </span>
        </div>

        <form onSubmit={handleCreateKey} className="grid grid-cols-1 sm:grid-cols-12 gap-3 mt-4">
          <div className="sm:col-span-2">
            <label className="text-xs font-black text-zinc-950 uppercase block mb-1">SERVICE</label>
            <select
              value={keyService}
              onChange={(e) => setKeyService(e.target.value)}
              className="w-full h-10 px-3 text-xs font-black uppercase text-zinc-950 bg-white border-2 border-zinc-950 shadow-xs focus:ring-0 focus:outline-none cursor-pointer"
            >
              <option value="gemini">Google Gemini</option>
              <option value="virustotal">VirusTotal</option>
              <option value="abuseipdb">AbuseIPDB</option>
              <option value="custom">Custom API</option>
            </select>
          </div>
          <div className="sm:col-span-3">
            <label className="text-xs font-black text-zinc-950 uppercase block mb-1">KEY LABEL</label>
            <input
              type="text"
              value={keyName}
              onChange={(e) => setKeyName(e.target.value)}
              placeholder="e.g. Om-1 Primary, Backup Key"
              className="w-full h-10 px-3 text-xs font-mono font-bold text-zinc-950 bg-white border-2 border-zinc-950 placeholder-zinc-400 focus:outline-none focus:ring-0"
              required
            />
          </div>
          <div className="sm:col-span-5">
            <label className="text-xs font-black text-zinc-950 uppercase block mb-1">API KEY SECRET</label>
            <input
              type="password"
              value={apiKeyVal}
              onChange={(e) => setApiKeyVal(e.target.value)}
              placeholder="Paste Plaintext Secret Key (AIzaSy...)"
              className="w-full h-10 px-3 text-xs font-mono font-bold text-zinc-950 bg-white border-2 border-zinc-950 placeholder-zinc-400 focus:outline-none focus:ring-0"
              required
            />
          </div>
          <div className="sm:col-span-2 flex items-end">
            <button
              type="submit"
              disabled={storeKeyMutation.isPending || !apiKeyVal.trim()}
              className="w-full h-10 bg-zinc-950 hover:bg-zinc-800 disabled:opacity-50 text-white text-xs font-black uppercase tracking-wider transition-all border-2 border-zinc-950 flex items-center justify-center gap-1.5 cursor-pointer shadow-xs"
            >
              <Plus className="w-4 h-4 text-red-500" />
              <span>{storeKeyMutation.isPending ? 'SAVING...' : '+ SAVE TO DB'}</span>
            </button>
          </div>
        </form>

        {keySuccess && (
          <div className="mt-4 p-3 bg-emerald-50 border-2 border-zinc-950 text-emerald-950 text-xs font-bold flex items-center gap-2 font-mono">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            <span>{keySuccess}</span>
          </div>
        )}

        {keyError && (
          <div className="mt-4 p-3 bg-red-50 border-2 border-zinc-950 text-red-950 text-xs font-bold flex items-center gap-2 font-mono">
            <AlertTriangle className="w-4 h-4 text-red-600 flex-shrink-0" />
            <span>{keyError}</span>
          </div>
        )}
      </div>

      {/* Main Table Explorer & Data Manipulation Studio */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Table Directory / Navigator (3 Cols) */}
        <div className="lg:col-span-3 bg-white border-2 border-zinc-950 p-4 shadow-xs space-y-3">
          <div className="flex items-center justify-between pb-3 border-b-2 border-zinc-950">
            <span className="text-xs font-black text-zinc-950 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-red-600" />
              <span>DATABASE TABLES</span>
            </span>
            <span className="text-xs font-mono font-bold text-zinc-950 bg-zinc-100 border-2 border-zinc-950 px-2 py-0.5">
              {filteredTables.length} TABLES
            </span>
          </div>

          <div className="relative">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3 top-3" />
            <input
              type="text"
              value={searchTableQuery}
              onChange={(e) => setSearchTableQuery(e.target.value)}
              placeholder="Filter table name..."
              className="w-full h-10 pl-9 pr-3 text-xs font-mono font-bold text-zinc-950 bg-white border-2 border-zinc-950 placeholder-zinc-400 focus:outline-none focus:ring-0"
            />
          </div>

          <div className="space-y-1.5 max-h-[500px] overflow-y-auto pr-1">
            {filteredTables.map((t: any) => {
              const isSelected = selectedTable === t.table_name;
              return (
                <button
                  key={t.table_name}
                  onClick={() => {
                    setSelectedTable(t.table_name);
                    setCurrentPage(1);
                  }}
                  className={`w-full text-left px-3 py-2.5 text-xs font-bold transition-all flex items-center justify-between border-2 cursor-pointer ${
                    isSelected
                      ? 'bg-zinc-950 text-white border-zinc-950 shadow-xs'
                      : 'hover:bg-zinc-100 text-zinc-900 border-zinc-200 bg-white'
                  }`}
                >
                  <div className="truncate pr-2">
                    <span className="font-mono">{t.table_name}</span>
                    <span className={`text-[10px] block font-normal ${isSelected ? 'text-zinc-400' : 'text-zinc-500'}`}>
                      {t.size}
                    </span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 border font-bold ${
                    isSelected ? 'bg-red-600 text-white border-red-600' : 'bg-zinc-100 text-zinc-800 border-zinc-300'
                  }`}>
                    {t.row_count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Right: Data View, Live Manipulation & Records Table (9 Cols) */}
        <div className="lg:col-span-9 bg-white border-2 border-zinc-950 p-4 shadow-xs space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b-2 border-zinc-950 gap-2">
            <div>
              <div className="flex items-center gap-2 flex-wrap">
                <TableIcon className="w-4 h-4 text-red-600" />
                <h3 className="text-sm font-black text-zinc-950 font-mono uppercase tracking-wider">
                  {selectedTable}
                </h3>
                <span className="text-xs font-black text-white bg-zinc-950 border-2 border-zinc-950 px-2.5 py-0.5 font-mono">
                  {tableData?.total_rows || 0} TOTAL ROWS
                </span>
                <AskSpectraButton
                  title={`Database Table: ${selectedTable}`}
                  sourceType="database"
                  data={{ table: selectedTable, total_rows: tableData?.total_rows, columns: tableData?.columns }}
                  summaryText={`Database Table: ${selectedTable}\nTotal Rows: ${tableData?.total_rows || 0}\nColumns: ${(tableData?.columns || []).join(', ')}`}
                  variant="badge"
                  label="ASK AI ABOUT TABLE"
                />
              </div>
              <p className="text-xs text-zinc-500 mt-1 font-sans">
                Showing Page {currentPage} of {Math.ceil((tableData?.total_rows || 1) / 20)} • Safe CRUD Operations Enabled
              </p>
            </div>

            {/* Pagination Controls */}
            <div className="flex items-center gap-2 self-start sm:self-auto font-mono">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage <= 1 || tableLoading}
                className="px-3 py-1.5 bg-white border-2 border-zinc-950 hover:bg-zinc-950 hover:text-white disabled:opacity-40 text-zinc-950 text-xs font-bold uppercase transition-all cursor-pointer"
              >
                PREVIOUS
              </button>
              <span className="text-xs font-mono text-zinc-950 font-black px-2">
                {currentPage}
              </span>
              <button
                onClick={() => setCurrentPage((p) => p + 1)}
                disabled={(currentPage * 20) >= (tableData?.total_rows || 0) || tableLoading}
                className="px-3 py-1.5 bg-white border-2 border-zinc-950 hover:bg-zinc-950 hover:text-white disabled:opacity-40 text-zinc-950 text-xs font-bold uppercase transition-all cursor-pointer"
              >
                NEXT
              </button>
            </div>
          </div>

          {/* Table Data Grid */}
          <div className="overflow-x-auto border-2 border-zinc-950 max-h-[550px] overflow-y-auto">
            {tableLoading ? (
              <div className="p-8 text-center text-xs font-bold uppercase text-zinc-400">
                Loading table data from PostgreSQL...
              </div>
            ) : !tableData?.rows || tableData.rows.length === 0 ? (
              <div className="p-8 text-center text-xs font-bold text-zinc-600">
                No records currently stored in <span className="font-mono font-black text-zinc-950">{selectedTable}</span>.
              </div>
            ) : (
              <table className="w-full text-left text-xs border-collapse font-mono">
                <thead className="bg-zinc-950 text-white text-xs font-extrabold uppercase tracking-wider sticky top-0 z-10 border-b-2 border-zinc-950">
                  <tr>
                    <th className="px-3 py-3 text-center w-20">ACTIONS</th>
                    {tableData.columns.map((col: string) => (
                      <th key={col} className="px-3 py-3 font-mono whitespace-nowrap">
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y-2 divide-zinc-950 font-mono text-xs bg-white text-zinc-900">
                  {tableData.rows.map((row: any, idx: number) => {
                    const pkCol = 'id' in row ? 'id' : tableData.columns[0];
                    const pkVal = row[pkCol];

                    return (
                      <tr key={idx} className="hover:bg-zinc-50 transition-colors">
                        {/* Action buttons (Edit & Delete) */}
                        <td className="px-2 py-3 text-center whitespace-nowrap">
                          <div className="flex items-center justify-center gap-1.5">
                            <button
                              onClick={() => handleStartEdit(row)}
                              className="p-1.5 bg-white hover:bg-zinc-950 hover:text-white border-2 border-zinc-950 text-zinc-700 transition-all cursor-pointer"
                              title="Edit Record Values"
                            >
                              <Edit2 className="w-3.5 h-3.5" />
                            </button>
                            <button
                              onClick={() => {
                                if (window.confirm(`Are you sure you want to delete row ${pkCol}='${pkVal}'?`)) {
                                  deleteRecordMutation.mutate({
                                    table_name: selectedTable,
                                    primary_key_column: pkCol,
                                    primary_key_value: pkVal
                                  });
                                }
                              }}
                              className="p-1.5 bg-white hover:bg-red-600 hover:text-white border-2 border-zinc-950 text-zinc-700 transition-all cursor-pointer"
                              title="Delete Record"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </td>

                        {/* Cell Values */}
                        {tableData.columns.map((col: string) => {
                          const val = row[col];
                          const isKeyCol = col.includes('key') || col.includes('secret');
                          
                          let displayVal = val;
                          if (val === null || val === undefined) {
                            displayVal = <span className="text-zinc-400 italic">null</span>;
                          } else if (typeof val === 'boolean') {
                            displayVal = val ? (
                              <span className="text-emerald-800 bg-emerald-50 border border-zinc-950 px-2 py-0.5 font-bold uppercase">true</span>
                            ) : (
                              <span className="text-red-800 bg-red-50 border border-zinc-950 px-2 py-0.5 font-bold uppercase">false</span>
                            );
                          } else if (typeof val === 'object') {
                            displayVal = (
                              <span className="truncate max-w-xs block font-mono text-[11px] text-zinc-700">
                                {JSON.stringify(val)}
                              </span>
                            );
                          } else if (isKeyCol && typeof val === 'string' && val.length > 8) {
                            displayVal = `${val.substring(0, 4)}...${val.substring(val.length - 4)}`;
                          } else if (typeof val === 'string' && val.length > 50) {
                            displayVal = `${val.substring(0, 50)}...`;
                          }

                          return (
                            <td key={col} className="px-3 py-3 text-zinc-900 font-bold whitespace-nowrap">
                              {displayVal}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {/* Edit Record Slide-Over / Modal */}
      {editingRecord && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white border-2 border-zinc-950 shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[85vh]">
            <div className="px-5 py-4 border-b-2 border-zinc-950 flex items-center justify-between bg-zinc-950 text-white">
              <div className="flex items-center gap-2">
                <Edit2 className="w-4 h-4 text-red-500" />
                <h3 className="text-xs font-black uppercase tracking-wider font-mono">
                  EDIT RECORD IN <span className="text-red-500 font-mono">[{selectedTable}]</span>
                </h3>
              </div>
              <button
                onClick={() => setEditingRecord(null)}
                className="p-1 text-zinc-400 hover:text-white transition-colors cursor-pointer"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="p-5 space-y-3 overflow-y-auto flex-1 text-xs font-mono">
              {Object.keys(editFormData).map((field) => {
                const val = editFormData[field];
                const isBool = typeof val === 'boolean';

                return (
                  <div key={field} className="space-y-1">
                    <label className="text-xs font-black text-zinc-950 uppercase block">
                      {field}
                    </label>

                    {isBool ? (
                      <select
                        value={val ? 'true' : 'false'}
                        onChange={(e) => setEditFormData({ ...editFormData, [field]: e.target.value === 'true' })}
                        className="w-full h-10 px-3 text-xs font-mono font-bold text-zinc-950 bg-white border-2 border-zinc-950 focus:outline-none"
                      >
                        <option value="true">true</option>
                        <option value="false">false</option>
                      </select>
                    ) : (
                      <input
                        type="text"
                        value={typeof val === 'object' ? JSON.stringify(val) : (val ?? '')}
                        onChange={(e) => {
                          let finalVal: any = e.target.value;
                          try {
                            if (finalVal.startsWith('{') || finalVal.startsWith('[')) {
                              finalVal = JSON.parse(finalVal);
                            }
                          } catch (_) {}
                          setEditFormData({ ...editFormData, [field]: finalVal });
                        }}
                        className="w-full h-10 px-3 text-xs font-mono font-bold text-zinc-950 bg-white border-2 border-zinc-950 focus:outline-none"
                      />
                    )}
                  </div>
                );
              })}

              {editStatusMsg && (
                <div
                  className={`p-3 border-2 border-zinc-950 text-xs font-bold flex items-center gap-2 ${
                    editStatusMsg.type === 'success'
                      ? 'bg-emerald-50 text-emerald-950'
                      : 'bg-red-50 text-red-950'
                  }`}
                >
                  {editStatusMsg.type === 'success' ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  ) : (
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                  )}
                  <span>{editStatusMsg.text}</span>
                </div>
              )}
            </div>

            <div className="px-5 py-3.5 border-t-2 border-zinc-950 bg-zinc-50 flex items-center justify-end gap-2 font-mono">
              <button
                type="button"
                onClick={() => setEditingRecord(null)}
                className="px-4 py-2 bg-white border-2 border-zinc-950 hover:bg-zinc-100 text-zinc-950 text-xs font-bold uppercase transition-all cursor-pointer"
              >
                CANCEL
              </button>
              <button
                type="button"
                onClick={handleSaveEdit}
                disabled={updateRecordMutation.isPending}
                className="px-4 py-2 bg-zinc-950 hover:bg-zinc-800 disabled:opacity-50 text-white text-xs font-black uppercase tracking-wider transition-all border-2 border-zinc-950 flex items-center gap-1.5 cursor-pointer"
              >
                <Save className="w-4 h-4 text-red-500" />
                <span>{updateRecordMutation.isPending ? 'SAVING...' : 'SAVE CHANGES'}</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
