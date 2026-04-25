import numpy as np
import logging
from typing import Dict, List, Any, Optional

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
