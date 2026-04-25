import logging
from sqlalchemy.orm import Session
from app.ai.rl_engine import rl_engine
from app.models import User
from app.db.database import SessionLocal
from datetime import datetime

logger = logging.getLogger(__name__)

def train_all_users(db: Session):
    """
    Daily training job - train RL model on all users' data
    """
    
    logger.info("Starting daily RL training job")
    
    try:
        users = db.query(User).filter_by(is_active=True).all()
        
        for user in users:
            try:
                rl_engine.train_on_user_feedback(user.id, db, timesteps=200)
            except Exception as e:
                logger.error(f"Error training user {user.id}: {e}")
                
    except Exception as e:
        logger.error(f"Failed to query active users: {e}")
    
    logger.info("Daily RL training completed")


def run_training_job():
    """Wrapper for the scheduler to handle DB sessions"""
    db = SessionLocal()
    try:
        train_all_users(db)
    finally:
        db.close()


def schedule_daily_training():
    """
    Schedule the daily training job using APScheduler
    """
    
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    
    scheduler = BackgroundScheduler()
    
    # Train at 3 AM daily
    scheduler.add_job(
        run_training_job,
        trigger=CronTrigger(hour=3, minute=0),
        id='daily_rl_training',
        name='Daily RL Training',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("RL training scheduler started")
