import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Mail, Phone, MapPin, Calendar, ShieldAlert, FileText, CreditCard } from 'lucide-react';
import client from '../api/client';

export default function CustomerDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [customer, setCustomer] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCustomer = async () => {
      try {
        setLoading(true);
        const res = await client.get(`/api/v1/customers/${id}`);
        setCustomer(res.data);
      } catch (err: any) {
        console.error('Failed to fetch customer detail', err);
        setError(err.response?.data?.detail || 'Customer not found');
      } finally {
        setLoading(false);
      }
    };
    
    if (id) fetchCustomer();
  }, [id]);

  if (loading) {
    return <div className="flex justify-center p-12 text-gray-400">Loading customer profile...</div>;
  }

  if (error || !customer) {
    return (
      <div className="text-center p-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Error</h2>
        <p className="text-red-500">{error || 'Customer not found'}</p>
        <button 
          onClick={() => navigate(-1)} 
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Go Back
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex items-center gap-4">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 hover:bg-gray-100 rounded-lg text-gray-500 transition-colors"
        >
          <ArrowLeft size={20} />
        </button>
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{customer.name}</h1>
          <p className="text-gray-500 mt-1">ID: {customer.customer_id}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Sidebar */}
        <div className="space-y-6">
          <div className="card-glass p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Info</h3>
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-sm">
                <Mail size={16} className="text-gray-400" />
                <span className="text-gray-700">{customer.email || 'N/A'}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Phone size={16} className="text-gray-400" />
                <span className="text-gray-700">{customer.phone || 'N/A'}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <MapPin size={16} className="text-gray-400" />
                <span className="text-gray-700">{customer.address || 'N/A'}</span>
              </div>
              <div className="flex items-center gap-3 text-sm">
                <Calendar size={16} className="text-gray-400" />
                <span className="text-gray-700">Joined {new Date(customer.created_at).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
          
          <div className="card-glass p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <ShieldAlert size={18} className="text-orange-500" /> Active Alerts
            </h3>
            {customer.alerts?.length === 0 ? (
              <p className="text-sm text-gray-500 italic">No alerts found for this customer.</p>
            ) : (
              <div className="space-y-3">
                {customer.alerts?.map((alert: any) => (
                  <div key={alert.id} className="p-3 border border-red-100 bg-red-50 rounded-lg text-sm">
                    <div className="font-semibold text-red-800">{alert.alert_id}</div>
                    <div className="text-red-600 flex justify-between mt-1">
                      <span>{alert.status}</span>
                      <span>{new Date(alert.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Recent Transactions */}
          <div className="card-glass p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <CreditCard size={18} className="text-indigo-500" /> Recent Transactions
            </h3>
            {customer.transactions?.length === 0 ? (
              <p className="text-sm text-gray-500 italic">No recent transactions.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse text-sm">
                  <thead>
                    <tr className="border-b border-gray-100 text-gray-500">
                      <th className="py-3 font-medium">ID</th>
                      <th className="py-3 font-medium">Merchant</th>
                      <th className="py-3 font-medium">Amount</th>
                      <th className="py-3 font-medium">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {customer.transactions?.map((tx: any) => (
                      <tr key={tx.id} className="border-b border-gray-50 text-gray-700">
                        <td className="py-3 font-medium text-indigo-600">{tx.transaction_id}</td>
                        <td className="py-3">{tx.merchant}</td>
                        <td className="py-3 font-medium">{new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(tx.amount)}</td>
                        <td className="py-3 text-gray-500">{new Date(tx.date_time).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Investigation Cases */}
          <div className="card-glass p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText size={18} className="text-blue-500" /> Investigation History
            </h3>
            {customer.cases?.length === 0 ? (
              <p className="text-sm text-gray-500 italic">No investigations found.</p>
            ) : (
              <div className="space-y-3">
                {customer.cases?.map((c: any) => (
                  <div key={c.id} className="p-4 border border-gray-100 rounded-lg flex justify-between items-center bg-gray-50 hover:bg-gray-100 transition-colors cursor-pointer">
                    <div>
                      <div className="font-semibold text-gray-900">{c.case_id}</div>
                      <div className="text-xs text-gray-500 mt-1">{new Date(c.created_at).toLocaleString()}</div>
                    </div>
                    <div className="flex gap-2">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${c.priority === 'CRITICAL' ? 'bg-red-100 text-red-700' : 'bg-orange-100 text-orange-700'}`}>
                        {c.priority}
                      </span>
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-gray-200 text-gray-800">
                        {c.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
