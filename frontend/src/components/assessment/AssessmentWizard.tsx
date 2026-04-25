import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { apiService } from '../../services/api';

const phq9Questions = [
  "Little interest or pleasure in doing things?",
  "Feeling down, depressed, or hopeless?",
  "Trouble falling or staying asleep, or sleeping too much?",
  "Feeling tired or having little energy?",
  "Poor appetite or overeating?",
  "Feeling bad about yourself — or that you are a failure or have let yourself or your family down?",
  "Trouble concentrating on things, such as reading the newspaper or watching television?",
  "Moving or speaking so slowly that other people could have noticed? Or the opposite — being so fidgety or restless that you have been moving around a lot more than usual?",
  "Thoughts that you would be better off dead or of hurting yourself in some way?"
];

const phq9Options = [
  "Not at all",
  "Several days",
  "More than half the days",
  "Nearly every day"
];

const AssessmentWizard: React.FC<{ type: 'phq9' | 'gad7', onComplete: (result: any) => void }> = ({ type, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [responses, setResponses] = useState<number[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSelect = (value: number) => {
    const newResponses = [...responses];
    newResponses[currentStep] = value;
    setResponses(newResponses);

    if (currentStep < phq9Questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      submitAssessment(newResponses);
    }
  };

  const submitAssessment = async (finalResponses: number[]) => {
    setIsSubmitting(true);
    try {
      const result = await apiService.submitAssessment(type, finalResponses);
      onComplete(result);
    } catch (error) {
      console.error("Assessment submission failed", error);
      // Still proceed even if submission fails (demo mode)
      const totalScore = finalResponses.reduce((a, b) => a + b, 0);
      onComplete({
        type,
        total_score: totalScore,
        severity: totalScore <= 4 ? 'minimal' : totalScore <= 9 ? 'mild' : totalScore <= 14 ? 'moderate' : 'severe',
        submitted_at: new Date().toISOString()
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const progress = ((currentStep + 1) / phq9Questions.length) * 100;

  return (
    <div className="max-w-2xl w-full mx-auto p-8 bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl">
      <div className="mb-12">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-sm font-bold uppercase tracking-widest text-indigo-400">
            {type.toUpperCase()} Assessment
          </h2>
          <span className="text-xs text-slate-500">Step {currentStep + 1} of {phq9Questions.length}</span>
        </div>
        <div className="w-full h-1 bg-slate-800 rounded-full overflow-hidden">
          <motion.div 
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            className="h-full bg-indigo-500"
          />
        </div>
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          className="min-h-[300px]"
        >
          <h3 className="text-2xl font-bold text-white mb-10 leading-tight">
            {phq9Questions[currentStep]}
          </h3>

          <div className="grid grid-cols-1 gap-4">
            {phq9Options.map((option, idx) => (
              <button
                key={idx}
                onClick={() => handleSelect(idx)}
                className="group relative p-5 rounded-2xl bg-white/5 border border-white/10 text-left hover:bg-indigo-500/10 hover:border-indigo-500/50 transition-all duration-300"
              >
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 group-hover:text-white transition">{option}</span>
                  <div className="w-6 h-6 rounded-full border border-slate-700 group-hover:bg-indigo-500 group-hover:border-indigo-400 transition" />
                </div>
              </button>
            ))}
          </div>
        </motion.div>
      </AnimatePresence>

      <div className="mt-12 flex justify-between items-center text-xs text-slate-500">
        <p>This information is confidential and used for clinical titration.</p>
        {currentStep > 0 && (
          <button onClick={() => setCurrentStep(currentStep - 1)} className="hover:text-white transition">
            ← Previous Question
          </button>
        )}
      </div>
    </div>
  );
};

export default AssessmentWizard;
