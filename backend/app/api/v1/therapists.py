from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.user import User
from app.models.therapist import Therapist, ClinicalPrescription
from app.security.auth import get_current_user
from pydantic import BaseModel
from typing import List

router = APIRouter()

class TherapistOnboard(BaseModel):
    license_number: str
    specialization: str
    bio: str

class PrescriptionCreate(BaseModel):
    patient_id: int
    target_area: str
    intensity_adjustment: float
    notes: str

@router.post("/onboard", response_model=dict)
async def onboard_therapist(
    data: TherapistOnboard,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Onboard a user as a licensed therapist.
    """
    if current_user.role != "professional":
        raise HTTPException(status_code=403, detail="Only professionals can onboard as therapists")
        
    existing = db.query(Therapist).filter_by(user_id=current_user.id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already onboarded as therapist")
        
    therapist = Therapist(
        user_id=current_user.id,
        license_number=data.license_number,
        specialization=data.specialization,
        bio=data.bio,
        status="onboarding" # Requires manual admin verification in production
    )
    
    db.add(therapist)
    db.commit()
    db.refresh(therapist)
    
    return {"status": "success", "message": "Onboarding started. Pending clinical verification."}

@router.get("/patients", response_model=List[dict])
async def get_my_patients(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all patients assigned to this therapist.
    """
    therapist = db.query(Therapist).filter_by(user_id=current_user.id).first()
    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist profile not found")
        
    patients = db.query(User).filter_by(therapist_id=therapist.id).all()
    
    return [
        {
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "email": p.email,
            "phq9": p.latest_phq9_score,
            "gad7": p.latest_gad7_score,
            "severity": p.clinical_severity,
            "ba_week": 3, # Mock week for demo
        } for p in patients
    ]

@router.post("/prescribe")
async def issue_prescription(
    data: PrescriptionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Therapists can issue clinical prescriptions to override or augment AI plans.
    """
    therapist = db.query(Therapist).filter_by(user_id=current_user.id).first()
    if not therapist:
        raise HTTPException(status_code=403, detail="Not an authorized therapist")
        
    prescription = ClinicalPrescription(
        therapist_id=therapist.id,
        patient_id=data.patient_id,
        target_area=data.target_area,
        intensity_adjustment=data.intensity_adjustment,
        notes=data.notes
    )
    
    db.add(prescription)
    db.commit()
    
    return {"status": "success", "message": "Clinical prescription issued."}
