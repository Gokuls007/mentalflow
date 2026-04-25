import React from 'react';
import { motion } from 'framer-motion';
import { AlertTriangle, Phone, MessageSquare, Globe } from 'lucide-react';

interface CrisisOverlayProps {
  level: number;
  onClose?: () => void;
}

const CrisisOverlay: React.FC<CrisisOverlayProps> = ({ level }) => {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-950 px-6"
    >
      {/* Background Warning Pulses */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-red-600/10 rounded-full blur-[120px] animate-pulse" />
      </div>

      <div className="relative max-w-xl w-full bg-white/5 backdrop-blur-3xl p-10 rounded-[40px] border border-red-500/30 text-center shadow-2xl">
        <div className="w-20 h-20 bg-red-500/20 rounded-full flex items-center justify-center mx-auto mb-8">
          <AlertTriangle className="text-red-500 w-10 h-10" />
        </div>

        <h2 className="text-3xl font-black text-white mb-4 tracking-tight">Your Safety is Our Priority</h2>
        <p className="text-slate-400 mb-10 leading-relaxed text-lg">
          Based on your recent responses, we have activated our clinical safety protocol. Please connect with one of these free, confidential resources immediately.
        </p>

        <div className="grid grid-cols-1 gap-4 mb-10">
          <a 
            href="tel:988" 
            className="flex items-center justify-between p-6 bg-red-500 hover:bg-red-600 rounded-2xl transition-all shadow-lg shadow-red-500/20 group"
          >
            <div className="flex items-center gap-4 text-left">
              <Phone className="w-6 h-6 text-white" />
              <div>
                <p className="font-bold text-white">Call 988</p>
                <p className="text-red-100 text-xs uppercase tracking-widest font-bold">Suicide & Crisis Lifeline</p>
              </div>
            </div>
            <span className="text-red-200 group-hover:translate-x-1 transition-transform">→</span>
          </a>

          <a 
            href="sms:741741?&body=HOME" 
            className="flex items-center justify-between p-6 bg-white/5 hover:bg-white/10 rounded-2xl transition-all border border-white/10 group"
          >
            <div className="flex items-center gap-4 text-left">
              <MessageSquare className="w-6 h-6 text-indigo-400" />
              <div>
                <p className="font-bold text-white">Text HOME to 741741</p>
                <p className="text-slate-500 text-xs">Crisis Text Line (24/7)</p>
              </div>
            </div>
            <span className="text-slate-600 group-hover:translate-x-1 transition-transform">→</span>
          </a>

          <a 
            href="https://www.iasp.info/resources/Crisis_Centres/" 
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between p-6 bg-white/5 hover:bg-white/10 rounded-2xl transition-all border border-white/10 group"
          >
            <div className="flex items-center gap-4 text-left">
              <Globe className="w-6 h-6 text-emerald-400" />
              <div>
                <p className="font-bold text-white">International Resources</p>
                <p className="text-slate-500 text-xs">Global Crisis Center Locator</p>
              </div>
            </div>
            <span className="text-slate-600 group-hover:translate-x-1 transition-transform">→</span>
          </a>
        </div>

        <p className="text-xs text-slate-500 italic">
          Emergency Services are available at 911. Please do not isolate yourself during this time.
        </p>
      </div>
    </motion.div>
  );
};

export default CrisisOverlay;
