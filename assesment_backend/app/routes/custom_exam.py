from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.security import verify_token
from app.services.custom_exam_service import create_custom_exam
from app.services.custom_exam_service import create_exam_sets
from app.services.custom_exam_service import populate_exam_from_bank
from app.services.custom_exam_service import preview_question_sets
from app.services.question_seed_service import seed_question_bank


router = APIRouter()


@router.post("/custom_exam")
def generate_custom_exam(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") not in ["student", "teacher"]:
        raise HTTPException(
            status_code=403,
            detail="Student Or Teacher Access Only"
        )

    return create_custom_exam(
        db,
        data,
        current_user["email"]
    )


@router.post("/seed_question_bank")
def seed_questions(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Teacher Access Only"
        )

    count = seed_question_bank(db)

    return {
        "message": "Question bank ready",
        "seed_questions": count
    }


@router.post("/populate_exam_from_bank")
def add_bank_questions_to_exam(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Teacher Access Only"
        )

    return populate_exam_from_bank(
        db,
        data,
        current_user["email"]
    )


@router.post("/preview_question_sets")
def preview_sets(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Teacher Access Only")

    return preview_question_sets(db, data)


@router.post("/create_exam_sets")
def create_sets(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Teacher Access Only")

    return create_exam_sets(db, data, current_user["email"])
