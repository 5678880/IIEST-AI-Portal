from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database import get_db

from app.models import ExamSubmission

from app.security import verify_token

router = APIRouter()

# ===================================
# FETCH STUDENT RESULTS
# ===================================

@router.get("/my_results")

def get_my_results(

    db: Session = Depends(get_db),

    current_user: dict = Depends(
        verify_token
    )
):

    try:

        # -----------------------------------
        # FETCH SUBMISSIONS
        # -----------------------------------

        submissions = db.query(
            ExamSubmission
        ).filter(

            ExamSubmission.student_name
            ==
            current_user["email"]

        ).all()

        results = []

        # -----------------------------------
        # SERIALIZE RESULTS
        # -----------------------------------

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
                submission.ai_feedback
            })

        return results

    except Exception as e:

        print("\nMY RESULTS ERROR:\n")
        print(str(e))

        return []