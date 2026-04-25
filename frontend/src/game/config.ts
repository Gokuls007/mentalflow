import * as Phaser from 'phaser';
import { GameplayScene } from './scenes/GameplayScene';

export const createGameConfig = (difficulty: 'easy' | 'medium' | 'hard'): Phaser.Types.Core.GameConfig => {
  return {
    type: Phaser.AUTO,
    width: 800,
    height: 600,
    backgroundColor: '#0f172a',
    physics: {
      default: 'arcade',
      arcade: {
        gravity: { y: 0, x: 0 },
        debug: false,
      },
    },
    scene: [GameplayScene],
    scale: {
      mode: Phaser.Scale.FIT,
      autoCenter: Phaser.Scale.CENTER_BOTH,
    },
    parent: 'game-container',
    input: {
      keyboard: true,
      mouse: true,
      touch: true,
    },
    // Pass difficulty via the global registry so the scene can read it on init
    callbacks: {
      preBoot: (game: Phaser.Game) => {
        game.registry.set('difficulty', difficulty);
      },
    },
  };
};
