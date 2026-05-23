from sqlalchemy import inspect
from sqlalchemy import text

from app.database import engine


QUESTION_COLUMNS = {
    "subject": "VARCHAR",
    "question_type": "VARCHAR DEFAULT 'mcq'",
    "marks": "FLOAT DEFAULT 1",
    "keywords": "TEXT",
    "solution_steps": "TEXT",
    "explanation": "TEXT",
    "test_cases": "TEXT",
    "source": "VARCHAR",
    "university_pattern": "VARCHAR",
    "repeated_concept": "VARCHAR"
}


EXAM_COLUMNS = {
    "subject": "VARCHAR",
    "subject_code": "VARCHAR",
    "semester": "VARCHAR",
    "exam_type": "VARCHAR"
}


ENROLLMENT_COLUMNS = {
    "student_name": "VARCHAR",
    "roll_no": "VARCHAR"
}


def ensure_question_schema():
    inspector = inspect(engine)

    if "questions" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("questions")
    }

    with engine.begin() as connection:
        for column_name, column_type in QUESTION_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE questions ADD COLUMN {column_name} {column_type}"
                    )
                )


def ensure_exam_schema():
    inspector = inspect(engine)

    if "exams" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("exams")
    }

    with engine.begin() as connection:
        for column_name, column_type in EXAM_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE exams ADD COLUMN {column_name} {column_type}"
                    )
                )


def ensure_enrollment_schema():
    inspector = inspect(engine)

    if "student_subject_enrollments" not in inspector.get_table_names():
        return

    existing_columns = {
        column["name"]
        for column in inspector.get_columns("student_subject_enrollments")
    }

    with engine.begin() as connection:
        for column_name, column_type in ENROLLMENT_COLUMNS.items():
            if column_name not in existing_columns:
                connection.execute(
                    text(
                        f"ALTER TABLE student_subject_enrollments ADD COLUMN {column_name} {column_type}"
                    )
                )


def cleanup_placeholder_questions():
    inspector = inspect(engine)

    if "questions" not in inspector.get_table_names():
        return

    with engine.begin() as connection:
        rows = connection.execute(
            text(
                """
                SELECT id, question, topic, subject
                FROM questions
                WHERE option_a = 'Correct Answer'
                   OR option_b LIKE 'Wrong Answer%'
                   OR option_c LIKE 'Wrong Answer%'
                   OR option_d LIKE 'Wrong Answer%'
                   OR question LIKE 'What is the purpose of %'
                """
            )
        ).mappings().all()

        for row in rows:
            raw_topic = (
                row.get("topic")
                or row.get("subject")
                or row.get("question")
                or "this concept"
            )
            topic = (
                raw_topic
                .replace("What is the purpose of", "")
                .replace("?", "")
                .strip()
            )

            if not topic:
                topic = "this concept"

            question = f"Which option best explains {topic}?"
            option_a = (
                f"{topic} is a core concept used to understand, design, "
                "or solve real problems in this subject."
            )
            option_b = (
                f"{topic} is only a memorized term and has no practical "
                "use in exams or projects."
            )
            option_c = (
                f"{topic} is mainly used to decorate diagrams and does not "
                "affect how a system works."
            )
            option_d = (
                f"{topic} can be ignored because it is unrelated to the "
                "main ideas of the subject."
            )

            connection.execute(
                text(
                    """
                    UPDATE questions
                    SET question = :question,
                        option_a = :option_a,
                        option_b = :option_b,
                        option_c = :option_c,
                        option_d = :option_d,
                        correct_answer = :option_a,
                        question_type = 'mcq',
                        marks = 1,
                        source = 'Cleaned legacy question bank'
                    WHERE id = :question_id
                    """
                ),
                {
                    "question_id": row["id"],
                    "question": question,
                    "option_a": option_a,
                    "option_b": option_b,
                    "option_c": option_c,
                    "option_d": option_d
                }
            )
