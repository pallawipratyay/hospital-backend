from app.core.firebase import create_firebase_user, create_user_profile
from app.dependencies.auth import Role
from app.schemas.patient_schema import PatientCreate
from app.schemas.user_schema import UserOut


class PatientService:
    @staticmethod
    def register_patient(patient_data: PatientCreate) -> UserOut:
        user_record = create_firebase_user(
            email=patient_data.email,
            password=patient_data.password,
            display_name=patient_data.full_name,
            role=Role.PATIENT,
            phone=patient_data.phone,
        )
        profile_data = {
            "full_name": patient_data.full_name,
            "email": patient_data.email,
            "phone": patient_data.phone,
            "gender": patient_data.gender,
            "age": patient_data.age,
            "address": patient_data.address,
            "role": Role.PATIENT,
            "is_verified": False,
        }
        create_user_profile(user_record.uid, profile_data)
        return UserOut(
            id=user_record.uid,
            firebase_uid=user_record.uid,
            full_name=patient_data.full_name,
            email=patient_data.email,
            phone=patient_data.phone,
            gender=patient_data.gender,
            age=patient_data.age,
            address=patient_data.address,
            role=Role.PATIENT,
            is_active=True,
            is_verified=False,
            created_at=profile_data.get("created_at"),
        )
