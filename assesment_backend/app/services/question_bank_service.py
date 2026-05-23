from app.models import Question

# ===================================
# SAVE GENERATED QUESTIONS
# ===================================

def save_generated_questions(

    db,

    questions,

    teacher_email,

    exam_id
):

    saved_questions = []

    for question_data in questions:

        options = question_data.get(
            "options",
            []
        )

        # -----------------------------------
        # ENSURE 4 OPTIONS
        # -----------------------------------

        while len(options) < 4:

            options.append("N/A")

        db_question = Question(

            question=question_data.get(
                "question"
            ),

            option_a=options[0],

            option_b=options[1],

            option_c=options[2],

            option_d=options[3],

            correct_answer=question_data.get(
                "correct_answer"
            ),

            difficulty=question_data.get(
                "difficulty"
            ),

            subject=question_data.get(
                "subject",
                question_data.get("topic")
            ),

            topic=question_data.get(
                "topic"
            ),

            question_type=question_data.get(
                "question_type",
                "mcq"
            ),

            marks=question_data.get(
                "marks",
                1
            ),

            keywords=question_data.get(
                "keywords"
            ),

            solution_steps=question_data.get(
                "solution_steps"
            ),

            explanation=question_data.get(
                "explanation"
            ),

            test_cases=question_data.get(
                "test_cases"
            ),

            source=question_data.get(
                "source",
                "AI Generated"
            ),

            created_by=teacher_email,

            exam_id=exam_id
        )

        db.add(db_question)

        saved_questions.append(
            db_question
        )

    db.commit()

    return saved_questions
