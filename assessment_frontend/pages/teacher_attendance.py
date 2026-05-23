from datetime import date

import pandas as pd
import streamlit as st

from components.auth import require_login
from components.sidebar import show_sidebar
from components.theme import hero, ai_feature_grid
from services.api_client import ask_ai_tutor
from services.file_extraction import extract_text_from_file, extraction_note
from services.study_catalog import BTECH_CSE_SUBJECTS


st.set_page_config(
    page_title="IIEST Attendance Intelligence",
    layout="wide"
)


require_login()

if st.session_state.get("user", {}).get("role") != "teacher":
    st.error("Teacher Access Only")
    st.stop()


show_sidebar()

hero(
    "Attendance Intelligence",
    "Mark attendance, detect repeated absence patterns, and let AI suggest teacher interventions before students fall behind."
)

if "attendance_records" not in st.session_state:
    st.session_state.attendance_records = pd.DataFrame(
        [
            {"roll_no": "CSE001", "student": "Aarav Sharma", "subject": "Database Management Systems", "present": True, "attention": "Focused", "risk_note": ""},
            {"roll_no": "CSE002", "student": "Meera Iyer", "subject": "Operating Systems", "present": False, "attention": "Absent", "risk_note": "Missed last class too"},
            {"roll_no": "CSE003", "student": "Kabir Khan", "subject": "Data Structures", "present": True, "attention": "Distracted", "risk_note": "Needs practice"},
            {"roll_no": "CSE004", "student": "Ananya Rao", "subject": "Computer Networks", "present": True, "attention": "Focused", "risk_note": ""}
        ]
    )


subject = st.selectbox("Class subject", BTECH_CSE_SUBJECTS)
class_date = st.date_input("Class date", value=date.today())

upload_tab, sheet_tab = st.tabs(["Upload Attendance Record", "Manual Attendance Sheet"])

with upload_tab:
    st.subheader("Upload Attendance Sheet")
    st.caption("Upload scanned attendance, CSV, Excel, PDF, image, TXT, or DOCX. OCR will extract text where possible.")

    uploaded_attendance = st.file_uploader(
        "Upload attendance file",
        type=["pdf", "png", "jpg", "jpeg", "webp", "txt", "docx", "csv", "xlsx"]
    )

    if uploaded_attendance:
        extracted_attendance = extract_text_from_file(uploaded_attendance)
        st.caption(extraction_note())

        corrected_attendance = st.text_area(
            "Extracted attendance text - correct OCR mistakes before analysis",
            value=extracted_attendance,
            height=230,
            placeholder="Example: CSE001 Aarav Present Focused..."
        )

        if st.button("Convert Uploaded Attendance", type="primary"):
            if not corrected_attendance.strip():
                st.warning("Add readable attendance text first.")
            else:
                prompt = f"""
Convert this uploaded attendance record into a clean attendance table.

Subject: {subject}
Date: {class_date}
Raw attendance text:
{corrected_attendance}

Return:
1. Student roll/name
2. Present or absent
3. Late or attention notes
4. Students needing follow-up
5. Any OCR uncertainty
6. Teacher action plan
"""
                with st.spinner("Reading attendance file..."):
                    result = ask_ai_tutor(
                        prompt,
                        subject,
                        "medium",
                        st.session_state.token,
                        task="improvement"
                    )

                st.success("Attendance extraction analysis ready.")
                st.info(result.get("answer", "No attendance analysis generated."))

with sheet_tab:
    st.subheader("Attendance Sheet")
    edited = st.data_editor(
        st.session_state.attendance_records,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "present": st.column_config.CheckboxColumn("Present"),
            "attention": st.column_config.SelectboxColumn(
                "Attention",
                options=["Focused", "Distracted", "Absent", "Late", "Needs help"]
            )
        }
    )
    st.session_state.attendance_records = edited

st.subheader("Attendance Summary")
edited = st.session_state.attendance_records

present_rate = round(float(edited["present"].mean()) * 100, 2) if len(edited) else 0
at_risk = edited[(edited["present"] == False) | (edited["attention"].isin(["Distracted", "Needs help", "Absent"]))]

col1, col2, col3 = st.columns(3)
col1.metric("Present Rate", f"{present_rate}%")
col2.metric("Students Needing Attention", len(at_risk))
col3.metric("AI Intervention Queue", "Ready")

st.divider()

ai_feature_grid(
    [
        {
            "title": "AI absence pattern detector",
            "body": "Flags repeated absence or late patterns so teachers know whom to check on before exam performance drops."
        },
        {
            "title": "AI attention marker",
            "body": "Turns observations like distracted, late, or needs help into a follow-up queue instead of leaving them as notes."
        },
        {
            "title": "AI intervention drafting",
            "body": "Generates a respectful message or remedial action plan for each student based on attendance and attention signals."
        }
    ]
)

st.subheader("AI Teacher Action Plan")

if st.button("Generate Attendance Intervention Plan", type="primary"):
    attendance_text = edited.to_string(index=False)
    prompt = (
        f"Create a teacher action plan for attendance on {class_date} in {subject}. "
        f"Attendance table:\n{attendance_text}\n"
        "Identify risk students, what the teacher should do next, and how AI is helping."
    )

    with st.spinner("Analyzing attendance patterns..."):
        result = ask_ai_tutor(
            prompt,
            subject,
            "medium",
            st.session_state.token,
            task="improvement"
        )

    st.info(result.get("answer", "No attendance plan generated."))

if len(at_risk):
    st.subheader("At-Risk Students")
    st.dataframe(at_risk, use_container_width=True)
