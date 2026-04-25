import React, { useState } from 'react';

interface PreGameModalProps {
  difficulty: string;
  onStart: (mood: number) => void;
  onCancel: () => void;
}

const PreGameModal: React.FC<PreGameModalProps> = ({ difficulty, onStart, onCancel }) => {
  const [mood, setMood] = useState(5);

  return (
    <div className="p-8 max-w-md w-full bg-white/10 backdrop-blur-2xl rounded-3xl border border-white/20 shadow-2xl text-white">
      <h2 className="text-3xl font-bold mb-2">Check-in</h2>
      <p className="text-slate-300 mb-8 text-sm">How are you feeling right now?</p>

      <div className="space-y-6 mb-10">
        <div className="flex justify-between text-2xl">
          <span>😔</span>
          <span>😐</span>
          <span>😊</span>
        </div>
        <input 
          type="range" 
          min="1" 
          max="10" 
          value={mood} 
          onChange={(e) => setMood(parseInt(e.target.value))}
          className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
        />
        <div className="text-center font-medium text-indigo-300">
          Intensity: {mood}/10
        </div>
      </div>

      <div className="bg-indigo-500/10 p-4 rounded-xl border border-indigo-500/20 mb-8">
        <p className="text-xs uppercase tracking-widest text-indigo-300 mb-1">AI Recommendation</p>
        <p className="font-semibold capitalize">Difficulty: {difficulty}</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <button 
          onClick={onCancel}
          className="py-3 px-6 rounded-2xl bg-white/5 hover:bg-white/10 transition font-medium"
        >
          Cancel
        </button>
        <button 
          onClick={() => onStart(mood)}
          className="py-3 px-6 rounded-2xl bg-indigo-500 hover:bg-indigo-600 transition font-bold shadow-lg shadow-indigo-500/20"
        >
          Begin Session
        </button>
      </div>
    </div>
  );
};

export default PreGameModal;
