import os
from datetime import datetime
from typing import Any

import firebase_admin
from firebase_admin import auth, credentials, firestore

from app.core.config import settings


def _credentials_from_json_or_path(value: str):
    value = value.strip()
    # firebase_admin.credentials.Certificate accepts either:
    # - a filesystem path to a service account JSON file
    # - the JSON string itself (commonly injected as an env var)
    return credentials.Certificate(value)




def initialize_firebase() -> None:
    if firebase_admin._apps:
        return

    credentials_path = settings.firebase_credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    # Normalize Render-provided env quirks.
    if credentials_path and isinstance(credentials_path, str):
        credentials_path = credentials_path.strip()
        # If the value is clearly invalid (e.g. just "{"), treat as missing.
        if credentials_path == "{":
            credentials_path = ""



    # Render often injects Firebase credentials as an env var containing JSON.
    # Support both:
    # - credentials_path pointing to a JSON file
    # - credentials JSON string directly
    if not credentials_path:
        firebase_admin.initialize_app(credentials.ApplicationDefault())
        return

    # If Render provides credentials as inline JSON, skip file loading.
    credentials_path = credentials_path.strip()
    if credentials_path.startswith("{"):
        # credentials.Certificate accepts an object or path depending on firebase-admin version.
        # Passing JSON string is the most reliable across environments.
        cred = credentials.Certificate(credentials_path)
        firebase_admin.initialize_app(cred)
        return

    # Otherwise treat it as a filesystem path.
    cred = credentials.Certificate(credentials_path)
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
