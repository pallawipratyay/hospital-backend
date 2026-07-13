from datetime import datetime

from fastapi import HTTPException, status

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role
from app.schemas.appointment_schema import AppointmentCreate, AppointmentUpdate, AppointmentResponse


class AppointmentService:
    @staticmethod
    def book(payload: AppointmentCreate, current_user) -> AppointmentResponse:
        if current_user.role != Role.PATIENT:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can book appointments")
        if payload.patient_id and payload.patient_id != current_user.uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot book for another patient")

        client = get_firestore_client()
        data = payload.model_dump()
        data["patient_id"] = current_user.uid
        data["created_at"] = datetime.utcnow()

        appointment_ref = client.collection("appointments").document()
        appointment_ref.set(data)
        return AppointmentResponse(id=appointment_ref.id, **data)

    @staticmethod
    def list(current_user):
        client = get_firestore_client()
        query = client.collection("appointments")
        if current_user.role == Role.PATIENT:
            query = query.where("patient_id", "==", current_user.uid)
        elif current_user.role == Role.DOCTOR:
            query = query.where("doctor_id", "==", current_user.uid)
        return [AppointmentResponse(id=doc.id, **doc.to_dict()) for doc in query.stream()]

    @staticmethod
    def update(appointment_id: str, payload: AppointmentUpdate, current_user):
        client = get_firestore_client()
        appointment_ref = client.collection("appointments").document(appointment_id)
        appointment_snapshot = appointment_ref.get()
        if not appointment_snapshot.exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")

        appointment = appointment_snapshot.to_dict() or {}
        if current_user.role == Role.PATIENT and appointment.get("patient_id") != current_user.uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        if current_user.role == Role.DOCTOR and appointment.get("doctor_id") != current_user.uid:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        updates = {k: v for k, v in payload.model_dump().items() if v is not None}
        if updates:
            appointment_ref.update(updates)

        updated_snapshot = appointment_ref.get()
        return AppointmentResponse(id=updated_snapshot.id, **updated_snapshot.to_dict())
