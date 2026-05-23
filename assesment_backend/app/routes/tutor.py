from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException

from app.security import verify_token
from app.services.tutor_service import generate_tutor_answer


router = APIRouter()


@router.post("/ai_tutor")
def ai_tutor(data: dict, current_user: dict = Depends(verify_token)):
    if current_user.get("role") not in ["student", "teacher"]:
        raise HTTPException(
            status_code=403,
            detail="Student Or Teacher Access Only"
        )

    question = data.get(
        "question",
        ""
    ).strip()

    if not question:
        return {
            "answer": "Please enter a question so I can help you learn it.",
            "source": "validation"
        }

    subject = data.get(
        "subject",
        "General"
    )

    difficulty = data.get(
        "difficulty",
        "medium"
    )

    task = data.get(
        "task",
        "answer"
    )

    return generate_tutor_answer(
        question,
        subject,
        difficulty,
        task
    )
