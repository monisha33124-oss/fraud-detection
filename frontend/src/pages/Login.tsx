import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { ShieldAlert, Lock, User, Loader2, ArrowLeft, Search, CheckCircle2, Eye, EyeOff, Settings } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import client from '../api/client';

type Role = 'ADMIN' | 'INVESTIGATOR';

export default function Login() {
  const [role, setRole] = useState<Role>('ADMIN');
  const [email, setEmail] = useState('admin@bank.com');
  const [password, setPassword] = useState('AdminPass123!');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleRoleSelect = (selectedRole: Role) => {
    setRole(selectedRole);
    setError('');
    if (selectedRole === 'ADMIN') {
      setEmail('admin@bank.com');
      setPassword('AdminPass123!');
    } else {
      setEmail('investigator@bank.com');
      setPassword('Investigate123!');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    
    try {
      const formData = new URLSearchParams();
      
      const loginEmail = email; // Removed the incorrect mapping
      
      formData.append('username', loginEmail);
      formData.append('password', password);

      const res = await client.post('/api/v1/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      
      const { access_token } = res.data;
      
      const userRes = await client.get('/api/v1/auth/me', {
        headers: { Authorization: `Bearer ${access_token}` }
      });

      if (userRes.data.role !== role) {
        throw new Error('This account does not have permission to access this role.');
      }

      login(access_token, userRes.data);
      if (role === 'ADMIN') {
        navigate('/dashboard', { replace: true });
      } else {
        navigate('/investigations', { replace: true });
      }
      
    } catch (err: any) {
      console.error('Login Error:', err);
      if (err.response) {
        setError(`Server Error [${err.response.status}]: ${JSON.stringify(err.response.data)}`);
      } else if (err.request) {
        setError(`Network Error: Cannot reach backend at ${client.defaults.baseURL}. Is it running?`);
      } else {
        setError(`Error: ${err.message}`);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#030712] text-slate-300 font-sans flex flex-col items-center justify-center p-6 relative overflow-x-hidden">
      {/* Background glowing rings */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-indigo-900/20 rounded-full blur-[150px] pointer-events-none"></div>
      <div className="absolute bottom-0 w-full h-[400px] bg-gradient-to-t from-blue-900/10 to-transparent pointer-events-none"></div>

      {/* Cyber Circuit Lines (SVG Pattern) */}
      <div className="absolute inset-0 opacity-[0.02] pointer-events-none" style={{ backgroundImage: 'linear-gradient(#4f46e5 1px, transparent 1px), linear-gradient(90deg, #4f46e5 1px, transparent 1px)', backgroundSize: '50px 50px' }}></div>

      <div className="w-full max-w-5xl grid lg:grid-cols-2 gap-12 items-center relative z-10 my-8">
        
        {/* LEFT: Role Selection & Security Visual */}
        <div className="flex flex-col h-full justify-center">
          <div className="flex items-center gap-2 mb-8">
            <ShieldAlert className="text-indigo-400" size={32} />
            <span className="text-3xl font-bold text-white tracking-tight">FraudShield AI</span>
          </div>

          <h2 className="text-2xl font-bold text-white mb-2">Select Your Role</h2>
          <p className="text-slate-400 mb-6">Please identify your authorization level before logging in.</p>

          <div className="space-y-4 mb-8">
            {/* Admin Role Card */}
            <div 
              onClick={() => handleRoleSelect('ADMIN')}
              className={`cursor-pointer relative overflow-hidden rounded-2xl p-5 border transition-all duration-300 ${
                role === 'ADMIN' 
                ? 'bg-indigo-900/20 border-indigo-500 shadow-[0_0_20px_rgba(79,70,229,0.3)]' 
                : 'bg-[#0B1120]/60 border-white/5 hover:border-indigo-500/30 hover:bg-white/5'
              }`}
            >
              {role === 'ADMIN' && (
                <div className="absolute top-4 right-4 text-indigo-400 animate-in zoom-in">
                  <CheckCircle2 size={20} />
                </div>
              )}
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl ${role === 'ADMIN' ? 'bg-indigo-600/20 text-indigo-400' : 'bg-white/5 text-slate-400'}`}>
                  <Settings size={24} />
                </div>
                <div>
                  <h3 className={`text-lg font-bold mb-1 ${role === 'ADMIN' ? 'text-white' : 'text-slate-300'}`}>ADMIN</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    Manage users, transactions, fraud detection, reports, analytics, and system settings.
                  </p>
                </div>
              </div>
            </div>

            {/* Investigator Role Card */}
            <div 
              onClick={() => handleRoleSelect('INVESTIGATOR')}
              className={`cursor-pointer relative overflow-hidden rounded-2xl p-5 border transition-all duration-300 ${
                role === 'INVESTIGATOR' 
                ? 'bg-indigo-900/20 border-indigo-500 shadow-[0_0_20px_rgba(79,70,229,0.3)]' 
                : 'bg-[#0B1120]/60 border-white/5 hover:border-indigo-500/30 hover:bg-white/5'
              }`}
            >
              {role === 'INVESTIGATOR' && (
                <div className="absolute top-4 right-4 text-indigo-400 animate-in zoom-in">
                  <CheckCircle2 size={20} />
                </div>
              )}
              <div className="flex items-start gap-4">
                <div className={`p-3 rounded-xl ${role === 'INVESTIGATOR' ? 'bg-indigo-600/20 text-indigo-400' : 'bg-white/5 text-slate-400'}`}>
                  <Search size={24} />
                </div>
                <div>
                  <h3 className={`text-lg font-bold mb-1 ${role === 'INVESTIGATOR' ? 'text-white' : 'text-slate-300'}`}>FRAUD INVESTIGATOR</h3>
                  <p className="text-sm text-slate-400 leading-relaxed">
                    Investigate suspicious transactions, review AI explanations, manage evidence, and submit investigation decisions.
                  </p>
                </div>
              </div>
            </div>
          </div>
          
          <div className="hidden lg:flex items-center justify-center mt-auto p-8 relative">
            <div className="absolute w-[250px] h-[250px] bg-blue-600/20 blur-[60px] rounded-full"></div>
            <div className="relative w-32 h-40 bg-[#0B1120] rounded-[2rem] border border-indigo-500/50 shadow-[0_0_30px_rgba(79,70,229,0.4)] flex items-center justify-center backdrop-blur-md">
              <div className="absolute inset-2 border border-indigo-400/20 rounded-[1.5rem]"></div>
              <Lock size={48} className="text-blue-400 drop-shadow-[0_0_10px_rgba(96,165,250,0.8)]" />
            </div>
          </div>
        </div>

        {/* RIGHT: Login Form Container */}
        <div className="bg-[#0B1120]/80 backdrop-blur-xl border border-white/10 rounded-3xl p-8 lg:p-10 shadow-2xl animate-in fade-in slide-in-from-right-8 duration-700">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-white mb-2">Welcome Back!</h2>
            <p className="text-slate-400">
              {role === 'ADMIN' ? 'Admin Login' : 'Fraud Investigator Login'}
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 text-red-400 text-sm font-medium rounded-xl border border-red-500/20 flex items-start gap-3">
              <ShieldAlert size={18} className="shrink-0 mt-0.5" />
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">Email</label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full pl-12 pr-4 py-3.5 bg-[#030712]/50 border border-white/10 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white placeholder:text-slate-600 transition-all"
                  placeholder="admin@bank.com"
                />
              </div>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-medium text-slate-300">Password</label>
                <a href="#" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors">Forgot Password?</a>
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-500" size={18} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full pl-12 pr-12 py-3.5 bg-[#030712]/50 border border-white/10 rounded-xl focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-white placeholder:text-slate-600 transition-all"
                  placeholder="••••••••"
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300 transition-colors"
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            <div className="flex items-center">
              <input 
                type="checkbox" 
                id="remember" 
                className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-gray-900"
              />
              <label htmlFor="remember" className="ml-2 text-sm text-slate-400">Remember Me</label>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-4 px-4 mt-4 bg-[#5E3BEE] hover:bg-[#7252FF] text-white font-bold rounded-xl transition-all flex items-center justify-center disabled:opacity-70 shadow-[0_0_20px_rgba(94,59,238,0.4)] hover:shadow-[0_0_30px_rgba(94,59,238,0.6)]"
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <Loader2 className="animate-spin" size={20} /> Signing In...
                </span>
              ) : 'Login Securely'}
            </button>
          </form>
          
          <div className="mt-8 pt-6 border-t border-white/5 text-center text-sm text-slate-500">
            Don't have an account? <a href="#" className="text-indigo-400 hover:text-indigo-300">Contact Administrator</a>
          </div>
        </div>

      </div>
      
      <div className="mt-8 text-xs text-slate-600 relative z-10">
        © 2026 FraudShield AI. All rights reserved.
      </div>
    </div>
  );
}
