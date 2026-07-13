from fastapi import APIRouter, Depends

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role, get_current_user, require_role
from app.schemas.appointment_schema import AppointmentResponse
from app.schemas.user_schema import UserOut

router = APIRouter(prefix="/doctor", tags=["Doctor"])


@router.get("/profile", response_model=UserOut)
async def doctor_profile(current_user=Depends(require_role(Role.DOCTOR))) -> UserOut:
    return UserOut(
        id=current_user.uid,
        firebase_uid=current_user.uid,
        full_name=current_user.full_name,
        email=current_user.email,
        phone=None,
        gender=None,
        age=None,
        address=None,
        role=current_user.role,
        specialization=None,
        department=None,
        experience=None,
        qualification=None,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=None,
    )


@router.get("/appointments", response_model=list[AppointmentResponse])
async def doctor_appointments(current_user=Depends(require_role(Role.DOCTOR))) -> list[AppointmentResponse]:
    client = get_firestore_client()
    appointments = [
        AppointmentResponse(id=doc.id, **doc.to_dict())
        for doc in client.collection("appointments").where("doctor_id", "==", current_user.uid).stream()
    ]
    return appointments
