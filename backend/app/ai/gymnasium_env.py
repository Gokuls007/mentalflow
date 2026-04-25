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
    Action: [0: EASY, 1: MEDIUM, 2: HARD]
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
        self.action_space = spaces.Discrete(3)
        
        self.current_state = None
        
    def reset(self, seed=None, options=None):
        """Reset environment and get initial state"""
        super().reset(seed=seed)
        self.current_state = self._get_state()
        return self.current_state, {}
    
    def step(self, action):
        """
        Execute action (recommend difficulty)
        In a clinical context, 'step' usually involves waiting for user feedback.
        For simulation/training, we use a stochastic patient model.
        """
        
        # 1. Simulate the user's response based on current state and difficulty
        # Logic: If user is depressed/anxious, HARD is likely to fail (low reward).
        # If user is doing well, EASY provides low engagement (low reward).
        
        anxiety, depression, engagement, completion_rate, mood_trend, days_since = self.current_state
        
        success_prob = 0.5
        if action == 0: # EASY
            success_prob = 0.9 - (anxiety * 0.2)
        elif action == 1: # MEDIUM
            success_prob = 0.7 - (depression * 0.3)
        elif action == 2: # HARD
            success_prob = 0.4 + (engagement * 0.4) - (depression * 0.5)
            
        success_prob = max(0.1, min(0.9, success_prob))
        completed = np.random.random() < success_prob
        
        # 2. Calculate reward
        pre_mood = 5
        post_mood = pre_mood + (1 if completed else -1) + (1 if action == 2 and completed else 0)
        user_engagement = int(engagement * 10) + (1 if completed else -1)
        
        reward = self.calculate_reward(completed, pre_mood, post_mood, user_engagement)
        
        # 3. Transition state (Simplified: mood improvement affects next state)
        new_state = self.current_state.copy()
        if completed:
            new_state[0] = max(0, new_state[0] - 0.05) # Anxiety down
            new_state[1] = max(0, new_state[1] - 0.05) # Depression down
            new_state[2] = min(1, new_state[2] + 0.1)  # Engagement up
        else:
            new_state[2] = max(0, new_state[2] - 0.1)  # Engagement down
            
        self.current_state = new_state
        
        return new_state, reward, False, False, {"completed": completed}
    
    def _get_state(self) -> np.ndarray:
        """
        Get current user state from DB
        Returns normalized 6D vector:
        [anxiety, depression, engagement, completion_rate, mood_trend, days_since_activity]
        """
        if not self.db:
            # Return a realistic default for initialization/simulation
            return np.array([0.5, 0.6, 0.4, 0.5, 0.5, 0.2], dtype=np.float32)

        user = self.db.query(User).filter_by(id=self.user_id).first()
        if not user:
            return np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5], dtype=np.float32)
        
        # 1. Anxiety Level (GAD-7 0-21 -> 0-1)
        gad7_score = getattr(user, 'latest_gad7_score', 10) or 10
        anxiety = min(gad7_score / 21.0, 1.0)
        
        # 2. Depression Level (PHQ-9 0-27 -> 0-1)
        phq9_score = getattr(user, 'latest_phq9_score', 13) or 13
        depression = min(phq9_score / 27.0, 1.0)
        
        # 3. Engagement (recent activity personalized scores 0-1 -> 0-1)
        recent_activities = self.db.query(Activity).filter(
            Activity.user_id == self.user_id,
            Activity.created_at >= (datetime.utcnow() - timedelta(days=7))
        ).all()
        
        if recent_activities:
            engagement_ratings = [a.personalization_score for a in recent_activities if a.personalization_score]
            engagement = np.mean(engagement_ratings) if engagement_ratings else 0.5
        else:
            engagement = 0.5
        
        # 4. Completion Rate
        completed_count = len([a for a in recent_activities if a.completed_at])
        completion_rate = completed_count / len(recent_activities) if recent_activities else 0.5
        
        # 5. Mood Trend
        mood_logs = self.db.query(MoodLog).filter(
            MoodLog.user_id == self.user_id,
            MoodLog.created_at >= (datetime.utcnow() - timedelta(days=7))
        ).order_by(MoodLog.created_at).all()
        
        if len(mood_logs) >= 2:
            mood_trend = (mood_logs[-1].mood_score - mood_logs[0].mood_score) / 10.0
            mood_trend = max(-1.0, min(1.0, mood_trend))
            mood_trend = (mood_trend + 1.0) / 2.0
        else:
            mood_trend = 0.5
        
        # 6. Days Since Last Activity
        latest_activity = self.db.query(Activity).filter(
            Activity.user_id == self.user_id,
            Activity.completed_at.isnot(None)
        ).order_by(Activity.completed_at.desc()).first()
        
        if latest_activity:
            days_since = (datetime.utcnow() - latest_activity.completed_at).days
            days_since_normalized = min(days_since / 30.0, 1.0)
        else:
            days_since_normalized = 1.0
        
        state = np.array([
            anxiety, depression, engagement, completion_rate, mood_trend, days_since_normalized
        ], dtype=np.float32)
        
        self.current_state = state
        return state
    
    def calculate_reward(self, completed: bool, pre_mood: int, post_mood: int, engagement: int) -> float:
        """
        SOTA Reward Shaping for Behavioral Activation
        Reward = 0.5*completion + 0.3*mood_improvement + 0.2*engagement_bonus
        """
        reward = 0.0
        
        # Completion (Binary Success)
        reward += 0.5 if completed else -0.3
        
        # Mood Improvement (Clinical Outcome)
        if pre_mood and post_mood:
            mood_delta = post_mood - pre_mood
            # Significant reward for improvement, penalty for deterioration
            reward += 0.1 * mood_delta 
        
        # Engagement (Experience Quality)
        if engagement and engagement >= 7:
            reward += 0.2
        elif engagement and engagement <= 3:
            reward -= 0.1
            
        return reward
