import { useEffect, useState } from 'react';
import { ShieldAlert, Activity, AlertTriangle, CheckCircle } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import client from '../api/client';

const StatCard = ({ icon: Icon, title, value, colorClass }: any) => (
  <div className="card-glass p-6 flex items-start gap-4">
    <div className={`p-3 rounded-2xl ${colorClass}`}>
      <Icon size={24} className="text-white" />
    </div>
    <div>
      <h3 className="text-gray-500 font-medium text-sm mb-1">{title}</h3>
      <div className="flex items-end gap-3">
        <span className="text-2xl font-bold text-gray-900">{value}</span>
      </div>
    </div>
  </div>
);

const COLORS = ['#0ea5e9', '#ef4444', '#f59e0b', '#10b981', '#8b5cf6'];

export default function Dashboard() {
  const [stats, setStats] = useState({
    transactions: 0,
    alerts: 0,
    investigations: 0,
    fraudRate: 0
  });
  
  const [trendData, setTrendData] = useState([]);
  const [locationData, setLocationData] = useState([]);
  const [typeData, setTypeData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const [overviewRes, trendsRes, investigationsRes, locRes, typeRes] = await Promise.all([
          client.get('/api/v1/analytics/overview'),
          client.get('/api/v1/analytics/fraud-trends'),
          client.get('/api/v1/investigations/?page_size=1'),
          client.get('/api/v1/analytics/fraud-by-location'),
          client.get('/api/v1/analytics/fraud-by-type')
        ]);
        
        setStats({
          transactions: overviewRes.data.total_transactions || 0,
          alerts: overviewRes.data.active_alerts || 0,
          investigations: investigationsRes.data.total || 0,
          fraudRate: overviewRes.data.fraud_rate || 0
        });
        
        setTrendData(trendsRes.data || []);
        setLocationData(locRes.data || []);
        setTypeData(typeRes.data || []);
      } catch (err: any) {
        console.error('Failed to fetch dashboard stats', err);
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return <div className="animate-pulse flex items-center justify-center min-h-[400px] text-gray-400">Loading metrics...</div>;
  }
  
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-red-500 flex-col gap-4">
        <AlertTriangle size={48} />
        <p>Error loading dashboard: {error}</p>
        <button 
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-slate-800 text-white rounded-md hover:bg-slate-700"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Overview</h1>
          <p className="text-gray-500 mt-1">Monitor real-time fraud metrics and platform activity.</p>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => window.open(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/reports/csv/transactions`, '_blank')}
            className="px-4 py-2 bg-white border border-gray-200 hover:border-gray-300 hover:bg-gray-50 text-gray-700 text-sm font-medium rounded-lg shadow-sm transition-all"
          >
            Export Transactions (CSV)
          </button>
          <button 
            onClick={() => window.open(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/reports/pdf/cases`, '_blank')}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg shadow-sm transition-all"
          >
            Download Cases (PDF)
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Activity}
          title="Total Transactions"
          value={stats.transactions.toLocaleString()}
          colorClass="bg-blue-500 shadow-blue-500/20"
        />
        <StatCard
          icon={AlertTriangle}
          title="Active Alerts"
          value={stats.alerts.toLocaleString()}
          colorClass="bg-orange-500 shadow-orange-500/20"
        />
        <StatCard
          icon={ShieldAlert}
          title="Open Investigations"
          value={stats.investigations.toLocaleString()}
          colorClass="bg-red-500 shadow-red-500/20"
        />
        <StatCard
          icon={CheckCircle}
          title="Fraud Rate"
          value={`${stats.fraudRate}%`}
          colorClass="bg-emerald-500 shadow-emerald-500/20"
        />
      </div>

      {/* Main Chart */}
      <div className="card-glass p-6">
        <div className="mb-6">
          <h2 className="text-lg font-bold text-gray-900">Transaction Volume vs Fraud</h2>
          <p className="text-sm text-gray-500">Historical trend</p>
        </div>
        <div className="h-[300px] w-full">
          {trendData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorTransactions" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorFraud" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  axisLine={false} 
                  tickLine={false} 
                  tick={{fill: '#6b7280'}} 
                  tickFormatter={(val) => new Date(val).toLocaleDateString(undefined, {month: 'short', day: 'numeric'})}
                />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#6b7280'}} />
                <Tooltip
                  contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                  labelFormatter={(val) => new Date(val).toLocaleDateString()}
                />
                <Area name="Legitimate" type="monotone" dataKey="legitimate" stroke="#0ea5e9" strokeWidth={3} fillOpacity={1} fill="url(#colorTransactions)" />
                <Area name="Fraudulent" type="monotone" dataKey="fraudulent" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorFraud)" />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full w-full flex items-center justify-center text-gray-400">
              No trend data available yet
            </div>
          )}
        </div>
      </div>
      
      {/* Secondary Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-glass p-6">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900">Top Fraud Locations</h2>
          </div>
          <div className="h-[250px] w-full">
            {locationData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={locationData} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={false} stroke="#e5e7eb" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="location" type="category" axisLine={false} tickLine={false} tick={{fill: '#4b5563', fontSize: 12}} width={100} />
                  <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                  <Bar dataKey="count" fill="#ef4444" radius={[0, 4, 4, 0]} barSize={20} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full w-full flex items-center justify-center text-gray-400">No location data</div>
            )}
          </div>
        </div>
        
        <div className="card-glass p-6">
          <div className="mb-6">
            <h2 className="text-lg font-bold text-gray-900">Fraud by Transaction Type</h2>
          </div>
          <div className="h-[250px] w-full">
            {typeData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={typeData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="count"
                    nameKey="transaction_type"
                  >
                    {typeData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full w-full flex items-center justify-center text-gray-400">No type data</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
