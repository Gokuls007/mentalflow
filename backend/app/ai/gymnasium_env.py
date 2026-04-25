import gymnasium as gym
from gymnasium import spaces
import numpy as np
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import User, Activity, Assessment, MoodLog

class MentalHealthEnv(gym.Env):
    """
    Reinforcement Learning Environment for Mental Health
    
    State: [anxiety_level, depression_level, engagement, completion_rate, mood_trend, days_since_activity]
    Action: [EASY, MEDIUM, HARD]
    Reward: completion + mood improvement + engagement bonus
    """
    
    def __init__(self, user_id: int, db: Session):
        super().__init__()
        
        self.user_id = user_id
        self.db = db
        
        # State space: 6 dimensions, all normalized 0-1
        self.observation_space = spaces.Box(
            low=0, 
            high=1, 
            shape=(6,), 
            dtype=np.float32
        )
        
        # Action space: 3 difficulty levels
        # 0 = EASY, 1 = MEDIUM, 2 = HARD
        self.action_space = spaces.Discrete(3)
        
        self.current_state = None
        self.last_activity = None
        
    def reset(self, seed=None, options=None):
        """Reset environment and get initial state"""
        super().reset(seed=seed)
        self.current_state = self._get_state()
        return self.current_state, {}
    
    def step(self, action):
        """
        Execute action (recommend difficulty)
        Returns: (new_state, reward, terminated, truncated, info)
        """
        
        # action: 0=EASY, 1=MEDIUM, 2=HARD
        # difficulty = ["EASY", "MEDIUM", "HARD"][action]
        
        # For now, assume activity will be completed
        # In real scenario, wait for user to complete and return feedback
        
        # Get new state
        new_state = self._get_state()
        
        # Calculate reward (placeholder - will be updated after user completes)
        reward = 0.0
        
        return new_state, reward, False, False, {}
    
    def _get_state(self) -> np.ndarray:
        """
        Get current user state
        Returns normalized 6D vector:
        [anxiety, depression, engagement, completion_rate, mood_trend, days_since_activity]
        """
        if not self.db:
            return np.zeros(6, dtype=np.float32)

        user = self.db.query(User).filter_by(id=self.user_id).first()
        if not user:
            return np.zeros(6, dtype=np.float32)
        
        # 1. Anxiety Level (0-21 normalized to 0-1)
        gad7_score = getattr(user, 'latest_gad7_score', 10) or 10
        anxiety = min(gad7_score / 21.0, 1.0)
        
        # 2. Depression Level (0-27 normalized to 0-1)
        phq9_score = getattr(user, 'latest_phq9_score', 13) or 13
        depression = min(phq9_score / 27.0, 1.0)
        
        # 3. Engagement (0-10 normalized to 0-1)
        # Based on recent activity completion ratings
        recent_activities = self.db.query(Activity).filter(
            Activity.user_id == self.user_id,
            Activity.created_at >= (datetime.utcnow() - timedelta(days=7))
        ).all()
        
        if recent_activities:
            engagement_ratings = [a.personalization_score for a in recent_activities if hasattr(a, 'personalization_score') and a.personalization_score]
            engagement = np.mean(engagement_ratings) if engagement_ratings else 0.5
        else:
            engagement = 0.5
        
        # 4. Completion Rate (past 7 days)
        completed = len([a for a in recent_activities if a.completed_at])
        completion_rate = completed / len(recent_activities) if recent_activities else 0.5
        
        # 5. Mood Trend (improving/declining)
        # Get last 7 mood logs
        mood_logs = self.db.query(MoodLog).filter(
            MoodLog.user_id == self.user_id,
            MoodLog.created_at >= (datetime.utcnow() - timedelta(days=7))
        ).order_by(MoodLog.created_at).all()
        
        if len(mood_logs) >= 2:
            mood_trend = (mood_logs[-1].mood_score - mood_logs[0].mood_score) / 10.0
            mood_trend = max(-1.0, min(1.0, mood_trend))  # Clamp to [-1, 1]
            mood_trend = (mood_trend + 1.0) / 2.0  # Normalize to [0, 1]
        else:
            mood_trend = 0.5
        
        # 6. Days Since Last Activity
        latest_activity = self.db.query(Activity).filter(
            Activity.user_id == self.user_id,
            Activity.completed_at.isnot(None)
        ).order_by(Activity.completed_at.desc()).first()
        
        if latest_activity:
            days_since = (datetime.utcnow() - latest_activity.completed_at).days
            days_since_normalized = min(days_since / 30.0, 1.0)  # Max 30 days
        else:
            days_since_normalized = 1.0  # No activity, worst case
        
        state = np.array([
            anxiety,
            depression,
            engagement,
            completion_rate,
            mood_trend,
            days_since_normalized
        ], dtype=np.float32)
        
        self.current_state = state
        return state
    
    def calculate_reward(self, completed: bool, pre_mood: int, post_mood: int, engagement: int) -> float:
        """
        Calculate reward based on activity outcome
        
        Reward = completion + mood_improvement + engagement_bonus
        """
        
        reward = 0.0
        
        # Completion reward
        if completed:
            reward += 1.0
        else:
            reward -= 0.5
        
        # Mood improvement reward
        if pre_mood and post_mood:
            mood_delta = post_mood - pre_mood
            reward += 0.05 * mood_delta  # +0.05 per point improvement
        
        # Engagement bonus
        if engagement and engagement >= 7:  # High engagement
            reward += 0.3
        
        return reward
