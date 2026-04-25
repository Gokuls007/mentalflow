from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.models.user import User
from app.models.clinical import Activity, Assessment
import logging

logger = logging.getLogger(__name__)

def calculate_xp_and_impact(user: User, game_session, db: Session):
    """
    Calculate XP and clinical impact for a completed activity session.
    """
    base_xp = 85 # Standard activity reward
    
    # 1. Mood improvement reward
    mood_delta = 0
    if game_session.mood_after is not None and game_session.mood_before is not None:
        mood_delta = game_session.mood_after - game_session.mood_before
    
    mood_bonus = max(0, mood_delta * 15) # +15 XP per point of improvement
    
    # 2. Engagement multiplier
    engagement = game_session.engagement_rating or 5
    engagement_multiplier = 1.0 + (engagement / 10.0) # 1.1x to 2.0x
    
    # 3. Streak bonus
    streak_multiplier = 1.0
    if user.current_streak >= 30: streak_multiplier = 3.0
    elif user.current_streak >= 14: streak_multiplier = 2.0
    elif user.current_streak >= 7: streak_multiplier = 1.5
    
    # Total Calculation
    total_xp = int((base_xp + mood_bonus) * engagement_multiplier * streak_multiplier)
    
    # Update User XP
    user.total_xp += total_xp
    
    # Check Level Up
    new_level = (user.total_xp // 1000) + 1
    if new_level > user.current_level:
        user.current_level = new_level
        _unlock_features_for_level(user)
        
    return {
        "xp_earned": total_xp,
        "mood_delta": mood_delta,
        "new_total_xp": user.total_xp,
        "new_level": user.current_level
    }

def update_clinical_scores(user: User, db: Session):
    """
    Update PHQ-9/GAD-7 scores based on recent activity trends.
    This simulates the 'Biological Impact' of the therapy.
    """
    
    # Get activities from the last 7 days
    one_week_ago = datetime.utcnow() - timedelta(days=7)
    recent_activities = db.query(Activity).filter(
        Activity.user_id == user.id,
        Activity.completed_at >= one_week_ago
    ).all()
    
    if not recent_activities:
        return None
    
    # Calculate average mood improvement
    improvements = []
    for a in recent_activities:
        # Check game sessions linked to these activities
        from app.models.clinical import GameSession
        session = db.query(GameSession).filter_by(activity_id=a.id, completed=True).first()
        if session and session.mood_after is not None and session.mood_before is not None:
            improvements.append(session.mood_after - session.mood_before)
            
    avg_improvement = sum(improvements) / len(improvements) if improvements else 0
    
    # Reduction logic: More activities + better mood = lower clinical scores
    # Every 2 activities = -1 point
    # Every 1.0 avg mood improvement = -1 point
    reduction = (len(recent_activities) * 0.5) + (avg_improvement * 1.0)
    
    # Update PHQ-9
    old_phq9 = user.latest_phq9_score or user.baseline_phq9 or 15
    new_phq9 = max(0, old_phq9 - reduction)
    user.latest_phq9_score = int(new_phq9)
    
    # Update GAD-7
    old_gad7 = user.latest_gad7_score or user.baseline_gad7 or 12
    new_gad7 = max(0, old_gad7 - reduction * 0.8) # Anxiety drops slightly slower than depression in this model
    user.latest_gad7_score = int(new_gad7)
    
    # Update Severity
    user.clinical_severity = _get_severity(user.latest_phq9_score)
    
    db.commit()
    
    return {
        "phq9": user.latest_phq9_score,
        "gad7": user.latest_gad7_score,
        "severity": user.clinical_severity,
        "reduction": reduction
    }

def _get_severity(score: int) -> str:
    if score < 5: return "Minimal"
    if score < 10: return "Mild"
    if score < 15: return "Moderate"
    if score < 20: return "Moderately Severe"
    return "Severe"

def _unlock_features_for_level(user: User):
    level_locks = {
        2: "mood_chart",
        3: "clinical_ai",
        5: "analytics_dashboard",
        7: "social_community",
        10: "therapist_connect"
    }
    
    # Ensure user.unlocked_features is a list
    if not isinstance(user.unlocked_features, list):
        user.unlocked_features = []
        
    for lvl, feature in level_locks.items():
        if user.current_level >= lvl and feature not in user.unlocked_features:
            user.unlocked_features.append(feature)
            logger.info(f"User {user.id} unlocked {feature} at level {user.current_level}")
