import React, { useState } from 'react';

interface PostGameModalProps {
  gameResult: {
    score: number;
    duration: number;
    completed: boolean;
    difficulty: string;
  };
  onSubmit: (moodAfter: number, engagement: number) => void;
}

const PostGameModal: React.FC<PostGameModalProps> = ({ gameResult, onSubmit }) => {
  const [moodAfter, setMoodAfter] = useState(5);
  const [engagement, setEngagement] = useState(5);

  const analysisMap: Record<string, string> = {
    easy_success: "Autonomic regulation achieved. Your ability to maintain a steady flow indicates high receptive capacity today.",
    easy_failure: "Even restorative sessions can be challenging when energy is low. This data point helps us calibrate your baseline.",
    medium_success: "Resilience verified. You managed moderate stimuli effectively, strengthening your cognitive-emotional boundaries.",
    medium_failure: "Adaptive struggle detected. We will lower the stimulation threshold in your next session to prevent burnout.",
    hard_success: "Executive breakthrough! Successfully navigating high-intensity challenges is a strong indicator of recovery momentum.",
    hard_failure: "High-activation attempt logged. Pushing into high-challenge zones is therapeutic in itself, regardless of completion."
  };

  const key = `${gameResult.difficulty}_${gameResult.completed ? 'success' : 'failure'}`;
  const insight = analysisMap[key] || "Session telemetry synced for clinical analysis.";

  return (
    <div className="p-10 max-w-lg w-full bg-[#0f172a]/95 backdrop-blur-3xl rounded-[40px] border border-white/10 shadow-2xl text-white">
      <div className="text-center mb-10">
        <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-6 bg-gradient-to-br ${gameResult.completed ? 'from-emerald-400 to-teal-500' : 'from-rose-400 to-orange-500'} shadow-lg`}>
          <span className="text-4xl">{gameResult.completed ? '✓' : '!'}</span>
        </div>
        <h2 className="text-3xl font-black mb-1">Session Analyzed</h2>
        <p className="text-slate-400 text-sm font-medium">Biometric Telemetry: SYNCED</p>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-2 gap-4 mb-10">
        <div className="p-5 bg-white/5 rounded-3xl border border-white/5">
          <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-1">Flow Points</p>
          <p className="text-3xl font-black text-indigo-400">{gameResult.score.toLocaleString()}</p>
        </div>
        <div className="p-5 bg-white/5 rounded-3xl border border-white/5">
          <p className="text-[10px] text-slate-500 uppercase font-black tracking-widest mb-1">Duration</p>
          <p className="text-3xl font-black text-emerald-400">{gameResult.duration}s</p>
        </div>
      </div>

      {/* Clinical Insight */}
      <div className="bg-white/[0.03] p-6 rounded-3xl border border-white/5 mb-10 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500" />
        <p className="text-xs font-black uppercase tracking-widest text-indigo-400 mb-3">Clinical Insight</p>
        <p className="text-slate-200 text-sm leading-relaxed font-medium">
          {insight}
        </p>
      </div>

      {/* Post-Mood Assessment */}
      <div className="space-y-8 mb-12">
        <div>
          <div className="flex justify-between items-center mb-4">
            <label className="text-xs font-black uppercase tracking-widest text-slate-500">Post-Flow Mood</label>
            <span className="text-xl font-bold text-indigo-300">{moodAfter}/10</span>
          </div>
          <input 
            type="range" 
            min="1" 
            max="10" 
            value={moodAfter} 
            onChange={(e) => setMoodAfter(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-800 rounded-full appearance-none cursor-pointer accent-indigo-500"
          />
        </div>

        <div>
          <label className="text-xs font-black uppercase tracking-widest text-slate-500 mb-4 block">Personalization Rating</label>
          <div className="flex justify-between gap-2">
            {[1, 2, 3, 4, 5].map((level) => (
              <button
                key={level}
                onClick={() => setEngagement(level)}
                className={`flex-1 py-4 rounded-2xl transition-all font-black text-sm border ${
                  engagement === level 
                  ? 'bg-indigo-500 border-indigo-400 shadow-xl shadow-indigo-500/20' 
                  : 'bg-white/5 border-white/10 text-slate-500 hover:bg-white/10 hover:text-slate-300'
                }`}
              >
                {level}
              </button>
            ))}
          </div>
        </div>
      </div>

      <button 
        onClick={() => onSubmit(moodAfter, engagement)}
        className="w-full py-5 rounded-[24px] bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 transition-all font-black text-lg shadow-2xl shadow-indigo-500/20"
      >
        Complete & Save Data
      </button>
    </div>
  );
};

export default PostGameModal;
