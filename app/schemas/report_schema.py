from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ReportCreate(BaseModel):
    appointment_id: str
    patient_id: str
    doctor_id: str
    report_name: str
    report_type: str
    diagnosis: Optional[str] = None
    medicines: Optional[str] = None
    dosage: Optional[str] = None
    notes: Optional[str] = None
    file_url: Optional[str] = None


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    appointment_id: str
    patient_id: str
    doctor_id: str
    report_name: str
    report_type: str
    diagnosis: Optional[str] = None
    medicines: Optional[str] = None
    dosage: Optional[str] = None
    notes: Optional[str] = None
    upload_date: Optional[datetime] = None
    file_url: Optional[str] = None
    created_at: Optional[datetime] = None
