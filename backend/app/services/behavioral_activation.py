from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models.user import User
from app.models.clinical import Activity
from typing import List, Dict, Any

class BehavioralActivationService:
    """
    Implements structured Behavioral Activation (BA) progression.
    Replaces random activities with clinical 4-week plans.
    """
    
    PLANS = {
        "PHYSICAL": {
            1: {"task": "5 min walk", "micro": True, "description": "Gentle movement to activate blood flow. No pressure to go further."},
            2: {"task": "10 min walk + Music", "micro": False, "description": "Extended movement with positive auditory stimulation."},
            3: {"task": "15 min brisk walk", "micro": False, "description": "Increasing intensity to stimulate endorphin release."},
            4: {"task": "Walk with a friend", "micro": False, "description": "Combining physical activation with social connection."}
        },
        "SOCIAL": {
            1: {"task": "Text one friend", "micro": True, "description": "Low-stakes reconnection to break isolation."},
            2: {"task": "5 min phone call", "micro": False, "description": "Real-time verbal engagement with a trusted person."},
            3: {"task": "Video chat (10 min)", "micro": False, "description": "Visual and verbal connection to enhance empathy and mirroring."},
            4: {"task": "Meet for coffee", "micro": False, "description": "In-person social interaction in a controlled environment."}
        },
        "COGNITIVE": {
            1: {"task": "Read 1 page of a book", "micro": True, "description": "Micro-focus to rebuild attention span."},
            2: {"task": "10 min journaling", "micro": False, "description": "Externalizing thoughts to gain perspective."},
            3: {"task": "Learn 1 new skill (video)", "micro": False, "description": "Stimulating neuroplasticity through novel learning."},
            4: {"task": "Solve a complex puzzle", "micro": False, "description": "Deep focus session to stimulate executive function."}
        },
        "SELF_CARE": {
            1: {"task": "Drink 500ml water", "micro": True, "description": "Foundation of physiological regulation."},
            2: {"task": "5 min shower/grooming", "micro": True, "description": "Maintaining personal hygiene as a baseline win."},
            3: {"task": "Cook one healthy meal", "micro": False, "description": "Active nutrition and mastery in the kitchen."},
            4: {"task": "Sleep protocol (Before 11pm)", "micro": False, "description": "Regulating circadian rhythm for mood stability."}
        }
    }

    @staticmethod
    def get_user_ba_plan(user: User, db: Session) -> Dict[str, Any]:
        """
        Determines the user's current BA week and next prescribed task.
        """
        # Calculate week since user joined/started BA
        days_active = (datetime.utcnow() - user.created_at).days
        current_week = (days_active // 7) + 1
        current_week = min(4, current_week) # Cap at 4 weeks for this phase
        
        # Get target area based on clinical profile
        # Default to PHYSICAL as it's the strongest BA starter
        target_area = user.anxiety_trigger.upper() if user.anxiety_trigger else "PHYSICAL"
        if target_area not in BehavioralActivationService.PLANS:
            target_area = "PHYSICAL"
            
        tasks = BehavioralActivationService.PLANS[target_area]
        current_task = tasks.get(current_week, tasks[1])
        
        return {
            "week": current_week,
            "target_area": target_area,
            "task": current_task["task"],
            "description": current_task["description"],
            "is_micro_habit": current_task["micro"],
            "progression_percent": (current_week / 4) * 100
        }

    @staticmethod
    def prescribe_ba_activities(user: User, db: Session):
        """
        Populates the user's activity list with the prescribed BA tasks.
        Clears out old 'random' activities.
        """
        plan = BehavioralActivationService.get_user_ba_plan(user, db)
        
        # Check if already prescribed today
        today = datetime.utcnow().date()
        existing = db.query(Activity).filter(
            Activity.user_id == user.id,
            Activity.date_scheduled == today,
            Activity.source == "ba_prescription"
        ).first()
        
        if existing:
            return existing

        # Create new BA Activity
        ba_activity = Activity(
            user_id=user.id,
            type=plan["target_area"].lower(),
            difficulty=float(plan["week"] * 2), # Difficulty scales with week
            duration_minutes=5 * plan["week"],
            title=plan["task"],
            description=plan["description"],
            date_scheduled=today,
            source="ba_prescription",
            clinical_explanation=f"Week {plan['week']} Behavioral Activation for {plan['target_area']}"
        )
        
        db.add(ba_activity)
        db.commit()
        db.refresh(ba_activity)
        return ba_activity
