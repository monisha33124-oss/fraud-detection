import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Transactions from './pages/Transactions';
import CaseManagement from './pages/CaseManagement';
import Customers from './pages/Customers';
import CustomerDetail from './pages/CustomerDetail';
import ModelPerformance from './pages/ModelPerformance';
import AuditLogs from './pages/AuditLogs';
import Login from './pages/Login';
import Landing from './pages/Landing';
import Unauthorized from './pages/Unauthorized';
import Profile from './pages/Profile';
import EmployeeDashboard from './pages/EmployeeDashboard';
import { UsersManagement, AlertsDashboard, Reports, SettingsPage } from './pages/AdminModules';

function ProtectedRoute({ children, allowedRoles }: { children: JSX.Element, allowedRoles?: string[] }) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center bg-[#030712] text-slate-500">Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return children;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/unauthorized" element={<Unauthorized />} />
      
      {/* Admin Routes */}
      <Route element={<ProtectedRoute allowedRoles={['ADMIN']}><Layout /></ProtectedRoute>}>
        <Route path="/admin/dashboard" element={<Dashboard />} />
        <Route path="/admin/users" element={<UsersManagement />} />
        <Route path="/admin/customers" element={<Customers />} />
        <Route path="/admin/customers/:id" element={<CustomerDetail />} />
        <Route path="/admin/transactions" element={<Transactions />} />
        <Route path="/admin/alerts" element={<AlertsDashboard />} />
        <Route path="/admin/investigations" element={<CaseManagement />} />
        <Route path="/admin/analytics" element={<Dashboard />} />
        <Route path="/admin/models" element={<ModelPerformance />} />
        <Route path="/admin/audit" element={<AuditLogs />} />
        <Route path="/admin/reports" element={<Reports />} />
        <Route path="/admin/settings" element={<SettingsPage />} />
        <Route path="/admin/profile" element={<Profile />} />
      </Route>

      {/* Employee Routes */}
      <Route element={<ProtectedRoute allowedRoles={['BANK_EMPLOYEE', 'ADMIN']}><Layout /></ProtectedRoute>}>
        <Route path="/employee/dashboard" element={<EmployeeDashboard />} />
        <Route path="/employee/cases" element={<CaseManagement />} />
        <Route path="/employee/transactions" element={<Transactions />} />
        <Route path="/employee/customers" element={<Customers />} />
        <Route path="/employee/customers/:id" element={<CustomerDetail />} />
        <Route path="/employee/alerts" element={<AlertsDashboard />} />
        <Route path="/employee/investigations/:id" element={<div className="p-4 text-white">Case Detail Page (Placeholder)</div>} />
        <Route path="/employee/reports" element={<Reports />} />
        <Route path="/employee/profile" element={<Profile />} />
      </Route>
      
      {/* Redirect old routes for backward compatibility */}
      <Route path="/dashboard" element={<Navigate to="/admin/dashboard" replace />} />
      <Route path="/transactions" element={<Navigate to="/admin/transactions" replace />} />
      <Route path="/investigations" element={<Navigate to="/admin/investigations" replace />} />
      <Route path="/customers" element={<Navigate to="/admin/customers" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
