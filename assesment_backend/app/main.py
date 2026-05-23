from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.services.schema_migration_service import (
    cleanup_placeholder_questions,
    ensure_enrollment_schema,
    ensure_exam_schema,
    ensure_question_schema
)

# -----------------------------------
# ROUTES
# -----------------------------------

from app.routes.auth import (
    router as auth_router
)

from app.routes.questions import (
    router as question_router
)

from app.routes.analytics import (
    router as analytics_router
)

from app.routes.exam_management import (
    router as exam_management_router
)

from app.routes.exam_assembly import (
    router as exam_assembly_router
)

from app.routes.exam_delivery import (
    router as exam_delivery_router
)

from app.routes.exam_submission import (
    router as exam_submission_router
)

from app.routes.results import (
    router as results_router
)

from app.routes.tutor import (
    router as tutor_router
)

from app.routes.custom_exam import (
    router as custom_exam_router
)

from app.routes.enrollments import (
    router as enrollments_router
)

from app.routes.exam_set_assignments import (
    router as exam_set_assignments_router
)

# -----------------------------------
# CREATE DATABASE TABLES
# -----------------------------------

Base.metadata.create_all(
    bind=engine
)

ensure_question_schema()
ensure_exam_schema()
ensure_enrollment_schema()
cleanup_placeholder_questions()

# -----------------------------------
# FASTAPI APP
# -----------------------------------

app = FastAPI(

    title="AI Assessment Platform API"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

# -----------------------------------
# INCLUDE ROUTERS
# -----------------------------------

app.include_router(
    auth_router
)

app.include_router(
    question_router
)

app.include_router(
    analytics_router
)

app.include_router(
    exam_management_router
)

app.include_router(
    exam_assembly_router
)

app.include_router(
    exam_delivery_router
)

app.include_router(
    exam_submission_router
)

app.include_router(
    results_router
)

app.include_router(
    tutor_router
)

app.include_router(
    custom_exam_router
)

app.include_router(
    enrollments_router
)

app.include_router(
    exam_set_assignments_router
)

# -----------------------------------
# ROOT API
# -----------------------------------

@app.get("/")

def home():

    return {

        "message":

        "AI Assessment Backend Running"
    }
