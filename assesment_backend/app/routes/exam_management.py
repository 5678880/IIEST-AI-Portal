from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.security import verify_token

from app.services.exam_management_service import (
    create_exam,
    get_all_exams
)

router = APIRouter()

# -----------------------------------
# CREATE EXAM
# -----------------------------------

@router.post("/create_exam")

def create_new_exam(

    data: dict,

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        verify_token
    )
):

    # -----------------------------------
    # TEACHER ONLY
    # -----------------------------------

    if current_user["role"] != "teacher":

        return {

            "error":

            "Only teachers can create exams"
        }

    exam = create_exam(

        db,

        data,

        current_user["email"]
    )

    return {

        "message":

        "Exam Created Successfully",

        "exam_id": exam.id
    }

# -----------------------------------
# FETCH EXAMS
# -----------------------------------

@router.get("/exams")

def fetch_exams(

    db: Session = Depends(get_db)
):

    exams = get_all_exams(db)

    # -----------------------------------
    # SERIALIZE DATA
    # -----------------------------------

    serialized_exams = []

    for exam in exams:

        serialized_exams.append({

            "id": exam.id,

            "title": exam.title,

            "description": exam.description,

            "subject": exam.subject,

            "subject_code": exam.subject_code,

            "semester": exam.semester,

            "exam_type": exam.exam_type,

            "duration_minutes":
            exam.duration_minutes,

            "start_time":
            exam.start_time,

            "end_time":
            exam.end_time,

            "status":
            exam.status,

            "created_by":
            exam.created_by
        })

    return serialized_exams
