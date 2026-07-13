from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    department: Optional[str] = None
    experience: Optional[str] = None
    qualification: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    role: Optional[str] = Field(default="patient")


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    department: Optional[str] = None
    experience: Optional[str] = None
    qualification: Optional[str] = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    firebase_uid: Optional[str] = None
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    role: str
    specialization: Optional[str] = None
    department: Optional[str] = None
    experience: Optional[str] = None
    qualification: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime] = None
