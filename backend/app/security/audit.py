from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Any, Dict
from app.models.audit import AuditLog
from fastapi import Request

class AuditLogger:
    """Log clinical and security actions for compliance."""
    
    @staticmethod
    def log_action(
        db: Session,
        user_id: Optional[int],
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        changes: Optional[Dict[str, Any]] = None,
        status: str = "success",
        error_message: Optional[str] = None,
        request: Optional[Request] = None
    ):
        """Log a security or clinical event."""
        
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            changes=changes,
            status=status,
            error_message=error_message,
        )
        
        db.add(audit_log)
        db.commit()

# Utility functions for specific logs
def log_clinical_event(db: Session, user_id: int, event: str, details: Dict[str, Any]):
    AuditLogger.log_action(
        db,
        user_id=user_id,
        action=f"clinical_{event}",
        resource_type="clinical",
        changes=details
    )

def log_phi_access(func):
    """Decorator to log access to Protected Health Information (PHI)."""
    import functools
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Implementation depends on context (e.g. current_user in FastAPI)
        # This is a placeholder for the logic to be injected in API routes
        return func(*args, **kwargs)
    return wrapper

class ResearchAnonymizer:
    """Utility for de-identifying data for research exports."""
    
    @staticmethod
    def de_identify_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove PII from user data."""
        safe_data = user_data.copy()
        pii_fields = ['email', 'first_name', 'last_name', 'phone', 'address']
        for field in pii_fields:
            if field in safe_data:
                safe_data[field] = "[REDACTED]"
        
        # Obfuscate ID
        if 'id' in safe_data:
            safe_data['participant_uuid'] = f"P-{hash(str(safe_data['id'])) % 10000:04d}"
            del safe_data['id']
            
        return safe_data
