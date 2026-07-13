from app.core.firebase import get_firestore_client
from app.schemas.user_schema import UserOut
from app.dependencies.auth import Role


class AdminService:
    @staticmethod
    def _build_user_response(doc) -> UserOut:
        data = doc.to_dict() or {}
        return UserOut(
            id=doc.id,
            firebase_uid=doc.id,
            full_name=data.get("full_name", ""),
            email=data.get("email", ""),
            phone=data.get("phone"),
            gender=data.get("gender"),
            age=data.get("age"),
            address=data.get("address"),
            role=data.get("role", Role.PATIENT),
            specialization=data.get("specialization"),
            department=data.get("department"),
            experience=data.get("experience"),
            qualification=data.get("qualification"),
            is_active=data.get("is_active", True),
            is_verified=data.get("is_verified", False),
            created_at=data.get("created_at"),
        )

    @staticmethod
    def dashboard() -> dict:
        client = get_firestore_client()
        return {
            "total_patients": len(list(client.collection("users").where("role", "==", Role.PATIENT).stream())),
            "total_doctors": len(list(client.collection("users").where("role", "==", Role.DOCTOR).stream())),
            "total_staff": len(list(client.collection("users").where("role", "==", Role.STAFF).stream())),
            "total_appointments": len(list(client.collection("appointments").stream())),
            "total_reports": len(list(client.collection("reports").stream())),
            "total_billing": len(list(client.collection("billings").stream())),
        }

    @staticmethod
    def list_users_by_role(role: str) -> list[UserOut]:
        client = get_firestore_client()
        return [
            AdminService._build_user_response(doc)
            for doc in client.collection("users").where("role", "==", role).stream()
        ]
