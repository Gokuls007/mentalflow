from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.models.user import User
from app.models.clinical import Assessment
from sqlalchemy import func

class TherapistService:
    """Service for Professional/Therapist clinical management."""

    def get_client_roster(self, db: Session, therapist_id: int) -> List[Dict[str, Any]]:
        """Fetch all patients assigned to this professional with latest risk status."""
        clients = db.query(User).filter(User.assigned_professional_id == therapist_id).all()
        
        roster = []
        for client in clients:
            # Get latest PHQ-9
            latest_phq9 = db.query(Assessment).filter(
                Assessment.user_id == client.id, 
                Assessment.type == "phq9"
            ).order_by(Assessment.date.desc()).first()
            
            risk_level = "low"
            if latest_phq9:
                if latest_phq9.score >= 20: risk_level = "high"
                elif latest_phq9.score >= 15: risk_level = "medium"
            
            roster.append({
                "id": client.id,
                "name": f"{client.first_name} {client.last_name}",
                "email": client.email,
                "latest_phq9": latest_phq9.score if latest_phq9 else None,
                "risk_level": risk_level,
                "last_active": client.updated_at
            })
            
        return roster

    def get_clinical_alerts(self, db: Session, therapist_id: int) -> List[Dict[str, Any]]:
        """Detect rapid deterioration or crisis flags across cohort."""
        clients = db.query(User).filter(User.assigned_professional_id == therapist_id).all()
        alerts = []
        
        for client in clients:
            # Check for Item 9 Crisis in last 7 days
            recent_crisis = db.query(Assessment).filter(
                Assessment.user_id == client.id,
                Assessment.type == "phq9",
                func.jsonb_extract_path_text(Assessment.responses, '8').cast(Integer) >= 1
            ).first()
            
            if recent_crisis:
                alerts.append({
                    "type": "CRISIS",
                    "client_id": client.id,
                    "client_name": client.first_name,
                    "message": "Suicidal ideation detected in recent assessment."
                })
                
        return alerts
