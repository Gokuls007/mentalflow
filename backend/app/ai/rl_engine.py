import numpy as np
import os
import torch
import logging
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from app.ai.gymnasium_env import MentalHealthEnv
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class RLEngine:
    """
    Reinforcement Learning Engine for adaptive difficulty
    
    Uses PPO (Proximal Policy Optimization) to learn:
    - When to recommend EASY activities (user struggling)
    - When to recommend MEDIUM activities (normal)
    - When to recommend HARD activities (user doing well)
    """
    
    def __init__(self, model_path: str = "models/rl_model.zip"):
        self.model_path = model_path
        self.model = None
        self.load_or_create_model()
    
    def load_or_create_model(self):
        """Load existing model or create new one"""
        
        if os.path.exists(self.model_path):
            logger.info("Loading existing RL model")
            try:
                self.model = PPO.load(self.model_path)
            except Exception as e:
                logger.error(f"Failed to load RL model: {e}")
                self._create_new_model()
        else:
            logger.info("Creating new RL model")
            self._create_new_model()
            
    def _create_new_model(self):
        # Dummy environment for initialization
        env = DummyVecEnv([lambda: MentalHealthEnv(user_id=1, db=None)])
        self.model = PPO(
            "MlpPolicy",
            env,
            learning_rate=3e-4,
            n_steps=128,
            batch_size=64,
            n_epochs=10,
            verbose=1
        )
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        # Save initial model
        self.model.save(self.model_path)
    
    def predict_difficulty(self, user_state: np.ndarray) -> dict:
        """
        Predict difficulty for user
        
        Returns:
        {
            "difficulty": "EASY" | "MEDIUM" | "HARD",
            "confidence": 0.0-1.0,
            "action_probs": [prob_easy, prob_medium, prob_hard]
        }
        """
        
        if self.model is None:
            # Fallback: recommend MEDIUM
            return {
                "difficulty": "MEDIUM",
                "confidence": 0.5,
                "action_probs": [0.33, 0.34, 0.33]
            }
        
        # Get action probabilities
        action, _ = self.model.predict(user_state, deterministic=True)
        
        # Get policy probabilities (confidence)
        policy = self.model.policy
        
        # Forward pass to get probabilities
        obs_tensor = torch.as_tensor(user_state.reshape(1, -1)).to(policy.device)
        with torch.no_grad():
            features = policy.extract_features(obs_tensor)
            latent_pi, _ = policy.mlp_extractor(features)
            distribution = policy.action_net(latent_pi)
            probs = torch.softmax(distribution, dim=-1).cpu().numpy()[0]
        
        confidence = float(probs[int(action)])
        difficulty_map = {0: "EASY", 1: "MEDIUM", 2: "HARD"}
        
        return {
            "difficulty": difficulty_map[int(action)],
            "confidence": float(confidence),
            "action_probs": probs.tolist()
        }
    
    def train_on_user_feedback(self, user_id: int, db: Session, timesteps: int = 500):
        """
        Train RL model on user's recent activities
        Called daily or when enough new data available
        """
        
        logger.info(f"Training RL model on user {user_id} data")
        
        env = DummyVecEnv([lambda: MentalHealthEnv(user_id=user_id, db=db)])
        
        if self.model is None:
            self._create_new_model()
            
        self.model.set_env(env)
        
        # Train for N steps
        self.model.learn(total_timesteps=timesteps)
        
        # Save updated model
        self.model.save(self.model_path)
        logger.info(f"RL model saved to {self.model_path}")
    
    def update_reward(self, user_id: int, activity_id: int, 
                     completed: bool, pre_mood: int, post_mood: int, 
                     engagement: int, db: Session):
        """
        Update model with reward after user completes activity
        """
        
        env = MentalHealthEnv(user_id=user_id, db=db)
        reward = env.calculate_reward(completed, pre_mood, post_mood, engagement)
        
        logger.info(f"User {user_id} activity {activity_id}: reward={reward:.2f}")
    
    def get_metrics(self, user_id: int, db: Session) -> dict:
        """Get RL metrics for user"""
        
        env = MentalHealthEnv(user_id=user_id, db=db)
        state = env._get_state()
        
        prediction = self.predict_difficulty(state)
        
        return {
            "user_id": user_id,
            "current_state": {
                "anxiety": float(state[0]),
                "depression": float(state[1]),
                "engagement": float(state[2]),
                "completion_rate": float(state[3]),
                "mood_trend": float(state[4]),
                "days_since_activity": float(state[5])
            },
            "predicted_difficulty": prediction["difficulty"],
            "confidence": prediction["confidence"],
            "action_probabilities": {
                "easy": prediction["action_probs"][0],
                "medium": prediction["action_probs"][1],
                "hard": prediction["action_probs"][2]
            }
        }

# Global instance
rl_engine = RLEngine()
