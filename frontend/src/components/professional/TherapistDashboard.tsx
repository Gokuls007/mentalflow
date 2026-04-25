import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, AlertCircle, TrendingDown, Clipboard, ShieldCheck } from 'lucide-react';

const riskColors: Record<string, string> = {
  high: 'text-red-400 bg-red-400/10 border-red-400/20',
  medium: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
  low: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
};

const TherapistDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'roster' | 'alerts'>('roster');

  const clients = [
    { id: 'C001', name: 'James Wilson', phq9: 22, gad7: 14, risk: 'high', status: 'Deteriorating' },
    { id: 'C002', name: 'Emma Baker', phq9: 8, gad7: 6, risk: 'low', status: 'Stable' },
    { id: 'C003', name: 'Sarah Chen', phq9: 14, gad7: 9, risk: 'medium', status: 'Recovering' },
    { id: 'C004', name: 'Michael Ross', phq9: 4, gad7: 3, risk: 'low', status: 'Stable' },
  ];

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-200">
      <nav className="border-b border-white/5 bg-slate-900/50 backdrop-blur-md px-10 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-white tracking-tight">MentalFlow Pro</span>
        </div>
        <div className="flex gap-8 text-sm font-medium">
          <button 
            onClick={() => setActiveTab('roster')}
            className={activeTab === 'roster' ? 'text-indigo-400' : 'text-slate-500 hover:text-slate-300'}
          >
            Client Roster
          </button>
          <button 
            onClick={() => setActiveTab('alerts')}
            className={activeTab === 'alerts' ? 'text-indigo-400' : 'text-slate-500 hover:text-slate-300'}
          >
            Safety Alerts
          </button>
        </div>
        <div className="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-xl border border-white/10">
          <p className="text-xs font-bold text-indigo-300">Dr. Sarah Vance</p>
        </div>
      </nav>

      <main className="p-10 max-w-7xl mx-auto">
        <header className="mb-12 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-extrabold text-white mb-2">Clinical Oversight</h1>
            <p className="text-slate-500">Managing 65 active participants • 4 Urgent Actions Required</p>
          </div>
          <div className="flex gap-4">
            <button className="px-6 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-xl text-white font-bold text-sm transition shadow-lg shadow-indigo-500/20">
              Export HIPAA Dataset
            </button>
          </div>
        </header>

        {/* Client Roster Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clients.map((client) => (
            <motion.div 
              key={client.id}
              whileHover={{ y: -5 }}
              className="group p-6 bg-slate-900/40 rounded-3xl border border-white/5 hover:border-white/20 transition-all duration-300 shadow-xl"
            >
              <div className="flex justify-between items-start mb-6">
                <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center text-indigo-400 font-bold">
                  {client.name.split(' ').map(n => n[0]).join('')}
                </div>
                <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${riskColors[client.risk]}`}>
                  {client.risk} Risk
                </span>
              </div>

              <h3 className="text-xl font-bold text-white mb-1">{client.name}</h3>
              <p className="text-xs text-slate-500 mb-6 font-mono">ID: {client.id}</p>

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="p-3 bg-white/5 rounded-xl border border-white/5 text-center">
                  <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">PHQ-9 (Latest)</p>
                  <p className="text-xl font-black text-indigo-300">{client.phq9}</p>
                </div>
                <div className="p-3 bg-white/5 rounded-xl border border-white/5 text-center">
                  <p className="text-[10px] text-slate-500 uppercase font-bold mb-1">GAD-7 (Latest)</p>
                  <p className="text-xl font-black text-emerald-300">{client.gad7}</p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-6 border-t border-white/5">
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  {client.status === 'Deteriorating' ? <TrendingDown className="w-3 h-3 text-red-400" /> : <AlertCircle className="w-3 h-3 text-indigo-400" />}
                  <span>{client.status}</span>
                </div>
                <button className="text-indigo-400 text-xs font-bold hover:underline transition">
                  Full Clinical History →
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </main>
    </div>
  );
};

export default TherapistDashboard;
