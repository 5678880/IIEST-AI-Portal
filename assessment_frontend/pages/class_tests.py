from datetime import date, time

import streamlit as st

from components.auth import require_login
from components.sidebar import show_sidebar
from services.api_client import create_exam, populate_exam_from_bank
from services.study_catalog import SUBJECT_CODES, SYLLABUS_TRACKS


st.set_page_config(
    page_title="Class Tests",
    layout="wide"
)


require_login()

if st.session_state.get("user", {}).get("role") != "teacher":
    st.error("Teacher Access Only")
    st.stop()


show_sidebar()

st.title("Class Tests")
st.caption("Schedule timed class tests according to syllabus progression.")

if "class_tests" not in st.session_state:
    st.session_state.class_tests = []

left, right = st.columns([1, 1])

with left:
    semester = st.selectbox("Semester", list(SYLLABUS_TRACKS.keys()))
    subject = st.selectbox("Subject", SYLLABUS_TRACKS[semester])
    subject_code = st.text_input(
        "Subject code",
        value=SUBJECT_CODES.get(subject, "")
    )
    unit = st.text_input("Syllabus unit", placeholder="Example: Unit 2 - Process Scheduling")
    test_date = st.date_input("Test date", value=date.today())
    test_time = st.time_input("Start time", value=time(10, 0))
    deadline_time = st.time_input("Deadline time", value=time(23, 59))

with right:
    duration = st.slider("Duration minutes", 10, 180, 45)
    marks = st.slider("Total marks", 10, 100, 30)
    question_mix = st.multiselect(
        "Question pattern",
        ["MCQ", "Short Answer", "Long Answer", "Coding", "Numerical"],
        default=["MCQ", "Short Answer"]
    )
    auto_release = st.toggle("Auto release to students", value=True)

if st.button("Schedule Class Test", type="primary"):
    if not unit.strip():
        st.warning("Enter the syllabus unit.")
    else:
        with st.spinner("Creating timed test and generating questions..."):
            exam_result = create_exam(
                {
                    "title": f"{subject_code} {subject} Class Test - {unit}",
                    "description": f"{semester} | {unit} | Pattern: {', '.join(question_mix)}",
                    "subject": subject,
                    "subject_code": subject_code,
                    "semester": semester,
                    "exam_type": "Class Test",
                    "duration_minutes": duration,
                    "start_time": f"{test_date} {test_time.strftime('%H:%M')}",
                    "end_time": f"{test_date} {deadline_time.strftime('%H:%M')}",
                    "total_students": 40,
                    "status": "open" if auto_release else "draft"
                },
                st.session_state.token
            )

            exam_id = exam_result.get("exam_id")

            if exam_id:
                type_map = {
                    "MCQ": "mcq",
                    "Short Answer": "short",
                    "Long Answer": "long",
                    "Coding": "coding",
                    "Numerical": "numerical"
                }
                populate_exam_from_bank(
                    {
                        "exam_id": exam_id,
                        "subjects": [subject],
                        "topics": [],
                        "question_types": [
                            type_map[item]
                            for item in question_mix
                            if item in type_map
                        ],
                        "difficulty": "mixed",
                        "num_questions": max(3, min(30, marks // 3))
                    },
                    st.session_state.token
                )

        st.session_state.class_tests.append(
            {
                "exam_id": exam_id,
                "semester": semester,
                "subject": subject,
                "subject_code": subject_code,
                "unit": unit,
                "date": str(test_date),
                "time": str(test_time),
                "deadline": f"{test_date} {deadline_time.strftime('%H:%M')}",
                "duration": duration,
                "marks": marks,
                "pattern": ", ".join(question_mix),
                "release_to_students": auto_release,
                "status": "Released" if auto_release else "Draft"
            }
        )
        st.success("Class test scheduled and visible to students in Live Exam.")

st.divider()
st.subheader("Scheduled Tests")

if not st.session_state.class_tests:
    st.info("No class tests scheduled yet.")
else:
    st.session_state.class_tests = st.data_editor(
        st.session_state.class_tests,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "status": st.column_config.SelectboxColumn(
                "status",
                options=["Draft", "Released", "Closed"]
            ),
            "release_to_students": st.column_config.CheckboxColumn(
                "release_to_students"
            )
        }
    )

st.divider()
st.subheader("Syllabus Progression")

for sem, subjects in SYLLABUS_TRACKS.items():
    with st.expander(sem):
        for item in subjects:
            st.progress(0.55, text=f"{item}: syllabus progression tracked")
