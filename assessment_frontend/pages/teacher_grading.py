import json

import pandas as pd
import streamlit as st

from components.auth import require_login
from components.sidebar import show_sidebar
from components.theme import ai_feature_grid, hero
from services.api_client import ask_ai_tutor, fetch_results
from services.file_extraction import extract_text_from_file, extraction_note
from services.study_catalog import BTECH_CSE_SUBJECTS


st.set_page_config(page_title="IIEST AI Grading Center", layout="wide")

require_login()

if st.session_state.get("user", {}).get("role") != "teacher":
    st.error("Teacher Access Only")
    st.stop()


show_sidebar()

hero(
    "AI Grading Center",
    "Grade uploaded copies or typed assignments. Use OCR when it helps, but paste clean typed answers when handwriting is unclear."
)

results = fetch_results(st.session_state.token)

if not results:
    results = [
        {
            "student_name": "demo.student@example.com",
            "exam_id": 1,
            "score": 24,
            "total_questions": 30,
            "percentage": 80,
            "status": "PASS",
            "ai_feedback": "Good conceptual clarity. Improve numerical steps.",
            "submitted_answers": "{}"
        }
    ]
    st.info("Showing demo grading data because no real submissions are available yet.")

df = pd.DataFrame(results)

col1, col2, col3 = st.columns(3)
col1.metric("Submissions", len(df))
col2.metric("Average", f"{round(float(df['percentage'].mean()), 2)}%")
col3.metric("Manual Review Queue", int((df["percentage"] < 60).sum()))

ai_feature_grid(
    [
        {
            "title": "Typed assignment grading",
            "body": "Teachers can paste a student's typed answer directly, avoiding OCR when handwriting is unclear."
        },
        {
            "title": "OCR with human correction",
            "body": "AI extracts text, but teachers can fix unclear handwriting before rubric-based grading."
        },
        {
            "title": "Rubric-backed feedback",
            "body": "The teacher provides questions or marking scheme; AI compares answers and suggests marks, missing points, and feedback."
        }
    ]
)

typed_tab, upload_tab, review_tab = st.tabs(
    [
        "Grade Typed Assignment",
        "Grade Uploaded Paper",
        "Submission Review"
    ]
)


with typed_tab:
    st.subheader("Typed Assignment Grading")
    st.caption("Use this when handwriting or OCR is unreliable. Paste the assignment question/rubric and the student's typed answer.")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        typed_student = st.text_input(
            "Student name / roll number",
            key="typed_student_name"
        )
        typed_subject = st.selectbox(
            "Subject",
            BTECH_CSE_SUBJECTS,
            key="typed_subject"
        )
        typed_total_marks = st.number_input(
            "Total marks",
            min_value=1,
            value=20,
            key="typed_total_marks"
        )

    with col_b:
        assignment_title = st.text_input(
            "Assignment title",
            placeholder="Example: DBMS Normalization Assignment"
        )
        grading_mode = st.selectbox(
            "Checking mode",
            [
                "Strict rubric marking",
                "Conceptual feedback",
                "Exam-style marking",
                "Improvement-only feedback"
            ]
        )

    typed_question = st.text_area(
        "Assignment question / marking scheme / expected answer",
        height=170,
        placeholder="Paste the question, expected points, model answer, or rubric."
    )

    typed_answer = st.text_area(
        "Student typed answer",
        height=260,
        placeholder="Paste the student's typed assignment answer here. No OCR needed."
    )

    if st.button("Grade Typed Assignment", type="primary"):
        if not typed_answer.strip():
            st.warning("Paste the student's typed answer first.")
        elif not typed_question.strip():
            st.warning("Paste the assignment question or marking scheme first.")
        else:
            prompt = f"""
Act as an AI assignment grading assistant for a teacher.

Subject: {typed_subject}
Student: {typed_student}
Assignment: {assignment_title}
Checking mode: {grading_mode}
Total marks: {typed_total_marks}

Assignment question / marking scheme / expected answer:
{typed_question}

Student typed answer:
{typed_answer}

Return:
1. Suggested marks out of {typed_total_marks}
2. Point-wise marking table
3. Correct concepts found
4. Missing concepts
5. Exact feedback teacher can give the student
6. What the teacher may manually override

Because this is typed text, do not mention handwriting or OCR uncertainty.
"""
            with st.spinner("Grading typed assignment..."):
                result = ask_ai_tutor(
                    prompt,
                    typed_subject,
                    "medium",
                    st.session_state.token,
                    task="improvement"
                )

            st.success("Typed assignment grading draft ready.")
            st.info(result.get("answer", "No grading response generated."))


with upload_tab:
    st.subheader("Upload Student Copy")

    col_a, col_b = st.columns([1, 1])

    with col_a:
        student_name = st.text_input("Student name / roll number")
        subject = st.selectbox("Subject", BTECH_CSE_SUBJECTS)
        uploaded_answer = st.file_uploader(
            "Upload answer sheet",
            type=["pdf", "png", "jpg", "jpeg", "webp", "txt", "docx"]
        )

    with col_b:
        marking_scheme = st.text_area(
            "Question paper / marking scheme / expected answer",
            height=180,
            placeholder="Paste the question, marking scheme, model answer, or rubric here."
        )
        total_marks = st.number_input("Total marks", min_value=1, value=30)

    if uploaded_answer:
        extracted_text = extract_text_from_file(uploaded_answer)

        if not extracted_text:
            st.warning("No text could be extracted. Try a clearer scan or paste the answer manually.")

        st.caption(extraction_note())

        corrected_text = st.text_area(
            "Extracted answer text - correct OCR/handwriting mistakes before grading",
            value=extracted_text,
            height=260
        )

        if st.button("Grade Uploaded Paper", type="primary"):
            if not corrected_text.strip():
                st.warning("Add readable answer text first.")
            elif not marking_scheme.strip():
                st.warning("Add question paper, marking scheme, or expected answer first.")
            else:
                prompt = f"""
Act as an AI grading assistant for a teacher.

Subject: {subject}
Student: {student_name}
Total marks: {total_marks}

Question paper / marking scheme / model answer:
{marking_scheme}

Student answer text extracted from uploaded copy:
{corrected_text}

Return:
1. Suggested marks out of {total_marks}
2. Question-wise or point-wise breakdown
3. Missing concepts
4. Handwriting/OCR uncertainty warnings
5. Feedback for the student
6. What the teacher must manually verify

Do not pretend handwriting OCR is perfect.
"""
                with st.spinner("Reading and grading uploaded paper..."):
                    result = ask_ai_tutor(
                        prompt,
                        subject,
                        "medium",
                        st.session_state.token,
                        task="improvement"
                    )

                st.success("AI grading draft ready. Teacher review is still required.")
                st.info(result.get("answer", "No grading response generated."))


with review_tab:
    st.subheader("Existing Digital Submissions")
    if "editable_grading_results" not in st.session_state:
        st.session_state.editable_grading_results = df

    st.session_state.editable_grading_results = st.data_editor(
        st.session_state.editable_grading_results,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "status": st.column_config.SelectboxColumn(
                "status",
                options=["PASS", "FAIL", "Needs Review", "Rechecked"]
            ),
            "percentage": st.column_config.NumberColumn(
                "percentage",
                min_value=0,
                max_value=100
            ),
            "score": st.column_config.NumberColumn(
                "score",
                min_value=0
            ),
            "ai_feedback": st.column_config.TextColumn(
                "teacher_feedback_or_ai_feedback"
            )
        }
    )

    if st.button("Save Review Changes In This Session"):
        st.success("Teacher review changes saved in the current session.")

    selected_student = st.selectbox(
        "Select submission",
        st.session_state.editable_grading_results["student_name"].tolist()
    )
    selected_row = st.session_state.editable_grading_results[
        st.session_state.editable_grading_results["student_name"] == selected_student
    ].iloc[0]

    with st.container(border=True):
        st.write(f"Exam ID: {selected_row['exam_id']}")
        st.write(f"Score: {selected_row['score']}")
        st.write(f"Feedback: {selected_row['ai_feedback']}")

        raw_answers = selected_row.get("submitted_answers", "{}")

        try:
            parsed_answers = json.loads(raw_answers) if raw_answers else {}
        except Exception:
            parsed_answers = {}

        if parsed_answers:
            st.json(parsed_answers)

    rubric_prompt = st.text_area(
        "Paste a question or answer to create a rubric",
        height=130,
        placeholder="Example: Explain normalization with advantages, limitations, and example."
    )

    if st.button("Generate Teacher Rubric", type="primary"):
        if not rubric_prompt.strip():
            st.warning("Paste a question or answer first.")
        else:
            with st.spinner("Creating grading rubric..."):
                result = ask_ai_tutor(
                    "Create a marking rubric for this answer/question: " + rubric_prompt,
                    "Teacher Grading",
                    "medium",
                    st.session_state.token,
                    task="improvement"
                )
            st.info(result.get("answer", "No rubric generated."))
