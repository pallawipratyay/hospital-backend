from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.firebase import get_firestore_client
from app.dependencies.auth import Role, get_current_user
from app.schemas.report_schema import ReportCreate, ReportResponse
from app.utils.response import success_response

router = APIRouter(prefix="/report", tags=["Reports"])


def _build_report_response(doc) -> ReportResponse:
    data = doc.to_dict() or {}
    return ReportResponse(
        id=doc.id,
        appointment_id=data.get("appointment_id", ""),
        patient_id=data.get("patient_id", ""),
        doctor_id=data.get("doctor_id", ""),
        report_name=data.get("report_name", ""),
        report_type=data.get("report_type", ""),
        diagnosis=data.get("diagnosis"),
        medicines=data.get("medicines"),
        dosage=data.get("dosage"),
        notes=data.get("notes"),
        upload_date=data.get("upload_date"),
        file_url=data.get("file_url"),
        created_at=data.get("created_at"),
    )


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def upload_report(payload: ReportCreate, current_user=Depends(get_current_user)):
    if current_user.role not in [Role.DOCTOR, Role.ADMIN]:
        raise HTTPException(status_code=403, detail="Only doctors or admin can upload reports")

    data = payload.model_dump()
    data["upload_date"] = datetime.utcnow()
    data["created_at"] = datetime.utcnow()

    client = get_firestore_client()
    report_ref = client.collection("reports").document()
    report_ref.set(data)

    report_data = _build_report_response(report_ref.get())
    return success_response(message="Report added successfully", data=report_data)


@router.get("/all")
async def list_reports(current_user=Depends(get_current_user)):
    client = get_firestore_client()
    query = client.collection("reports")

    # RBAC logic
    if current_user.role == Role.PATIENT:
        query = query.where("patient_id", "==", current_user.uid)
    elif current_user.role == Role.DOCTOR:
        query = query.where("doctor_id", "==", current_user.uid)

    reports = [_build_report_response(doc) for doc in query.stream()]
    return success_response(data=reports)


@router.get("/patient/{patient_id}")
async def get_patient_reports(patient_id: str, current_user=Depends(get_current_user)):
    if current_user.role == Role.PATIENT and current_user.uid != patient_id:
        raise HTTPException(status_code=403, detail="Access denied")

    client = get_firestore_client()
    reports = [_build_report_response(doc) for doc in client.collection("reports").where("patient_id", "==", patient_id).stream()]
    return success_response(data=reports)

@router.put("/update/{report_id}")
async def update_report(report_id: str, payload: ReportCreate, current_user=Depends(get_current_user)):
    client = get_firestore_client()
    report_ref = client.collection("reports").document(report_id)
    if not report_ref.get().exists:
        raise HTTPException(status_code=404, detail="Report not found")

    data = payload.model_dump()
    report_ref.update(data)
    return success_response(message="Report updated successfully")

@router.delete("/{report_id}")
async def delete_report(report_id: str, current_user=Depends(get_current_user)):
    client = get_firestore_client()
    report_ref = client.collection("reports").document(report_id)
    if not report_ref.get().exists:
        raise HTTPException(status_code=404, detail="Report not found")

    report_ref.delete()
    return success_response(message="Report deleted successfully")
