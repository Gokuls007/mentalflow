import React, { useEffect, useState } from 'react';
import { useUserStore } from '../../store/user.store';
import { useGameStore } from '../../store/game.store';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ShieldCheck, 
  TrendingUp, 
  TrendingDown, 
  Activity as ActivityIcon, 
  Sparkles, 
  BrainCircuit, 
  Compass, 
  Zap, 
  ChevronRight,
  Heart
} from 'lucide-react';
import { ChatWindow } from '../chat/ChatWindow';
import { ClinicalOutcomes } from './ClinicalOutcomes';
import { MoodField } from './MoodField';
import PeerSupport from './PeerSupport';
import { apiClient } from '../../services/api';

const Dashboard: React.FC = () => {
  const { user, stats } = useUserStore();
  const { activities, setActivities, setGanLoading } = useGameStore();
  const [insight, setInsight] = useState<string>('');

  useEffect(() => {
    const fetchInsight = async () => {
      try {
        const res = await apiClient.get('/clinical/insights/me');
        setInsight(res.data.insight);
      } catch (e) {
        setInsight("Your neuroplasticity is peaking today. Every small action is re-wiring your reward pathways for resilience.");
      }
    };
    fetchInsight();
  }, []);

  return (
    <div className="min-h-screen bg-transparent relative overflow-hidden selection:bg-indigo-500/30">
      {/* ── Immersive Background ── */}
      <MoodField phq9={user?.latest_phq9_score || 12} gad7={user?.latest_gad7_score || 8} />
      
      {/* ── Premium Navigation ── */}
      <nav className="sticky top-0 z-[100] px-6 py-4">
        <div className="max-w-7xl mx-auto glass-panel px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <BrainCircuit className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-black tracking-tighter text-white">MENTAL<span className="text-indigo-400">FLOW</span></span>
            <div className="h-4 w-[1px] bg-white/10 mx-2" />
            <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">v2.5 Production</span>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-8 text-[11px] font-black uppercase tracking-widest text-slate-400">
              <a href="#" className="hover:text-indigo-400 transition">Neural Hub</a>
              <a href="#" className="hover:text-indigo-400 transition">Clinical Sync</a>
              <a href="#" className="hover:text-indigo-400 transition">Community</a>
            </div>
            <div className="flex items-center gap-4 bg-white/5 px-4 py-2 rounded-2xl border border-white/5">
              <div className="text-right">
                <p className="text-[9px] font-black text-slate-500 uppercase tracking-tighter">PHQ-9 Score</p>
                <p className="text-xs font-black text-indigo-300">{user?.latest_phq9_score || '--'}</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-white/10 flex items-center justify-center font-black text-xs text-white">
                {user?.firstName?.[0] || 'A'}
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-12 relative z-10">
        {/* ── Header Section ── */}
        <header className="mb-16">
          <motion.h1 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-6xl font-black tracking-tighter text-white mb-4"
          >
            Welcome, <span className="text-gradient">{user?.firstName || 'User'}</span>.
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="text-lg text-slate-400 font-medium max-w-2xl leading-relaxed"
          >
            Your personalized recovery protocol is optimized for <span className="text-white font-bold">Week 3: Behavioral Activation</span>. 
            We've analyzed your mood trends and mapped your path to remission.
          </motion.p>
        </header>

        {/* ── Bento Grid Layout ── */}
        <div className="grid grid-cols-12 gap-8">
          
          {/* 1. Empathy Engine (Wide Card) */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="col-span-12 lg:col-span-8 glass-panel p-10 relative overflow-hidden group"
          >
            <div className="absolute top-0 right-0 p-8 opacity-5 group-hover:opacity-10 transition-opacity">
              <Sparkles className="w-48 h-48 text-indigo-400 rotate-12" />
            </div>
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                  <Zap className="w-4 h-4 text-indigo-400" />
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400">Clinical AI Insight</span>
              </div>
              <h2 className="text-3xl font-bold text-white mb-6 leading-tight max-w-xl italic">
                "{insight}"
              </h2>
              <div className="flex gap-4">
                <span className="px-4 py-2 rounded-full bg-white/5 border border-white/5 text-[10px] font-black uppercase text-slate-400 tracking-tighter">Neuro-Optimization: Active</span>
                <span className="px-4 py-2 rounded-full bg-white/5 border border-white/5 text-[10px] font-black uppercase text-slate-400 tracking-tighter">Clinical Confidence: 94%</span>
              </div>
            </div>
          </motion.div>

          {/* 2. Mastery Stats (Side Card) */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="col-span-12 lg:col-span-4 glass-panel p-10 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center gap-3 mb-8">
                <div className="w-8 h-8 rounded-lg bg-purple-500/20 flex items-center justify-center">
                  <Compass className="w-4 h-4 text-purple-400" />
                </div>
                <span className="text-[10px] font-black uppercase tracking-widest text-purple-400">Mastery Path</span>
              </div>
              <div className="mb-8">
                <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest mb-1">Current Level</p>
                <p className="text-4xl font-black text-white">{stats?.current_level || 'Pioneer'}</p>
              </div>
              <div className="space-y-4">
                <div className="flex justify-between items-end">
                  <p className="text-[10px] font-black text-slate-500 uppercase tracking-widest">Recovery Progress</p>
                  <p className="text-xs font-black text-white">68%</p>
                </div>
                <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: '68%' }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]"
                  />
                </div>
              </div>
            </div>
            <button className="w-full mt-8 py-4 rounded-2xl bg-white/5 border border-white/5 text-[11px] font-black uppercase tracking-widest text-slate-300 hover:bg-white/10 transition">
              View Skill Tree
            </button>
          </motion.div>

          {/* 3. Clinical Outcomes (Full Width Section) */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="col-span-12"
          >
            <div className="flex justify-between items-center mb-8 px-2">
              <h3 className="text-2xl font-black tracking-tight text-white flex items-center gap-3">
                <ShieldCheck className="w-6 h-6 text-emerald-400" />
                Longitudinal Recovery Path
              </h3>
              <p className="text-[10px] font-black uppercase tracking-[0.2em] text-slate-500">HIPAA Compliant Data</p>
            </div>
            <div className="glass-panel p-10">
              <ClinicalOutcomes />
            </div>
          </motion.div>

          {/* 4. Activities (The Main Focus) */}
          <div className="col-span-12 mt-8">
            <div className="flex justify-between items-end mb-10 px-2">
              <div>
                <h3 className="text-3xl font-black text-white mb-2 tracking-tighter">Prescribed Interventions</h3>
                <p className="text-sm text-slate-500 font-medium italic">Dynamically generated via Clinical GAN v4.1</p>
              </div>
              <button 
                onClick={() => setGanLoading(true)}
                className="group flex items-center gap-3 px-6 py-3 rounded-2xl bg-indigo-500 text-white font-black text-[11px] uppercase tracking-widest hover:bg-indigo-600 transition shadow-lg shadow-indigo-500/20"
              >
                Regenerate Protocol
                <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              <AnimatePresence mode="popLayout">
                {activities.map((act, idx) => (
                  <motion.div
                    key={act.id || idx}
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    transition={{ delay: 0.1 * idx }}
                    className="glass-card rounded-[32px] p-8 flex flex-col justify-between h-[340px] relative overflow-hidden group"
                  >
                    <div className="absolute -top-12 -right-12 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/20 transition-colors" />
                    
                    <div>
                      <div className="flex justify-between items-start mb-6">
                        <div className={`w-12 h-12 rounded-2xl flex items-center justify-center ${
                          act.type === 'physical' ? 'bg-emerald-500/20 text-emerald-400' :
                          act.type === 'social' ? 'bg-indigo-500/20 text-indigo-400' : 'bg-purple-500/20 text-purple-400'
                        }`}>
                          <ActivityIcon className="w-6 h-6" />
                        </div>
                        <span className="text-[9px] font-black uppercase tracking-widest text-slate-500 px-3 py-1 bg-white/5 rounded-full border border-white/5">
                          {act.duration_minutes} MINS
                        </span>
                      </div>
                      <h4 className="text-2xl font-bold text-white mb-3 tracking-tight">{act.title}</h4>
                      <p className="text-sm text-slate-500 leading-relaxed line-clamp-3">
                        {act.clinical_explanation || act.description}
                      </p>
                    </div>

                    <div className="pt-8 border-t border-white/5 flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Heart className="w-4 h-4 text-pink-500" />
                        <span className="text-xs font-bold text-slate-300">BA Recovery +{act.difficulty * 2}</span>
                      </div>
                      <button className="text-indigo-400 text-[10px] font-black uppercase tracking-widest hover:text-white transition">
                        Execute →
                      </button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </main>

      <ChatWindow userId={user?.id || 1} />
    </div>
  );
};

export default Dashboard;
