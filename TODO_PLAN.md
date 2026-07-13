# TODO Plan — Hospital Backend Production-Ready Build

## 0. Baseline inspection
- [x] Inspect existing FastAPI app entrypoint and config.
- [x] Inspect existing authentication (JWT + Firebase) and RBAC dependencies.
- [x] Inspect DB layer (async SQLAlchemy) and models (partial).
- [ ] Enumerate all current models/schemas/routers/services for mismatches with required DB spec.

## 1. Standardize architecture
- [ ] Unify repository package naming (`app/repositories/` vs `app/repository/`).
- [ ] Ensure imports are consistent across routers/services.
- [ ] Ensure dependency injection patterns are consistent.

## 2. Schema management with Alembic
- [ ] Check Alembic folder contents and add missing `alembic.ini` / `env.py` if required.
- [ ] Configure Alembic for async SQLAlchemy + PostgreSQL.
- [ ] Remove/disable `Base.metadata.create_all` usage in startup.
- [ ] Generate initial migration matching required tables.

## 3. Data model correctness
- [ ] Align SQLAlchemy models to required columns:
  - users: firebase_uid, phone, gender, age, address, role, specialization, department, experience, qualification
  - appointments: status, department, specialization
  - prescriptions: appointment_id/patient_id/doctor_id + diagnosis/medicines/dosage/notes
  - medical_reports: report_name/report_type/diagnosis/file_url/notes
  - billing: fees/discount/total_amount/payment_status/payment_method
- [ ] Ensure FK relationships & indexes.

## 4. Authentication & Security
- [ ] Add JWT claims: `jti`, role, type enforcement for access vs refresh.
- [ ] Implement refresh token rotation + persistence/denylist (or explicit stateless strategy).
- [ ] Add `/auth/logout`.
- [ ] Rate limiting: make config-driven and safe for multi-instance (Redis option or guardrails).
- [ ] Add security headers middleware (basic).

## 5. REST endpoints completion
- [ ] Implement missing endpoints per spec using APIRouter:
  - /patient/profile, /doctor/profile
  - /appointment/book, /appointment/list, /appointment/update
  - /prescription/create, /prescription/list
  - /report/upload, /report/list
  - /billing/create, /billing/list
  - admin dashboard + management endpoints
  - staff: patient check-in, appointment queue, generate bill, view patients
- [ ] Add pagination/filtering/search/sorting query params.

## 6. Global error handling & response schemas
- [ ] Add global exception handler.
- [ ] Standardize response format.

## 7. Observability
- [ ] Ensure structured logging and request logging.
- [ ] Add correlation/request id.

## 8. Async correctness
- [ ] Ensure repository queries are fully async.
- [ ] Ensure file uploads are handled with async and validated.

## 9. Docker + Render deployment
- [ ] Create Dockerfile + docker-compose.yml with PostgreSQL.
- [ ] Add `.env.example`.
- [ ] Add Render config files / Procfile alignment.
- [ ] README with run/migrate instructions.

## 10. Verification
- [ ] Run unit smoke checks: `python -m compileall`.
- [ ] Run migrations and start server in SQLite and Postgres modes.
- [ ] Verify Swagger auth flow.

