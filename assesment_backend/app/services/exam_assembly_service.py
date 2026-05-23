from app.models import ExamQuestion
from app.models import Question

# -----------------------------------
# LINK QUESTIONS TO EXAM
# -----------------------------------

def add_questions_to_exam(

    db,

    exam_id,

    question_ids
):

    mappings = []

    for question_id in question_ids:

        mapping = ExamQuestion(

            exam_id=exam_id,

            question_id=question_id
        )

        db.add(mapping)

        mappings.append(mapping)

    db.commit()

    return mappings

# -----------------------------------
# FETCH EXAM QUESTIONS
# -----------------------------------

def get_exam_questions(

    db,

    exam_id
):

    mappings = db.query(
        ExamQuestion
    ).filter(

        ExamQuestion.exam_id == exam_id
    ).all()

    questions = []

    for mapping in mappings:

        question = db.query(
            Question
        ).filter(

            Question.id == mapping.question_id
        ).first()

        if question:

            questions.append(question)

    return questions