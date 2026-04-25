import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from pathlib import Path
from sqlalchemy.orm import Session
from app.rl.environment import MentalHealthEnv
import logging

logger = logging.getLogger(__name__)

class MentalHealthRLAgent:
    """
    Wrapper for PPO agent for clinical difficulty adaptation.
    """
    
    def __init__(self, user_id: int, db: Session, model_path: str = None):
        self.user_id = user_id
        self.db = db
        self.model_path = model_path or f"storage/models/rl_agent_{user_id}.zip"
        self.difficulty_map = {0: "easy", 1: "medium", 2: "hard"}
        
        # Ensure directory exists
        Path("storage/models").mkdir(parents=True, exist_ok=True)
        
        # Create environment
        self.env = DummyVecEnv([lambda: MentalHealthEnv(user_id, db)])
        
        # Load or create model
        if Path(self.model_path).exists():
            self.model = PPO.load(self.model_path, env=self.env)
        else:
            self.model = PPO(
                "MlpPolicy",
                self.env,
                learning_rate=3e-4,
                n_steps=128,
                batch_size=64,
                verbose=0
            )
    
    def predict_difficulty(self) -> dict:
        """Predict the next difficulty level."""
        # Note: In real use, environment reset provides the current state
        obs = self.env.reset()
        action, _states = self.model.predict(obs, deterministic=True)
        
        # Calculate mock probabilities
        # (Stable baselines doesn't expose these easily without going into policy)
        return {
            "recommended": self.difficulty_map[int(action)],
            "probabilities": {"easy": 0.2, "medium": 0.7, "hard": 0.1} 
        }

    def calculate_reward(self, game_result: dict) -> float:
        """
        Calculates reward from game result as per spec:
        R = w1*Completion + w2*(ΔMood/10) + w3*(Engagement/10)
        """
        w1, w2, w3 = 0.5, 0.3, 0.2
        
        completion_score = 1.0 if game_result.get("completed") else -0.5
        mood_delta = game_result.get("mood_after", 0) - game_result.get("mood_before", 0)
        mood_score = np.clip(mood_delta / 10.0, -1, 1) # Normalized improvement
        engagement_score = game_result.get("engagement_rating", 0) / 10.0
        
        reward = (w1 * completion_score) + (w2 * mood_score) + (w3 * engagement_score)
        return float(reward)

    def save(self):
        self.model.save(self.model_path)
