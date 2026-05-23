from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import StudentSubjectEnrollment
from app.models import TeacherSubject
from app.models import User
from app.security import verify_token


router = APIRouter()


SUBJECT_CATALOG = [
    ("Engineering Mathematics", "MA101", "Semester 1"),
    ("Discrete Mathematics", "CS201", "Semester 3"),
    ("Engineering Physics", "PH101", "Semester 1"),
    ("Engineering Chemistry", "CH101", "Semester 2"),
    ("Basic Electrical Engineering", "EE101", "Semester 1"),
    ("Basic Electronics Engineering", "EC101", "Semester 2"),
    ("Programming in C", "CS101", "Semester 1"),
    ("Object Oriented Programming", "CS102", "Semester 2"),
    ("Data Structures", "CS201", "Semester 3"),
    ("Design and Analysis of Algorithms", "CS301", "Semester 4"),
    ("Computer Organization and Architecture", "CS202", "Semester 3"),
    ("Operating Systems", "CS302", "Semester 4"),
    ("Database Management Systems", "CS303", "Semester 4"),
    ("Computer Networks", "CS401", "Semester 5"),
    ("Theory of Computation", "CS402", "Semester 5"),
    ("Compiler Design", "CS501", "Semester 6"),
    ("Software Engineering", "CS304", "Semester 4"),
    ("Web Technologies", "CS203", "Semester 3"),
    ("Artificial Intelligence", "CS403", "Semester 5"),
    ("Machine Learning", "CS502", "Semester 6"),
    ("Deep Learning", "CS601", "Semester 7"),
    ("Data Science", "CS701", "Semester 8"),
    ("Cloud Computing", "CS503", "Semester 6"),
    ("Cyber Security", "CS404", "Semester 5"),
    ("Cryptography and Network Security", "CS702", "Semester 8"),
    ("Internet of Things", "CS602", "Semester 7"),
    ("Mobile Application Development", "CS603", "Semester 7"),
    ("Distributed Systems", "CS504", "Semester 6"),
    ("Big Data Analytics", "CS604", "Semester 7"),
    ("Human Computer Interaction", "CS703", "Semester 8"),
    ("Professional Ethics", "HS801", "Semester 8"),
    ("Environmental Studies", "EV101", "Semester 2")
]


def subject_code_for(subject):
    for catalog_subject, code, _semester in SUBJECT_CATALOG:
        if catalog_subject == subject:
            return code

    words = [
        word[0]
        for word in subject.split()
        if word
    ]
    return "".join(words).upper()[:4] or "SUBJ"


def serialize_teacher_subject(item, enrolled_count=0):
    return {
        "id": item.id,
        "teacher_email": item.teacher_email,
        "subject": item.subject,
        "subject_code": item.subject_code,
        "semester": item.semester,
        "section": item.section,
        "academic_year": item.academic_year,
        "enrolled_students": enrolled_count
    }


def serialize_student_enrollment(item):
    return {
        "id": item.id,
        "student_email": item.student_email,
        "student_name": item.student_name,
        "roll_no": item.roll_no,
        "subject": item.subject,
        "subject_code": item.subject_code,
        "semester": item.semester,
        "section": item.section,
        "academic_year": item.academic_year
    }


@router.get("/subject_catalog")
def subject_catalog():
    return [
        {
            "subject": subject,
            "subject_code": code,
            "semester": semester
        }
        for subject, code, semester in SUBJECT_CATALOG
    ]


@router.post("/teacher_subjects")
def add_teacher_subject(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Teacher Access Only")

    subject = data.get("subject", "").strip()
    if not subject:
        raise HTTPException(status_code=400, detail="Subject is required")

    subject_code = data.get("subject_code") or subject_code_for(subject)
    semester = data.get("semester", "Semester 4")
    section = data.get("section", "CSE-A")
    academic_year = data.get("academic_year", "2026")
    student_name = data.get("student_name") or current_user["email"]
    roll_no = data.get("roll_no") or ""
    student_name = data.get("student_name") or current_user["email"]
    roll_no = data.get("roll_no") or ""

    existing = db.query(TeacherSubject).filter(
        TeacherSubject.teacher_email == current_user["email"],
        TeacherSubject.subject_code == subject_code,
        TeacherSubject.semester == semester,
        TeacherSubject.section == section,
        TeacherSubject.academic_year == academic_year
    ).first()

    if existing:
        return serialize_teacher_subject(existing)

    item = TeacherSubject(
        teacher_email=current_user["email"],
        subject=subject,
        subject_code=subject_code,
        semester=semester,
        section=section,
        academic_year=academic_year
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_teacher_subject(item)


@router.get("/teacher_subjects")
def get_teacher_subjects(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Teacher Access Only")

    subjects = db.query(TeacherSubject).filter(
        TeacherSubject.teacher_email == current_user["email"]
    ).all()

    rows = []
    for item in subjects:
        count = db.query(StudentSubjectEnrollment).filter(
            StudentSubjectEnrollment.subject_code == item.subject_code,
            StudentSubjectEnrollment.semester == item.semester,
            StudentSubjectEnrollment.section == item.section,
            StudentSubjectEnrollment.academic_year == item.academic_year
        ).count()
        rows.append(serialize_teacher_subject(item, count))

    return rows


@router.post("/student_subjects")
def add_student_subject(
    data: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") not in ["student", "teacher"]:
        raise HTTPException(status_code=403, detail="Student Access Only")

    subject = data.get("subject", "").strip()
    if not subject:
        raise HTTPException(status_code=400, detail="Subject is required")

    subject_code = data.get("subject_code") or subject_code_for(subject)
    semester = data.get("semester", "Semester 4")
    section = data.get("section", "CSE-A")
    academic_year = data.get("academic_year", "2026")
    student_name = data.get("student_name") or current_user["email"]
    roll_no = data.get("roll_no") or ""

    existing = db.query(StudentSubjectEnrollment).filter(
        StudentSubjectEnrollment.student_email == current_user["email"],
        StudentSubjectEnrollment.subject_code == subject_code,
        StudentSubjectEnrollment.semester == semester,
        StudentSubjectEnrollment.section == section,
        StudentSubjectEnrollment.academic_year == academic_year
    ).first()

    if existing:
        existing.student_name = student_name
        existing.roll_no = roll_no
        db.commit()
        return serialize_student_enrollment(existing)

    item = StudentSubjectEnrollment(
        student_email=current_user["email"],
        student_name=student_name,
        roll_no=roll_no,
        subject=subject,
        subject_code=subject_code,
        semester=semester,
        section=section,
        academic_year=academic_year
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return serialize_student_enrollment(item)


@router.get("/student_subjects")
def get_student_subjects(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") not in ["student", "teacher"]:
        raise HTTPException(status_code=403, detail="Student Access Only")

    rows = db.query(StudentSubjectEnrollment).filter(
        StudentSubjectEnrollment.student_email == current_user["email"]
    ).all()
    return [serialize_student_enrollment(item) for item in rows]


@router.get("/teacher_subject_students")
def get_teacher_subject_students(
    db: Session = Depends(get_db),
    current_user: dict = Depends(verify_token)
):
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Teacher Access Only")

    teacher_subjects = db.query(TeacherSubject).filter(
        TeacherSubject.teacher_email == current_user["email"]
    ).all()

    roster = []
    for subject in teacher_subjects:
        enrollments = db.query(StudentSubjectEnrollment).filter(
            StudentSubjectEnrollment.subject_code == subject.subject_code,
            StudentSubjectEnrollment.semester == subject.semester,
            StudentSubjectEnrollment.section == subject.section,
            StudentSubjectEnrollment.academic_year == subject.academic_year
        ).all()

        for enrollment in enrollments:
            user = db.query(User).filter(
                User.email == enrollment.student_email
            ).first()
            roster.append({
                "subject": subject.subject,
                "subject_code": subject.subject_code,
                "semester": subject.semester,
                "section": subject.section,
                "academic_year": subject.academic_year,
                "student_name": enrollment.student_name or (user.name if user else enrollment.student_email),
                "roll_no": enrollment.roll_no,
                "student_email": enrollment.student_email
            })

    return roster
