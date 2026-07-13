from pydantic import BaseModel, EmailStr
from typing import Optional, List, Generic, TypeVar

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None

class DoctorBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    qualification: str
    department: str
    specialization: str
    experience: str

class DoctorCreate(DoctorBase):
    password: str

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    qualification: Optional[str] = None
    department: Optional[str] = None
    specialization: Optional[str] = None
    experience: Optional[str] = None

class DoctorResponse(DoctorBase):
    id: int
    class Config:
        from_attributes = True
