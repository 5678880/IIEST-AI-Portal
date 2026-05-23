from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ExamSetAssignment
from app.security import verify_token


router = APIRouter()


def serialize_assignment(item):
    return {
        "id": item.id,
        "teacher_email": item.teacher_email,
        "student_email": item.student_email,
        "student_name": item.student_name,
        "subject": item.subject,
        "subject_code": item.subject_code,
        "set_name": item.set_name,
        "exam_id": item.exam_id,
        "exam_title": item.exam_title,
        "assigned_at": item.assigned_at
    }


@router.post("/exam_set_assignments")
def save_exam_set_assignments(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Teacher Access Only")

    assignments = data.get("assignments") or []
    exam_ids = [
        item.get("exam_id")
        for item in assignments
        if item.get("exam_id")
    ]

    if exam_ids:
        db.query(ExamSetAssignment).filter(
            ExamSetAssignment.teacher_email == current_user["email"],
            ExamSetAssignment.exam_id.in_(exam_ids)
        ).delete(synchronize_session=False)

    saved = []
    assigned_at = datetime.now().strftime("%Y-%m-%d %H:%M")

    for item in assignments:
        row = ExamSetAssignment(
            teacher_email=current_user["email"],
            student_email=item.get("student_email"),
            student_name=item.get("student_name"),
            subject=item.get("subject"),
            subject_code=item.get("subject_code"),
            set_name=item.get("set_name"),
            exam_id=item.get("exam_id"),
            exam_title=item.get("exam_title"),
            assigned_at=assigned_at
        )
        db.add(row)
        saved.append(row)

    db.commit()

    return {
        "saved_assignments": len(saved),
        "assigned_at": assigned_at
    }


@router.get("/exam_set_assignments")
def get_exam_set_assignments(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Teacher Access Only")

    rows = db.query(ExamSetAssignment).filter(
        ExamSetAssignment.teacher_email == current_user["email"]
    ).all()

    return [
        serialize_assignment(item)
        for item in rows
    ]
