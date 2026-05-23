from app.models import Exam

# -----------------------------------
# CREATE EXAM
# -----------------------------------

def create_exam(

    db,

    exam_data,

    teacher_email
):

    exam = Exam(

        title=exam_data.get(
            "title"
        ),

        description=exam_data.get(
            "description"
        ),

        subject=exam_data.get(
            "subject"
        ),

        subject_code=exam_data.get(
            "subject_code"
        ),

        semester=exam_data.get(
            "semester"
        ),

        exam_type=exam_data.get(
            "exam_type"
        ),

        duration_minutes=exam_data.get(
            "duration_minutes"
        ),

        start_time=exam_data.get(
            "start_time"
        ),

        end_time=exam_data.get(
            "end_time"
        ),

        created_by=teacher_email,

        status=exam_data.get(
            "status",
            "open"
        )
    )

    db.add(exam)

    db.commit()

    db.refresh(exam)

    return exam

# -----------------------------------
# FETCH EXAMS
# -----------------------------------

def get_all_exams(db):

    exams = db.query(Exam).all()

    return exams
