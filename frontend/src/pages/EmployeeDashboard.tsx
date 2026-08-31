import { useEffect, useState } from 'react';
import { Briefcase, AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import client from '../api/client';
import { useAuth } from '../contexts/AuthContext';

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

export default function EmployeeDashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState({
    assigned_cases: 0,
    resolved_cases: 0,
    high_risk_alerts: 0,
    total_cases_handled: 0
  });
  
  const [recentTransactions, setRecentTransactions] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const [statsRes, txRes] = await Promise.all([
          client.get('/api/v1/analytics/employee-stats'),
          client.get('/api/v1/transactions/?page_size=5')
        ]);
        
        setStats(statsRes.data);
        setRecentTransactions(txRes.data.items || []);
      } catch (err: any) {
        console.error('Failed to fetch employee stats', err);
        setError(err.message || 'Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchDashboardData();
  }, []);

  if (isLoading) {
    return <div className="animate-pulse flex items-center justify-center min-h-[400px] text-gray-400">Loading your workspace...</div>;
  }
  
  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-red-500 flex-col gap-4">
        <AlertTriangle size={48} />
        <p>Error loading workspace: {error}</p>
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
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Welcome back, {user?.full_name || 'Investigator'}</h1>
          <p className="text-gray-500 mt-1">Here is your personal investigation workspace.</p>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Briefcase}
          title="Assigned Cases"
          value={stats.assigned_cases}
          colorClass="bg-blue-500 shadow-blue-500/20"
        />
        <StatCard
          icon={AlertTriangle}
          title="High-Risk Alerts"
          value={stats.high_risk_alerts}
          colorClass="bg-orange-500 shadow-orange-500/20"
        />
        <StatCard
          icon={CheckCircle}
          title="Resolved Cases"
          value={stats.resolved_cases}
          colorClass="bg-emerald-500 shadow-emerald-500/20"
        />
        <StatCard
          icon={Clock}
          title="Total Handled"
          value={stats.total_cases_handled}
          colorClass="bg-purple-500 shadow-purple-500/20"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card-glass p-6">
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Recent Transactions</h2>
              <p className="text-sm text-gray-500">Latest activity globally</p>
            </div>
            <a href="/employee/transactions" className="text-sm text-indigo-600 hover:text-indigo-800 font-medium">View all</a>
          </div>
          
          <div className="space-y-4">
            {recentTransactions.map((tx) => (
              <div key={tx.id} className="flex justify-between items-center p-3 rounded-lg hover:bg-gray-50 transition-colors">
                <div>
                  <div className="font-medium text-gray-900">{tx.transaction_id}</div>
                  <div className="text-xs text-gray-500">{new Date(tx.date_time).toLocaleString()} • {tx.merchant}</div>
                </div>
                <div className="text-right">
                  <div className="font-medium">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(tx.amount)}</div>
                  {tx.prediction && (
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                      tx.prediction.risk_level === 'CRITICAL' ? 'bg-red-100 text-red-700' :
                      tx.prediction.risk_level === 'HIGH' ? 'bg-orange-100 text-orange-700' :
                      'bg-green-100 text-green-700'
                    }`}>
                      {tx.prediction.risk_level}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card-glass p-6">
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h2 className="text-lg font-bold text-gray-900">Quick Actions</h2>
              <p className="text-sm text-gray-500">Jump to your tasks</p>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <a href="/employee/cases" className="p-4 border border-gray-200 rounded-xl hover:border-indigo-500 hover:bg-indigo-50 transition-all text-center">
              <Briefcase className="mx-auto mb-2 text-indigo-600" size={24} />
              <div className="font-medium text-gray-900">My Cases</div>
            </a>
            <a href="/employee/alerts" className="p-4 border border-gray-200 rounded-xl hover:border-orange-500 hover:bg-orange-50 transition-all text-center">
              <AlertTriangle className="mx-auto mb-2 text-orange-500" size={24} />
              <div className="font-medium text-gray-900">High Risk Alerts</div>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
