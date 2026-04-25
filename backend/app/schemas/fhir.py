from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class FHIRResource(BaseModel):
    resourceType: str
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class FHIRPatient(FHIRResource):
    resourceType: str = "Patient"
    active: bool = True
    name: List[Dict[str, Any]]
    gender: Optional[str] = None
    birthDate: Optional[str] = None
    telecom: Optional[List[Dict[str, Any]]] = None

class FHIRObservation(FHIRResource):
    resourceType: str = "Observation"
    status: str = "final"
    category: List[Dict[str, Any]]
    code: Dict[str, Any] # LOINC codes for PHQ-9 (44249-1) or GAD-7 (69737-5)
    subject: Dict[str, str] # Reference to Patient
    effectiveDateTime: datetime
    valueQuantity: Optional[Dict[str, Any]] = None
    valueString: Optional[str] = None
    interpretation: Optional[List[Dict[str, Any]]] = None

class FHIRCarePlan(FHIRResource):
    resourceType: str = "CarePlan"
    status: str = "active"
    intent: str = "plan"
    category: List[Dict[str, Any]]
    title: str
    description: Optional[str] = None
    subject: Dict[str, str]
    period: Dict[str, datetime]
    activity: List[Dict[str, Any]] # The Behavioral Activation tasks

class FHIRBundle(FHIRResource):
    """
    Used to wrap multiple clinical observations for a user.
    """
    resourceType: str = "Bundle"
    type: str = "collection"
    entry: List[Dict[str, Any]]
