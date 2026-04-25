from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from app.db.database import SessionLocal
from app.models.user import User
from app.ai.rl_engine import rl_engine
from app.services.clinical import update_clinical_scores
import logging

logger = logging.getLogger(__name__)

def run_daily_clinical_sync():
    """
    Nightly job to sync AI models and clinical outcomes.
    """
    db = SessionLocal()
    try:
        logger.info("Starting daily clinical sync job...")
        
        # 1. Get all active users
        users = db.query(User).filter_by(is_active=True).all()
        
        for user in users:
            try:
                # 2. Update PHQ-9/GAD-7 based on the week's performance
                update_clinical_scores(user, db)
                
                # 3. Retrain RL model for this user
                # LinUCB is updated live, but we can do a batch refinement here
                rl_engine.engine.save_model() # Ensure state is persisted
                
                logger.info(f"Sync complete for user {user.id}")
            except Exception as e:
                logger.error(f"Failed to sync user {user.id}: {e}")
                
        db.commit()
        logger.info("Daily clinical sync job finished successfully.")
    finally:
        db.close()

def schedule_clinical_jobs():
    """
    Initialize the background scheduler.
    """
    scheduler = BackgroundScheduler()
    
    # Run at 3:00 AM every day
    scheduler.add_job(
        run_daily_clinical_sync,
        'cron',
        hour=3,
        minute=0,
        id='clinical_sync'
    )
    
    scheduler.start()
    logger.info("Background scheduler for clinical jobs started.")
