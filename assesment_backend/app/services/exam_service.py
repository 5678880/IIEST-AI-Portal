from sqlalchemy.orm import Session

from app.models import ExamSubmission

# -----------------------------------
# SAVE EXAM SUBMISSION
# -----------------------------------

def save_exam_submission(

    db: Session,

    submission_data: dict
):

    submission = ExamSubmission(

        student_name=submission_data["student_name"],

        score=submission_data["score"],

        percentage=submission_data["percentage"],

        status=submission_data["status"]
    )

    db.add(submission)

    db.commit()

    db.refresh(submission)

    return submission