from pydantic import BaseModel, EmailStr, Field
from typing import Optional

from app.schemas.user_schema import UserOut


class LoginRequest(BaseModel):
    id_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ChangePasswordRequest(BaseModel):
    new_password: str = Field(..., min_length=6)


class TokenData(BaseModel):
    access_token: str
    refresh_token: str = ""
    token_type: str = "bearer"
    role: str
    user: Optional[UserOut] = None


class AuthResponse(BaseModel):
    success: bool
    message: str
    data: Optional[TokenData] = None


class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: Optional[str] = Field(default="patient")
    phone: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    address: Optional[str] = None
    specialization: Optional[str] = None
    department: Optional[str] = None
    experience: Optional[str] = None
    qualification: Optional[str] = None
