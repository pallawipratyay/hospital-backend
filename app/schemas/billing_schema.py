from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BillingCreate(BaseModel):
    appointment_id: str
    patient_id: str
    doctor_id: str
    consultation_fee: float = 0.0
    medicine_fee: float = 0.0
    physiotherapy_fee: float = 0.0
    test_fee: float = 0.0
    other_fee: float = 0.0
    discount: float = 0.0
    payment_method: Optional[str] = None


class BillingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    appointment_id: str
    patient_id: str
    doctor_id: str
    consultation_fee: float
    medicine_fee: float
    physiotherapy_fee: float
    test_fee: float
    other_fee: float
    discount: float
    total_amount: float
    payment_status: str
    payment_method: Optional[str] = None
    created_at: Optional[datetime] = None
