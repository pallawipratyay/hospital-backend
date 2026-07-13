from fastapi import HTTPException, status
from datetime import datetime

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role
from app.schemas.billing_schema import BillingCreate, BillingResponse


class BillingService:
    @staticmethod
    def create(payload: BillingCreate, current_user) -> BillingResponse:
        if current_user.role not in [Role.ADMIN, Role.STAFF]:
            raise PermissionError("Unauthorized")

        client = get_firestore_client()
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

        billing_ref = client.collection("billings").document()
        billing_ref.set(data)
        return BillingResponse(id=billing_ref.id, **data)

    @staticmethod
    def list(current_user):
        client = get_firestore_client()
        query = client.collection("billings")
        if current_user.role == Role.PATIENT:
            query = query.where("patient_id", "==", current_user.uid)
        return [BillingResponse(id=doc.id, **doc.to_dict()) for doc in query.stream()]
