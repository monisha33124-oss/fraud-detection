import React from 'react';
import { Users, Settings, FileText, Bell, AlertTriangle } from 'lucide-react';

export const UsersManagement = () => (
  <div className="space-y-6 animate-in fade-in duration-500">
    <div className="flex justify-between items-end">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Users Management</h1>
        <p className="text-gray-500 mt-1">Manage system administrators and bank employees.</p>
      </div>
    </div>
    <div className="card-glass p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
      <Users size={48} className="text-indigo-300 mb-4" />
      <h3 className="text-xl font-semibold text-gray-900">User Directory</h3>
      <p className="text-gray-500 max-w-md mt-2">The user directory is currently managed via identity provider sync. Direct user creation is disabled.</p>
    </div>
  </div>
);

export const AlertsDashboard = () => (
  <div className="space-y-6 animate-in fade-in duration-500">
    <div className="flex justify-between items-end">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">System Alerts</h1>
        <p className="text-gray-500 mt-1">Global view of all triggered system and fraud alerts.</p>
      </div>
    </div>
    <div className="card-glass p-12 text-center flex flex-col items-center justify-center min-h-[400px]">
      <Bell size={48} className="text-orange-300 mb-4" />
      <h3 className="text-xl font-semibold text-gray-900">All Alerts Routed to Investigations</h3>
      <p className="text-gray-500 max-w-md mt-2">Alerts are automatically converted into Cases. Please visit the Investigations tab to action them.</p>
    </div>
  </div>
);

import { useState } from 'react';

export const Reports = () => {
  const [reportType, setReportType] = useState('transaction');
  const [format, setFormat] = useState('csv');
  const [filters, setFilters] = useState({
    startDate: '',
    endDate: '',
    customerId: '',
    riskLevel: '',
    status: ''
  });
  const [isGenerating, setIsGenerating] = useState(false);

  const handleDownload = async () => {
    setIsGenerating(true);
    try {
      const queryParams = new URLSearchParams({
        report_type: reportType,
        format: format,
        ...(filters.startDate && { start_date: filters.startDate }),
        ...(filters.endDate && { end_date: filters.endDate }),
        ...(filters.customerId && { customer_id: filters.customerId }),
        ...(filters.riskLevel && { risk_level: filters.riskLevel }),
        ...(filters.status && { status: filters.status })
      }).toString();

      // We don't use the standard client for downloads because we need a Blob
      const token = localStorage.getItem('token');
      const response = await fetch(`http://localhost:8000/api/v1/reports/generate?${queryParams}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${reportType}_report_${new Date().getTime()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Download failed', err);
      alert('Failed to generate report. Make sure backend is running and dependencies are installed.');
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Reports Engine</h1>
          <p className="text-gray-500 mt-1">Export regulatory, compliance, and operational reports.</p>
        </div>
      </div>
      
      <div className="card-glass p-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Report Configuration */}
          <div className="lg:col-span-1 space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Report Type</label>
              <select 
                value={reportType} 
                onChange={(e) => setReportType(e.target.value)}
                className="w-full p-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
              >
                <option value="transaction">Transaction Report</option>
                <option value="fraud">Fraud Report</option>
                <option value="risk">Risk Report</option>
                <option value="investigation">Investigation Report</option>
                <option value="customer">Customer Risk Report</option>
                <option value="model">Model Performance Report</option>
                <option value="audit">Audit Log Report</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Export Format</label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="radio" name="format" value="csv" checked={format === 'csv'} onChange={() => setFormat('csv')} className="text-indigo-600 focus:ring-indigo-500"/>
                  <span className="text-sm font-medium">CSV (Excel)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="radio" name="format" value="pdf" checked={format === 'pdf'} onChange={() => setFormat('pdf')} className="text-indigo-600 focus:ring-indigo-500"/>
                  <span className="text-sm font-medium">PDF Document</span>
                </label>
              </div>
            </div>
          </div>
          
          {/* Filters */}
          <div className="lg:col-span-2 bg-gray-50 p-6 rounded-xl border border-gray-200">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Filter size={16}/> Filter Parameters
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">Start Date</label>
                <input type="date" value={filters.startDate} onChange={e => setFilters({...filters, startDate: e.target.value})} className="w-full p-2 border border-gray-300 rounded-lg text-sm" />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-600 mb-1">End Date</label>
                <input type="date" value={filters.endDate} onChange={e => setFilters({...filters, endDate: e.target.value})} className="w-full p-2 border border-gray-300 rounded-lg text-sm" />
              </div>
              
              {['transaction', 'fraud', 'customer'].includes(reportType) && (
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Customer ID</label>
                  <input type="text" placeholder="Optional..." value={filters.customerId} onChange={e => setFilters({...filters, customerId: e.target.value})} className="w-full p-2 border border-gray-300 rounded-lg text-sm" />
                </div>
              )}
              
              {['fraud', 'risk'].includes(reportType) && (
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Risk Level</label>
                  <select value={filters.riskLevel} onChange={e => setFilters({...filters, riskLevel: e.target.value})} className="w-full p-2 border border-gray-300 rounded-lg text-sm bg-white">
                    <option value="">All</option>
                    <option value="CRITICAL">Critical</option>
                    <option value="HIGH">High</option>
                    <option value="MEDIUM">Medium</option>
                    <option value="LOW">Low</option>
                  </select>
                </div>
              )}
              
              {['investigation'].includes(reportType) && (
                <div>
                  <label className="block text-xs font-semibold text-gray-600 mb-1">Case Status</label>
                  <select value={filters.status} onChange={e => setFilters({...filters, status: e.target.value})} className="w-full p-2 border border-gray-300 rounded-lg text-sm bg-white">
                    <option value="">All</option>
                    <option value="NEW">New</option>
                    <option value="ASSIGNED">Assigned</option>
                    <option value="UNDER_INVESTIGATION">Under Investigation</option>
                    <option value="CLOSED">Closed</option>
                  </select>
                </div>
              )}
            </div>
          </div>
          
        </div>
        
        <div className="mt-8 pt-6 border-t border-gray-100 flex justify-end">
          <button 
            onClick={handleDownload}
            disabled={isGenerating}
            className="flex items-center gap-2 px-6 py-3 bg-indigo-600 text-white font-medium rounded-xl hover:bg-indigo-700 transition-colors disabled:opacity-50"
          >
            <FileText size={18} />
            {isGenerating ? 'Generating...' : `Download ${format.toUpperCase()} Report`}
          </button>
        </div>
      </div>
    </div>
  );
};

export const SettingsPage = () => (
  <div className="space-y-6 animate-in fade-in duration-500">
    <div className="flex justify-between items-end">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Platform Settings</h1>
        <p className="text-gray-500 mt-1">Configure ML thresholds and system preferences.</p>
      </div>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="card-glass p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">ML Model Thresholds</h3>
        <div className="space-y-4">
          <div>
            <label className="flex justify-between text-sm font-medium text-gray-700 mb-1">
              <span>Critical Alert Threshold</span>
              <span>85/100</span>
            </label>
            <div className="w-full h-2 bg-gray-200 rounded-full"><div className="h-2 bg-red-500 rounded-full w-[85%]"></div></div>
          </div>
          <div>
            <label className="flex justify-between text-sm font-medium text-gray-700 mb-1">
              <span>High Risk Threshold</span>
              <span>65/100</span>
            </label>
            <div className="w-full h-2 bg-gray-200 rounded-full"><div className="h-2 bg-orange-500 rounded-full w-[65%]"></div></div>
          </div>
        </div>
        <button className="mt-6 w-full px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800">Save Thresholds</button>
      </div>
      
      <div className="card-glass p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">System Integration</h3>
        <div className="space-y-4">
          <div className="p-4 border border-gray-200 rounded-lg flex items-center justify-between">
            <div>
              <div className="font-medium text-gray-900">Core Banking API</div>
              <div className="text-sm text-green-600 flex items-center gap-1">Connected</div>
            </div>
            <button className="px-3 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50">Configure</button>
          </div>
        </div>
      </div>
    </div>
  </div>
);
