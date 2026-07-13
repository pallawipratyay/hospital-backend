from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.firebase import initialize_firebase
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import (
    admin_router,
    appointment_router,
    auth_router,
    billing_router,
    doctor_router,
    patient_router,
    prescription_router,
    report_router,
    staff_router,
)
from app.utils.error_handlers import register_exception_handlers
from app.utils.logging.logger import configure_logging

configure_logging()

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    version="1.0.0",
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(patient_router)
app.include_router(doctor_router)
app.include_router(admin_router)
app.include_router(appointment_router)
app.include_router(prescription_router)
app.include_router(report_router)
app.include_router(billing_router)
app.include_router(staff_router)

register_exception_handlers(app)


@app.on_event("startup")
async def startup_event() -> None:
    initialize_firebase()


@app.get("/", tags=["Health"])
def health_check() -> dict[str, str]:
    return {"status": "ok", "message": "Hospital backend running"}
