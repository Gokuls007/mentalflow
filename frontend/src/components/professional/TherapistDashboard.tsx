import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Users, AlertCircle, TrendingDown, Clipboard, ShieldCheck } from 'lucide-react';

const riskColors: Record<string, string> = {
  high: 'text-red-400 bg-red-400/10 border-red-400/20',
  medium: 'text-amber-400 bg-amber-400/10 border-amber-400/20',
  low: 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
};

const TherapistDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'roster' | 'alerts' | 'trials'>('roster');
  const [selectedPatient, setSelectedPatient] = useState<any>(null);

  const clients = [
    { id: 'C001', name: 'James Wilson', phq9: 22, gad7: 14, risk: 'high', status: 'Deteriorating', week: 1, type: 'PHYSICAL', activity: '5 min walk', progress: [1, 2, 0, 0, 0, 0, 0] },
    { id: 'C002', name: 'Emma Baker', phq9: 8, gad7: 6, risk: 'low', status: 'Stable', week: 4, type: 'SOCIAL', activity: 'Meet for coffee', progress: [1, 1, 1, 1, 1, 1, 0] },
    { id: 'C003', name: 'Sarah Chen', phq9: 14, gad7: 9, risk: 'medium', status: 'Recovering', week: 2, type: 'COGNITIVE', activity: '10 min journaling', progress: [1, 1, 0, 1, 0, 0, 0] },
  ];

  return (
    <div className="min-h-screen bg-[#080c14] text-slate-200">
      <nav className="border-b border-white/5 bg-slate-900/50 backdrop-blur-md px-10 py-4 flex justify-between items-center sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5 text-white" />
          </div>
          <span className="font-bold text-white tracking-tight">MentalFlow Pro <span className="text-[10px] bg-indigo-500/20 text-indigo-400 px-2 py-0.5 rounded ml-2 font-black">PRODUCTION</span></span>
        </div>
        <div className="flex gap-8 text-sm font-medium">
          {['roster', 'alerts', 'trials'].map((tab) => (
            <button 
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`capitalize transition ${activeTab === tab ? 'text-indigo-400' : 'text-slate-500 hover:text-slate-300'}`}
            >
              {tab === 'roster' ? 'Client Roster' : tab === 'alerts' ? 'Safety Alerts' : 'Clinical Trials'}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-3 bg-white/5 px-4 py-2 rounded-xl border border-white/10">
          <div className="w-6 h-6 rounded-full bg-indigo-500/20 flex items-center justify-center text-[10px] font-bold text-indigo-400">SV</div>
          <p className="text-xs font-bold text-indigo-300">Dr. Sarah Vance</p>
        </div>
      </nav>

      <main className="p-10 max-w-7xl mx-auto">
        <header className="mb-12 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-extrabold text-white mb-2">Clinical Oversight</h1>
            <p className="text-slate-500 flex items-center gap-2">
              <Users className="w-4 h-4" />
              65 Active Participants • 4 Critical Actions
            </p>
          </div>
          <div className="flex gap-4">
            <button className="px-6 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-slate-300 font-bold text-sm transition">
              View My Caseload
            </button>
            <button className="px-6 py-2 bg-indigo-500 hover:bg-indigo-600 rounded-xl text-white font-bold text-sm transition shadow-lg shadow-indigo-500/20">
              Onboard Patient
            </button>
          </div>
        </header>

        {/* Client Roster Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {clients.map((client) => (
            <motion.div 
              key={client.id}
              whileHover={{ y: -5 }}
              onClick={() => setSelectedPatient(client)}
              className={`group p-8 rounded-[32px] border transition-all duration-500 cursor-pointer ${
                selectedPatient?.id === client.id ? 'bg-indigo-500/10 border-indigo-500/40 shadow-2xl shadow-indigo-500/10' : 'bg-slate-900/40 border-white/5 hover:border-white/20'
              }`}
            >
              <div className="flex justify-between items-start mb-8">
                <div className="w-14 h-14 rounded-2xl bg-white/5 flex items-center justify-center text-xl font-black text-indigo-400 group-hover:scale-110 transition-transform">
                  {client.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div className="flex flex-col items-end gap-2">
                  <span className={`px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest border ${riskColors[client.risk]}`}>
                    {client.risk} Risk
                  </span>
                  <span className="text-[10px] text-slate-500 font-bold uppercase tracking-tighter">Last Seen: 2h ago</span>
                </div>
              </div>

              <h3 className="text-2xl font-black text-white mb-1 tracking-tight">{client.name}</h3>
              <p className="text-[10px] text-slate-500 mb-8 font-mono tracking-widest uppercase">Clinical ID: MF-{client.id}</p>

              <div className="grid grid-cols-2 gap-4 mb-8">
                <div className="p-4 bg-white/5 rounded-2xl border border-white/5 text-center group-hover:bg-indigo-500/10 transition">
                  <p className="text-[9px] text-slate-500 uppercase font-black tracking-widest mb-1">PHQ-9</p>
                  <p className="text-2xl font-black text-white">{client.phq9}</p>
                </div>
                <div className="p-4 bg-white/5 rounded-2xl border border-white/5 text-center group-hover:bg-emerald-500/10 transition">
                  <p className="text-[9px] text-slate-500 uppercase font-black tracking-widest mb-1">GAD-7</p>
                  <p className="text-2xl font-black text-white">{client.gad7}</p>
                </div>
              </div>

              {/* Behavioral Activation Plan Visibility */}
              <div className="mb-8 p-5 bg-indigo-500/5 rounded-[24px] border border-indigo-500/10 group-hover:border-indigo-500/30 transition">
                <div className="flex justify-between items-center mb-4">
                  <p className="text-[10px] text-indigo-400 font-black uppercase tracking-widest">Protocol Week {client.week}</p>
                  <span className="text-[9px] bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full font-black tracking-tighter">{client.type}</span>
                </div>
                <p className="text-base font-bold text-slate-200 mb-4">{client.activity}</p>
                <div className="flex gap-1.5">
                  {client.progress.map((day: number, idx: number) => (
                    <div 
                      key={idx} 
                      className={`h-2 flex-1 rounded-full transition-all duration-700 ${day === 1 ? 'bg-indigo-400 shadow-sm shadow-indigo-400/50' : 'bg-white/5'}`}
                    />
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between pt-6 border-t border-white/5">
                <div className="flex items-center gap-2 text-[10px] text-slate-500 font-black uppercase tracking-widest">
                  {client.status === 'Deteriorating' ? <TrendingDown className="w-4 h-4 text-red-400" /> : <TrendingDown className="w-4 h-4 text-emerald-400 rotate-180" />}
                  <span>{client.status}</span>
                </div>
                <button className="text-indigo-400 text-xs font-black uppercase tracking-widest hover:text-white transition">
                  Adjust Plan →
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
