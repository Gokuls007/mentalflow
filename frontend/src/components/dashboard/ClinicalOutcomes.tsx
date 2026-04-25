import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { apiService } from '../../services/api';

interface ProgressData {
  depression: {
    baseline: number;
    current: number;
    target: number;
    progress_percent: number;
    improved_by: number;
    remaining: number;
    status: string;
  };
  anxiety: {
    baseline: number;
    current: number;
    target: number;
    progress_percent: number;
    improved_by: number;
    remaining: number;
    status: string;
  };
  overall_progress: number;
  milestone: string;
}

export const ClinicalOutcomes: React.FC = () => {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProgress = async () => {
      try {
        const response = await apiService.instance_.get('/clinical/progress/me');
        setProgress(response.data);
      } catch (err) {
        console.error('Error fetching clinical progress:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchProgress();
  }, []);

  if (loading) {
    return (
      <div className="p-8 rounded-3xl bg-white/[0.03] border border-white/5 animate-pulse">
        <div className="h-8 w-48 bg-white/10 rounded mb-4" />
        <div className="h-32 w-full bg-white/5 rounded-2xl" />
      </div>
    );
  }

  if (!progress) return null;

  return (
    <div className="space-y-8 p-1">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-black tracking-tight text-white mb-2">Recovery Journey</h2>
          <p className="text-emerald-400/80 font-bold text-xs uppercase tracking-[0.2em]">{progress.milestone}</p>
        </div>
        <div className="text-right">
          <span className="text-4xl font-black text-indigo-400">Week 1</span>
          <p className="text-[10px] font-black uppercase tracking-widest text-slate-500">BA Protocol</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Depression Card */}
        <motion.div 
          className="relative overflow-hidden p-8 rounded-[32px] bg-gradient-to-br from-indigo-500/20 to-indigo-900/40 border border-indigo-500/20"
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-lg font-black text-indigo-300 mb-1">Depression (PHQ-9)</h3>
              <p className="text-xs text-indigo-400/80 font-bold tracking-wide uppercase">Target: &lt;5 Minimal</p>
            </div>
            <div className="text-right">
              <span className="text-4xl font-black text-white">{progress.depression.current}</span>
              <p className="text-[10px] text-indigo-400 font-black uppercase mt-1">Current Score</p>
            </div>
          </div>

          <div className="mb-8">
            <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-indigo-400/60 mb-2">
              <span>Baseline: {progress.depression.baseline}</span>
              <span>Goal: {progress.depression.target}</span>
            </div>
            <div className="h-3 bg-indigo-950/50 rounded-full overflow-hidden border border-white/5">
              <motion.div 
                className="h-full bg-gradient-to-r from-indigo-500 to-emerald-400"
                initial={{ width: 0 }}
                animate={{ width: `${progress.depression.progress_percent}%` }}
                transition={{ duration: 1.5, ease: "easeOut" }}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
              <p className="text-[10px] text-indigo-400 font-black uppercase mb-1">Improved</p>
              <p className="text-xl font-black text-emerald-400">-{progress.depression.improved_by}</p>
            </div>
            <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
              <p className="text-[10px] text-indigo-400 font-black uppercase mb-1">Remaining</p>
              <p className="text-xl font-black text-white">{progress.depression.remaining} pts</p>
            </div>
          </div>
        </motion.div>

        {/* Anxiety Card */}
        <motion.div 
          className="relative overflow-hidden p-8 rounded-[32px] bg-gradient-to-br from-purple-500/20 to-purple-900/40 border border-purple-500/20"
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
        >
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-lg font-black text-purple-300 mb-1">Anxiety (GAD-7)</h3>
              <p className="text-xs text-purple-400/80 font-bold tracking-wide uppercase">Target: &lt;5 Minimal</p>
            </div>
            <div className="text-right">
              <span className="text-4xl font-black text-white">{progress.anxiety.current}</span>
              <p className="text-[10px] text-purple-400 font-black uppercase mt-1">Current Score</p>
            </div>
          </div>

          <div className="mb-8">
            <div className="flex justify-between text-[10px] font-black uppercase tracking-widest text-purple-400/60 mb-2">
              <span>Baseline: {progress.anxiety.baseline}</span>
              <span>Goal: {progress.anxiety.target}</span>
            </div>
            <div className="h-3 bg-purple-950/50 rounded-full overflow-hidden border border-white/5">
              <motion.div 
                className="h-full bg-gradient-to-r from-purple-500 to-emerald-400"
                initial={{ width: 0 }}
                animate={{ width: `${progress.anxiety.progress_percent}%` }}
                transition={{ duration: 1.5, ease: "easeOut" }}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
              <p className="text-[10px] text-purple-400 font-black uppercase mb-1">Improved</p>
              <p className="text-xl font-black text-emerald-400">-{progress.anxiety.improved_by}</p>
            </div>
            <div className="p-4 bg-white/5 rounded-2xl border border-white/5">
              <p className="text-[10px] text-purple-400 font-black uppercase mb-1">Remaining</p>
              <p className="text-xl font-black text-white">{progress.anxiety.remaining} pts</p>
            </div>
          </div>
        </motion.div>
      </div>

      <div className="bg-emerald-500/10 border border-emerald-500/20 p-6 rounded-[28px] flex items-center gap-4">
        <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center text-2xl">✨</div>
        <div>
          <p className="text-emerald-300 font-bold">Every activity is a clinical step forward.</p>
          <p className="text-emerald-300/60 text-xs">Your brain is neuroplastically adapting to these behavioral successes.</p>
        </div>
      </div>
    </div>
  );
};
