from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth as firebase_auth

from app.core.firebase import (
    create_firebase_user,
    create_user_profile,
    generate_password_reset_link,
    get_user_profile,
    verify_firebase_token,
)
from app.dependencies.auth import Role, get_current_user
from app.schemas.auth_schema import (
    AuthResponse,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    TokenData,
)
from app.schemas.user_schema import UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse)
async def register_user(payload: RegisterRequest) -> AuthResponse:
    try:
        firebase_auth.get_user_by_email(payload.email)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    except firebase_auth.UserNotFoundError:
        pass

    role = payload.role.lower() if payload.role else Role.PATIENT
    user_record = create_firebase_user(
        email=payload.email,
        password=payload.password,
        display_name=payload.full_name,
        role=role,
        phone=payload.phone,
    )

    user_data = {
        "full_name": payload.full_name,
        "email": payload.email,
        "phone": payload.phone,
        "gender": payload.gender,
        "age": payload.age,
        "address": payload.address,
        "role": role,
        "specialization": payload.specialization,
        "department": payload.department,
        "experience": payload.experience,
        "qualification": payload.qualification,
        "firebase_uid": user_record.uid,
        "is_verified": False,
    }
    create_user_profile(user_record.uid, user_data)

    return AuthResponse(
        success=True,
        message="Registered successfully",
        data=TokenData(
            access_token="",
            refresh_token="",
            role=role,
            user=UserOut(
                id=user_record.uid,
                firebase_uid=user_record.uid,
                full_name=payload.full_name,
                email=payload.email,
                phone=payload.phone,
                gender=payload.gender,
                age=payload.age,
                address=payload.address,
                role=role,
                specialization=payload.specialization,
                department=payload.department,
                experience=payload.experience,
                qualification=payload.qualification,
                is_active=True,
                is_verified=False,
                created_at=user_data["created_at"],
            ),
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest) -> AuthResponse:
    payload_data = verify_firebase_token(payload.id_token)
    uid = payload_data.get("uid") or payload_data.get("sub")
    if not uid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Firebase ID token")

    user_profile = get_user_profile(uid)
    if not user_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    return AuthResponse(
        success=True,
        message="Login successful",
        data=TokenData(
            access_token=payload.id_token,
            refresh_token="",
            role=user_profile.get("role", Role.PATIENT),
            user=UserOut(
                id=uid,
                firebase_uid=uid,
                full_name=user_profile.get("full_name", ""),
                email=user_profile.get("email", ""),
                phone=user_profile.get("phone"),
                gender=user_profile.get("gender"),
                age=user_profile.get("age"),
                address=user_profile.get("address"),
                role=user_profile.get("role", Role.PATIENT),
                specialization=user_profile.get("specialization"),
                department=user_profile.get("department"),
                experience=user_profile.get("experience"),
                qualification=user_profile.get("qualification"),
                is_active=user_profile.get("is_active", True),
                is_verified=user_profile.get("is_verified", False),
                created_at=user_profile.get("created_at"),
            ),
        ),
    )


@router.post("/forgot-password", response_model=AuthResponse)
async def forgot_password(payload: ForgotPasswordRequest) -> AuthResponse:
    reset_link = generate_password_reset_link(payload.email)
    return AuthResponse(success=True, message="Password reset link generated", data=TokenData(access_token="", refresh_token=reset_link, role="", user=None))


@router.post("/change-password", response_model=AuthResponse)
async def change_password(payload: ChangePasswordRequest, current_user=Depends(get_current_user)) -> AuthResponse:
    update_user_password(current_user.uid, payload.new_password)
    return AuthResponse(success=True, message="Password updated successfully")


@router.get("/verify-firebase")
async def verify_firebase(current_user=Depends(get_current_user)) -> dict[str, str]:
    return {"status": "verified", "user_id": current_user.uid}
