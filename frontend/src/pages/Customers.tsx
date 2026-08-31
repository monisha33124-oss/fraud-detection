import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, Search, Filter } from 'lucide-react';
import client from '../api/client';

interface Customer {
  id: number;
  customer_id: string;
  name: string;
  email: string;
  risk_score_avg: number;
  total_transactions: number;
}

export default function Customers() {
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCustomers = async () => {
      try {
        const res = await client.get('/api/v1/customers/?page_size=50');
        setCustomers(res.data);
      } catch (err) {
        console.error('Failed to fetch customers', err);
      } finally {
        setLoading(false);
      }
    };
    fetchCustomers();
  }, []);

  const filtered = customers.filter(c => 
    c.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
    c.customer_id.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6 animate-in fade-in duration-500">
      <div className="flex flex-col sm:flex-row justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Customer Management</h1>
          <p className="text-gray-500 mt-1">View and manage customer risk profiles.</p>
        </div>
      </div>

      <div className="card-glass p-6">
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              placeholder="Search by name or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 bg-gray-50 border border-gray-200 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors">
            <Filter size={20} />
            Filters
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-gray-100 text-sm text-gray-500">
                <th className="py-4 font-medium">Customer ID</th>
                <th className="py-4 font-medium">Name</th>
                <th className="py-4 font-medium">Email</th>
                <th className="py-4 font-medium">Avg Risk Score</th>
                <th className="py-4 font-medium">Total Transactions</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {loading ? (
                <tr><td colSpan={5} className="py-8 text-center text-gray-400">Loading customers...</td></tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center text-gray-500">
                    <Users size={48} className="mx-auto text-gray-300 mb-4" />
                    No customers found matching your search.
                  </td>
                </tr>
              ) : (
                filtered.map((customer) => (
                  <tr 
                    key={customer.id} 
                    onClick={() => navigate(`../customers/${customer.customer_id}`)}
                    className="border-b border-gray-50 hover:bg-gray-50/50 transition-colors cursor-pointer text-gray-700"
                  >
                    <td className="py-4 font-medium text-indigo-600">{customer.customer_id}</td>
                    <td className="py-4">{customer.name}</td>
                    <td className="py-4">{customer.email}</td>
                    <td className="py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                        customer.risk_score_avg > 70 ? 'bg-red-100 text-red-700' :
                        customer.risk_score_avg > 30 ? 'bg-orange-100 text-orange-700' :
                        'bg-emerald-100 text-emerald-700'
                      }`}>
                        {customer.risk_score_avg.toFixed(1)}
                      </span>
                    </td>
                    <td className="py-4">{customer.total_transactions}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
