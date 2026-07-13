import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import firebase_admin
from firebase_admin import auth, credentials, firestore

from app.core.config import settings


def _load_credentials() -> credentials.Certificate:
    firebase_credentials = os.getenv("FIREBASE_CREDENTIALS", "").strip()
    if firebase_credentials:
        try:
            service_account_info = json.loads(firebase_credentials)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FIREBASE_CREDENTIALS is not valid JSON.") from exc
        return credentials.Certificate(service_account_info)

    credentials_path = settings.firebase_credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    credentials_path = str(credentials_path).strip()

    if credentials_path.startswith("{"):
        try:
            service_account_info = json.loads(credentials_path)
        except json.JSONDecodeError as exc:
            raise RuntimeError("FIREBASE_CREDENTIALS_PATH contains invalid JSON.") from exc
        return credentials.Certificate(service_account_info)

    if credentials_path:
        credentials_file = Path(credentials_path)
        if credentials_file.is_file():
            return credentials.Certificate(str(credentials_file))
        raise RuntimeError(f"Firebase credentials file not found at: {credentials_path}")

    local_file = Path(__file__).resolve().parents[2] / "firebase-adminsdk.json"
    if local_file.is_file():
        return credentials.Certificate(str(local_file))

    raise RuntimeError(
        "Firebase credentials not configured. Set FIREBASE_CREDENTIALS env var with service account JSON "
        "or provide a local firebase-adminsdk.json file for development."
    )


def initialize_firebase() -> None:
    if firebase_admin._apps:
        return

    cred = _load_credentials()
    firebase_admin.initialize_app(cred)



def get_firestore_client() -> firestore.Client:
    initialize_firebase()
    return firestore.client()


def get_auth_client() -> auth:
    initialize_firebase()
    return auth


def verify_firebase_token(id_token: str) -> dict[str, Any]:
    try:
        return auth.verify_id_token(id_token)
    except Exception as exc:
        raise ValueError("Invalid Firebase token") from exc


def create_firebase_user(
    email: str,
    password: str,
    display_name: str,
    role: str,
    phone: str | None = None,
) -> auth.UserRecord:
    initialize_firebase()
    user = auth.create_user(
        email=email,
        password=password,
        display_name=display_name,
        disabled=False,
        phone_number=phone,
    )
    auth.set_custom_user_claims(user.uid, {"role": role})
    return user


def create_user_profile(uid: str, profile_data: dict[str, Any]) -> None:
    client = get_firestore_client()
    profile_data = profile_data.copy()
    profile_data["created_at"] = datetime.utcnow()
    profile_data["updated_at"] = datetime.utcnow()
    profile_data["is_active"] = True
    profile_data["is_verified"] = profile_data.get("is_verified", False)
    client.collection("users").document(uid).set(profile_data)


def get_user_profile(uid: str) -> dict[str, Any] | None:
    client = get_firestore_client()
    user_doc = client.collection("users").document(uid).get()
    if not user_doc.exists:
        return None
    return user_doc.to_dict()


def generate_password_reset_link(email: str) -> str:
    initialize_firebase()
    return auth.generate_password_reset_link(email)


def update_user_password(uid: str, new_password: str) -> auth.UserRecord:
    initialize_firebase()
    return auth.update_user(uid, password=new_password)
