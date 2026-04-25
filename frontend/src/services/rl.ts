import { apiService } from './api';

export interface RLPrediction {
  recommended_difficulty: 'easy' | 'medium' | 'hard';
  confidence_scores: {
    easy: number;
    medium: number;
    hard: number;
  };
  explanation?: string;
}

export interface RLMetrics {
  games_processed: number;
  model_trained: boolean;
  last_training?: string;
  adaptation_effectiveness: number;
  predicted_next_difficulty: string;
}

export const rlService = {
  /**
   * Get difficulty prediction from the clinical PPO agent
   */
  getPrediction: async (userId: number = 1): Promise<RLPrediction> => {
    try {
      const data = await apiService.getDifficultyPrediction(userId);
      return data;
    } catch (error) {
      console.error('RL Prediction failed, falling back to medium:', error);
      return {
        recommended_difficulty: 'medium',
        confidence_scores: { easy: 0.33, medium: 0.34, hard: 0.33 }
      };
    }
  },

  /**
   * Get clinical RL training metrics
   */
  getMetrics: async (): Promise<RLMetrics> => {
    const response = await fetch('/api/v1/rl/metrics');
    return response.json();
  },

  /**
   * Trigger agent training (usually after a BA loop cycle)
   */
  trainAgent: async () => {
    return apiService.submitPHQ9({ type: 'training_trigger' }); // Mocked
  }
};
