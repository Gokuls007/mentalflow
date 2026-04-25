from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from app.models.clinical import Assessment
from app.schemas.assessment import PHQ9Create, GAD7Create

class AssessmentService:
    """Business logic for Clinical Assessments (PHQ-9, GAD-7)."""
    
    SEVERITY_MAPS = {
        "phq9": [
            (4, "minimal"), (9, "mild"), (14, "moderate"), 
            (19, "moderately severe"), (27, "severe")
        ],
        "gad7": [
            (4, "minimal"), (9, "mild"), (14, "moderate"), (21, "severe")
        ]
    }
    
    def _calculate_severity(self, assessment_type: str, score: int) -> str:
        mapping = self.SEVERITY_MAPS.get(assessment_type, [])
        for threshold, severity in mapping:
            if score <= threshold:
                return severity
        return "unknown"

    def detect_crisis_level(self, responses: List[int]) -> int:
        """
        Safety protocol for PHQ-9.
        Item 9: 'Thoughts that you would be better off dead, or of hurting yourself'
        0 = Not at all, 1 = Several days, 2 = More than half the days, 3 = Nearly every day
        """
        # PHQ-9 has 9 items. Index 8 is Item 9.
        if len(responses) < 9:
            return 0
            
        item_9 = responses[8]
        if item_9 >= 1:
            return 1 # Passive Ideation (Level 1)
            
        return 0

    def create_assessment(
        self, 
        db: Session, 
        user_id: int, 
        assessment_type: str, 
        assessment_in: Any
    ) -> Dict[str, Any]:
        score = sum(assessment_in.responses)
        severity = self._calculate_severity(assessment_type, score)
        
        db_assessment = Assessment(
            user_id=user_id,
            type=assessment_type,
            score=score,
            responses=assessment_in.responses,
            severity=severity,
            date=assessment_in.date
        )
        db.add(db_assessment)
        
        # Safety Check
        crisis_level = 0
        if assessment_type == "phq9":
            crisis_level = self.detect_crisis_level(assessment_in.responses)
            
        db.commit()
        db.refresh(db_assessment)
        
        return {
            "assessment": db_assessment,
            "crisis_level": crisis_level,
            "severity": severity,
            "score": score
        }

    def get_latest_assessment(self, db: Session, user_id: int, assessment_type: str) -> Optional[Assessment]:
        return db.query(Assessment).filter(
            Assessment.user_id == user_id,
            Assessment.type == assessment_type
        ).order_by(Assessment.date.desc()).first()

    def get_assessment_history(
        self, 
        db: Session, 
        user_id: int, 
        assessment_type: str = "all",
        limit: int = 20
    ) -> Dict[str, Any]:
        """Fetch history and calculate trends."""
        history = {"phq9": [], "gad7": [], "phq9_trend": 0, "gad7_trend": 0}
        
        types_to_fetch = ["phq9", "gad7"] if assessment_type == "all" else [assessment_type]
        
        for t in types_to_fetch:
            assessments = db.query(Assessment).filter(
                Assessment.user_id == user_id,
                Assessment.type == t
            ).order_by(Assessment.date.desc()).limit(limit).all()
            
            history[t] = assessments
            if len(assessments) >= 2:
                history[f"{t}_trend"] = assessments[0].score - assessments[1].score
                
        return history
