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

const gad7Questions = [
  "Feeling nervous, anxious, or on edge?",
  "Not being able to stop or control worrying?",
  "Worrying too much about different things?",
  "Trouble relaxing?",
  "Being so restless that it is hard to sit still?",
  "Becoming easily annoyed or irritable?",
  "Feeling afraid, as if something awful might happen?"
];

// Standard published cutoffs (PHQ-9: 0-4, 5-9, 10-14, 15-19, 20-27; GAD-7: 0-4, 5-9, 10-14, 15-21)
const localSeverity = (type: 'phq9' | 'gad7', score: number): string => {
  if (score <= 4) return 'minimal';
  if (score <= 9) return 'mild';
  if (score <= 14) return 'moderate';
  if (type === 'gad7') return 'severe';
  return score <= 19 ? 'moderately severe' : 'severe';
};

interface AssessmentResult {
  type: 'phq9' | 'gad7';
  score: number;
  total_score: number;
  severity: string;
  crisis_level: number;
  saved: boolean;
}

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
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const questions = type === 'gad7' ? gad7Questions : phq9Questions;

  const handleSelect = (value: number) => {
    const newResponses = [...responses];
    newResponses[currentStep] = value;
    setResponses(newResponses);

    if (currentStep < questions.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      submitAssessment(newResponses);
    }
  };

  const submitAssessment = async (finalResponses: number[]) => {
    setIsSubmitting(true);
    try {
      const saved = await apiService.submitAssessment(type, finalResponses);
      setResult({ ...saved, type, saved: true });
    } catch (error) {
      console.error("Assessment submission failed, scoring locally", error);
      // Fall back to local scoring only when the request fails (result is not saved)
      const totalScore = finalResponses.reduce((a, b) => a + b, 0);
      setResult({
        type,
        score: totalScore,
        total_score: totalScore,
        severity: localSeverity(type, totalScore),
        crisis_level: type === 'phq9' && (finalResponses[8] || 0) > 0 ? 1 : 0,
        saved: false
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const progress = ((currentStep + 1) / questions.length) * 100;

  if (result) {
    const maxScore = type === 'gad7' ? 21 : 27;
    return (
      <div className="max-w-2xl w-full mx-auto p-8 bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl text-center">
        <h2 className="text-sm font-bold uppercase tracking-widest text-indigo-400 mb-8">
          {type.toUpperCase()} Result
        </h2>
        <p className="text-6xl font-black text-white mb-2">
          {result.score}<span className="text-2xl text-slate-500"> / {maxScore}</span>
        </p>
        <p className="text-lg font-bold text-indigo-300 capitalize mb-6">{result.severity}</p>

        {result.crisis_level > 0 && (
          <p className="mb-6 p-4 rounded-2xl bg-red-500/10 border border-red-500/30 text-red-200 text-sm leading-relaxed">
            If you're in immediate danger, please call 988 (Suicide & Crisis Lifeline) or emergency services immediately.
          </p>
        )}

        <p className="text-xs text-slate-500 mb-8">
          {result.saved ? 'Saved to your clinical record.' : 'Could not reach the server; this result was scored locally and not saved.'}
        </p>

        <button
          onClick={() => onComplete(result)}
          className="w-full py-4 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 rounded-2xl transition-all font-black text-white"
        >
          Continue
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl w-full mx-auto p-8 bg-slate-900/50 backdrop-blur-xl rounded-3xl border border-white/10 shadow-2xl">
      <div className="mb-12">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-sm font-bold uppercase tracking-widest text-indigo-400">
            {type.toUpperCase()} Assessment
          </h2>
          <span className="text-xs text-slate-500">Step {currentStep + 1} of {questions.length}</span>
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
            {questions[currentStep]}
          </h3>

          <div className="grid grid-cols-1 gap-4">
            {phq9Options.map((option, idx) => (
              <button
                key={idx}
                onClick={() => handleSelect(idx)}
                disabled={isSubmitting}
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
