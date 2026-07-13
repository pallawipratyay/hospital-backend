from fastapi import APIRouter, Depends

from app.dependencies.auth import Role, require_role

router = APIRouter(prefix="/staff", tags=["Staff"])


@router.get("/dashboard")
async def staff_dashboard(current_user=Depends(require_role(Role.STAFF))):
    return {"message": "Staff dashboard placeholder"}
