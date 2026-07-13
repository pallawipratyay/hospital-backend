from datetime import datetime

from fastapi import HTTPException, status

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role
from app.schemas.prescription_schema import PrescriptionCreate, PrescriptionResponse


class PrescriptionService:
    @staticmethod
    def create(payload: PrescriptionCreate, current_user) -> PrescriptionResponse:
        if current_user.role != Role.DOCTOR:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors can create prescriptions")

        client = get_firestore_client()
        data = payload.model_dump()
        data["created_at"] = datetime.utcnow()
        prescription_ref = client.collection("prescriptions").document()
        prescription_ref.set(data)
        return PrescriptionResponse(id=prescription_ref.id, **data)

    @staticmethod
    def list(current_user) -> list[PrescriptionResponse]:
        client = get_firestore_client()
        query = client.collection("prescriptions")
        if current_user.role == Role.PATIENT:
            query = query.where("patient_id", "==", current_user.uid)
        elif current_user.role == Role.DOCTOR:
            query = query.where("doctor_id", "==", current_user.uid)
        return [PrescriptionResponse(id=doc.id, **doc.to_dict()) for doc in query.stream()]
