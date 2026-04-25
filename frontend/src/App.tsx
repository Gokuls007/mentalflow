import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Dashboard from './components/dashboard/Dashboard';
import GameContainer from './components/game/GameContainer';
import AssessmentWizard from './components/assessment/AssessmentWizard';
import TherapistDashboard from './components/professional/TherapistDashboard';
import InformedConsent from './components/legal/InformedConsent';
import CrisisOverlay from './components/safety/CrisisOverlay';
import { useUserStore } from './store/user.store';

const App: React.FC = () => {
  const { user, setUser, clinicalSafetyLevel, role } = useUserStore();

  useEffect(() => {
    // Mock user identification for Phase 4 demo
    if (!user) {
      setUser({
        id: 1,
        email: 'patient.demo@example.com',
        firstName: 'Alex',
        lastName: 'Resilience',
        role: 'patient'
      } as any);
    }
  }, [user, setUser]);

  return (
    <Router>
      <div className="min-h-screen bg-[#0f172a] relative overflow-hidden">
        {/* Global Crisis Lockout */}
        {clinicalSafetyLevel > 0 && <CrisisOverlay level={clinicalSafetyLevel} />}

        {/* Dynamic Background Effects */}
        <div className="liquid-glow w-[500px] h-[500px] bg-indigo-600/20 top-[-100px] left-[-100px] animate-pulse"></div>
        <div className="liquid-glow w-[400px] h-[400px] bg-emerald-600/10 bottom-[-100px] right-[-100px] animate-pulse" style={{ animationDelay: '2s' }}></div>

        <Routes>
          <Route path="/" element={<Navigate to="/consent" replace />} />
          
          {/* Baseline Flow */}
          <Route path="/consent" element={<InformedConsent onAccept={() => window.location.href = '/assessment'} />} />
          <Route path="/assessment" element={<div className="p-12 flex justify-center"><AssessmentWizard type="phq9" onComplete={() => window.location.href = '/dashboard'} /></div>} />

          {/* Core App */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/game/:id" element={<GameContainer activityId={1} />} />

          {/* Professional Context */}
          <Route path="/professional" element={<TherapistDashboard />} />

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
