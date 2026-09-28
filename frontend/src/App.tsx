import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useParams } from 'react-router-dom';
import Dashboard from './components/dashboard/Dashboard';
import GameContainer from './components/game/GameContainer';
import AssessmentWizard from './components/assessment/AssessmentWizard';
import TherapistDashboard from './components/professional/TherapistDashboard';
import InformedConsent from './components/legal/InformedConsent';
import CrisisOverlay from './components/safety/CrisisOverlay';
import { useUserStore } from './store/user.store';
import { apiService, DEMO_USER_ID } from './services/api';

// Pass the activity id from the URL (/game/:id) to the game, defaulting to 1 for the demo
const GameRoute: React.FC = () => {
  const { id } = useParams();
  const activityId = Number(id) || 1;
  return <GameContainer activityId={activityId} />;
};

const App: React.FC = () => {
  const { user, setUser, clinicalSafetyLevel, role } = useUserStore();

  useEffect(() => {
    // Use the logged-in account when a token exists; otherwise the seeded demo account
    const setDemoUser = () => {
      setUser({
        id: DEMO_USER_ID,
        email: 'demo@mentalflow.local',
        firstName: 'Demo',
        lastName: 'User',
        role: 'patient'
      } as any);
    };

    if (localStorage.getItem('authToken')) {
      apiService.getMe()
        .then((me) => setUser({ ...me, firstName: me.first_name, lastName: me.last_name } as any))
        .catch((err) => {
          // Expired/invalid token: drop it. Network errors keep the stored session.
          if (err?.response?.status === 401) {
            localStorage.removeItem('authToken');
            setDemoUser();
          } else if (!user) {
            setDemoUser();
          }
        });
    } else if (!user || user.id !== DEMO_USER_ID) {
      setDemoUser();
    }
    // Run once on load
  }, []);

  return (
    <Router>
      <div className="min-h-screen bg-[#020617] text-slate-200">
        {/* Global Crisis Lockout */}
        {clinicalSafetyLevel > 0 && <CrisisOverlay level={clinicalSafetyLevel} />}

        <Routes>
          <Route path="/" element={<Navigate to="/consent" replace />} />
          
          {/* Baseline Flow */}
          <Route path="/consent" element={<InformedConsent onAccept={() => window.location.href = '/assessment'} />} />
          <Route path="/assessment" element={<div className="p-12 flex justify-center"><AssessmentWizard type="phq9" onComplete={() => window.location.href = '/dashboard'} /></div>} />

          {/* Core App */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/game/:id" element={<GameRoute />} />

          {/* Professional Context */}
          <Route path="/professional" element={<TherapistDashboard />} />

          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
