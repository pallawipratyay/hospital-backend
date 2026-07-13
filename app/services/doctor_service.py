from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role
from app.schemas.user_schema import UserOut
from app.schemas.doctor_schema import DoctorCreate, DoctorUpdate
from datetime import datetime

class DoctorService:
    @staticmethod
    def add_doctor(doctor_in: DoctorCreate):
        client = get_firestore_client()
        docs = list(client.collection("users").where("email", "==", doctor_in.email).stream())
        if docs:
            return None, "Doctor with this email already exists"

        data = doctor_in.model_dump()
        data["role"] = Role.DOCTOR
        data["created_at"] = datetime.utcnow()
        doctor_ref = client.collection("users").document()
        doctor_ref.set(data)
        return doctor_ref.id, "Doctor Added Successfully"

    @staticmethod
    def get_doctors() -> list[UserOut]:
        client = get_firestore_client()
        doctors = []
        for doc in client.collection("users").where("role", "==", Role.DOCTOR).stream():
            doctors.append(UserOut(id=doc.id, firebase_uid=doc.id, **doc.to_dict()))
        return doctors

    @staticmethod
    def get_doctor_by_id(doctor_id: str) -> UserOut | None:
        client = get_firestore_client()
        doc = client.collection("users").document(doctor_id).get()
        if not doc.exists:
            return None
        return UserOut(id=doc.id, firebase_uid=doc.id, **doc.to_dict())

    @staticmethod
    def update_doctor(doctor_id: str, doctor_in: DoctorUpdate):
        client = get_firestore_client()
        doctor_ref = client.collection("users").document(doctor_id)
        if not doctor_ref.get().exists:
            return None
        updates = {k: v for k, v in doctor_in.model_dump().items() if v is not None}
        if updates:
            doctor_ref.update(updates)
        return doctor_id

    @staticmethod
    def remove_doctor(doctor_id: str) -> bool:
        client = get_firestore_client()
        doctor_ref = client.collection("users").document(doctor_id)
        if not doctor_ref.get().exists:
            return False
        doctor_ref.delete()
        return True
