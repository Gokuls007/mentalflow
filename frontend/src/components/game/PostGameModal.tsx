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

  return (
    <div className="p-8 max-w-lg w-full bg-slate-800/80 backdrop-blur-2xl rounded-3xl border border-white/10 shadow-2xl text-white">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold mb-2">Session Complete</h2>
        <p className="text-slate-400 text-sm italic">Training the Clinical Agent...</p>
      </div>

      {/* Stats Summary */}
      <div className="grid grid-cols-3 gap-4 mb-10">
        <div className="p-4 bg-white/5 rounded-2xl text-center">
          <p className="text-xs text-slate-400 uppercase mb-1">Score</p>
          <p className="text-2xl font-bold text-indigo-400">{gameResult.score}</p>
        </div>
        <div className="p-4 bg-white/5 rounded-2xl text-center">
          <p className="text-xs text-slate-400 uppercase mb-1">Time</p>
          <p className="text-2xl font-bold text-emerald-400">{gameResult.duration}s</p>
        </div>
        <div className="p-4 bg-white/5 rounded-2xl text-center">
          <p className="text-xs text-slate-400 uppercase mb-1">Status</p>
          <p className={`text-sm font-bold uppercase mt-2 ${gameResult.completed ? 'text-green-400' : 'text-red-400'}`}>
            {gameResult.completed ? 'Goal Met' : 'Incomplete'}
          </p>
        </div>
      </div>

      {/* Mood Assessment After */}
      <div className="space-y-8 mb-10">
        <div>
          <label className="block text-sm text-slate-400 mb-4">How do you feel AFTER the activity?</label>
          <input 
            type="range" 
            min="1" 
            max="10" 
            value={moodAfter} 
            onChange={(e) => setMoodAfter(parseInt(e.target.value))}
            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
          />
          <div className="flex justify-between text-xs text-slate-500 mt-2">
            <span>Low Energy</span>
            <span className="text-indigo-300 font-bold">{moodAfter}/10</span>
            <span>High Energy</span>
          </div>
        </div>

        <div>
          <label className="block text-sm text-slate-400 mb-4">How engaging did you find this session?</label>
          <div className="flex justify-between gap-2">
            {[1, 2, 3, 4, 5].map((level) => (
              <button
                key={level}
                onClick={() => setEngagement(level)}
                className={`flex-1 py-3 rounded-xl transition font-bold border ${
                  engagement === level 
                  ? 'bg-indigo-500 border-indigo-400 shadow-lg shadow-indigo-500/20' 
                  : 'bg-white/5 border-white/10 text-slate-400 hover:bg-white/10'
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
        className="w-full py-4 rounded-2xl bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 transition font-bold text-lg shadow-xl"
      >
        Save & Sync Report
      </button>
    </div>
  );
};

export default PostGameModal;
