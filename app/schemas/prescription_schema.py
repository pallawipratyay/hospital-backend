from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PrescriptionCreate(BaseModel):
    appointment_id: str
    patient_id: str
    doctor_id: str
    diagnosis: Optional[str] = None
    medicines: Optional[str] = None
    dosage: Optional[str] = None
    notes: Optional[str] = None


class PrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    appointment_id: str
    patient_id: str
    doctor_id: str
    diagnosis: Optional[str] = None
    medicines: Optional[str] = None
    dosage: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
