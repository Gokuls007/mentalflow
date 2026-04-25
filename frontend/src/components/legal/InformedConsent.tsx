import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Shield, Lock, FileText, CheckCircle } from 'lucide-react';

const InformedConsent: React.FC<{ onAccept: () => void }> = ({ onAccept }) => {
  const [agreed, setAgreed] = useState(false);

  return (
    <div className="min-h-screen bg-[#0f172a] flex items-center justify-center p-6 bg-gradient-to-tr from-[#020617] via-[#0f172a] to-indigo-950/20">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-4xl w-full bg-white/[0.03] backdrop-blur-2xl p-12 rounded-[48px] border border-white/10 shadow-3xl"
      >
        <div className="flex gap-12 items-start">
          {/* Left: Info */}
          <div className="flex-1">
            <header className="mb-10">
              <div className="inline-flex py-1 px-3 bg-indigo-500/10 rounded-full border border-indigo-500/30 text-xs font-bold text-indigo-400 uppercase tracking-widest mb-4">
                Clinical Trial Protocol v1.0
              </div>
              <h1 className="text-4xl font-extrabold text-white tracking-tight leading-tight">
                MentalFlow Informed Consent
              </h1>
            </header>

            <div className="space-y-8 text-slate-400 leading-relaxed text-sm">
              <div className="flex gap-4">
                <Shield className="w-5 h-5 text-indigo-400 shrink-0" />
                <div>
                  <h3 className="text-white font-bold mb-1">Privacy & Data Security</h3>
                  <p>Your health data is protected using HIPAA-grade AES-256 encryption. We remove all identifiers (PII) before using data for research purposes.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <Lock className="w-5 h-5 text-emerald-400 shrink-0" />
                <div>
                  <h3 className="text-white font-bold mb-1">Crisis Protocol</h3>
                  <p>In the event of acute distress or suicidal ideation, our safety protocol will trigger an automatic lockout and connect you with emergency services.</p>
                </div>
              </div>
              <div className="flex gap-4">
                <FileText className="w-5 h-5 text-purple-400 shrink-0" />
                <div>
                  <h3 className="text-white font-bold mb-1">Voluntary Participation</h3>
                  <p>You may withdraw from this study at any time without penalty. Your participation helps us validate Behavioral Activation efficacy for digital interventions.</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Actions */}
          <div className="w-80 p-8 bg-white/[0.02] rounded-[32px] border border-white/5">
            <h3 className="text-lg font-bold text-white mb-6">Agreement</h3>
            <div className="space-y-4 mb-10">
              {["I understand the risks", "I consent to data collection", "I am 18 or older"].map((text, i) => (
                <div key={i} className="flex items-center gap-3">
                  <CheckCircle className="w-4 h-4 text-emerald-500" />
                  <span className="text-xs text-slate-400">{text}</span>
                </div>
              ))}
            </div>

            <button 
              onClick={() => setAgreed(!agreed)}
              className={`w-full py-4 rounded-2xl mb-4 text-xs font-bold transition-all border ${
                agreed 
                ? 'bg-indigo-500 text-white border-transparent shadow-lg shadow-indigo-500/20' 
                : 'bg-white/5 text-slate-500 border-white/10 hover:bg-white/10'
              }`}
            >
              {agreed ? 'Agreed & Signed' : 'Click to Sign Digitally'}
            </button>

            <button 
              disabled={!agreed}
              onClick={onAccept}
              className={`w-full py-4 rounded-2xl font-black transition-all ${
                agreed 
                ? 'bg-gradient-to-r from-emerald-500 to-indigo-500 hover:from-emerald-600 hover:to-indigo-600 text-white shadow-xl translate-y-0' 
                : 'bg-slate-800 text-slate-600 cursor-not-allowed translate-y-2 opacity-50'
              }`}
            >
              Continue to Onboarding
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default InformedConsent;
