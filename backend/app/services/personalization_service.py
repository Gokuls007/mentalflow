from sqlalchemy.orm import Session
from app.models.user import User
from app.models.clinical import Activity, GameSession
from app.ai.personalization_engine import personalization_engine
from app.services.behavioral_activation import BehavioralActivationService
from typing import List

class PersonalizationService:
    """
    Orchestrates the selection of activities using both 
    Behavioral Activation rules and ML predictions.
    """
    
    @staticmethod
    def get_prescribed_activities(user: User, db: Session) -> List[Activity]:
        """
        Returns a set of activities optimized for the user's current clinical state.
        """
        # 1. Get the standard BA tasks for the week
        ba_plan = BehavioralActivationService.get_user_ba_plan(user, db)
        
        # 2. Get candidates (recent or generic)
        # In production, this would query a large library of GAN-generated activities
        candidates = db.query(Activity).filter(
            Activity.user_id == user.id
        ).limit(10).all()
        
        if not candidates:
            # Fallback to prescribing new BA activity
            ba_activity = BehavioralActivationService.prescribe_ba_activities(user, db)
            return [ba_activity]
            
        # 3. Use ML to rank candidates based on predicted mood improvement
        prediction = personalization_engine.predict_best_activity(user, candidates)
        
        # 4. Tag the best activity with the ML reason
        best_activity = prediction["activity"]
        best_activity.clinical_explanation = prediction["reason"]
        best_activity.personalization_score = prediction["predicted_gain"]
        
        db.commit()
        
        return candidates

    @staticmethod
    def process_session_completion(user: User, session: GameSession, db: Session):
        """
        Called when a user finishes a game session.
        Feeds the results back into the ML personalization engine.
        """
        activity = db.query(Activity).filter_by(id=session.activity_id).first()
        if activity:
            gain = personalization_engine.track_outcome(user, session, activity, db)
            return gain
        return 0
