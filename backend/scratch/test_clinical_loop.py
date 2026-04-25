from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.models.clinical import Activity, GameSession
from app.services.clinical import calculate_xp_and_impact, update_clinical_scores
from datetime import datetime

def test_clinical_feedback_loop():
    db = SessionLocal()
    try:
        # 1. Setup Mock User
        user = db.query(User).filter_by(id=1).first()
        if not user:
            print("❌ User 1 not found. Creating mock user.")
            user = User(id=1, email="test@mentalflow.com", password_hash="hash", baseline_phq9=14, latest_phq9_score=14)
            db.add(user)
            db.commit()

        print(f"--- START STATE ---")
        print(f"XP: {user.total_xp} | Level: {user.current_level} | PHQ-9: {user.latest_phq9_score}")

        # 2. Simulate 5 successful activities with mood improvement
        for i in range(5):
            activity = Activity(user_id=user.id, type="physical", difficulty=5.0, completed_at=datetime.utcnow())
            db.add(activity)
            db.flush()
            
            session = GameSession(
                user_id=user.id,
                activity_id=activity.id,
                completed=True,
                mood_before=4,
                mood_after=7, # +3 improvement
                engagement_rating=9,
                difficulty_level="medium",
                score=1000
            )
            db.add(session)
            
            # Calculate impact
            impact = calculate_xp_and_impact(user, session, db)
            print(f"Session {i+1}: +{impact['xp_earned']} XP | Level now: {impact['new_level']}")

        db.commit()

        # 3. Trigger Weekly Clinical Update
        print(f"\n--- TRIGGERING CLINICAL SYNC ---")
        update = update_clinical_scores(user, db)
        print(f"New PHQ-9: {update['phq9']} (Reduction: {update['reduction']})")
        print(f"Clinical Severity: {update['severity']}")

        print(f"\n--- FINAL STATE ---")
        print(f"XP: {user.total_xp} | Level: {user.current_level} | PHQ-9: {user.latest_phq9_score} | Severity: {user.clinical_severity}")

    finally:
        db.close()

if __name__ == "__main__":
    test_clinical_feedback_loop()
