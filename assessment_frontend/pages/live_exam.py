from datetime import datetime
from datetime import timedelta

import streamlit as st
import streamlit.components.v1 as components

from components.auth import require_login
from components.sidebar import show_sidebar
from services.api_client import (
    create_custom_exam,
    fetch_exams,
    start_exam,
    submit_exam
)
from services.study_catalog import BTECH_CSE_SUBJECTS


st.set_page_config(
    page_title="Live Exam",
    layout="wide"
)


require_login()

if st.session_state.get("user", {}).get("role") not in ["student", "teacher"]:
    st.error("Student Or Teacher Access Only")
    st.stop()


show_sidebar()

st.markdown(
    """
    <style>
    .exam-hero {
        background: linear-gradient(135deg, #0f172a, #1d4ed8 55%, #0f766e);
        color: white;
        border-radius: 22px;
        padding: 28px;
        margin-bottom: 18px;
        box-shadow: 0 20px 44px rgba(15, 23, 42, 0.20);
    }
    .exam-hero h1 { margin: 0 0 8px; font-size: 38px; }
    .exam-hero p { color: #dbeafe; margin: 0; }
.question-meta {
        display: inline-block;
        background: #eef2ff;
        color: #3730a3;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 12px;
        margin-right: 6px;
    }
    .exam-card {
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 16px;
        margin-bottom: 12px;
        background: rgba(255,255,255,0.92);
        box-shadow: 0 12px 28px rgba(15,23,42,0.06);
    }
    .exam-card h4 { margin: 0 0 8px; }
    .exam-card p { margin: 4px 0; color: #475569; }
    </style>
    <div class="exam-hero">
        <h1>Live Exam Studio</h1>
        <p>Create quick tests, practice tests, full-length exams, or custom mixed-format papers from a structured CSE question bank.</p>
    </div>
    """,
    unsafe_allow_html=True
)

available_teacher_exams = fetch_exams()

if available_teacher_exams:
    latest_test = available_teacher_exams[-1]
    st.toast(
        f"Teacher test available: {latest_test['title']}",
        icon="📝"
    )
    st.info(
        f"Teacher created test available: {latest_test['title']}. Open the Teacher Exams tab to start it."
    )


if "exam_data" not in st.session_state:
    st.session_state.exam_data = None

if "exam_started_at" not in st.session_state:
    st.session_state.exam_started_at = None


def get_duration_minutes():
    if not st.session_state.exam_data:
        return 0

    return int(
        st.session_state.exam_data.get(
            "duration_minutes",
            30
        )
    )


def render_timer():
    if not st.session_state.exam_started_at:
        return

    duration = get_duration_minutes()
    end_time = st.session_state.exam_started_at + timedelta(
        minutes=duration
    )
    end_timestamp = int(end_time.timestamp() * 1000)

    components.html(
        f"""
        <div style="
            font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #ffffff, #eef2ff 58%, #fff7ed);
            border: 1px solid rgba(148, 163, 184, 0.25);
            border-radius: 18px;
            padding: 18px 22px;
            box-shadow: 0 18px 42px rgba(15, 23, 42, 0.10);
        ">
            <div style="font-size: 14px; font-weight: 700; color: #475569; margin-bottom: 8px;">
                Time Remaining
            </div>
            <div id="examTimer" style="
                font-size: 40px;
                line-height: 1;
                font-weight: 900;
                letter-spacing: 0;
                color: #111827;
            ">--:--</div>
            <div id="timerStatus" style="margin-top: 8px; font-size: 13px; color: #64748b;"></div>
        </div>
        <script>
            const endTime = {end_timestamp};
            const timerEl = document.getElementById("examTimer");
            const statusEl = document.getElementById("timerStatus");

            function renderCountdown() {{
                const remaining = endTime - Date.now();

                if (remaining <= 0) {{
                    timerEl.textContent = "00:00";
                    timerEl.style.color = "#dc2626";
                    statusEl.textContent = "Time is over. Submit your exam now.";
                    clearInterval(window.examTimerInterval);
                    return;
                }}

                const minutes = Math.floor(remaining / 60000);
                const seconds = Math.floor((remaining % 60000) / 1000);
                timerEl.textContent = String(minutes).padStart(2, "0") + ":" + String(seconds).padStart(2, "0");

                if (remaining <= 300000) {{
                    timerEl.style.color = "#dc2626";
                    statusEl.textContent = "Last 5 minutes.";
                }} else {{
                    timerEl.style.color = "#111827";
                    statusEl.textContent = "Your answers are kept on this page until you submit.";
                }}
            }}

            renderCountdown();
            window.examTimerInterval = setInterval(renderCountdown, 1000);
        </script>
        """,
        height=124
    )


def repair_legacy_mcq(question):
    options = [
        option
        for option in question.get("options", [])
        if option
    ]

    has_placeholder = any(
        option == "Correct Answer" or option.startswith("Wrong Answer")
        for option in options
    )

    if not has_placeholder:
        return options

    raw_topic = (
        question.get("topic")
        or question.get("subject")
        or question.get("question")
        or "this concept"
    )
    topic = (
        raw_topic
        .replace("What is the purpose of", "")
        .replace("?", "")
        .strip()
    ) or "this concept"

    question["question"] = f"Which option best explains {topic}?"
    return [
        f"{topic} is a core concept used to understand, design, or solve real problems in this subject.",
        f"{topic} is only a memorized term and has no practical use in exams or projects.",
        f"{topic} is mainly used to decorate diagrams and does not affect how a system works.",
        f"{topic} can be ignored because it is unrelated to the main ideas of the subject."
    ]


def render_question(question, index):
    question_type = (
        question.get("question_type")
        or "mcq"
    ).lower()

    with st.container(border=True):
        st.subheader(f"Question {index}")
        st.markdown(
            f"""
            <span class="question-meta">{question_type.upper()}</span>
            <span class="question-meta">{question.get('difficulty', 'mixed')}</span>
            <span class="question-meta">{question.get('marks', 1)} marks</span>
            """,
            unsafe_allow_html=True
        )
        st.write(question["question"])

        key = f"answer_{question['id']}"

        if question_type == "mcq":
            options = repair_legacy_mcq(question)
            return st.radio(
                "Select answer",
                options,
                key=key
            )

        if question_type == "short":
            return st.text_area(
                "Short answer",
                height=100,
                key=key,
                placeholder="Write a concise 3-5 line answer."
            )

        if question_type == "long":
            return st.text_area(
                "Long descriptive answer",
                height=220,
                key=key,
                placeholder="Write definition, explanation, example, advantages/limitations, and conclusion."
            )

        if question_type == "numerical":
            return st.text_area(
                "Numerical solution",
                height=180,
                key=key,
                placeholder="Show formula, substitution, steps, final answer, and units."
            )

        if question_type == "coding":
            return st.text_area(
                "Code / SQL answer",
                height=260,
                key=key,
                placeholder="Write code, explain input/output, and mention edge cases."
            )

        return st.text_area(
            "Answer",
            height=140,
            key=key
        )


config_tab, teacher_tab, exam_tab = st.tabs(
    [
        "Custom Exam",
        "Teacher Exams",
        "Attempt Paper"
    ]
)


with config_tab:
    col1, col2, col3 = st.columns(3)

    with col1:
        subjects = st.multiselect(
            "Subjects",
            BTECH_CSE_SUBJECTS,
            default=["Database Management Systems"]
        )
        topics_text = st.text_input(
            "Topics",
            placeholder="Optional: SQL Joins, Normalization"
        )

    with col2:
        question_types = st.multiselect(
            "Question types",
            ["mcq", "short", "long", "numerical", "coding"],
            default=["mcq", "short", "numerical"]
        )
        difficulty = st.selectbox(
            "Difficulty",
            ["mixed", "easy", "medium", "hard"]
        )

    with col3:
        duration_mode = st.selectbox(
            "Exam duration",
            [
                "quick",
                "practice",
                "full",
                "custom"
            ],
            format_func=lambda value: {
                "quick": "10-minute quick test",
                "practice": "30-minute practice test",
                "full": "1-hour full-length exam",
                "custom": "Custom duration"
            }[value]
        )

        custom_duration = st.number_input(
            "Custom minutes",
            min_value=5,
            max_value=180,
            value=45,
            disabled=duration_mode != "custom"
        )

        num_questions = st.slider(
            "Number of questions",
            3,
            40,
            10
        )

    if st.button("Generate Custom Exam", type="primary"):
        if not subjects:
            st.warning("Select at least one subject.")
        elif not question_types:
            st.warning("Select at least one question type.")
        else:
            topics = [
                topic.strip()
                for topic in topics_text.split(",")
                if topic.strip()
            ]

            with st.spinner("Building high-quality mixed-format exam..."):
                exam_data = create_custom_exam(
                    {
                        "title": "Student Custom Exam",
                        "subjects": subjects,
                        "topics": topics,
                        "question_types": question_types,
                        "difficulty": difficulty,
                        "num_questions": num_questions,
                        "duration_mode": duration_mode,
                        "duration_minutes": custom_duration if duration_mode == "custom" else None
                    },
                    st.session_state.token
                )

            if not exam_data.get("questions"):
                st.error("No questions matched your settings. Try fewer filters.")
            else:
                st.session_state.exam_data = exam_data
                st.session_state.exam_started_at = datetime.now()
                st.success("Custom exam generated. Open the Attempt Paper tab.")


with teacher_tab:
    exams = [
        exam
        for exam in available_teacher_exams
        if (exam.get("status") or "open").lower() == "open"
    ]

    if not exams:
        st.info("No teacher-created exams available.")
    else:
        exam_options = {}
        for exam in exams:
            label = (
                f"{exam.get('subject_code') or 'NO-CODE'} | "
                f"{exam.get('subject') or 'General'} | "
                f"{exam['title']} | Due {exam.get('end_time') or 'not set'}"
            )
            exam_options[label] = exam["id"]

        selected_exam = st.selectbox("Select teacher exam", list(exam_options.keys()))
        selected_exam_id = exam_options[selected_exam]
        selected_meta = next(
            exam
            for exam in exams
            if exam["id"] == selected_exam_id
        )

        st.markdown(
            f"""
            <div class="exam-card">
                <h4>{selected_meta.get('title')}</h4>
                <p><strong>Subject:</strong> {selected_meta.get('subject') or 'General'} ({selected_meta.get('subject_code') or 'NO-CODE'})</p>
                <p><strong>Semester:</strong> {selected_meta.get('semester') or 'Not set'} | <strong>Type:</strong> {selected_meta.get('exam_type') or 'Exam'}</p>
                <p><strong>Status:</strong> {selected_meta.get('status') or 'open'} | <strong>Duration:</strong> {selected_meta.get('duration_minutes', 30)} minutes</p>
                <p><strong>Deadline:</strong> {selected_meta.get('end_time') or 'Not set'}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button("Start Teacher Exam"):
            exam_data = start_exam(
                selected_exam_id,
                st.session_state.token
            )

            exam_data["duration_minutes"] = selected_meta.get(
                "duration_minutes",
                30
            )
            exam_data["subject"] = selected_meta.get("subject")
            exam_data["subject_code"] = selected_meta.get("subject_code")
            exam_data["title"] = selected_meta.get("title")
            exam_data["deadline"] = selected_meta.get("end_time")
            st.session_state.exam_data = exam_data
            st.session_state.exam_started_at = datetime.now()
            st.success("Teacher exam opened. Open the Attempt Paper tab.")


with exam_tab:
    if not st.session_state.exam_data:
        st.info("Generate or start an exam first.")
    else:
        render_timer()

        if st.session_state.exam_data.get("title"):
            st.info(
                f"{st.session_state.exam_data.get('subject_code') or 'NO-CODE'} "
                f"{st.session_state.exam_data.get('subject') or ''} | "
                f"{st.session_state.exam_data.get('title')} | "
                f"Deadline: {st.session_state.exam_data.get('deadline') or 'Not set'}"
            )

        questions = st.session_state.exam_data.get("questions", [])

        st.subheader("Exam Questions")

        student_answers = {}

        for index, question in enumerate(questions, start=1):
            answer = render_question(question, index)
            student_answers[str(question["id"])] = answer

        if st.button("Submit Exam", type="primary"):
            result = submit_exam(
                st.session_state.exam_data["exam_id"],
                student_answers,
                st.session_state.token
            )

            exam_result = result.get("result", {})
            st.success("Exam submitted.")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Score", exam_result.get("score", 0))
            col2.metric("Total Marks", exam_result.get("total_marks", 0))
            col3.metric("Percentage", f"{exam_result.get('percentage', 0)}%")
            col4.metric("Status", exam_result.get("status", "N/A"))

            st.subheader("Question-wise Evaluation")
            st.dataframe(
                exam_result.get("breakdown", []),
                use_container_width=True
            )

            if exam_result.get("ai_feedback"):
                st.subheader("AI Feedback")
                st.info(exam_result["ai_feedback"])
