from app.core.firebase import create_firebase_user, create_user_profile, update_user_password
from app.dependencies.auth import Role
from app.schemas.auth_schema import LoginRequest, RegisterRequest
from app.schemas.user_schema import UserOut


class AuthService:
    @staticmethod
    def register(payload: RegisterRequest) -> UserOut:
        role = payload.role.lower() if payload.role else Role.PATIENT
        user_record = create_firebase_user(
            email=payload.email,
            password=payload.password,
            display_name=payload.full_name,
            role=role,
            phone=payload.phone,
        )

        user_data = {
            "full_name": payload.full_name,
            "email": payload.email,
            "phone": payload.phone,
            "gender": payload.gender,
            "age": payload.age,
            "address": payload.address,
            "role": role,
            "specialization": payload.specialization,
            "department": payload.department,
            "experience": payload.experience,
            "qualification": payload.qualification,
            "firebase_uid": user_record.uid,
            "is_verified": False,
        }
        create_user_profile(user_record.uid, user_data)
        return UserOut(
            id=user_record.uid,
            firebase_uid=user_record.uid,
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            gender=payload.gender,
            age=payload.age,
            address=payload.address,
            role=role,
            specialization=payload.specialization,
            department=payload.department,
            experience=payload.experience,
            qualification=payload.qualification,
            is_active=True,
            is_verified=False,
            created_at=user_data.get("created_at"),
        )

    @staticmethod
    def login(payload: LoginRequest):
        return payload

    @staticmethod
    def change_password(user, new_password: str) -> bool:
        update_user_password(user.uid, new_password)
        return True
