import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface UserProfile {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  age: number;
  anxietyTrigger: string;
  baselinePhq9: number;
  baselineGad7: number;
  createdAt: string;
}

export interface UserStats {
  totalActivities: number;
  totalGamesPlayed: number;
  currentStreak: number;
  averageMood: number;
  moodTrend: number;
  currentPhq9: number;
  currentGad7: number;
  phq9Improvement: number;
  gad7Improvement: number;
  gameCompletionRate: number;
}

export interface UserStore {
  user: UserProfile | null;
  clinicalSafetyLevel: number;
  role: 'patient' | 'professional' | 'admin';
  stats: UserStats | null;
  isLoading: boolean;
  error: string | null;
  
  setUser: (user: UserProfile) => void;
  setStats: (stats: UserStats) => void;
  setSafetyLevel: (level: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clear: () => void;
}

export const useUserStore = create<UserStore>()(
  devtools(
    persist(
      (set) => ({
        user: null,
        clinicalSafetyLevel: 0,
        role: 'patient',
        stats: null,
        isLoading: false,
        error: null,

        setUser: (user) => set({ user, role: (user as any).role || 'patient' }),
        setStats: (stats) => set({ stats }),
        setSafetyLevel: (level) => set({ clinicalSafetyLevel: level }),
        setLoading: (loading) => set({ isLoading: loading }),
        setError: (error) => set({ error }),
        clear: () => set({ user: null, stats: null, error: null, clinicalSafetyLevel: 0 }),
      }),
      {
        name: 'user-store',
      }
    )
  )
);
