from sqlalchemy.orm import Session

from app.models import Question

# -----------------------------------
# FETCH QUESTIONS
# -----------------------------------

def get_all_questions(db: Session):

    return db.query(Question).all()

# -----------------------------------
# CREATE QUESTION
# -----------------------------------

def create_question(

    db: Session,

    question_data: dict
):

    question = Question(

        question=question_data["question"],

        option_a=question_data["option_a"],

        option_b=question_data["option_b"],

        option_c=question_data["option_c"],

        option_d=question_data["option_d"],

        correct_answer=question_data["correct_answer"],

        difficulty=question_data["difficulty"],

        subject=question_data["subject"]
    )

    db.add(question)

    db.commit()

    db.refresh(question)

    return question