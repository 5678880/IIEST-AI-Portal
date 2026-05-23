from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.security import verify_token

from app.services.exam_delivery_service import (
    get_exam_for_student
)

router = APIRouter()

# -----------------------------------
# START EXAM
# -----------------------------------

@router.get("/start_exam/{exam_id}")

def start_exam(

    exam_id: int,

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        verify_token
    )
):

    questions = get_exam_for_student(

        db,

        exam_id
    )

    return {

        "exam_id": exam_id,

        "student": current_user["email"],

        "questions": questions
    }