from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.clinical import Activity, GameSession
from app.schemas.activity import ActivityCreate, ActivityUpdate

# Optional RL import - not required for basic activity CRUD
try:
    from app.rl.agent import MentalHealthRLAgent
except ImportError:
    MentalHealthRLAgent = None

class ActivityService:
    """Business logic for Behavioral Activation activities."""
    
    def get_activity(self, db: Session, activity_id: int, user_id: int) -> Optional[Activity]:
        return db.query(Activity).filter(
            Activity.id == activity_id, 
            Activity.user_id == user_id
        ).first()
        
    def list_activities(
        self, 
        db: Session, 
        user_id: int, 
        activity_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Activity]:
        query = db.query(Activity).filter(Activity.user_id == user_id)
        if activity_type:
            query = query.filter(Activity.type == activity_type)
        return query.offset(offset).limit(limit).all()
        
    def create_activity(self, db: Session, user_id: int, activity_in: ActivityCreate) -> Activity:
        db_activity = Activity(
            user_id=user_id,
            **activity_in.dict()
        )
        db.add(db_activity)
        db.commit()
        db.refresh(db_activity)
        return db_activity

    def update_activity(
        self, 
        db: Session, 
        activity_id: int, 
        user_id: int, 
        activity_update: ActivityUpdate
    ) -> Optional[Activity]:
        db_activity = self.get_activity(db, activity_id, user_id)
        if not db_activity:
            return None
            
        update_data = activity_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_activity, field, value)
            
        db.commit()
        db.refresh(db_activity)
        return db_activity

    def complete_activity(self, db: Session, activity_id: int, user_id: int) -> Optional[Activity]:
        """
        Mark activity as completed and initialize a GameSession for data tracking.
        """
        db_activity = self.get_activity(db, activity_id, user_id)
        if not db_activity:
            return None
            
        db_activity.completion_count += 1
        db_activity.last_completed = datetime.utcnow()
        db_activity.completed_at = datetime.utcnow()
        db_activity.date_completed = datetime.utcnow().date()
        
        # Create a GameSession record
        game_session = GameSession(
            user_id=user_id,
            activity_id=activity_id,
            difficulty_level="medium", # Default, updated by RL prediction later
            completed=True,
            created_at=datetime.utcnow()
        )
        db.add(game_session)
        
        db.commit()
        db.refresh(db_activity)
        return db_activity

    def delete_activity(self, db: Session, activity_id: int, user_id: int) -> bool:
        db_activity = self.get_activity(db, activity_id, user_id)
        if db_activity:
            db.delete(db_activity)
            db.commit()
            return True
        return False
