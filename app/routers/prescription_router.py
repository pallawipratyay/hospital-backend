from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role, get_current_user
from app.schemas.prescription_schema import PrescriptionCreate, PrescriptionResponse

router = APIRouter(prefix="/prescription", tags=["Prescriptions"])


def _build_prescription_response(doc) -> PrescriptionResponse:
    data = doc.to_dict() or {}
    return PrescriptionResponse(
        id=doc.id,
        appointment_id=data.get("appointment_id", ""),
        patient_id=data.get("patient_id", ""),
        doctor_id=data.get("doctor_id", ""),
        diagnosis=data.get("diagnosis"),
        medicines=data.get("medicines"),
        dosage=data.get("dosage"),
        notes=data.get("notes"),
        created_at=data.get("created_at"),
    )


@router.post("/create", response_model=PrescriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_prescription(payload: PrescriptionCreate, current_user=Depends(get_current_user)) -> PrescriptionResponse:
    if current_user.role != Role.DOCTOR:
        raise HTTPException(status_code=403, detail="Only doctors can create prescriptions")

    data = payload.model_dump()
    data["created_at"] = datetime.utcnow()

    client = get_firestore_client()
    prescription_ref = client.collection("prescriptions").document()
    prescription_ref.set(data)
    return _build_prescription_response(prescription_ref.get())


@router.get("/list", response_model=list[PrescriptionResponse])
async def list_prescriptions(current_user=Depends(get_current_user)) -> list[PrescriptionResponse]:
    client = get_firestore_client()
    query = client.collection("prescriptions")
    if current_user.role == Role.PATIENT:
        query = query.where("patient_id", "==", current_user.uid)
    elif current_user.role == Role.DOCTOR:
        query = query.where("doctor_id", "==", current_user.uid)

    return [_build_prescription_response(doc) for doc in query.stream()]
