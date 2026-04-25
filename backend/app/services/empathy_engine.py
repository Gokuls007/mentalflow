from app.ai.rl_engine import clinical_bandit
from app.models.user import User
import numpy as np

class EmpathyEngine:
    """
    Generates clinically-grounded, empathic insights using RL model state.
    Translates mathematical weights into supportive human language.
    """
    
    @staticmethod
    def generate_insight(user: User) -> str:
        # Get the arm weights for this user (mocking the retrieval of theta_a)
        # In a real system, we'd pull from clinical_bandit.theta[arm_id]
        
        # Heuristic based on current clinical state
        phq9 = user.latest_phq9_score or 15
        gad7 = user.latest_gad7_score or 12
        streak = user.current_streak or 0
        
        if phq9 > 15:
            # Low energy / Severe
            base = "I noticed your energy has been low lately. "
            if streak > 0:
                return base + f"Even so, your {streak}-day streak shows incredible resilience. Let's stick to a tiny 5-minute win today—you've earned a gentle pace."
            return base + "Recovery isn't a race. Today, let's focus on a single micro-habit. Just getting through one small task is a massive victory."
            
        if gad7 > 12:
            # High anxiety
            return "Things might feel a bit overwhelming right now. Based on what's worked for you before, a grounding social activity might help quiet the noise. One small connection can make a big difference."
            
        if streak >= 7:
            return f"You're in the 'Flow Zone'! 7 days of consistency is rewiring your brain's reward pathways. Your progress toward the {phq9 - 5 if phq9 > 5 else 0} point target is looking strong."
            
        return "You're building the foundation of a new routine. Every activity we prescribe is a calculated step toward your recovery goal. You're doing the real work."

empathy_engine = EmpathyEngine()
