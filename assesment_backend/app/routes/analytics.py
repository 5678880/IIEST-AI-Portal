from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import ExamSubmission

from app.security import verify_token

router = APIRouter()

# ===================================
# ANALYTICS
# ===================================

@router.get("/analytics")

def analytics(

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        verify_token
    )
):

    submissions = db.query(
        ExamSubmission
    ).all()

    total_submissions = len(submissions)

    if total_submissions == 0:

        return {

            "total_submissions": 0,

            "average_score": 0,

            "pass_rate": 0
        }

    total_percentage = 0

    pass_count = 0

    for submission in submissions:

        percentage = 0

        if submission.total_questions > 0:

            percentage = (

                submission.score
                /
                submission.total_questions

            ) * 100

        total_percentage += percentage

        if percentage >= 70:

            pass_count += 1

    average_score = round(

        total_percentage
        /
        total_submissions,

        2
    )

    pass_rate = round(

        (

            pass_count
            /
            total_submissions

        ) * 100,

        2
    )

    return {

        "total_submissions":
        total_submissions,

        "average_score":
        average_score,

        "pass_rate":
        pass_rate
    }

# ===================================
# ALL RESULTS
# ===================================

@router.get("/results")

def results(

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        verify_token
    )
):

    submissions = db.query(
        ExamSubmission
    ).all()

    results = []

    for submission in submissions:

        percentage = 0

        if submission.total_questions > 0:

            percentage = round(

                (

                    submission.score
                    /
                    submission.total_questions

                ) * 100,

                2
            )

        status = "PASS"

        if percentage < 70:

            status = "FAIL"

        results.append({

            "student_name":
            submission.student_name,

            "exam_id":
            submission.exam_id,

            "score":
            submission.score,

            "total_questions":
            submission.total_questions,

            "percentage":
            percentage,

            "status":
            status,

            "ai_feedback":
            submission.ai_feedback,

            "submitted_answers":
            submission.submitted_answers
        })

    return results

# ===================================
# STUDENT RESULTS
# ===================================

@router.get("/my_results")

def my_results(

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        verify_token
    )
):

    submissions = db.query(
        ExamSubmission
    ).filter(

        ExamSubmission.student_name
        ==
        current_user["email"]

    ).all()

    results = []

    for submission in submissions:

        percentage = 0

        if submission.total_questions > 0:

            percentage = round(

                (

                    submission.score
                    /
                    submission.total_questions

                ) * 100,

                2
            )

        status = "PASS"

        if percentage < 70:

            status = "FAIL"

        results.append({

            "student_name":
            submission.student_name,

            "exam_id":
            submission.exam_id,

            "score":
            submission.score,

            "total_questions":
            submission.total_questions,

            "percentage":
            percentage,

            "status":
            status,

            "ai_feedback":
            submission.ai_feedback,

            "submitted_answers":
            submission.submitted_answers
        })

    return results
