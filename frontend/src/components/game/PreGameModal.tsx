import React, { useState } from 'react';

interface PreGameModalProps {
  difficulty: string;
  onStart: (mood: number) => void;
  onCancel: () => void;
}

const PreGameModal: React.FC<PreGameModalProps> = ({ difficulty, onStart, onCancel }) => {
  const [mood, setMood] = useState(5);

  const intentMap: Record<string, string> = {
    easy: "Restorative Protocol: Lowering autonomic arousal through gentle, rhythmic flow.",
    medium: "Maintenance Protocol: Balancing cognitive load to stabilize emotional regulation.",
    hard: "Activation Protocol: High-intensity engagement to break through depressive rumination."
  };

  return (
    <div className="p-10 max-w-lg w-full bg-[#0f172a]/95 backdrop-blur-3xl rounded-[40px] border border-white/10 shadow-2xl text-white">
      <div className="mb-10">
        <h2 className="text-4xl font-black mb-2 tracking-tight">Session Check-in</h2>
        <p className="text-slate-400">The Clinical Agent is synchronizing with your current state.</p>
      </div>

      <div className="space-y-8 mb-12">
        <div className="flex justify-between items-end">
          <label className="text-sm font-bold uppercase tracking-widest text-slate-500">Current Energy</label>
          <span className="text-3xl font-black text-indigo-400">{mood}/10</span>
        </div>
        <input 
          type="range" 
          min="1" 
          max="10" 
          value={mood} 
          onChange={(e) => setMood(parseInt(e.target.value))}
          className="w-full h-3 bg-slate-800 rounded-full appearance-none cursor-pointer accent-indigo-500"
        />
        <div className="flex justify-between text-xs text-slate-500 px-1">
          <span>Slight / Dull</span>
          <span>Intense / Vibrant</span>
        </div>
      </div>

      <div className="bg-gradient-to-br from-indigo-500/10 to-purple-500/10 p-6 rounded-3xl border border-white/5 mb-10">
        <div className="flex items-center gap-3 mb-4">
          <div className={`w-3 h-3 rounded-full animate-pulse ${difficulty === 'hard' ? 'bg-red-500' : (difficulty === 'medium' ? 'bg-amber-500' : 'bg-emerald-500')}`} />
          <p className="text-xs uppercase tracking-widest text-slate-400 font-bold">Clinical Intent — {difficulty}</p>
        </div>
        <p className="text-slate-200 leading-relaxed italic font-medium">
          "{intentMap[difficulty] || "Custom adaptive session."}"
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <button 
          onClick={onCancel}
          className="py-4 px-6 rounded-2xl bg-white/5 hover:bg-white/10 transition-all font-bold border border-white/5"
        >
          Postpone
        </button>
        <button 
          onClick={() => onStart(mood)}
          className="py-4 px-6 rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 transition-all font-bold shadow-xl shadow-indigo-500/20"
        >
          Begin Protocol
        </button>
      </div>
    </div>
  );
};

export default PreGameModal;
