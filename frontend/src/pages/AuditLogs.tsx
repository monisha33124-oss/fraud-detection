import React, { useState, useEffect } from 'react';
import { Clock, User, Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react';
import client from '../api/client';

export default function AuditLogs() {
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  // Pagination
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 50;

  useEffect(() => {
    fetchLogs();
  }, [page]);

  const fetchLogs = async (searchQuery = search) => {
    try {
      setLoading(true);
      let url = `/api/v1/audit/?page=${page}&page_size=${pageSize}`;
      if (searchQuery) {
        url += `&action=${searchQuery}`;
      }
      const res = await client.get(url);
      setLogs(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error("Failed to fetch audit logs", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setSearch(val);
    setPage(1); // Reset page
  };

  const executeSearch = () => {
    fetchLogs();
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <div className="space-y-6 animate-in fade-in duration-500 h-full flex flex-col">
      <div className="flex flex-col sm:flex-row justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Audit Logs</h1>
          <p className="text-gray-500 mt-1">System-wide security and access history.</p>
        </div>
        
        <div className="flex gap-3 items-center">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search by action..." 
              value={search}
              onChange={handleSearch}
              onKeyDown={(e) => e.key === 'Enter' && executeSearch()}
              className="pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 w-full sm:w-64 transition-all"
            />
          </div>
          <button onClick={executeSearch} className="px-4 py-2 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors shadow-sm font-medium text-sm">
            Search
          </button>
        </div>
      </div>

      <div className="card-glass overflow-hidden flex-1 flex flex-col">
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-gray-500 uppercase bg-gray-50 border-b border-gray-100 sticky top-0">
              <tr>
                <th className="px-6 py-4 font-bold">Timestamp</th>
                <th className="px-6 py-4 font-bold">User / Role</th>
                <th className="px-6 py-4 font-bold">Action</th>
                <th className="px-6 py-4 font-bold">Resource</th>
                <th className="px-6 py-4 font-bold">Status</th>
                <th className="px-6 py-4 font-bold">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">Loading audit logs...</td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">No logs found.</td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-3 whitespace-nowrap text-gray-600">
                      <div className="flex items-center gap-2">
                        <Clock size={14} className="text-gray-400" />
                        {new Date(log.timestamp).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-3">
                      <div className="flex flex-col">
                        <span className="font-medium text-gray-900">{log.user_id ? log.user_id.substring(0,8) + '...' : 'System'}</span>
                        {log.role && <span className="text-[10px] uppercase font-bold text-indigo-600">{log.role}</span>}
                      </div>
                    </td>
                    <td className="px-6 py-3 font-medium text-gray-900">
                      {log.action}
                    </td>
                    <td className="px-6 py-3 text-gray-500 text-xs">
                      {log.resource || '-'}
                    </td>
                    <td className="px-6 py-3">
                      <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        log.status === 'SUCCESS' ? 'bg-emerald-100 text-emerald-700' :
                        (log.status === 'FAILED' || log.status === 'FAILURE') ? 'bg-red-100 text-red-700' :
                        log.status === 'LOCKED' ? 'bg-orange-100 text-orange-700' :
                        'bg-gray-100 text-gray-700'
                      }`}>
                        {log.status || 'INFO'}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-gray-500 font-mono text-xs">
                      {log.ip_address || '127.0.0.1'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
        
        {/* Pagination Footer */}
        <div className="bg-gray-50 border-t border-gray-100 px-6 py-3 flex items-center justify-between">
          <span className="text-sm text-gray-500">
            Showing <span className="font-medium text-gray-900">{logs.length > 0 ? (page - 1) * pageSize + 1 : 0}</span> to <span className="font-medium text-gray-900">{Math.min(page * pageSize, total)}</span> of <span className="font-medium text-gray-900">{total}</span> results
          </span>
          
          <div className="flex gap-2">
            <button 
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1 || loading}
              className="p-1 rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronLeft size={20} />
            </button>
            <button 
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page >= totalPages || loading}
              className="p-1 rounded-lg border border-gray-200 bg-white text-gray-600 hover:bg-gray-50 disabled:opacity-50"
            >
              <ChevronRight size={20} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
