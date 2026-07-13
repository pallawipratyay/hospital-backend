from fastapi import APIRouter, Depends

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role, get_current_user
from app.schemas.user_schema import UserOut

router = APIRouter(prefix="/admin", tags=["Admin"])


def _load_users_by_role(role: str) -> list[UserOut]:
    client = get_firestore_client()
    users = []
    for doc in client.collection("users").where("role", "==", role).stream():
        user_data = doc.to_dict() or {}
        users.append(
            UserOut(
                id=doc.id,
                firebase_uid=doc.id,
                full_name=user_data.get("full_name", ""),
                email=user_data.get("email", ""),
                phone=user_data.get("phone"),
                gender=user_data.get("gender"),
                age=user_data.get("age"),
                address=user_data.get("address"),
                role=user_data.get("role", role),
                specialization=user_data.get("specialization"),
                department=user_data.get("department"),
                experience=user_data.get("experience"),
                qualification=user_data.get("qualification"),
                is_active=user_data.get("is_active", True),
                is_verified=user_data.get("is_verified", False),
                created_at=user_data.get("created_at"),
            )
        )
    return users


def _count_documents(collection: str, field: str | None = None, value: str | None = None) -> int:
    client = get_firestore_client()
    query = client.collection(collection)
    if field and value is not None:
        query = query.where(field, "==", value)
    return len(list(query.stream()))


@router.get("/dashboard")
async def admin_dashboard(current_user=Depends(get_current_user)):
    if current_user.role != Role.ADMIN:
        return {"detail": "Unauthorized"}

    return {
        "total_patients": _count_documents("users", "role", Role.PATIENT),
        "total_doctors": _count_documents("users", "role", Role.DOCTOR),
        "total_staff": _count_documents("users", "role", Role.STAFF),
        "total_appointments": _count_documents("appointments"),
        "total_reports": _count_documents("reports"),
        "total_billing": _count_documents("billings"),
    }


@router.get("/patients", response_model=list[UserOut])
async def get_patients(current_user=Depends(get_current_user)) -> list[UserOut]:
    if current_user.role != Role.ADMIN:
        return []
    return _load_users_by_role(Role.PATIENT)


@router.get("/doctors", response_model=list[UserOut])
async def get_doctors(current_user=Depends(get_current_user)) -> list[UserOut]:
    if current_user.role != Role.ADMIN:
        return []
    return _load_users_by_role(Role.DOCTOR)


@router.get("/staff", response_model=list[UserOut])
async def get_staff(current_user=Depends(get_current_user)) -> list[UserOut]:
    if current_user.role != Role.ADMIN:
        return []
    return _load_users_by_role(Role.STAFF)
