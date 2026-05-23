from app.models import Question

# ===================================
# FETCH EXAM QUESTIONS
# ===================================

def get_exam_for_student(

    db,

    exam_id
):

    # -----------------------------------
    # FETCH QUESTIONS DIRECTLY
    # -----------------------------------

    questions = db.query(
        Question
    ).filter(

        Question.exam_id == exam_id
    ).all()

    formatted_questions = []

    # -----------------------------------
    # FORMAT QUESTIONS
    # -----------------------------------

    for question in questions:

        formatted_questions.append({

            "id": question.id,

            "question": question.question,

            "question_type": question.question_type or "mcq",

            "difficulty": question.difficulty,

            "subject": question.subject,

            "topic": question.topic,

            "marks": question.marks or 1,

            "options": [

                question.option_a,

                question.option_b,

                question.option_c,

                question.option_d
            ],

            "keywords": question.keywords,

            "solution_steps": question.solution_steps,

            "test_cases": question.test_cases
        })

    return formatted_questions
