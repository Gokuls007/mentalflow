import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

export interface GameStoreState {
  currentActivityId: number | null;
  isPlaying: boolean;
  gameStartTime: number | null;
  gameDuration: number;
  currentScore: number;
  totalSessionsPlayed: number;
  totalSessionsCompleted: number;
  currentStreak: number;
  totalXP: number;
  currentDifficulty: 'easy' | 'medium' | 'hard';
  difficultyHistory: Array<{ date: string; difficulty: string; completed: boolean }>;
  unlockedAchievements: string[];
}

interface GameStoreActions {
  startGame: (activityId: number, difficulty: string) => void;
  endGame: (score: number, completed: boolean) => void;
  updateScore: (points: number) => void;
  addXP: (amount: number) => void;
  unlockAchievement: (achievementId: string) => void;
  reset: () => void;
}

const initialState: GameStoreState = {
  currentActivityId: null,
  isPlaying: false,
  gameStartTime: null,
  gameDuration: 0,
  currentScore: 0,
  totalSessionsPlayed: 0,
  totalSessionsCompleted: 0,
  currentStreak: 0,
  totalXP: 0,
  currentDifficulty: 'medium',
  difficultyHistory: [],
  unlockedAchievements: [],
};

export const useGameStore = create<GameStoreState & GameStoreActions>()(
  devtools(
    persist(
      (set) => ({
        ...initialState,

        startGame: (activityId: number, difficulty: string) => {
          set((state) => ({
            currentActivityId: activityId,
            isPlaying: true,
            gameStartTime: Date.now(),
            currentScore: 0,
            currentDifficulty: difficulty as any,
          }));
        },

        endGame: (score: number, completed: boolean) => {
          set((state) => {
            const newStreak = completed ? state.currentStreak + 1 : 0;
            return {
              isPlaying: false,
              currentScore: score,
              totalSessionsPlayed: state.totalSessionsPlayed + 1,
              totalSessionsCompleted: completed
                ? state.totalSessionsCompleted + 1
                : state.totalSessionsCompleted,
              currentStreak: newStreak,
              gameDuration: state.gameStartTime
                ? Math.floor((Date.now() - state.gameStartTime) / 1000)
                : 0,
              difficultyHistory: [
                ...state.difficultyHistory,
                {
                  date: new Date().toISOString(),
                  difficulty: state.currentDifficulty,
                  completed,
                },
              ],
            };
          });
        },

        updateScore: (points: number) => {
          set((state) => ({
            currentScore: state.currentScore + points,
          }));
        },

        addXP: (amount: number) => {
          set((state) => ({
            totalXP: state.totalXP + amount,
          }));
        },

        unlockAchievement: (achievementId: string) => {
          set((state) => {
            if (!state.unlockedAchievements.includes(achievementId)) {
              return {
                unlockedAchievements: [...state.unlockedAchievements, achievementId],
                totalXP: state.totalXP + 50,
              };
            }
            return state;
          });
        },

        reset: () => {
          set(initialState);
        },
      }),
      {
        name: 'game-store',
      }
    )
  )
);
