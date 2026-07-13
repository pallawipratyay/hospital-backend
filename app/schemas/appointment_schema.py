from datetime import date, datetime, time
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AppointmentCreate(BaseModel):
    patient_id: str
    doctor_id: str
    appointment_date: date
    appointment_time: time
    department: Optional[str] = None
    specialization: Optional[str] = None
    symptoms: Optional[str] = None


class AppointmentUpdate(BaseModel):
    status: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    symptoms: Optional[str] = None


class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    patient_id: str
    doctor_id: str
    appointment_date: date
    appointment_time: time
    department: Optional[str] = None
    specialization: Optional[str] = None
    symptoms: Optional[str] = None
    status: str
    created_at: Optional[datetime] = None
