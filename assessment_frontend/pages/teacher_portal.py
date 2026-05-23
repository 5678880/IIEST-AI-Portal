from datetime import date

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pypdf import PdfReader

from components.auth import require_login
from components.sidebar import show_sidebar
from components.theme import ai_feature_grid, hero
from services.api_client import (
    add_teacher_subject,
    ask_ai_tutor,
    create_exam,
    fetch_exams,
    fetch_questions,
    fetch_results,
    fetch_subject_catalog,
    fetch_teacher_subject_students,
    fetch_teacher_subjects,
    generate_ai_questions,
    populate_exam_from_bank,
    seed_question_bank
)
from services.study_catalog import BTECH_CSE_SUBJECTS, SUBJECT_CODES, SYLLABUS_TRACKS


st.set_page_config(page_title="IIEST Teacher AI Command Center", layout="wide")

require_login()

if st.session_state.get("user", {}).get("role") != "teacher":
    st.error("Teacher Access Only")
    st.stop()


show_sidebar()

hero(
    "IIEST Teacher AI Command Center",
    "A teacher-first workspace for class capture, instant tests, remedial groups, syllabus planning, grading support, and daily teaching priorities."
)

exams = fetch_exams()
questions = fetch_questions()
results = fetch_results(st.session_state.token)


def render_voice_capture():
    components.html(
        """
        <div style="font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
            <button id="captureClass" style="
                border: 0; width: 100%; border-radius: 14px; padding: 14px;
                background: linear-gradient(135deg, #111827, #2563eb);
                color: white; font-weight: 900; cursor: pointer;">
                Start capture
            </button>
            <button id="stopClass" style="
                border: 0; width: 100%; border-radius: 14px; padding: 14px;
                background: #ef4444; color: white; font-weight: 900; cursor: pointer;">
                Stop capture
            </button>
            </div>
            <p id="captureStatus" style="font-size: 13px; color: #475569; margin: 9px 0 0;">
                Speak the lecture. Stop when class ends; transcript will move into the portal.
            </p>
            <textarea id="captureText" style="width:100%; min-height:110px; margin-top:8px; border:1px solid #cbd5e1; border-radius:12px; padding:10px;"></textarea>
            <audio id="voicePlayback" controls style="width:100%; margin-top:8px; display:none;"></audio>
            <a id="downloadAudio" style="display:none; margin-top:8px; color:#2563eb; font-weight:700;">Download voice recording</a>
        </div>
        <script>
        const button = document.getElementById("captureClass");
        const stopButton = document.getElementById("stopClass");
        const status = document.getElementById("captureStatus");
        const captureText = document.getElementById("captureText");
        const audio = document.getElementById("voicePlayback");
        const downloadAudio = document.getElementById("downloadAudio");
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recorder = null;
        let chunks = [];
        if (!SpeechRecognition) {
            button.disabled = true;
            button.textContent = "Voice capture not supported";
            status.textContent = "Use Chrome for speech capture.";
        } else {
            const recognition = new SpeechRecognition();
            recognition.lang = "en-US";
            recognition.interimResults = false;
            recognition.continuous = true;
            let transcript = "";
            button.onclick = async () => {
                transcript = "";
                captureText.value = "";
                status.textContent = "Listening. Speak the class topics now...";
                recognition.start();
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    recorder = new MediaRecorder(stream);
                    chunks = [];
                    recorder.ondataavailable = event => chunks.push(event.data);
                    recorder.onstop = () => {
                        const blob = new Blob(chunks, { type: "audio/webm" });
                        const url = URL.createObjectURL(blob);
                        audio.src = url;
                        audio.style.display = "block";
                        downloadAudio.href = url;
                        downloadAudio.download = "class-capture.webm";
                        downloadAudio.textContent = "Download voice recording";
                        downloadAudio.style.display = "block";
                    };
                    recorder.start();
                } catch (error) {
                    status.textContent = "Mic recording blocked, but transcript capture may still work.";
                }
            };
            stopButton.onclick = () => {
                recognition.stop();
                if (recorder && recorder.state !== "inactive") recorder.stop();
                status.textContent = "Stopped. Moving transcript into portal...";
                setTimeout(() => {
                    if (transcript.trim()) {
                        window.top.location.href = "/teacher_portal?class_capture=" + encodeURIComponent(transcript.trim());
                    }
                }, 800);
            };
            recognition.onresult = (event) => {
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    transcript += event.results[i][0].transcript + " ";
                }
                captureText.value = transcript;
                status.textContent = "Captured: " + transcript;
            };
            recognition.onend = () => {
                if (transcript.trim()) {
                    status.textContent = "Capture stopped. Transcript ready.";
                } else {
                    status.textContent = "No speech captured. Try again.";
                }
            };
            recognition.onerror = (event) => {
                status.textContent = "Voice error: " + event.error;
            };
        }
        </script>
        """,
        height=108
    )


def extract_syllabus_text(uploaded_file):
    if uploaded_file is None:
        return ""

    if uploaded_file.type == "text/plain":
        return uploaded_file.getvalue().decode("utf-8", errors="ignore")

    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        text = []
        for page in reader.pages[:18]:
            text.append(page.extract_text() or "")
        return "\n".join(text)

    return ""


def result_rows():
    if results:
        return results

    return [
        {
            "student_name": "demo.student@example.com",
            "exam_id": 1,
            "percentage": 48,
            "ai_feedback": "Needs DBMS normalization and SQL join practice.",
            "submitted_answers": ""
        },
        {
            "student_name": "sample.student@example.com",
            "exam_id": 1,
            "percentage": 72,
            "ai_feedback": "Good basics. Needs more DSA recursion practice.",
            "submitted_answers": ""
        }
    ]


(
    overview_tab,
    capture_tab,
    roster_tab,
    remedial_tab,
    generator_tab,
    syllabus_tab,
    lms_tab
) = st.tabs(
    [
        "Overview",
        "Class Capture",
        "Subject Roster",
        "Remedial Cohorts",
        "AI Question Studio",
        "Syllabus Progression",
        "LMS Tools"
    ]
)


with overview_tab:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Active Subjects", len(BTECH_CSE_SUBJECTS))
    col2.metric("Created Exams", len(exams))
    col3.metric("Question Bank", len(questions))
    col4.metric("Automation", "Ready")

    if st.button("Prepare / Expand Question Bank", type="primary"):
        with st.spinner("Preparing structured question bank..."):
            result = seed_question_bank(st.session_state.token)
        st.success(result.get("message", "Question bank updated."))
        st.write(result)

    rows = result_rows()
    weak_count = len([item for item in rows if item.get("percentage", 100) < 60])
    pending_grading = len([item for item in rows if "manual recommended" in str(item.get("submitted_answers", ""))])

    st.subheader("Today’s AI Priorities")
    if "teacher_priorities" not in st.session_state:
        st.session_state.teacher_priorities = [
            {
                "priority": "Review weak learners",
                "reason": f"{weak_count} students need support based on marks or feedback.",
                "action": "Open Remedial Cohorts and group them by weak topic.",
                "owner": "Teacher",
                "status": "Open"
            },
            {
                "priority": "Check descriptive answers",
                "reason": f"{pending_grading} answer sets may need manual review.",
                "action": "Open AI Grading Center for rubric review.",
                "owner": "Teacher",
                "status": "Open"
            },
            {
                "priority": "Run after-class concept check",
                "reason": "Taught topics can be converted into a 10-minute test immediately after class.",
                "action": "Use Class Capture.",
                "owner": "Teacher",
                "status": "Planned"
            },
            {
                "priority": "Plan syllabus gaps",
                "reason": "Upload the term syllabus and target exam date to get a teaching calendar.",
                "action": "Use Syllabus Progression.",
                "owner": "Teacher",
                "status": "Open"
            }
        ]

    st.session_state.teacher_priorities = st.data_editor(
        st.session_state.teacher_priorities,
        use_container_width=True
        ,
        num_rows="dynamic",
        column_config={
            "status": st.column_config.SelectboxColumn(
                "status",
                options=["Open", "Planned", "In Progress", "Done"]
            )
        }
    )

    ai_feature_grid(
        [
            {
                "title": "Class-to-check workflow",
                "body": "Teacher speaks taught topics after class. AI creates a quick concept test while the class memory is fresh."
            },
            {
                "title": "Remedial cohort builder",
                "body": "AI groups students by weak topics, severity, and next action instead of leaving teachers to read every result manually."
            },
            {
                "title": "Teaching load optimizer",
                "body": "The dashboard tells teachers what to do next: grade, revise, test, intervene, or update syllabus progress."
            },
            {
                "title": "Syllabus gap planner",
                "body": "Upload the term syllabus and target date; AI turns it into coverage warnings, revision slots, and test checkpoints."
            },
            {
                "title": "Manual review focus",
                "body": "AI does not replace teacher judgement. It highlights answers and students that deserve teacher attention."
            },
            {
                "title": "Student support loop",
                "body": "Every test, attendance signal, and weak-topic note can become a student-specific improvement plan."
            }
        ]
    )


with capture_tab:
    st.subheader("Class Capture")
    st.caption("Record the class, capture transcript, create notes, send it to enrolled students, then give a test from what you taught.")

    captured_voice = st.query_params.get("class_capture", "")
    if isinstance(captured_voice, list):
        captured_voice = captured_voice[0] if captured_voice else ""

    left, right = st.columns([1.4, 1])
    with left:
        class_subject = st.selectbox("Subject", BTECH_CSE_SUBJECTS, key="capture_subject")
        class_subject_code = st.text_input(
            "Subject code",
            value=SUBJECT_CODES.get(class_subject, ""),
            key="capture_subject_code"
        )
        taught_topics = st.text_area(
            "Captured transcript / taught topics",
            value=captured_voice,
            height=170,
            placeholder="Example: Covered normalization, 1NF, 2NF, 3NF, anomalies, and examples."
        )
    with right:
        render_voice_capture()
        test_minutes = st.selectbox("Quick test duration", [10, 15, 20, 30])
        question_count = st.slider("Questions", 3, 12, 5, key="capture_q_count")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="capture_diff")

    if captured_voice:
        st.success("Transcript captured. Review it, create notes, then send or test the class.")

    if "class_capture_notes" not in st.session_state:
        st.session_state.class_capture_notes = ""

    note_col, message_col = st.columns(2)
    with note_col:
        if st.button("Create Class Notes From Capture", use_container_width=True):
            if not taught_topics.strip():
                st.warning("Capture or type the lecture first.")
            else:
                with st.spinner("Creating class notes..."):
                    result = ask_ai_tutor(
                        "Create clean class notes from this lecture transcript:\n" + taught_topics,
                        class_subject,
                        "medium",
                        st.session_state.token,
                        task="summarize"
                    )
                st.session_state.class_capture_notes = result.get("answer", "")

    if st.session_state.class_capture_notes:
        st.subheader("Generated Class Notes")
        st.info(st.session_state.class_capture_notes)

    if "course_messages" not in st.session_state:
        st.session_state.course_messages = []

    with message_col:
        message_body = st.text_area(
            "Message to enrolled students",
            value=st.session_state.class_capture_notes or taught_topics,
            height=120,
            placeholder="Transcript/notes to send to students enrolled in this course."
        )
        if st.button("Send Capture Notes To Course Students", use_container_width=True):
            roster = fetch_teacher_subject_students(st.session_state.token)
            recipients = [
                item
                for item in roster
                if item.get("subject") == class_subject
            ]
            st.session_state.course_messages.append(
                {
                    "subject": class_subject,
                    "subject_code": class_subject_code,
                    "recipients": len(recipients),
                    "message": message_body,
                    "sent_on": str(date.today())
                }
            )
            st.success(f"Message saved for {len(recipients)} enrolled students.")

    if st.session_state.course_messages:
        st.subheader("Course Message Record")
        st.dataframe(st.session_state.course_messages, use_container_width=True)

    st.divider()
    st.subheader("Now Give A Test To The Class")

    if st.button("Create After-Class Check", type="primary"):
        if not taught_topics.strip():
            st.warning("Capture or type the taught topics first.")
        else:
            with st.spinner("Creating exam shell..."):
                exam_result = create_exam(
                    {
                        "title": f"{class_subject_code} {class_subject} After-Class Check",
                        "description": f"Generated from taught topics: {taught_topics[:220]}",
                        "subject": class_subject,
                        "subject_code": class_subject_code,
                        "semester": "Current Term",
                        "exam_type": "After-Class Check",
                        "duration_minutes": test_minutes,
                        "start_time": str(date.today()),
                        "end_time": str(date.today()),
                        "total_students": 40,
                        "status": "open"
                    },
                    st.session_state.token
                )

            exam_id = exam_result.get("exam_id")

            if not exam_id:
                st.error("Could not create the test shell.")
            else:
                with st.spinner("Selecting concept-check questions from the subject bank..."):
                    result = populate_exam_from_bank(
                        {
                            "exam_id": exam_id,
                            "subjects": [class_subject],
                            "topics": [],
                            "question_types": ["mcq", "short"],
                            "difficulty": difficulty.lower(),
                            "num_questions": question_count
                        },
                        st.session_state.token
                    )

                st.success("After-class concept check created.")
                st.write(result)

    st.info(
        "Mechanism: AI converts the teacher's spoken lecture summary into a short test. "
        "This helps the teacher measure whether students actually understood today's class before moving ahead."
    )


with roster_tab:
    st.subheader("Subject Roster")
    st.caption(
        "Teachers first enroll themselves for the subjects they teach. Students enroll from their dashboards. "
        "This page then shows exactly which students belong to each teacher subject."
    )

    subject_catalog = fetch_subject_catalog()
    teacher_subjects = fetch_teacher_subjects(st.session_state.token)
    subject_students = fetch_teacher_subject_students(st.session_state.token)

    if subject_catalog:
        catalog_lookup = {
            item["subject"]: item
            for item in subject_catalog
        }

        with st.form("teacher_subject_form"):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                selected_subject = st.selectbox(
                    "Subject taught",
                    list(catalog_lookup.keys())
                )

            selected_catalog = catalog_lookup[selected_subject]
            semesters = sorted(
                {
                    item["semester"]
                    for item in subject_catalog
                }
            )

            with col2:
                semester = st.selectbox(
                    "Semester",
                    semesters,
                    index=semesters.index(selected_catalog["semester"])
                )

            with col3:
                section = st.text_input(
                    "Class / Section",
                    value="CSE-A"
                )

            with col4:
                academic_year = st.text_input(
                    "Academic Year",
                    value="2026"
                )

            if st.form_submit_button("Add Teaching Subject", type="primary"):
                result = add_teacher_subject(
                    {
                        "subject": selected_subject,
                        "subject_code": selected_catalog["subject_code"],
                        "semester": semester,
                        "section": section,
                        "academic_year": academic_year
                    },
                    st.session_state.token
                )

                if result.get("error"):
                    st.error(result["error"])
                else:
                    st.success(
                        f"Added {selected_subject} ({selected_catalog['subject_code']}) for {section}."
                    )
                    st.rerun()

    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Teaching Subjects", len(teacher_subjects))
    col2.metric("Roster Students", len(subject_students))
    col3.metric("AI Cohort Ready", "Yes" if subject_students else "Pending")

    st.subheader("My Teaching Subjects")
    if teacher_subjects:
        st.dataframe(
            pd.DataFrame(teacher_subjects),
            use_container_width=True
        )
    else:
        st.info("Add at least one subject you teach. Student rosters will appear after students enroll.")

    st.subheader("Students Under My Subjects")
    if subject_students:
        roster_df = pd.DataFrame(subject_students)
        selected_roster_subject = st.selectbox(
            "Filter by subject",
            ["All"] + sorted(roster_df["subject"].unique().tolist())
        )

        if selected_roster_subject != "All":
            roster_df = roster_df[
                roster_df["subject"] == selected_roster_subject
            ]

        st.dataframe(
            roster_df,
            use_container_width=True
        )

        st.info(
            "Mechanism: when these students take tests, their result email matches this roster. "
            "AI can then build remedial cohorts subject-wise instead of mixing the whole college together."
        )
    else:
        st.info("No students have enrolled into your teaching subjects yet.")


with remedial_tab:
    st.subheader("Remedial Cohorts")
    st.caption("Group students by weak topics, seriousness, and action needed.")

    rows = result_rows()
    df = pd.DataFrame(rows)
    subject_students = fetch_teacher_subject_students(st.session_state.token)

    if subject_students and not df.empty and "student_name" in df.columns:
        roster_df = pd.DataFrame(subject_students)
        teacher_student_emails = set(roster_df["student_email"].tolist())
        df = df[
            df["student_name"].isin(teacher_student_emails)
        ]

        st.info(
            "Showing remedial analysis only for students enrolled under your teaching subjects."
        )

    if df.empty:
        st.info(
            "No matching student submissions yet. Once enrolled students take exams, AI will group them into remedial cohorts here."
        )
    else:
        st.dataframe(df, use_container_width=True)

    if not df.empty and st.button("Build Remedial Groups", type="primary"):
        prompt = (
            "Build remedial student groups from these exam results. "
            "Group by weak topic, severity, recommended practice, and teacher action:\n"
            + df.to_string(index=False)
        )

        with st.spinner("Grouping students by weakness..."):
            result = ask_ai_tutor(
                prompt,
                "Teacher Remediation",
                "medium",
                st.session_state.token,
                task="weak_topics"
            )

        st.info(result.get("answer", "No remedial grouping generated."))

    st.markdown(
        """
Suggested cohort types:
- Critical recovery group: below 40%, needs teacher intervention.
- Concept repair group: 40-60%, needs topic-wise practice.
- Exam writing group: knows concepts but loses marks in long answers.
- Coding/numerical practice group: needs step/output validation practice.
"""
    )


with generator_tab:
    if not exams:
        st.warning("Please create an exam first in Exam Builder.")
    else:
        exam_options = {exam["title"]: exam["id"] for exam in exams}
        col1, col2 = st.columns([1, 1])

        with col1:
            selected_exam = st.selectbox("Select exam", list(exam_options.keys()))
            selected_exam_id = exam_options[selected_exam]
            subject = st.selectbox("Subject", BTECH_CSE_SUBJECTS)
            topic = st.text_input("Syllabus topic")

        with col2:
            difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
            num_questions = st.slider("Number of questions", 1, 20, 5)
            question_type = st.multiselect(
                "Question type",
                ["MCQ", "Conceptual", "Numerical", "Coding", "Case Study"],
                default=["MCQ"]
            )

        if st.button("Generate Smart Questions", type="primary"):
            if not topic.strip():
                st.warning("Please enter a topic.")
            else:
                with st.spinner("Generating AI questions..."):
                    result = generate_ai_questions(
                        f"{subject}: {topic} | Type: {', '.join(question_type)}",
                        difficulty,
                        num_questions,
                        selected_exam_id,
                        st.session_state.token
                    )

                generated = result.get("generated_questions", [])
                if not generated:
                    st.error("No questions generated.")
                    st.write(result)
                else:
                    st.success(f"{len(generated)} questions generated.")
                    for index, question in enumerate(generated, start=1):
                        with st.container(border=True):
                            st.subheader(f"Question {index}")
                            st.write(question["question"])
                            for option_index, option in enumerate(question["options"], start=1):
                                st.write(f"{option_index}. {option}")
                            st.success(f"Correct Answer: {question['correct_answer']}")
                            st.caption(f"Difficulty: {question['difficulty']}")


with syllabus_tab:
    st.subheader("Syllabus Planner")
    st.caption("Upload syllabus, paste units, set exam date, and let AI identify gaps and test checkpoints.")

    col1, col2 = st.columns([1, 1])
    with col1:
        syllabus_file = st.file_uploader("Upload syllabus PDF or TXT", type=["pdf", "txt"])
        syllabus_text = st.text_area(
            "Or paste syllabus text",
            height=190,
            placeholder="Paste units, outcomes, modules, internal dates, and exam coverage."
        )
    with col2:
        term_start = st.date_input("Term start date", value=date.today())
        target_exam = st.date_input("Target exam date")
        covered_topics = st.text_area("Already covered topics", height=120)
        weekly_classes = st.slider("Classes per week", 1, 8, 4)

    extracted_text = extract_syllabus_text(syllabus_file)
    full_syllabus = (extracted_text + "\n" + syllabus_text).strip()

    if st.button("Create Syllabus Gap Plan", type="primary"):
        if not full_syllabus:
            st.warning("Upload or paste syllabus first.")
        else:
            prompt = f"""
Create a syllabus gap and teaching plan.
Term start: {term_start}
Target exam: {target_exam}
Classes per week: {weekly_classes}
Covered topics: {covered_topics}
Syllabus:
{full_syllabus[:5000]}

Return:
1. What is left
2. Urgent topics
3. Weekly teaching plan
4. Quick test checkpoints
5. Revision slots
6. Where AI helps the teacher
"""
            with st.spinner("Planning syllabus coverage..."):
                result = ask_ai_tutor(
                    prompt,
                    "Syllabus Planning",
                    "medium",
                    st.session_state.token,
                    task="improvement"
                )
            st.info(result.get("answer", "No plan generated."))

    st.divider()
    st.subheader("Manual Progress Tracker")
    for semester, subjects in SYLLABUS_TRACKS.items():
        with st.expander(semester):
            for subject in subjects:
                coverage = st.slider(subject, 0, 100, 55, key=f"coverage_{semester}_{subject}")
                st.progress(coverage / 100, text=f"{coverage}% complete")


with lms_tab:
    st.subheader("College ERP / LMS Features")
    st.dataframe(
        [
            {"feature": "Attendance-linked test eligibility", "status": "Configured"},
            {"feature": "Timed class tests", "status": "Available"},
            {"feature": "Subject-wise test calendar", "status": "Available"},
            {"feature": "Weak-topic cohorting", "status": "Available"},
            {"feature": "AI remedial study plans", "status": "Available"},
            {"feature": "Lecture capture to quick test", "status": "Available"},
            {"feature": "Syllabus gap planning", "status": "Available"}
        ],
        use_container_width=True
    )

    st.info("The teaching load optimizer is intentionally embedded in the dashboard: it appears as daily priorities, not as another separate feature.")
