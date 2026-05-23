from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.security import verify_token

from app.services.grading_service import (
    grade_exam
)

router = APIRouter()

# -----------------------------------
# SUBMIT EXAM
# -----------------------------------

@router.post("/submit_exam")

def submit_exam(

    data: dict,

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        verify_token
    )
):

    exam_id = data.get(
        "exam_id"
    )

    answers = data.get(
        "answers",
        {}
    )

    result = grade_exam(

        db,

        exam_id,

        answers,

        current_user["email"]
    )

    return {

        "message":

        "Exam Submitted Successfully",

        "result": result
    }