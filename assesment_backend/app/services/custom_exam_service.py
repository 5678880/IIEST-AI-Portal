import random

from app.models import Exam
from app.models import Question
from app.services.question_seed_service import seed_question_bank


DURATION_PRESETS = {
    "quick": 10,
    "practice": 30,
    "full": 60
}


def question_to_dict(question):
    return {
        "id": question.id,
        "question": question.question,
        "question_type": question.question_type or "mcq",
        "difficulty": question.difficulty,
        "subject": question.subject,
        "topic": question.topic,
        "marks": question.marks or 1,
        "options": [
            option
            for option in [
                question.option_a,
                question.option_b,
                question.option_c,
                question.option_d
            ]
            if option
        ],
        "keywords": question.keywords,
        "solution_steps": question.solution_steps,
        "explanation": question.explanation,
        "test_cases": question.test_cases
    }


def copy_question_for_exam(db, question, exam_id):
    copied_question = Question(
        question=question.question,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        correct_answer=question.correct_answer,
        difficulty=question.difficulty,
        subject=question.subject,
        topic=question.topic,
        question_type=question.question_type,
        marks=question.marks,
        keywords=question.keywords,
        solution_steps=question.solution_steps,
        explanation=question.explanation,
        test_cases=question.test_cases,
        source=question.source,
        university_pattern=question.university_pattern,
        repeated_concept=question.repeated_concept,
        created_by="custom_exam",
        exam_id=exam_id
    )

    db.add(copied_question)
    db.flush()

    return copied_question


def create_custom_exam(db, data, student_email):
    seed_question_bank(db)

    subjects = data.get("subjects") or []
    topics = data.get("topics") or []
    question_types = data.get("question_types") or ["mcq"]
    difficulty = data.get("difficulty") or "mixed"
    num_questions = int(data.get("num_questions") or 10)
    duration_mode = data.get("duration_mode") or "practice"
    duration_minutes = int(
        data.get("duration_minutes")
        or DURATION_PRESETS.get(duration_mode, 30)
    )

    query = db.query(Question).filter(
        Question.created_by == "system_seed"
    )

    if subjects:
        query = query.filter(
            Question.subject.in_(subjects)
        )

    if topics:
        query = query.filter(
            Question.topic.in_(topics)
        )

    if question_types:
        query = query.filter(
            Question.question_type.in_(question_types)
        )

    if difficulty != "mixed":
        query = query.filter(
            Question.difficulty.ilike(difficulty)
        )

    available_questions = query.all()

    if len(available_questions) < num_questions:
        available_questions = db.query(Question).filter(
            Question.created_by == "system_seed"
        ).filter(
            Question.question_type.in_(question_types)
        ).all()

    selected_questions = random.sample(
        available_questions,
        min(num_questions, len(available_questions))
    )

    exam = Exam(
        title=data.get("title") or "Custom Practice Exam",
        description=(
            f"Student custom exam | Types: {', '.join(question_types)} | "
            f"Duration: {duration_minutes} minutes"
        ),
        duration_minutes=duration_minutes,
        start_time="student_generated",
        end_time="student_generated",
        created_by=student_email,
        status="active",
        total_students=1
    )

    db.add(exam)
    db.flush()

    copied_questions = [
        copy_question_for_exam(db, question, exam.id)
        for question in selected_questions
    ]

    db.commit()
    db.refresh(exam)

    return {
        "exam_id": exam.id,
        "duration_minutes": duration_minutes,
        "questions": [
            question_to_dict(question)
            for question in copied_questions
        ]
    }


def populate_exam_from_bank(db, data, teacher_email):
    seed_question_bank(db)

    exam_id = int(data.get("exam_id"))
    subjects = data.get("subjects") or []
    topics = data.get("topics") or []
    question_types = data.get("question_types") or ["mcq"]
    difficulty = data.get("difficulty") or "mixed"
    num_questions = int(data.get("num_questions") or 10)

    query = db.query(Question).filter(
        Question.created_by == "system_seed"
    )

    if subjects:
        query = query.filter(
            Question.subject.in_(subjects)
        )

    if topics:
        query = query.filter(
            Question.topic.in_(topics)
        )

    if question_types:
        query = query.filter(
            Question.question_type.in_(question_types)
        )

    if difficulty != "mixed":
        query = query.filter(
            Question.difficulty.ilike(difficulty)
        )

    available_questions = query.all()

    if len(available_questions) < num_questions:
        fallback_query = db.query(Question).filter(
            Question.created_by == "system_seed",
            Question.question_type.in_(question_types)
        )

        if subjects:
            fallback_query = fallback_query.filter(
                Question.subject.in_(subjects)
            )

        available_questions = fallback_query.all()

    selected_questions = random.sample(
        available_questions,
        min(num_questions, len(available_questions))
    )

    copied_questions = [
        copy_question_for_exam(db, question, exam_id)
        for question in selected_questions
    ]

    exam = db.query(Exam).filter(
        Exam.id == exam_id
    ).first()

    if exam:
        exam.status = "open"

    db.commit()

    return {
        "exam_id": exam_id,
        "questions_added": len(copied_questions),
        "questions": [
            question_to_dict(question)
            for question in copied_questions
        ]
    }


def query_bank_questions(db, data):
    seed_question_bank(db)

    subjects = data.get("subjects") or []
    topics = data.get("topics") or []
    question_types = data.get("question_types") or ["mcq"]
    difficulty = data.get("difficulty") or "mixed"

    query = db.query(Question).filter(
        Question.created_by == "system_seed"
    )

    if subjects:
        query = query.filter(Question.subject.in_(subjects))

    if topics:
        query = query.filter(Question.topic.in_(topics))

    if question_types:
        query = query.filter(Question.question_type.in_(question_types))

    if difficulty != "mixed":
        query = query.filter(Question.difficulty.ilike(difficulty))

    return query.all()


def preview_question_sets(db, data):
    questions = query_bank_questions(db, data)
    number_of_sets = int(data.get("number_of_sets") or 2)
    questions_per_set = int(data.get("questions_per_set") or 10)

    sets = []
    used_ids = set()

    for set_index in range(number_of_sets):
        available = [
            question
            for question in questions
            if question.id not in used_ids
        ]

        if len(available) < questions_per_set:
            available = questions
            used_ids = set()

        selected = random.sample(
            available,
            min(questions_per_set, len(available))
        )

        used_ids.update(question.id for question in selected)
        sets.append(
            {
                "set_name": f"Set {chr(65 + set_index)}",
                "question_ids": [question.id for question in selected],
                "questions": [question_to_dict(question) for question in selected]
            }
        )

    return {
        "available_questions": len(questions),
        "sets": sets
    }


def create_exam_sets(db, data, teacher_email):
    preview = preview_question_sets(db, data)
    created_exams = []

    subject = (data.get("subjects") or ["General"])[0]
    subject_code = data.get("subject_code") or ""
    semester = data.get("semester") or ""
    exam_type = data.get("exam_type") or "Class Test"
    title = data.get("title") or "Auto Generated Test"
    description = data.get("description") or "Auto generated from subject question bank."
    duration_minutes = int(data.get("duration_minutes") or 30)
    start_time = data.get("start_time") or "Not scheduled"
    end_time = data.get("end_time") or "No deadline"
    total_students = int(data.get("total_students") or 40)

    for item in preview["sets"]:
        exam = Exam(
            title=f"{subject_code} {subject} - {title} - {item['set_name']}",
            description=f"{description} | {item['set_name']}",
            subject=subject,
            subject_code=subject_code,
            semester=semester,
            exam_type=exam_type,
            duration_minutes=duration_minutes,
            start_time=start_time,
            end_time=end_time,
            created_by=teacher_email,
            status="open",
            total_students=total_students
        )
        db.add(exam)
        db.flush()

        bank_questions = db.query(Question).filter(
            Question.id.in_(item["question_ids"])
        ).all()

        copied = [
            copy_question_for_exam(db, question, exam.id)
            for question in bank_questions
        ]

        created_exams.append(
            {
                "exam_id": exam.id,
                "title": exam.title,
                "set_name": item["set_name"],
                "questions_added": len(copied),
                "deadline": end_time
            }
        )

    db.commit()

    return {
        "created_exams": created_exams
    }
