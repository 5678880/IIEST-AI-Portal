from app.models import ExamSubmission

# -----------------------------------
# FETCH ALL RESULTS
# -----------------------------------

def get_all_results(db):

    submissions = db.query(
        ExamSubmission
    ).all()

    results = []

    for submission in submissions:

        percentage = 0

        if submission.total_questions > 0:

            percentage = (

                submission.score
                /
                submission.total_questions

            ) * 100

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
            status
        })

    return results

# -----------------------------------
# ANALYTICS SUMMARY
# -----------------------------------

def get_analytics_summary(db):

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

    passed_students = 0

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

            passed_students += 1

    average_score = (

        total_percentage
        /
        total_submissions
    )

    pass_rate = (

        passed_students
        /
        total_submissions
    ) * 100

    return {

        "total_submissions":
        total_submissions,

        "average_score":
        round(average_score, 2),

        "pass_rate":
        round(pass_rate, 2)
    }