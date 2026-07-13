from datetime import datetime

from fastapi import HTTPException, status

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role
from app.schemas.report_schema import ReportCreate, ReportResponse


class ReportService:
    @staticmethod
    def upload(payload: ReportCreate, current_user) -> ReportResponse:
        if current_user.role not in [Role.DOCTOR, Role.ADMIN]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only doctors or admin can upload reports")

        client = get_firestore_client()
        data = payload.model_dump()
        data["upload_date"] = datetime.utcnow()
        data["created_at"] = datetime.utcnow()
        report_ref = client.collection("reports").document()
        report_ref.set(data)
        return ReportResponse(id=report_ref.id, **data)

    @staticmethod
    def list(current_user) -> list[ReportResponse]:
        client = get_firestore_client()
        query = client.collection("reports")
        if current_user.role == Role.PATIENT:
            query = query.where("patient_id", "==", current_user.uid)
        elif current_user.role == Role.DOCTOR:
            query = query.where("doctor_id", "==", current_user.uid)
        return [ReportResponse(id=doc.id, **doc.to_dict()) for doc in query.stream()]

    @staticmethod
    def list_by_patient(patient_id: str, current_user) -> list[ReportResponse]:
        if current_user.role == Role.PATIENT and current_user.uid != patient_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        client = get_firestore_client()
        return [ReportResponse(id=doc.id, **doc.to_dict()) for doc in client.collection("reports").where("patient_id", "==", patient_id).stream()]
