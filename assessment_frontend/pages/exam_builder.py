from datetime import date, time

import streamlit as st

from components.auth import require_login
from components.sidebar import show_sidebar
from services.api_client import (
    create_exam,
    create_exam_sets,
    fetch_exam_set_assignments,
    fetch_exams,
    fetch_teacher_subject_students,
    populate_exam_from_bank,
    preview_question_sets,
    save_exam_set_assignments
)
from services.study_catalog import BTECH_CSE_SUBJECTS, SUBJECT_CODES, SUBJECT_TOPICS, SYLLABUS_TRACKS


st.set_page_config(
    page_title="Exam Builder",
    layout="wide"
)


require_login()

if st.session_state.get("user", {}).get("role") != "teacher":
    st.error("Teacher Access Only")
    st.stop()


show_sidebar()

st.markdown(
    """
    <style>
    .builder-hero {
        background: linear-gradient(135deg, #0f172a, #1d4ed8 55%, #0f766e);
        color: white;
        border-radius: 22px;
        padding: 28px;
        margin-bottom: 18px;
        box-shadow: 0 20px 44px rgba(15, 23, 42, 0.20);
    }
    .builder-hero h1 { margin: 0 0 8px; font-size: 38px; }
    .builder-hero p { color: #dbeafe; margin: 0; }
    </style>
    <div class="builder-hero">
        <h1>Live Exam Builder</h1>
        <p>Create timed exams, assign questions, schedule class tests, and map papers to the B.Tech CSE syllabus.</p>
    </div>
    """,
    unsafe_allow_html=True
)


create_tab, sets_tab, assign_tab, blueprint_tab = st.tabs(
    [
        "Create Exam",
        "Auto Exam Sets",
        "Assign Questions",
        "Subject Blueprint"
    ]
)


with create_tab:
    col1, col2, col3 = st.columns(3)

    with col1:
        title = st.text_input("Exam title")
        semester = st.selectbox("Semester", list(SYLLABUS_TRACKS.keys()))
        subject = st.selectbox("Subject", BTECH_CSE_SUBJECTS)
        subject_code = st.text_input(
            "Subject code",
            value=SUBJECT_CODES.get(subject, "")
        )

    with col2:
        description = st.text_area("Description", height=125)
        exam_date = st.date_input("Exam date", value=date.today())
        start_time = st.time_input("Start time", value=time(10, 0))

    with col3:
        duration = st.number_input("Duration minutes", min_value=5, value=45)
        deadline_date = st.date_input("Submission deadline", value=date.today())
        deadline_time = st.time_input("Deadline time", value=time(23, 59))
        total_students = st.number_input("Students", min_value=1, value=40)
        test_type = st.selectbox(
            "Assessment type",
            ["Class Test", "Mid Semester", "End Semester", "Lab Test", "Practice Test"]
        )
        auto_fill = st.toggle(
            "Auto-fill from 500-question subject bank",
            value=True
        )

    if st.button("Create Timed Exam", type="primary"):
        if not title.strip():
            st.warning("Please enter exam title.")
        else:
            start_time_text = f"{exam_date} {start_time.strftime('%H:%M')}"
            deadline_text = f"{deadline_date} {deadline_time.strftime('%H:%M')}"
            result = create_exam(
                {
                    "title": f"{subject_code} {subject} - {title}",
                    "description": f"{test_type} | {semester} | {description}",
                    "subject": subject,
                    "subject_code": subject_code,
                    "semester": semester,
                    "exam_type": test_type,
                    "duration_minutes": duration,
                    "start_time": start_time_text,
                    "end_time": deadline_text,
                    "total_students": total_students,
                    "status": "open"
                },
                st.session_state.token
            )

            if auto_fill and result.get("exam_id"):
                bank_result = populate_exam_from_bank(
                    {
                        "exam_id": result["exam_id"],
                        "subjects": [subject],
                        "topics": [],
                        "question_types": ["mcq", "short", "long"],
                        "difficulty": "mixed",
                        "num_questions": 20
                    },
                    st.session_state.token
                )
                result["bank_questions_added"] = bank_result.get(
                    "questions_added",
                    0
                )

            st.success("Exam created.")
            st.write(result)


with sets_tab:
    st.subheader("Automatic Exam Set Builder")
    st.caption("Choose the subject, topics, question type, level, number of questions, and number of sets. The system previews and creates Set A, Set B, Set C automatically.")

    col1, col2, col3 = st.columns(3)

    with col1:
        set_title = st.text_input("Base exam title", value="Class Test", key="set_title")
        set_semester = st.selectbox("Semester", list(SYLLABUS_TRACKS.keys()), key="set_semester")
        set_subject = st.selectbox("Subject", BTECH_CSE_SUBJECTS, key="set_subject")
        set_subject_code = st.text_input("Subject code", value=SUBJECT_CODES.get(set_subject, ""), key="set_subject_code")

    with col2:
        topic_options = SUBJECT_TOPICS.get(set_subject, [])
        selected_topics = st.multiselect("Topics", topic_options, default=topic_options[:1])
        question_types = st.multiselect(
            "Question types",
            ["mcq", "short", "long"],
            default=["mcq"]
        )
        set_difficulty = st.selectbox("Question level", ["mixed", "easy", "medium", "hard"])

    with col3:
        number_of_sets = st.number_input("Number of sets", min_value=1, max_value=8, value=2)
        questions_per_set = st.number_input("Questions per set", min_value=1, max_value=100, value=10)
        set_duration = st.number_input("Duration minutes", min_value=5, max_value=180, value=30)
        set_deadline_date = st.date_input("Deadline date", value=date.today(), key="set_deadline_date")
        set_deadline_time = st.time_input("Deadline time", value=time(23, 59), key="set_deadline_time")

    start_text = f"{date.today()} 00:00"
    deadline_text = f"{set_deadline_date} {set_deadline_time.strftime('%H:%M')}"
    set_payload = {
        "title": set_title,
        "description": f"Auto sets | Topics: {', '.join(selected_topics) if selected_topics else 'All'}",
        "subjects": [set_subject],
        "subject_code": set_subject_code,
        "semester": set_semester,
        "exam_type": "Auto Set",
        "topics": selected_topics,
        "question_types": question_types,
        "difficulty": set_difficulty,
        "number_of_sets": int(number_of_sets),
        "questions_per_set": int(questions_per_set),
        "duration_minutes": int(set_duration),
        "start_time": start_text,
        "end_time": deadline_text,
        "total_students": 40
    }

    col_preview, col_create = st.columns(2)
    with col_preview:
        if st.button("Preview Sets", type="primary", use_container_width=True):
            if not question_types:
                st.warning("Choose at least one question type.")
            else:
                with st.spinner("Building preview sets from the bank..."):
                    st.session_state.auto_set_preview = preview_question_sets(
                        set_payload,
                        st.session_state.token
                    )

    with col_create:
        if st.button("Create These Sets", use_container_width=True):
            if not question_types:
                st.warning("Choose at least one question type.")
            else:
                with st.spinner("Creating released teacher exam sets..."):
                    result = create_exam_sets(
                        set_payload,
                        st.session_state.token
                    )
                st.success("Exam sets created and visible to students.")
                st.write(result)

    preview = st.session_state.get("auto_set_preview")
    if preview:
        st.info(f"Available matching questions in bank: {preview.get('available_questions', 0)}")
        for set_item in preview.get("sets", []):
            with st.expander(set_item["set_name"], expanded=True):
                for index, question in enumerate(set_item.get("questions", []), start=1):
                    st.markdown(
                        f"**{index}. [{question.get('question_type', '').upper()} | {question.get('difficulty')}]** {question.get('question')}"
                    )
                    if question.get("options"):
                        for option in question["options"]:
                            st.write(f"- {option}")


with assign_tab:
    exams = fetch_exams()
    roster = fetch_teacher_subject_students(st.session_state.token)
    saved_assignments = fetch_exam_set_assignments(st.session_state.token)

    st.subheader("Student Set Allocation")
    st.caption(
        "No manual question picking here. Create sets in Auto Exam Sets, then assign students alphabetically and evenly across Set A, Set B, Set C, etc."
    )

    if not exams:
        st.info("No exams created yet. Create automatic sets first.")
    elif not roster:
        st.info("No enrolled students found. Add your subject in Teacher Portal and ask students to enroll from Student Dashboard.")
    else:
        subjects_with_roster = sorted(
            {
                item["subject"]
                for item in roster
            }
        )
        selected_subject_for_assign = st.selectbox(
            "Subject roster",
            subjects_with_roster
        )

        subject_roster = sorted(
            [
                item
                for item in roster
                if item["subject"] == selected_subject_for_assign
            ],
            key=lambda item: (
                item.get("student_name") or "",
                item.get("student_email") or ""
            )
        )

        matching_set_exams = [
            exam
            for exam in exams
            if exam.get("subject") == selected_subject_for_assign
            and (exam.get("status") or "open").lower() == "open"
        ]

        matching_set_exams = sorted(
            matching_set_exams,
            key=lambda exam: exam.get("title") or ""
        )

        if not matching_set_exams:
            st.warning("No open set exams found for this subject. Create sets in the Auto Exam Sets tab first.")
        else:
            max_sets = min(8, len(matching_set_exams))
            set_count = st.number_input(
                "Number of sets to use",
                min_value=1,
                max_value=max_sets,
                value=min(2, max_sets)
            )
            selected_set_exams = matching_set_exams[: int(set_count)]

            manual_cap = st.toggle(
                "Set custom student cap per group",
                value=False
            )
            group_cap = None
            if manual_cap:
                group_cap = st.number_input(
                    "Students per group",
                    min_value=1,
                    max_value=max(1, len(subject_roster)),
                    value=max(1, len(subject_roster) // int(set_count))
                )

            assignments = []
            group_counts = {
                f"Set {chr(65 + index)}": 0
                for index in range(int(set_count))
            }

            for index, student in enumerate(subject_roster):
                if group_cap:
                    set_index = min(
                        index // int(group_cap),
                        int(set_count) - 1
                    )
                else:
                    set_index = index % int(set_count)

                exam = selected_set_exams[set_index]
                set_name = f"Set {chr(65 + set_index)}"
                group_counts[set_name] += 1
                assignments.append(
                    {
                        "student_name": student.get("student_name"),
                        "student_email": student.get("student_email"),
                        "subject": selected_subject_for_assign,
                        "subject_code": exam.get("subject_code"),
                        "set_name": set_name,
                        "exam_id": exam.get("id"),
                        "exam_title": exam.get("title")
                    }
                )

            count_cols = st.columns(int(set_count))
            for index, (set_name, count) in enumerate(group_counts.items()):
                count_cols[index].metric(set_name, f"{count} students")

            st.dataframe(
                assignments,
                use_container_width=True
            )

            if st.button("Save Student Set Allocation", type="primary"):
                result = save_exam_set_assignments(
                    assignments,
                    st.session_state.token
                )
                st.success(
                    f"Saved {result.get('saved_assignments', len(assignments))} student set assignments."
                )
                st.write(result)

    st.divider()
    st.subheader("Saved Assignment Record")
    if saved_assignments:
        st.dataframe(
            saved_assignments,
            use_container_width=True
        )
    else:
        st.info("No saved set assignment record yet.")


with blueprint_tab:
    st.subheader("B.Tech CSE Subject Coverage")
    selected_semester = st.selectbox(
        "View semester track",
        list(SYLLABUS_TRACKS.keys()),
        key="blueprint_semester"
    )

    for item in SYLLABUS_TRACKS[selected_semester]:
        st.progress(
            0.65,
            text=f"{item}: class tests, assignments, and final exam blueprint ready"
        )

    st.divider()
    st.subheader("Major Subjects Supported")
    st.dataframe(
        [{"subject": subject} for subject in BTECH_CSE_SUBJECTS],
        use_container_width=True
    )
