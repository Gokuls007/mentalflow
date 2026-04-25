import numpy as np
import os
import logging
import pickle
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from app.ai.gymnasium_env import MentalHealthEnv

logger = logging.getLogger(__name__)

class LinUCBEngine:
    """
    Contextual Multi-Armed Bandit using LinUCB algorithm
    SOTA for clinical personalized recommendations.
    
    Models reward for each difficulty as a linear function of user state.
    """
    
    def __init__(self, state_dim: int = 6, n_actions: int = 3, alpha: float = 1.0, model_path: str = "models/linucb_model.pkl"):
        self.state_dim = state_dim
        self.n_actions = n_actions
        self.alpha = alpha # Exploration parameter
        self.model_path = model_path
        
        # Initialize LinUCB parameters for each action
        # A: (n_actions, state_dim, state_dim) identity matrices
        # b: (n_actions, state_dim) zero vectors
        self.A = [np.identity(state_dim) for _ in range(n_actions)]
        self.b = [np.zeros(state_dim) for _ in range(n_actions)]
        
        self.load_model()
        
    def load_model(self):
        if os.path.exists(self.model_path):
            try:
                with open(self.model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.A = data['A']
                    self.b = data['b']
                logger.info(f"Loaded LinUCB model from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load LinUCB model: {e}")
                
    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({'A': self.A, 'b': self.b}, f)
        logger.info(f"Saved LinUCB model to {self.model_path}")
        
    def predict_difficulty(self, state: np.ndarray) -> Dict:
        """
        Predict best difficulty using UCB scores
        """
        x = state.reshape(-1, 1)
        p = np.zeros(self.n_actions)
        
        for a in range(self.n_actions):
            A_inv = np.linalg.inv(self.A[a])
            theta = A_inv @ self.b[a].reshape(-1, 1)
            
            # UCB score = expected_reward + uncertainty_bonus
            expected_reward = theta.T @ x
            uncertainty = self.alpha * np.sqrt(x.T @ A_inv @ x)
            p[a] = expected_reward + uncertainty
            
        action = np.argmax(p)
        difficulty_map = {0: "EASY", 1: "MEDIUM", 2: "HARD"}
        
        # Calculate pseudo-probabilities for confidence reporting
        exp_p = np.exp(p - np.max(p))
        probs = exp_p / exp_p.sum()
        
        return {
            "difficulty": difficulty_map[action],
            "confidence": float(probs[action]),
            "action_probs": probs.tolist(),
            "ucb_scores": p.tolist()
        }
        
    def update(self, state: np.ndarray, action: int, reward: float):
        """
        Update LinUCB parameters with observed reward
        """
        x = state.reshape(-1, 1)
        self.A[action] += x @ x.T
        self.b[action] += reward * x.flatten()
        self.save_model()
        
    def train_on_batch(self, experiences: List[Dict]):
        """
        Batch update from historical data
        experiences: list of {'state': np.ndarray, 'action': int, 'reward': float}
        """
        for exp in experiences:
            self.update(exp['state'], exp['action'], exp['reward'])

class RLEngine:
    """Wrapper for LinUCB to maintain API compatibility"""
    def __init__(self, model_path: str = "models/linucb_model.pkl"):
        self.engine = LinUCBEngine(model_path=model_path)
        
    def predict_difficulty(self, user_state: np.ndarray) -> dict:
        return self.engine.predict_difficulty(user_state)
        
    def update_reward(self, user_id: int, activity_id: int, 
                     completed: bool, pre_mood: int, post_mood: int, 
                     engagement: int, db: Session):
        
        env = MentalHealthEnv(user_id=user_id, db=db)
        state = env._get_state()
        reward = env.calculate_reward(completed, pre_mood, post_mood, engagement)
        
        # Find which action was taken for this activity
        # In a real app, you'd store the action index in the Activity model
        # For now, let's derive it or fetch it from the latest RL state
        from app.models.rl import RLState
        rl_state = db.query(RLState).filter_by(user_id=user_id).first()
        action = rl_state.last_action if rl_state else 1
        
        self.engine.update(state, action, reward)
        logger.info(f"RL Updated for user {user_id}: reward={reward:.2f}")

    def get_metrics(self, user_id: int, db: Session) -> dict:
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
            },
            "ucb_scores": prediction["ucb_scores"]
        }

# Global instance
rl_engine = RLEngine()
