import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, ListOrdered, ShieldAlert, LogOut, Users, Cpu, ClipboardList } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const SidebarItem = ({ icon: Icon, label, path, active }: any) => (
  <Link
    to={path}
    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
      active
        ? 'bg-primary-500 text-white shadow-md'
        : 'text-gray-500 hover:bg-gray-100 hover:text-gray-900'
    }`}
  >
    <Icon size={20} />
    <span className="font-medium">{label}</span>
  </Link>
);

export default function Layout() {
  const location = useLocation();
  const { logout, user } = useAuth();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col h-screen fixed">
        <div className="p-6 border-b border-gray-100">
          <div className="flex items-center gap-3 text-primary-600">
            <ShieldAlert size={28} className="text-primary-500" />
            <h1 className="text-xl font-bold tracking-tight">FraudShield AI</h1>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <SidebarItem
            icon={LayoutDashboard}
            label="Dashboard"
            path="/dashboard"
            active={location.pathname.startsWith('/dashboard')}
          />
          <SidebarItem
            icon={ListOrdered}
            label="Transactions"
            path="/transactions"
            active={location.pathname.startsWith('/transactions')}
          />
          <SidebarItem
            icon={ShieldAlert}
            label="Investigations"
            path="/investigations"
            active={location.pathname.startsWith('/investigations')}
          />
          <SidebarItem
            icon={Users}
            label="Customers"
            path="/customers"
            active={location.pathname.startsWith('/customers')}
          />
          {user?.role === 'ADMIN' && (
            <>
              <SidebarItem
                icon={Cpu}
                label="ML Models"
                path="/models"
                active={location.pathname.startsWith('/models')}
              />
              <SidebarItem
                icon={ClipboardList}
                label="Audit Logs"
                path="/audit-logs"
                active={location.pathname.startsWith('/audit-logs')}
              />
            </>
          )}
        </nav>

        <div className="p-4 border-t border-gray-100">
          <button 
            onClick={logout}
            className="flex items-center gap-3 px-4 py-3 w-full text-left text-gray-500 hover:bg-red-50 hover:text-red-600 rounded-xl transition-all"
          >
            <LogOut size={20} />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 ml-64 min-h-screen p-8">
        <Outlet />
      </main>
    </div>
  );
}
