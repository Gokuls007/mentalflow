from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from app.models.clinical import MoodLog, Activity

class MoodService:
    """Business logic for mood tracking and analytics."""
    
    def create_mood_log(self, db: Session, user_id: int, mood_in: Any) -> MoodLog:
        db_mood = MoodLog(
            user_id=user_id,
            **mood_in.dict()
        )
        db.add(db_mood)
        db.commit()
        db.refresh(db_mood)
        return db_mood
        
    def get_moods_by_date(self, db: Session, user_id: int, target_date: date) -> List[MoodLog]:
        return db.query(MoodLog).filter(
            MoodLog.user_id == user_id,
            func.date(MoodLog.timestamp) == target_date
        ).all()
        
    def get_mood_history(self, db: Session, user_id: int, days: int = 7, limit: int = 100) -> List[MoodLog]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        return db.query(MoodLog).filter(
            MoodLog.user_id == user_id,
            MoodLog.timestamp >= cutoff
        ).order_by(MoodLog.timestamp.desc()).limit(limit).all()
        
    def calculate_mood_trend(self, db: Session, user_id: int, days: int = 7) -> Dict[str, Any]:
        moods = self.get_mood_history(db, user_id, days=days)
        if not moods:
            return {"average_mood": 0.0, "trend": 0.0, "std_dev": 0.0, "min_mood": 0, "max_mood": 0, "improvement_since_baseline": 0.0}
            
        scores = [m.mood_score for m in moods]
        avg = sum(scores) / len(scores)
        
        # Simple trend: contrast first half vs second half of history
        mid = len(scores) // 2
        trend = (sum(scores[:mid]) / mid - sum(scores[mid:]) / (len(scores) - mid)) if mid > 0 else 0.0
        
        return {
            "average_mood": float(avg),
            "trend": float(trend),
            "std_dev": float(0.0), # Simplified for now
            "min_mood": min(scores),
            "max_mood": max(scores),
            "improvement_since_baseline": 0.0 # Calculate against baseline_phq9 or similar
        }

    def get_activity_mood_correlation(self, db: Session, user_id: int, days: int = 7) -> Dict[str, Any]:
        """Analyze average mood after specific activity types."""
        # This would require more complex grouping logic
        return {"social": {"improvement": 1.2}, "exercise": {"improvement": 0.8}}
