from pydantic import BaseModel, EmailStr, Field
from typing import TypeVar, Generic, Optional

T = TypeVar("T")

class BaseResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None

class PatientCreate(BaseModel):
    full_name: str

    email: EmailStr
    password: str
    age: int
    gender: str
    phone: str
    address: Optional[str] = None

class PatientResponse(BaseModel):
    id: int
    full_name: str

    email: str
    age: int
    gender: str
    phone: str
    address: Optional[str] = None

    class Config:
        from_attributes = True
