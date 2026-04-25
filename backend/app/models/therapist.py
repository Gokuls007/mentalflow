from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Therapist(Base):
    __tablename__ = "therapist"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    
    license_number = Column(String(100), nullable=False, unique=True)
    specialization = Column(String(255))
    bio = Column(Text)
    
    # Onboarding Checks
    license_verified = Column(Boolean, default=False)
    insurance_active = Column(Boolean, default=False)
    background_check_passed = Column(Boolean, default=False)
    hipaa_certified = Column(Boolean, default=False)
    
    max_caseload = Column(Integer, default=20)
    current_caseload = Column(Integer, default=0)
    
    rating = Column(Float, default=5.0)
    status = Column(String(50), default="onboarding") # onboarding, active, suspended
    
    created_at = Column(DateTime, server_default=func.now())
    
    user = relationship("User", back_populates="therapist_profile")
    patients = relationship("User", back_populates="assigned_therapist", foreign_keys="User.therapist_id")

class ClinicalPrescription(Base):
    """
    Therapists can manually adjust or prescribe BA plans for patients.
    """
    __tablename__ = "clinical_prescription"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    therapist_id = Column(Integer, ForeignKey("therapist.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    
    target_area = Column(String(50)) # PHYSICAL, SOCIAL, COGNITIVE
    intensity_adjustment = Column(Float, default=1.0) # Multiplier for task difficulty
    notes = Column(Text)
    
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    
    therapist = relationship("Therapist")
    patient = relationship("User", foreign_keys=[patient_id])
