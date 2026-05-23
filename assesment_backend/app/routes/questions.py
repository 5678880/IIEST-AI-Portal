from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import Question

from app.security import verify_token

from app.services.ai_generation_service import (
    generate_questions
)

from app.services.question_bank_service import (
    save_generated_questions
)

router = APIRouter()

# ===================================
# GENERATE QUESTIONS
# ===================================

@router.post("/generate_questions")

def ai_generate_questions(

    data: dict,

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        verify_token
    )
):

    try:

        # -----------------------------------
        # ROLE CHECK
        # -----------------------------------

        if current_user["role"] != "teacher":

            return {

                "generated_questions": []
            }

        # -----------------------------------
        # INPUT DATA
        # -----------------------------------

        topic = data.get("topic")

        difficulty = data.get("difficulty")

        num_questions = data.get(
            "num_questions"
        )

        exam_id = data.get(
            "exam_id"
        )

        # -----------------------------------
        # AI GENERATION
        # -----------------------------------

        questions = generate_questions(

            topic,

            difficulty,

            num_questions
        )

        # -----------------------------------
        # SAVE QUESTIONS
        # -----------------------------------

        save_generated_questions(

            db,

            questions,

            current_user["email"],

            exam_id
        )

        return {

            "generated_questions":
            questions
        }

    except Exception as e:

        print("\nQUESTION ROUTE ERROR:\n")
        print(str(e))

        return {

            "generated_questions": []
        }

# ===================================
# FETCH QUESTIONS
# ===================================

@router.get("/questions")

def fetch_questions(

    db: Session = Depends(get_db)
):

    questions = db.query(
        Question
    ).all()

    serialized_questions = []

    for question in questions:

        serialized_questions.append({

            "id": question.id,

            "question": question.question,

            "subject":
            question.subject,

            "difficulty":
            question.difficulty,

            "topic":
            question.topic,

            "question_type":
            question.question_type,

            "marks":
            question.marks,

            "source":
            question.source,

            "university_pattern":
            question.university_pattern
        })

    return serialized_questions
