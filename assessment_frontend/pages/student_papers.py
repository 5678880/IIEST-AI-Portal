import streamlit as st
from pypdf import PdfReader

from components.auth import require_login
from components.sidebar import show_sidebar
from services.api_client import ask_ai_tutor
from services.study_catalog import BTECH_CSE_SUBJECTS


st.set_page_config(
    page_title="Papers",
    layout="wide"
)


require_login()

if st.session_state.get("user", {}).get("role") not in ["student", "teacher"]:
    st.error("Student Or Teacher Access Only")
    st.stop()


show_sidebar()

st.title("Papers")
st.caption("Upload question papers, PDFs, or notes and turn them into study material.")

if "uploaded_papers" not in st.session_state:
    st.session_state.uploaded_papers = []

if "latest_paper_text" not in st.session_state:
    st.session_state.latest_paper_text = ""


def extract_uploaded_text(uploaded_file):
    if uploaded_file is None:
        return ""

    if uploaded_file.type == "text/plain":
        return uploaded_file.getvalue().decode(
            "utf-8",
            errors="ignore"
        )

    if uploaded_file.type == "application/pdf":
        reader = PdfReader(uploaded_file)
        page_text = []

        for page in reader.pages[:12]:
            page_text.append(
                page.extract_text() or ""
            )

        return "\n".join(page_text)

    return ""

left, right = st.columns([1.2, 1])

with left:
    subject = st.selectbox("Subject", BTECH_CSE_SUBJECTS)
    paper_type = st.selectbox(
        "Paper type",
        [
            "University Question Paper",
            "Class Test",
            "Assignment",
            "Lecture Notes",
            "Reference PDF"
        ]
    )
    uploaded_file = st.file_uploader(
        "Upload PDF, TXT, or DOCX",
        type=["pdf", "txt", "docx"]
    )

    if uploaded_file and st.button("Add Paper", type="primary"):
        extracted_text = extract_uploaded_text(
            uploaded_file
        )
        st.session_state.latest_paper_text = extracted_text
        st.session_state.uploaded_papers.append(
            {
                "name": uploaded_file.name,
                "subject": subject,
                "type": paper_type,
                "size": uploaded_file.size,
                "text_extracted": bool(extracted_text.strip())
            }
        )
        st.success("Paper added to your study vault.")

with right:
    st.subheader("Smart Paper Actions")
    paper_prompt = st.text_area(
        "Ask about this paper",
        value=st.session_state.latest_paper_text[:2500],
        height=150,
        placeholder="Example: Make a revision plan for this DBMS paper."
    )

    if st.button("Generate Paper Study Plan", use_container_width=True):
        if not paper_prompt.strip():
            st.warning("Enter what you want to do with the paper.")
        else:
            with st.spinner("Creating study plan..."):
                result = ask_ai_tutor(
                    paper_prompt,
                    subject,
                    "medium",
                    st.session_state.token,
                    task="summarize"
                )
            st.info(result.get("answer", "No response generated."))

st.divider()

st.subheader("Uploaded Papers")

if not st.session_state.uploaded_papers:
    st.info("No papers uploaded yet.")
else:
    st.dataframe(
        st.session_state.uploaded_papers,
        use_container_width=True
    )

st.divider()

st.subheader("Quick Paper Prep Template")
st.markdown(
    """
1. First pass: mark repeated topics and formulas.
2. Second pass: solve all short questions.
3. Third pass: solve long answers under timed conditions.
4. Final pass: revise mistakes and create a one-page cheat sheet.
"""
)
