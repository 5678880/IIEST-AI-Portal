from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import Text

from app.database import Base

# ===================================
# USER TABLE
# ===================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(String)

    email = Column(
        String,
        unique=True
    )

    password = Column(String)

    role = Column(String)

# ===================================
# QUESTION TABLE
# ===================================

class Question(Base):

    __tablename__ = "questions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    question = Column(String)

    option_a = Column(String)

    option_b = Column(String)

    option_c = Column(String)

    option_d = Column(String)

    correct_answer = Column(String)

    difficulty = Column(String)

    subject = Column(String)

    topic = Column(String)

    question_type = Column(String, default="mcq")

    marks = Column(Float, default=1)

    keywords = Column(Text)

    solution_steps = Column(Text)

    explanation = Column(Text)

    test_cases = Column(Text)

    source = Column(String)

    university_pattern = Column(String)

    repeated_concept = Column(String)

    created_by = Column(String)

    # -----------------------------------
    # LINK QUESTION TO EXAM
    # -----------------------------------

    exam_id = Column(Integer)

    # -----------------------------------
    # STUDENT GROUP
    # -----------------------------------

    student_group = Column(String)

# ===================================
# EXAM TABLE
# ===================================

class Exam(Base):

    __tablename__ = "exams"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    title = Column(String)

    description = Column(String)

    subject = Column(String)

    subject_code = Column(String)

    semester = Column(String)

    exam_type = Column(String)

    duration_minutes = Column(Integer)

    start_time = Column(String)

    end_time = Column(String)

    created_by = Column(String)

    status = Column(String)

    total_students = Column(Integer)

# ===================================
# EXAM QUESTION TABLE
# ===================================

class ExamQuestion(Base):

    __tablename__ = "exam_questions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    exam_id = Column(Integer)

    question_id = Column(Integer)

    student_group = Column(String)

# ===================================
# EXAM SUBMISSION TABLE
# ===================================

class ExamSubmission(Base):

    __tablename__ = "exam_submissions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_name = Column(String)

    exam_id = Column(Integer)

    score = Column(Float)

    total_questions = Column(Integer)

    submitted_answers = Column(String)

    ai_feedback = Column(String)


# ===================================
# TEACHER SUBJECT TABLE
# ===================================

class TeacherSubject(Base):

    __tablename__ = "teacher_subjects"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    teacher_email = Column(String)

    subject = Column(String)

    subject_code = Column(String)

    semester = Column(String)

    section = Column(String)

    academic_year = Column(String)


# ===================================
# STUDENT SUBJECT ENROLLMENT TABLE
# ===================================

class StudentSubjectEnrollment(Base):

    __tablename__ = "student_subject_enrollments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    student_email = Column(String)

    student_name = Column(String)

    roll_no = Column(String)

    subject = Column(String)

    subject_code = Column(String)

    semester = Column(String)

    section = Column(String)

    academic_year = Column(String)


# ===================================
# EXAM SET ASSIGNMENT TABLE
# ===================================

class ExamSetAssignment(Base):

    __tablename__ = "exam_set_assignments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    teacher_email = Column(String)

    student_email = Column(String)

    student_name = Column(String)

    subject = Column(String)

    subject_code = Column(String)

    set_name = Column(String)

    exam_id = Column(Integer)

    exam_title = Column(String)

    assigned_at = Column(String)
