from dataclasses import dataclass
from typing import Any

from fastapi import Depends, Header, HTTPException, status

from app.core.firebase import get_firestore_client, verify_firebase_token


class Role(str):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    STAFF = "staff"


@dataclass
class UserContext:
    uid: str
    email: str
    full_name: str
    role: str
    is_active: bool
    is_verified: bool
    extra: dict[str, Any] | None = None


async def get_current_user(authorization: str | None = Header(None)) -> UserContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token required",
        )

    token = authorization.split(" ", 1)[1]
    payload = verify_firebase_token(token)
    uid = payload.get("uid") or payload.get("sub")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )

    client = get_firestore_client()
    user_doc = client.collection("users").document(uid).get()
    if not user_doc.exists:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    user_data = user_doc.to_dict() or {}
    role = user_data.get("role")
    if not role:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User role missing")

    return UserContext(
        uid=uid,
        email=user_data.get("email", payload.get("email", "")),
        full_name=user_data.get("full_name", ""),
        role=role,
        is_active=user_data.get("is_active", True),
        is_verified=user_data.get("is_verified", False),
        extra={"firebase_token": payload},
    )


def require_role(role: str):
    async def role_guard(current_user: UserContext = Depends(get_current_user)) -> UserContext:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User must have role {role}",
            )
        return current_user

    return role_guard
