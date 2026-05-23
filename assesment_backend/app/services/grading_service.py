import json

import requests

from app.models import ExamSubmission
from app.models import Question


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"


def normalize_text(text):
    if not text:
        return ""

    return (
        str(text)
        .strip()
        .lower()
        .replace(".", "")
        .replace(",", "")
        .replace(":", "")
        .replace(";", "")
    )


def split_keywords(keywords):
    if not keywords:
        return []

    return [
        keyword.strip().lower()
        for keyword in keywords.split(",")
        if keyword.strip()
    ]


def keyword_score(answer, keywords, marks):
    normalized_answer = normalize_text(answer)
    keyword_list = split_keywords(keywords)

    if not keyword_list:
        return 0

    matched = [
        keyword
        for keyword in keyword_list
        if keyword in normalized_answer
    ]

    return round(
        (len(matched) / len(keyword_list)) * marks,
        2
    )


def grade_mcq(question, student_answer):
    if normalize_text(student_answer) == normalize_text(question.correct_answer):
        return question.marks or 1

    return 0


def grade_written(question, student_answer):
    marks = question.marks or 1
    base_score = keyword_score(
        student_answer,
        question.keywords,
        marks
    )

    if normalize_text(question.correct_answer) in normalize_text(student_answer):
        base_score = max(
            base_score,
            marks * 0.75
        )

    return min(
        round(base_score, 2),
        marks
    )


def grade_numerical(question, student_answer):
    marks = question.marks or 1
    normalized_answer = normalize_text(student_answer)
    score = 0

    rubric = {
        "formula": marks * 0.25,
        "substitution": marks * 0.20,
        "steps": marks * 0.25,
        "final": marks * 0.20,
        "unit": marks * 0.10
    }

    for keyword, value in rubric.items():
        if keyword in normalized_answer:
            score += value

    score = max(
        score,
        keyword_score(
            student_answer,
            question.keywords,
            marks
        )
    )

    return min(
        round(score, 2),
        marks
    )


def grade_coding(question, student_answer):
    marks = question.marks or 1
    normalized_answer = normalize_text(student_answer)
    score = 0

    checks = {
        "input": marks * 0.15,
        "output": marks * 0.15,
        "logic": marks * 0.30,
        "edge": marks * 0.15,
        "return": marks * 0.10
    }

    for keyword, value in checks.items():
        if keyword in normalized_answer:
            score += value

    if "for" in normalized_answer or "while" in normalized_answer or "select" in normalized_answer:
        score += marks * 0.15

    return min(
        round(score, 2),
        marks
    )


def grade_question(question, student_answer):
    question_type = (
        question.question_type
        or "mcq"
    ).lower()

    if question_type == "mcq":
        score = grade_mcq(question, student_answer)
        review = "auto"
    elif question_type in ["short", "long"]:
        score = grade_written(question, student_answer)
        review = "manual recommended" if question_type == "long" else "ai-assisted"
    elif question_type == "numerical":
        score = grade_numerical(question, student_answer)
        review = "step marking"
    elif question_type == "coding":
        score = grade_coding(question, student_answer)
        review = "output validation recommended"
    else:
        score = grade_written(question, student_answer)
        review = "ai-assisted"

    return {
        "question_id": question.id,
        "question_type": question_type,
        "score": score,
        "marks": question.marks or 1,
        "review": review,
        "expected": question.correct_answer,
        "keywords": question.keywords,
        "solution_steps": question.solution_steps
    }


def generate_ai_feedback(percentage, breakdown):
    weak_types = [
        item["question_type"]
        for item in breakdown
        if item["score"] < (item["marks"] * 0.5)
    ]

    prompt = f"""
A student scored {percentage}% in a mixed-format exam.
Weak question types: {', '.join(weak_types) if weak_types else 'none'}

Provide:
1. Performance feedback
2. Weak areas
3. Study suggestions
4. How to improve answer writing and problem solving

Keep it concise.
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=25
        )
        response.raise_for_status()

        return response.json().get(
            "response",
            ""
        )

    except Exception:
        return "Revise weak topics, practice mixed question formats, and review answer structure before the next test."


def grade_exam(db, exam_id, student_answers, student_email):
    questions = db.query(Question).filter(
        Question.exam_id == exam_id
    ).all()

    total_marks = sum(
        question.marks or 1
        for question in questions
    )

    earned_marks = 0
    breakdown = []

    for question in questions:
        student_answer = student_answers.get(
            str(question.id),
            ""
        )

        result = grade_question(
            question,
            student_answer
        )
        breakdown.append(result)
        earned_marks += result["score"]

    percentage = 0

    if total_marks > 0:
        percentage = round(
            (earned_marks / total_marks) * 100,
            2
        )

    status = "PASS" if percentage >= 40 else "FAIL"
    ai_feedback = generate_ai_feedback(
        percentage,
        breakdown
    )

    submission = ExamSubmission(
        student_name=student_email,
        exam_id=exam_id,
        score=earned_marks,
        total_questions=len(questions),
        submitted_answers=json.dumps(
            {
                "answers": student_answers,
                "breakdown": breakdown
            }
        ),
        ai_feedback=ai_feedback
    )

    db.add(submission)
    db.commit()
    db.refresh(submission)

    return {
        "score": round(earned_marks, 2),
        "total_marks": round(total_marks, 2),
        "total_questions": len(questions),
        "percentage": percentage,
        "status": status,
        "ai_feedback": ai_feedback,
        "breakdown": breakdown
    }
