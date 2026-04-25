import React, { useState, useEffect, useRef } from 'react';
import * as Phaser from 'phaser';
import { createGameConfig } from '../../game/config';
import { useGameStore } from '../../store/game.store';
import { rlService } from '../../services/rl';
import { apiService } from '../../services/api';
import PreGameModal from './PreGameModal';
import PostGameModal from './PostGameModal';

interface GameContainerProps {
  activityId: number;
}

const GameContainer: React.FC<GameContainerProps> = ({ activityId }) => {
  const gameRef = useRef<Phaser.Game | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [gameState, setGameState] = useState<'loading' | 'pre-game' | 'playing' | 'post-game' | 'complete'>('loading');
  const [difficulty, setDifficulty] = useState<'easy' | 'medium' | 'hard'>('medium');
  const [gameResult, setGameResult] = useState<any>(null);
  const [moodBefore, setMoodBefore] = useState(5);

  const { startGame, endGame } = useGameStore();

  // 1. Fetch difficulty from RL agent on mount
  useEffect(() => {
    const initRL = async () => {
      const prediction = await rlService.getPrediction();
      setDifficulty(prediction.recommended_difficulty);
      setGameState('pre-game');
    };
    initRL();
  }, []);

  // Keep callbacks in refs so Phaser always sees latest React state
  const endGameRef = useRef(endGame);
  endGameRef.current = endGame;
  const setGameResultRef = useRef(setGameResult);
  setGameResultRef.current = setGameResult;
  const setGameStateRef = useRef(setGameState);
  setGameStateRef.current = setGameState;

  // 2. Initialize Phaser when state transitions to 'playing'
  useEffect(() => {
    if (gameState !== 'playing') return;

    // Destroy any previous instance
    if (gameRef.current) {
      gameRef.current.destroy(true);
      gameRef.current = null;
    }

    // Small delay to ensure DOM container is rendered
    const bootTimer = setTimeout(() => {
      if (!containerRef.current) return;

      const config = createGameConfig(difficulty);
      const game = new Phaser.Game(config);
      gameRef.current = game;

      // Poll until the scene is active, then hook into its events.
      // This is more reliable than game.events.once('ready') across Phaser versions.
      let attempts = 0;
      const pollInterval = setInterval(() => {
        attempts++;
        const scene = game.scene.getScene('GameplayScene');
        if (scene && scene.scene.isActive()) {
          clearInterval(pollInterval);

          scene.events.on('gameEnded', (result: any) => {
            setGameResultRef.current(result);
            setGameStateRef.current('post-game');
            endGameRef.current(result.score, result.completed);
          });

          // Focus the canvas for keyboard input
          const canvas = containerRef.current?.querySelector('canvas');
          if (canvas) {
            canvas.setAttribute('tabindex', '1');
            canvas.style.outline = 'none';
            canvas.focus();
          }
        }
        // Give up after 5 seconds
        if (attempts > 50) clearInterval(pollInterval);
      }, 100);
    }, 100);

    return () => {
      clearTimeout(bootTimer);
      if (gameRef.current) {
        gameRef.current.destroy(true);
        gameRef.current = null;
      }
    };
  }, [gameState, difficulty]);

  const handleStartGame = (mood: number) => {
    setMoodBefore(mood);
    startGame(activityId, difficulty);
    setGameState('playing');
  };

  const handlePostGameSubmit = async (moodAfter: number, engagement: number) => {
    try {
      await apiService.submitGameSession({
        activity_id: activityId,
        difficulty_level: difficulty,
        score: gameResult?.score || 0,
        completion_time: gameResult?.duration || 0,
        completed: gameResult?.completed || false,
        mood_before: moodBefore,
        mood_after: moodAfter,
        engagement_rating: engagement
      });
    } catch (err) {
      console.warn('[Game] Failed to submit session, continuing in demo mode');
    }
    
    setGameState('complete');
  };

  if (gameState === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-[#0f172a] text-white gap-4">
        <div className="w-10 h-10 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin" />
        <p className="text-slate-400 text-sm animate-pulse">Initializing Clinical Environment...</p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-full min-h-screen bg-[#0f172a] overflow-hidden">
      {/* Phaser Canvas Container — brought to front when playing */}
      <div 
        ref={containerRef}
        id="game-container" 
        className={`absolute inset-0 flex items-center justify-center ${gameState !== 'playing' ? 'hidden' : ''}`}
        style={{ zIndex: 20 }}
      />

      {/* UI Overlay — completely unmounted when playing so it can't steal focus */}
      {gameState !== 'playing' && (
        <div className="relative z-10 flex items-center justify-center w-full h-full min-h-screen">
          {gameState === 'pre-game' && (
            <PreGameModal 
              difficulty={difficulty} 
              onStart={handleStartGame} 
              onCancel={() => window.location.href = '/dashboard'} 
            />
          )}

          {gameState === 'post-game' && gameResult && (
            <PostGameModal 
              gameResult={gameResult} 
              onSubmit={handlePostGameSubmit} 
            />
          )}

          {gameState === 'complete' && (
            <div className="p-10 bg-white/[0.04] backdrop-blur-2xl rounded-[32px] border border-white/10 text-center text-white max-w-md shadow-2xl">
              <div className="w-20 h-20 bg-emerald-500/20 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">✓</span>
              </div>
              <h2 className="text-3xl font-extrabold mb-3 tracking-tight">Daily Goal Achieved!</h2>
              <p className="text-slate-400 mb-8 text-sm leading-relaxed">
                Your emotional data has been synced with the clinical agent. Your RL model will adapt based on this session.
              </p>
              <button 
                onClick={() => window.location.href = '/dashboard'}
                className="px-8 py-3 bg-gradient-to-r from-indigo-500 to-purple-500 hover:from-indigo-600 hover:to-purple-600 rounded-2xl transition-all font-bold shadow-lg shadow-indigo-500/20"
              >
                Return to Dashboard
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default GameContainer;
