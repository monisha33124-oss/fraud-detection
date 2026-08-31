import { Link } from 'react-router-dom';
import { 
  ShieldAlert, Lock, Activity, TrendingUp, Users, Database, 
  Search, Shield, CheckCircle2, ChevronRight, Menu 
} from 'lucide-react';

export default function Landing() {
  return (
    <div className="min-h-screen bg-[#030712] text-slate-300 font-sans selection:bg-indigo-500/30 overflow-x-hidden">
      {/* Background glow effects */}
      <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[1000px] h-[500px] bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="fixed bottom-0 right-0 w-[600px] h-[600px] bg-blue-600/10 rounded-full blur-[150px] pointer-events-none"></div>

      {/* HEADER */}
      <header className="fixed top-0 w-full z-50 bg-[#030712]/80 backdrop-blur-md border-b border-white/5">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 bg-indigo-500/10 rounded-lg border border-indigo-500/20">
              <ShieldAlert className="text-indigo-400" size={24} />
            </div>
            <span className="text-xl font-bold text-white tracking-tight">FraudShield AI</span>
          </div>

          <nav className="hidden md:flex items-center gap-8 text-sm font-medium">
            <a href="#" className="text-white hover:text-indigo-400 transition-colors">Home</a>
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#workflow" className="hover:text-white transition-colors">How It Works</a>
            <a href="#security" className="hover:text-white transition-colors">Security</a>
          </nav>

          <div className="hidden md:flex items-center gap-4">
            <Link to="/login" className="text-sm font-medium hover:text-white transition-colors px-4 py-2">
              Login
            </Link>
            <Link to="/login" className="text-sm font-medium bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl transition-all shadow-[0_0_20px_rgba(79,70,229,0.3)]">
              Get Started
            </Link>
          </div>

          <button className="md:hidden p-2 text-slate-400 hover:text-white">
            <Menu size={24} />
          </button>
        </div>
      </header>

      <main className="relative z-10 pt-32 pb-20">
        {/* HERO SECTION */}
        <section className="max-w-7xl mx-auto px-6 pt-12 pb-24 grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-xs font-semibold uppercase tracking-wider">
              <span className="w-2 h-2 rounded-full bg-indigo-400 animate-pulse"></span>
              AI-Powered • Secure • Intelligent
            </div>
            
            <h1 className="text-5xl lg:text-7xl font-extrabold text-white leading-[1.1] tracking-tight">
              Explainable AI-Based <br />
              Financial <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-500">Fraud & Risk</span> <br />
              Detection System
            </h1>
            
            <p className="text-lg text-slate-400 max-w-xl leading-relaxed">
              Detect fraud. Assess financial risk. Understand every AI decision. Secure your enterprise with enterprise-grade machine learning and transparent SHAP explanations.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/login" className="inline-flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl font-semibold transition-all shadow-[0_0_30px_rgba(79,70,229,0.4)]">
                Get Started
              </Link>
              <Link to="/login" className="inline-flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white px-8 py-4 rounded-xl font-semibold transition-all">
                Login to Dashboard
              </Link>
            </div>
          </div>

          {/* Custom Hero Visual */}
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500/20 to-blue-500/20 rounded-3xl blur-2xl"></div>
            <div className="relative bg-[#0B1120] border border-white/10 rounded-3xl p-6 shadow-2xl">
              {/* Fake Dashboard Header */}
              <div className="flex items-center justify-between mb-8 pb-4 border-b border-white/5">
                <div className="flex items-center gap-2">
                  <ShieldAlert className="text-indigo-400" size={18} />
                  <span className="text-white font-medium text-sm">Live Monitoring</span>
                </div>
                <div className="flex gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500/20 border border-red-500/50"></div>
                  <div className="w-3 h-3 rounded-full bg-yellow-500/20 border border-yellow-500/50"></div>
                  <div className="w-3 h-3 rounded-full bg-green-500/20 border border-green-500/50"></div>
                </div>
              </div>
              
              {/* Fake Dashboard Stats */}
              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-white/5 rounded-xl p-4 border border-white/5">
                  <p className="text-xs text-slate-400 mb-1">Total Analyzed</p>
                  <p className="text-2xl font-bold text-white">12,458</p>
                  <p className="text-xs text-green-400 mt-1">+12.5% today</p>
                </div>
                <div className="bg-white/5 rounded-xl p-4 border border-white/5 relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-16 h-16 bg-red-500/10 rounded-bl-full"></div>
                  <p className="text-xs text-slate-400 mb-1">Fraud Detected</p>
                  <p className="text-2xl font-bold text-red-400">2,213</p>
                  <p className="text-xs text-red-400/70 mt-1">+18.7% today</p>
                </div>
              </div>

              {/* Fake Risk Score Chart */}
              <div className="bg-white/5 rounded-xl p-6 border border-white/5 flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400 mb-2">Transaction Risk Score</p>
                  <div className="flex items-end gap-2">
                    <span className="text-4xl font-bold text-white">92</span>
                    <span className="text-sm text-slate-500 mb-1">/100</span>
                  </div>
                  <span className="inline-block mt-2 text-xs px-2 py-1 bg-red-500/20 text-red-400 rounded-md border border-red-500/30">CRITICAL RISK</span>
                </div>
                {/* Glowing Shield */}
                <div className="relative w-24 h-24 flex items-center justify-center">
                  <div className="absolute inset-0 border-[4px] border-indigo-500/30 rounded-full border-t-indigo-500 animate-spin"></div>
                  <Shield size={32} className="text-indigo-400" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* STATISTICS STRIP */}
        <section className="border-y border-white/5 bg-white/[0.02]">
          <div className="max-w-7xl mx-auto px-6 py-12 grid grid-cols-2 lg:grid-cols-4 gap-8 divide-x divide-white/5">
            <div className="text-center px-4">
              <h3 className="text-4xl font-bold text-white mb-2 text-shadow-glow">10K+</h3>
              <p className="text-sm text-slate-400">Transactions Analyzed</p>
            </div>
            <div className="text-center px-4">
              <h3 className="text-4xl font-bold text-indigo-400 mb-2 text-shadow-glow">2K+</h3>
              <p className="text-sm text-slate-400">Fraud Detected</p>
            </div>
            <div className="text-center px-4">
              <h3 className="text-4xl font-bold text-blue-400 mb-2 text-shadow-glow">95%+</h3>
              <p className="text-sm text-slate-400">Model Accuracy</p>
            </div>
            <div className="text-center px-4">
              <h3 className="text-4xl font-bold text-white mb-2 text-shadow-glow">24/7</h3>
              <p className="text-sm text-slate-400">Real-time Monitoring</p>
            </div>
          </div>
        </section>

        {/* FEATURES SECTION */}
        <section id="features" className="max-w-7xl mx-auto px-6 py-24">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Enterprise-Grade Security Features</h2>
            <p className="text-slate-400">Protect your financial assets with cutting-edge machine learning and transparent investigation tools.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Activity, title: "AI Fraud Detection", desc: "Detect suspicious and fraudulent transactions using advanced machine learning models." },
              { icon: TrendingUp, title: "Risk Scoring", desc: "Generate risk scores from 0–100 and classify transactions as Low, Medium, or High risk." },
              { icon: Search, title: "Explainable AI", desc: "Understand why the AI classified a transaction as risky using precise SHAP explanations." },
              { icon: Users, title: "Investigation Management", desc: "Manage fraud cases, assign investigators, review evidence, and record decisions." },
              { icon: Database, title: "Real-Time Monitoring", desc: "Monitor transactions, risk levels, and fraud trends with real-time analytics." },
              { icon: Lock, title: "Secure & Reliable", desc: "Role-based access, audit logging, secure data handling, and protected storage." }
            ].map((f, i) => (
              <div key={i} className="group bg-white/[0.02] border border-white/5 hover:border-indigo-500/50 rounded-2xl p-6 transition-all hover:bg-white/[0.04] hover:-translate-y-1">
                <div className="w-12 h-12 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                  <f.icon className="text-indigo-400" size={24} />
                </div>
                <h3 className="text-xl font-semibold text-white mb-3">{f.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* HOW IT WORKS */}
        <section id="workflow" className="border-y border-white/5 bg-white/[0.02] py-24">
          <div className="max-w-7xl mx-auto px-6">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">How It Works</h2>
              <p className="text-slate-400">A seamless pipeline from transaction creation to final investigation.</p>
            </div>
            
            <div className="flex flex-col md:flex-row items-center justify-between gap-4 md:gap-0 relative">
              {/* Connecting Line */}
              <div className="hidden md:block absolute top-1/2 left-0 w-full h-[2px] bg-gradient-to-r from-transparent via-indigo-500/20 to-transparent -translate-y-1/2"></div>
              
              {[
                { step: "1", title: "Transaction Data", icon: Database },
                { step: "2", title: "AI Analysis", icon: Activity },
                { step: "3", title: "Risk Score", icon: TrendingUp },
                { step: "4", title: "SHAP Explanation", icon: Search },
                { step: "5", title: "Investigation", icon: ShieldAlert }
              ].map((s, i) => (
                <div key={i} className="relative z-10 flex flex-col items-center bg-[#030712] p-4 rounded-xl">
                  <div className="w-16 h-16 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center mb-4 shadow-[0_0_15px_rgba(79,70,229,0.2)]">
                    <s.icon className="text-indigo-400" size={28} />
                  </div>
                  <h4 className="text-white font-medium text-sm text-center">{s.title}</h4>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* SECURITY & COMPLIANCE */}
        <section id="security" className="max-w-7xl mx-auto px-6 py-24">
          <div className="bg-gradient-to-br from-indigo-900/20 to-blue-900/10 border border-indigo-500/20 rounded-3xl p-12 text-center relative overflow-hidden">
            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/20 blur-[100px]"></div>
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-500/20 blur-[100px]"></div>
            
            <Shield className="mx-auto text-indigo-400 mb-6" size={48} />
            <h2 className="text-3xl font-bold text-white mb-4 relative z-10">Security & Compliance</h2>
            <p className="text-slate-400 max-w-2xl mx-auto mb-8 relative z-10">
              Built for enterprise financial institutions. Our platform ensures data integrity, strict access control, and complete auditability for all investigation actions.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 relative z-10">
              {['Secure Authentication', 'Role-Based Access', 'Audit Logging', 'Protected Data'].map((tag, i) => (
                <div key={i} className="flex items-center gap-2 bg-[#0B1120] border border-white/10 rounded-full px-4 py-2">
                  <CheckCircle2 size={16} className="text-indigo-400" />
                  <span className="text-sm font-medium text-slate-300">{tag}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="max-w-7xl mx-auto px-6 pb-12 text-center">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Detect Fraud. Understand Risk. <br/> Make Better Decisions.</h2>
          <p className="text-slate-400 mb-8 max-w-xl mx-auto">Use AI-powered fraud detection with transparent, explainable risk analysis.</p>
          <div className="flex justify-center gap-4">
            <Link to="/login" className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-3 rounded-xl font-semibold transition-all">Get Started</Link>
            <Link to="/login" className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-8 py-3 rounded-xl font-semibold transition-all">Login</Link>
          </div>
        </section>
      </main>

      {/* FOOTER */}
      <footer className="border-t border-white/5 bg-[#0B1120] pt-16 pb-8">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          <div className="md:col-span-1">
            <div className="flex items-center gap-2 mb-4">
              <ShieldAlert className="text-indigo-400" size={24} />
              <span className="text-xl font-bold text-white">FraudShield AI</span>
            </div>
            <p className="text-sm text-slate-400">Explainable AI-Based Financial Fraud and Risk Detection System</p>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">About</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><a href="#" className="hover:text-indigo-400">Overview</a></li>
              <li><a href="#" className="hover:text-indigo-400">Mission</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Features</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li><a href="#" className="hover:text-indigo-400">AI Fraud Detection</a></li>
              <li><a href="#" className="hover:text-indigo-400">Explainable AI</a></li>
              <li><a href="#" className="hover:text-indigo-400">Investigation</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-semibold mb-4">Contact</h4>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>Support</li>
              <li>support@fraudshield.ai</li>
            </ul>
          </div>
        </div>
        <div className="max-w-7xl mx-auto px-6 pt-8 border-t border-white/5 text-center text-sm text-slate-500">
          © 2026 FraudShield AI. All rights reserved.
        </div>
      </footer>
    </div>
  );
}
