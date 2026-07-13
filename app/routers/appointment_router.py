from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role, get_current_user, require_role
from app.schemas.appointment_schema import AppointmentCreate, AppointmentResponse, AppointmentUpdate

router = APIRouter(prefix="/appointment", tags=["Appointments"])


@router.post("/book", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def book_appointment(
    payload: AppointmentCreate,
    current_user=Depends(require_role(Role.PATIENT)),
) -> AppointmentResponse:
    if payload.patient_id != current_user.uid:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot book for another patient")

    client = get_firestore_client()
    appointment_data = payload.model_dump()
    appointment_data["status"] = "pending"
    appointment_data["created_at"] = datetime.utcnow()

    appointment_ref = client.collection("appointments").document()
    appointment_ref.set(appointment_data)
    return AppointmentResponse(id=appointment_ref.id, **appointment_data)


@router.get("/list", response_model=list[AppointmentResponse])
async def list_appointments(current_user=Depends(get_current_user)) -> list[AppointmentResponse]:
    client = get_firestore_client()
    query = client.collection("appointments")

    if current_user.role == Role.PATIENT:
        query = query.where("patient_id", "==", current_user.uid)
    elif current_user.role == Role.DOCTOR:
        query = query.where("doctor_id", "==", current_user.uid)

    appointments = [
        AppointmentResponse(id=doc.id, **doc.to_dict())
        for doc in query.stream()
    ]

    return appointments


@router.put("/update/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    payload: AppointmentUpdate,
    current_user=Depends(get_current_user),
) -> AppointmentResponse:
    client = get_firestore_client()
    appointment_ref = client.collection("appointments").document(appointment_id)
    appointment_snapshot = appointment_ref.get()
    if not appointment_snapshot.exists:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment_data = appointment_snapshot.to_dict() or {}
    if current_user.role == Role.PATIENT and appointment_data.get("patient_id") != current_user.uid:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == Role.DOCTOR and appointment_data.get("doctor_id") != current_user.uid:
        raise HTTPException(status_code=403, detail="Access denied")

    updated_data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not updated_data:
        return AppointmentResponse(id=appointment_id, **appointment_data)

    appointment_ref.update(updated_data)
    appointment_data.update(updated_data)
    return AppointmentResponse(id=appointment_id, **appointment_data)
