import React from 'react';
import { motion } from 'framer-motion';
import { MessageSquare, Users, Heart } from 'lucide-react';

const PeerSupport: React.FC = () => {
  const posts = [
    { id: 1, user: 'User442', text: 'Just completed my first 5-min walk of Week 1. It was hard to get out but I feel slightly better now.', likes: 12, week: 1 },
    { id: 2, user: 'PathFinder', text: 'Week 3 of Social Activation - finally met a friend for coffee today! It gets easier everyone, keep going.', likes: 24, week: 3 },
    { id: 3, user: 'QuietMind', text: 'Micro-win: I drank 1L of water today and did a 2-min stretch. Small steps count.', likes: 18, week: 2 },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-black text-white mb-1">Peer Support</h2>
          <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Anonymous Community Feed</p>
        </div>
        <div className="flex gap-2">
          <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[10px] font-black text-slate-400">#Physical</span>
          <span className="px-3 py-1 bg-white/5 border border-white/10 rounded-full text-[10px] font-black text-slate-400">#Social</span>
        </div>
      </div>

      <div className="space-y-4">
        {posts.map((post, idx) => (
          <motion.div 
            key={post.id}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="p-5 bg-white/[0.03] backdrop-blur-xl rounded-[28px] border border-white/5 hover:border-white/10 transition-all group"
          >
            <div className="flex justify-between items-start mb-3">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-[10px] font-black text-white">
                  {post.user[0]}
                </div>
                <span className="text-xs font-black text-indigo-300">{post.user}</span>
                <span className="text-[10px] text-slate-600 font-bold tracking-tighter">BA Week {post.week}</span>
              </div>
              <button className="text-slate-600 group-hover:text-rose-400 transition-colors flex items-center gap-1">
                <Heart className="w-3 h-3 fill-current" />
                <span className="text-[10px] font-black">{post.likes}</span>
              </button>
            </div>
            <p className="text-sm text-slate-300 font-medium leading-relaxed italic">"{post.text}"</p>
            
            <div className="mt-4 pt-4 border-t border-white/5 flex gap-4">
              <button className="text-[10px] font-black text-slate-500 hover:text-indigo-400 uppercase tracking-widest transition flex items-center gap-1">
                <MessageSquare className="w-3 h-3" />
                Reply
              </button>
              <button className="text-[10px] font-black text-slate-500 hover:text-emerald-400 uppercase tracking-widest transition flex items-center gap-1">
                <Heart className="w-3 h-3" />
                Support
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      <button className="w-full py-4 bg-white/5 hover:bg-white/10 border border-white/10 rounded-2xl text-[11px] font-black uppercase tracking-[0.2em] text-slate-400 transition">
        Join the Squad →
      </button>
    </div>
  );
};

export default PeerSupport;
