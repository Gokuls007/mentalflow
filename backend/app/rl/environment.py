import numpy as np
import gymnasium as gym
from gymnasium import spaces
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.user import User
from app.models.clinical import Assessment, MoodLog, GameSession, Activity

class MentalHealthEnv(gym.Env):
    """
    Custom Gymnasium environment for clinical difficulty adaptation.
    State: [Anxiety, PHQ9, GAD7, Engagement, Performance, MoodTrend, Recency]
    """
    
    def __init__(self, user_id: int, db: Session):
        super().__init__()
        self.user_id = user_id
        self.db = db
        
        # State and action spaces
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(7,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(3) # 0: easy, 1: medium, 2: hard
        
        # Difficulty mapping
        self.difficulty_map = {0: "easy", 1: "medium", 2: "hard"}
        
        # Initialize state
        self.state = self._get_current_state()
        self.last_action = None
        self.last_reward = 0.0
        
    def _get_current_state(self) -> np.ndarray:
        """Fetch and normalize user clinical state from database."""
        user = self.db.query(User).filter(User.id == self.user_id).first()
        if not user:
            return np.zeros(7, dtype=np.float32)
            
        # Get latest assessments
        latest_phq9 = self.db.query(Assessment).filter(
            Assessment.user_id == self.user_id,
            Assessment.type == "phq9"
        ).order_by(Assessment.date.desc()).first()
        
        latest_gad7 = self.db.query(Assessment).filter(
            Assessment.user_id == self.user_id,
            Assessment.type == "gad7"
        ).order_by(Assessment.date.desc()).first()
        
        phq9_score = latest_phq9.score if latest_phq9 else (user.baseline_phq9 or 0)
        gad7_score = latest_gad7.score if latest_gad7 else (user.baseline_gad7 or 0)
        
        # Calculate completion rate (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        total_games = self.db.query(GameSession).filter(
            GameSession.user_id == self.user_id,
            GameSession.created_at >= seven_days_ago
        ).count()
        
        completed_games = self.db.query(GameSession).filter(
            GameSession.user_id == self.user_id,
            GameSession.created_at >= seven_days_ago,
            GameSession.completed == True
        ).count()
        
        completion_rate = (completed_games / total_games) if total_games > 0 else 0.5
        
        # Performance (last 5 games)
        recent_games = self.db.query(GameSession).filter(
            GameSession.user_id == self.user_id
        ).order_by(GameSession.created_at.desc()).limit(5).all()
        
        game_performance = sum(1 for g in recent_games if g.completed) / len(recent_games) if recent_games else 0.5
        
        # Mood trend
        mood_logs = self.db.query(MoodLog).filter(
            MoodLog.user_id == self.user_id
        ).order_by(MoodLog.timestamp.desc()).limit(3).all()
        mood_trend = 0.5 # Neutral
        if len(mood_logs) > 1:
            delta = mood_logs[0].mood_score - mood_logs[-1].mood_score
            mood_trend = np.clip((delta / 10.0) + 0.5, 0, 1)
            
        # Recency (days since last activity)
        last_activity = self.db.query(GameSession).filter(
            GameSession.user_id == self.user_id
        ).order_by(GameSession.created_at.desc()).first()
        days_since = (datetime.utcnow() - last_activity.created_at).days if last_activity else 7
        recency = np.clip(days_since / 7.0, 0, 1)

        return np.array([
            (user.baseline_gad7 or 0) / 21.0,
            phq9_score / 27.0,
            gad7_score / 21.0,
            completion_rate,
            game_performance,
            mood_trend,
            recency
        ], dtype=np.float32)
    
    def step(self, action: int):
        """Update based on action. In real deployment, this is called after a game."""
        self.last_action = action
        # Placeholder for actual outcome integration
        reward = self.last_reward
        self.state = self._get_current_state()
        return self.state, reward, False, False, {}

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.state = self._get_current_state()
        return self.state, {}
