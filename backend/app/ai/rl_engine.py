import numpy as np
import os
import logging
import pickle
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class LinUCB:
    """
    Implementation of the LinUCB algorithm for Contextual Bandits.
    Used for clinical intervention selection (Behavioral Activation).
    Ref: 'A Contextual-Bandit Approach to Personalized News Article Recommendation' (Li et al. 2010)
    """
    
    def __init__(self, context_dim: int, alpha: float = 0.1):
        self.d = context_dim
        self.alpha = alpha
        # A_a = I + D_a^T * D_a (Identity matrix + Context^T * Context)
        self.A = {} # Dict of arm_id -> matrix (d x d)
        # b_a = D_a^T * r_a (Context^T * Rewards)
        self.b = {} # Dict of arm_id -> vector (d x 1)
        
    def _init_arm(self, arm_id: str):
        if arm_id not in self.A:
            self.A[arm_id] = np.identity(self.d)
            self.b[arm_id] = np.zeros((self.d, 1))
            
    def select_arm(self, context: np.ndarray, arms: List[str]) -> str:
        """
        Selects the best intervention (arm) given the current context.
        context: flattened feature vector (d x 1)
        """
        best_p = -np.inf
        best_arm = arms[0]
        
        x = context.reshape(-1, 1)
        
        for arm_id in arms:
            self._init_arm(arm_id)
            
            # Solve A_a * theta_a = b_a
            A_inv = np.linalg.inv(self.A[arm_id])
            theta = A_inv @ self.b[arm_id]
            
            # p_a = theta_a^T * x + alpha * sqrt(x^T * A_a^-1 * x)
            # This is the Upper Confidence Bound calculation
            p = theta.T @ x + self.alpha * np.sqrt(x.T @ A_inv @ x)
            
            if p > best_p:
                best_p = p
                best_arm = arm_id
                
        return best_arm

    def update(self, arm_id: str, context: np.ndarray, reward: float):
        """
        Updates the model after an intervention is completed and a reward is observed.
        """
        self._init_arm(arm_id)
        x = context.reshape(-1, 1)
        
        # A_a = A_a + x * x^T
        self.A[arm_id] += x @ x.T
        # b_a = b_a + reward * x
        self.b[arm_id] += reward * x

class DigitalPhenotypeEngine:
    """
    Extracts 'Digital Phenotypes' from high-dimensional user data.
    Uses a latent-space mapping to summarize behavioral patterns.
    """
    
    @staticmethod
    def extract_features(user: Any, wearable_data: Optional[Dict] = None) -> np.ndarray:
        """
        Converts user state and passive data into a context vector for LinUCB.
        Vector: [Mood, PHQ-9, GAD-7, ActivityLevel, SleepQuality, SocialEngagement]
        """
        # Baseline features
        features = [
            float(user.latest_phq9_score or 15) / 27.0,   # Normalized PHQ-9
            float(user.latest_gad7_score or 12) / 21.0,   # Normalized GAD-7
            float(user.current_streak) / 30.0,            # Engagement streak
            float(user.current_level) / 100.0,            # Mastery level
        ]
        
        # Passive data (if available)
        if wearable_data:
            features.extend([
                float(wearable_data.get('hrv', 50)) / 100.0,
                float(wearable_data.get('steps', 5000)) / 10000.0,
                float(wearable_data.get('sleep_hours', 7)) / 12.0
            ])
        else:
            features.extend([0.5, 0.5, 0.5]) # Defaults
            
        return np.array(features)

# Global Instance for Clinical Context
# Dimension = 7 (PHQ-9, GAD-7, Streak, Level, HRV, Steps, Sleep)
clinical_bandit = LinUCB(context_dim=7)


class LinUCBEngine:
    """
    Contextual bandit (LinUCB) over the 3 game difficulty levels.
    Models the reward of each difficulty as a linear function of the 6-D user state
    produced by MentalHealthEnv._get_state().
    """

    def __init__(self, state_dim: int = 6, n_actions: int = 3, alpha: float = 1.0, model_path: str = "models/linucb_model.pkl"):
        self.state_dim = state_dim
        self.n_actions = n_actions
        self.alpha = alpha  # Exploration parameter
        self.model_path = model_path

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
        model_dir = os.path.dirname(self.model_path)
        if model_dir:
            os.makedirs(model_dir, exist_ok=True)
        with open(self.model_path, 'wb') as f:
            pickle.dump({'A': self.A, 'b': self.b}, f)
        logger.info(f"Saved LinUCB model to {self.model_path}")

    def predict_difficulty(self, state: np.ndarray) -> Dict:
        """Predict the best difficulty using UCB scores."""
        x = np.asarray(state, dtype=float).reshape(-1, 1)
        p = np.zeros(self.n_actions)

        for a in range(self.n_actions):
            A_inv = np.linalg.inv(self.A[a])
            theta = A_inv @ self.b[a].reshape(-1, 1)
            expected_reward = (theta.T @ x).item()
            uncertainty = self.alpha * np.sqrt((x.T @ A_inv @ x).item())
            p[a] = expected_reward + uncertainty

        action = int(np.argmax(p))
        difficulty_map = {0: "EASY", 1: "MEDIUM", 2: "HARD"}

        # Pseudo-probabilities for confidence reporting
        exp_p = np.exp(p - np.max(p))
        probs = exp_p / exp_p.sum()

        return {
            "difficulty": difficulty_map[action],
            "confidence": float(probs[action]),
            "action_probs": probs.tolist(),
            "ucb_scores": p.tolist()
        }

    def update(self, state: np.ndarray, action: int, reward: float, save: bool = True):
        """Update LinUCB parameters with an observed reward."""
        x = np.asarray(state, dtype=float).reshape(-1, 1)
        self.A[action] += x @ x.T
        self.b[action] += reward * x.flatten()
        if save:
            self.save_model()


class RLEngine:
    """Difficulty-adaptation engine used by the /rl API and the training jobs."""

    def __init__(self, model_path: str = "models/linucb_model.pkl"):
        self.engine = LinUCBEngine(model_path=model_path)

    def predict_difficulty(self, user_state: np.ndarray) -> dict:
        return self.engine.predict_difficulty(user_state)

    def update_reward(self, user_id: int, activity_id: int,
                      completed: bool, pre_mood: int, post_mood: int,
                      engagement: int, db: Session):
        from app.ai.gymnasium_env import MentalHealthEnv
        from app.models.rl import RLState

        env = MentalHealthEnv(user_id=user_id, db=db)
        state = env._get_state()
        reward = env.calculate_reward(completed, pre_mood, post_mood, engagement)

        # The action taken is the last difficulty predicted for this user
        rl_state = db.query(RLState).filter_by(user_id=user_id).first()
        action = rl_state.last_action if rl_state and rl_state.last_action is not None else 1

        self.engine.update(state, action, reward)
        if rl_state:
            rl_state.last_reward = reward
            rl_state.games_count = (rl_state.games_count or 0) + 1
        logger.info(f"RL Updated for user {user_id}: reward={reward:.2f}")
        return reward

    def train_on_user_feedback(self, user_id: int, db: Session, timesteps: int = 200):
        """Refine the model by simulating episodes starting from the user's current state."""
        from app.ai.gymnasium_env import MentalHealthEnv

        env = MentalHealthEnv(user_id=user_id, db=db)
        state, _ = env.reset()
        for _ in range(timesteps):
            action = ["EASY", "MEDIUM", "HARD"].index(self.predict_difficulty(state)["difficulty"])
            next_state, reward, _, _, _ = env.step(action)
            self.engine.update(state, action, reward, save=False)
            state = next_state
        self.engine.save_model()

    def get_metrics(self, user_id: int, db: Session) -> dict:
        from app.ai.gymnasium_env import MentalHealthEnv

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


# Global instance for difficulty adaptation (used by app.api.v1.rl and the jobs)
rl_engine = RLEngine()
