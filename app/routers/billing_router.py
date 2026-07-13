from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role, get_current_user
from app.schemas.billing_schema import BillingCreate, BillingResponse

router = APIRouter(prefix="/billing", tags=["Billing"])


def _build_billing_response(doc) -> BillingResponse:
    data = doc.to_dict() or {}
    return BillingResponse(
        id=doc.id,
        appointment_id=data.get("appointment_id", ""),
        patient_id=data.get("patient_id", ""),
        doctor_id=data.get("doctor_id", ""),
        consultation_fee=data.get("consultation_fee", 0.0),
        medicine_fee=data.get("medicine_fee", 0.0),
        physiotherapy_fee=data.get("physiotherapy_fee", 0.0),
        test_fee=data.get("test_fee", 0.0),
        other_fee=data.get("other_fee", 0.0),
        discount=data.get("discount", 0.0),
        total_amount=data.get("total_amount", 0.0),
        payment_status=data.get("payment_status", "pending"),
        payment_method=data.get("payment_method"),
        created_at=data.get("created_at"),
    )


@router.post("/create", response_model=BillingResponse, status_code=status.HTTP_201_CREATED)
async def create_billing(payload: BillingCreate, current_user=Depends(get_current_user)) -> BillingResponse:
    if current_user.role not in [Role.ADMIN, Role.STAFF]:
        raise HTTPException(status_code=403, detail="Unauthorized")

    data = payload.model_dump()
    data["total_amount"] = (
        data["consultation_fee"]
        + data["medicine_fee"]
        + data["physiotherapy_fee"]
        + data["test_fee"]
        + data["other_fee"]
        - data["discount"]
    )
    data["payment_status"] = "pending"
    data["created_at"] = datetime.utcnow()

    client = get_firestore_client()
    billing_ref = client.collection("billings").document()
    billing_ref.set(data)
    return _build_billing_response(billing_ref.get())


@router.get("/list", response_model=list[BillingResponse])
async def list_bills(current_user=Depends(get_current_user)) -> list[BillingResponse]:
    client = get_firestore_client()
    query = client.collection("billings")
    if current_user.role == Role.PATIENT:
        query = query.where("patient_id", "==", current_user.uid)

    return [_build_billing_response(doc) for doc in query.stream()]
