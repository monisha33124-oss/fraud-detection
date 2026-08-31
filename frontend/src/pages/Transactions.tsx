import React, { useState, useEffect } from 'react';
import { Search, Filter, AlertTriangle, ShieldCheck, CreditCard, ChevronDown, ChevronUp, Activity, ChevronLeft, ChevronRight } from 'lucide-react';
import client from '../api/client';

export default function Transactions() {
  const [searchTerm, setSearchTerm] = useState('');
  const [transactions, setTransactions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const pageSize = 15;

  useEffect(() => {
    fetchTransactions();
  }, [page]);

  const fetchTransactions = async () => {
    try {
      setIsLoading(true);
      const res = await client.get(`/api/v1/transactions/?page=${page}&page_size=${pageSize}`);
      setTransactions(res.data.items || []);
      setTotalPages(res.data.pages || Math.ceil(res.data.total / pageSize) || 1);
    } catch (err) {
      console.error('Failed to fetch transactions', err);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredTransactions = transactions.filter(tx => 
    tx.transaction_id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (tx.customer_name && tx.customer_name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const toggleRow = (id: string) => {
    if (expandedRow === id) {
      setExpandedRow(null);
    } else {
      setExpandedRow(id);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Transactions</h1>
          <p className="text-gray-500 mt-1">Real-time feed of all transactions with ML risk analysis.</p>
        </div>
        
        <div className="flex gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input 
              type="text" 
              placeholder="Search transactions..." 
              className="pl-10 pr-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 w-64"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors">
            <Filter size={18} />
            Filter
          </button>
        </div>
      </div>

      <div className="card-glass overflow-hidden flex flex-col">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading transactions...</div>
        ) : filteredTransactions.length === 0 ? (
          <div className="p-8 text-center text-gray-500">No transactions found.</div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-100">
                <th className="px-6 py-4 text-sm font-semibold text-gray-600">Transaction ID</th>
                <th className="px-6 py-4 text-sm font-semibold text-gray-600">Customer / Account</th>
                <th className="px-6 py-4 text-sm font-semibold text-gray-600">Amount & Date</th>
                <th className="px-6 py-4 text-sm font-semibold text-gray-600">ML Risk Score</th>
                <th className="px-6 py-4 text-sm font-semibold text-gray-600"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {filteredTransactions.map((tx) => (
                <React.Fragment key={tx.id}>
                  <tr 
                    className={`hover:bg-gray-50/50 transition-colors cursor-pointer ${expandedRow === tx.id ? 'bg-gray-50/80' : ''}`}
                    onClick={() => toggleRow(tx.id)}
                  >
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                          <CreditCard size={18} />
                        </div>
                        <span className="font-medium text-gray-900">{tx.transaction_id}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-gray-600">
                      <div>{tx.customer_id}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">
                        {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(tx.amount)}
                      </div>
                      <div className="text-xs text-gray-500">{new Date(tx.date_time).toLocaleString()}</div>
                    </td>
                    <td className="px-6 py-4">
                      {tx.prediction ? (
                        <div className="flex items-center gap-2">
                          <span className={`font-bold ${
                            tx.prediction.risk_score > 75 ? 'text-red-600' : tx.prediction.risk_score > 40 ? 'text-orange-500' : 'text-green-600'
                          }`}>
                            {tx.prediction.risk_score.toFixed(1)}/100
                          </span>
                          <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                            tx.prediction.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                            tx.prediction.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                            tx.prediction.risk_level === 'MEDIUM' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-green-100 text-green-700'
                          }`}>
                            {tx.prediction.risk_level}
                          </span>
                        </div>
                      ) : (
                        <span className="text-gray-400 text-sm">No ML Data</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right">
                      {expandedRow === tx.id ? <ChevronUp size={20} className="text-gray-400" /> : <ChevronDown size={20} className="text-gray-400" />}
                    </td>
                  </tr>
                  
                  {expandedRow === tx.id && (
                    <tr>
                      <td colSpan={5} className="bg-slate-50 border-b border-gray-100">
                        <div className="p-6">
                          <div className="grid grid-cols-2 gap-8">
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-4">Transaction Details</h4>
                              <div className="space-y-3 text-sm">
                                <div className="flex justify-between">
                                  <span className="text-gray-500">Location:</span>
                                  <span className="font-medium text-gray-900">{tx.location}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-500">Merchant:</span>
                                  <span className="font-medium text-gray-900">{tx.merchant}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-500">Method:</span>
                                  <span className="font-medium text-gray-900">{tx.payment_method}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span className="text-gray-500">Device:</span>
                                  <span className="font-medium text-gray-900">{tx.device_info}</span>
                                </div>
                              </div>
                            </div>
                            
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                                <Activity size={18} className="text-indigo-600" /> 
                                Fraud Intelligence (SHAP)
                              </h4>
                              {tx.prediction?.explanations?.length > 0 ? (
                                <div className="space-y-3">
                                  {tx.prediction.explanations.slice(0, 5).map((exp: any, idx: number) => (
                                    <div key={idx} className="flex justify-between items-center text-sm">
                                      <span className="text-gray-600 truncate max-w-[200px]" title={exp.feature_name}>
                                        {exp.feature_name.replace(/_/g, ' ')}
                                      </span>
                                      <div className="flex items-center gap-3">
                                        <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                          <div 
                                            className={`h-full ${exp.shap_value > 0 ? 'bg-red-500' : 'bg-green-500'}`} 
                                            style={{ width: `${Math.min(Math.abs(exp.shap_value) * 100, 100)}%` }}
                                          ></div>
                                        </div>
                                        <span className={`font-mono text-xs w-12 text-right ${exp.shap_value > 0 ? 'text-red-600' : 'text-green-600'}`}>
                                          {exp.shap_value > 0 ? '+' : ''}{exp.shap_value.toFixed(2)}
                                        </span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              ) : (
                                <div className="text-sm text-gray-500 italic">No feature explanations available.</div>
                              )}
                            </div>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        )}
        
        {/* Pagination Footer */}
        {!isLoading && filteredTransactions.length > 0 && (
          <div className="border-t border-gray-100 p-4 flex items-center justify-between bg-gray-50">
            <span className="text-sm text-gray-500">
              Page {page} of {totalPages}
            </span>
            <div className="flex gap-2">
              <button 
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="p-2 border border-gray-200 rounded-lg hover:bg-white disabled:opacity-50 transition-colors"
              >
                <ChevronLeft size={18} />
              </button>
              <button 
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page >= totalPages}
                className="p-2 border border-gray-200 rounded-lg hover:bg-white disabled:opacity-50 transition-colors"
              >
                <ChevronRight size={18} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
