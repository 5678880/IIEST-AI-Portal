import json

import streamlit as st
import streamlit.components.v1 as components

from components.auth import require_login
from components.sidebar import show_sidebar
from services.api_client import BASE_URL
from services.api_client import ask_ai_tutor
from services.file_extraction import extract_text_from_file
from services.file_extraction import extraction_note


st.set_page_config(
    page_title="AI Study Assistant",
    layout="wide"
)


def require_student():
    require_login()

    user = st.session_state.get(
        "user",
        {}
    )

    if user.get("role") not in ["student", "teacher"]:
        st.error(
            "Student Or Teacher Access Only"
        )
        st.stop()


def render_styles():
    st.markdown(
        """
        <style>
        .main .block-container {
            padding-top: 2rem;
            max-width: 1240px;
        }
        .assistant-hero {
            background: linear-gradient(135deg, #0f766e 0%, #2563eb 55%, #7c3aed 100%);
            color: white;
            padding: 28px 30px;
            border-radius: 18px;
            margin-bottom: 22px;
            box-shadow: 0 18px 40px rgba(37, 99, 235, 0.20);
        }
        .assistant-hero h1 {
            margin: 0 0 8px 0;
            font-size: 38px;
            letter-spacing: 0;
        }
        .assistant-hero p {
            margin: 0;
            font-size: 17px;
            opacity: 0.94;
        }
        .metric-strip {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 14px;
            margin-bottom: 20px;
        }
        .study-card {
            border: 1px solid #e5e7eb;
            background: #ffffff;
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06);
        }
        .study-card span {
            display: block;
            color: #64748b;
            font-size: 13px;
            margin-bottom: 6px;
        }
        .study-card strong {
            color: #111827;
            font-size: 24px;
        }
        .answer-box {
            border-left: 5px solid #2563eb;
            background: #f8fafc;
            padding: 18px 20px;
            border-radius: 12px;
            margin-top: 12px;
        }
        .source-pill {
            display: inline-block;
            background: #eef2ff;
            color: #3730a3;
            border-radius: 999px;
            padding: 5px 10px;
            font-size: 12px;
            margin-bottom: 8px;
        }
        .berribot-shell {
            display: grid;
            grid-template-columns: 220px 1fr;
            gap: 20px;
            align-items: center;
            background: radial-gradient(circle at 15% 20%, rgba(45, 212, 191, 0.22), transparent 30%),
                        linear-gradient(135deg, #020617 0%, #111827 48%, #312e81 100%);
            color: white;
            border-radius: 22px;
            padding: 24px;
            margin-bottom: 22px;
            box-shadow: 0 22px 46px rgba(15, 23, 42, 0.28);
        }
        .bot-stage {
            display: grid;
            place-items: center;
            min-height: 170px;
        }
        .bot-head {
            width: 132px;
            height: 104px;
            border-radius: 32px;
            background: linear-gradient(145deg, #f8fafc, #c7d2fe);
            position: relative;
            box-shadow: inset 0 -10px 24px rgba(79, 70, 229, 0.26), 0 20px 38px rgba(14, 165, 233, 0.24);
            animation: botFloat 3.4s ease-in-out infinite;
        }
        .bot-head:before {
            content: "";
            position: absolute;
            top: -28px;
            left: 50%;
            width: 3px;
            height: 28px;
            background: #67e8f9;
            transform: translateX(-50%);
        }
        .bot-head:after {
            content: "";
            position: absolute;
            top: -39px;
            left: 50%;
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background: #22d3ee;
            transform: translateX(-50%);
            box-shadow: 0 0 22px #22d3ee;
        }
        .bot-eye {
            position: absolute;
            top: 38px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #0f172a;
            box-shadow: 0 0 14px rgba(14, 165, 233, 0.85);
        }
        .bot-eye.left { left: 34px; }
        .bot-eye.right { right: 34px; }
        .bot-mouth {
            position: absolute;
            left: 42px;
            bottom: 24px;
            width: 48px;
            height: 8px;
            border-radius: 999px;
            background: #2563eb;
        }
        @keyframes botFloat {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }
        .berribot-shell h2 {
            margin: 0 0 8px 0;
            font-size: 30px;
        }
        .berribot-shell p {
            color: #dbeafe;
            margin: 0 0 14px 0;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_voice_input():
    components.html(
        """
        <div style="font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;">
            <button id="speakQuestion" style="
                width: 100%;
                border: 0;
                border-radius: 12px;
                padding: 12px 14px;
                background: #111827;
                color: white;
                font-weight: 700;
                cursor: pointer;">
                Start voice question
            </button>
            <p id="voiceStatus" style="font-size: 13px; color: #475569; margin: 9px 0 0;">
                Click, speak, and the question box will fill automatically.
            </p>
        </div>
        <script>
        const button = document.getElementById("speakQuestion");
        const status = document.getElementById("voiceStatus");
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

        if (!SpeechRecognition) {
            button.disabled = true;
            button.textContent = "Voice input not supported";
            status.textContent = "Use Chrome for speech recognition.";
        } else {
            const recognition = new SpeechRecognition();
            recognition.lang = "en-US";
            recognition.interimResults = false;
            recognition.continuous = false;

            button.onclick = () => {
                status.textContent = "Listening...";
                recognition.start();
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                status.textContent = "Heard: " + transcript;
                window.top.location.href = "/student_ai_assistant?voice_question=" + encodeURIComponent(transcript);
            };

            recognition.onerror = (event) => {
                status.textContent = "Voice error: " + event.error;
            };

            recognition.onend = () => {
                if (status.textContent === "Listening...") {
                    status.textContent = "Listening stopped. Try again.";
                }
            };
        }
        </script>
        """,
        height=96
    )


def render_voice_player(answer, auto_speak=False):
    safe_answer = json.dumps(answer)
    auto_speak_js = "setTimeout(speakCurrentAnswer, 700);" if auto_speak else ""

    components.html(
        f"""
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
                    font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;">
            <button id="speakAnswer">Speak</button>
            <button id="pauseAnswer">Pause</button>
            <button id="resumeAnswer">Resume</button>
            <button id="stopAnswer">Stop</button>
        </div>
        <style>
        button {{
            border: 1px solid #cbd5e1;
            border-radius: 10px;
            padding: 10px;
            background: white;
            color: #0f172a;
            font-weight: 700;
            cursor: pointer;
        }}
        button:hover {{
            background: #f1f5f9;
        }}
        </style>
        <script>
        const answerText = {safe_answer};
        let utterance = null;

        function speakCurrentAnswer() {{
            window.speechSynthesis.cancel();
            utterance = new SpeechSynthesisUtterance(answerText);
            utterance.rate = 0.92;
            utterance.pitch = 1;
            window.speechSynthesis.speak(utterance);
        }}

        document.getElementById("speakAnswer").onclick = speakCurrentAnswer;

        document.getElementById("pauseAnswer").onclick = () => {{
            window.speechSynthesis.pause();
        }};

        document.getElementById("resumeAnswer").onclick = () => {{
            window.speechSynthesis.resume();
        }};

        document.getElementById("stopAnswer").onclick = () => {{
            window.speechSynthesis.cancel();
        }};

        {auto_speak_js}
        </script>
        """,
        height=58
    )


def render_berribot_agent(
    answer,
    token="",
    source_mode="Universal knowledge",
    material_text=""
):
    safe_answer = json.dumps(answer or "")
    safe_token = json.dumps(token or "")
    safe_base_url = json.dumps(BASE_URL)
    safe_source_mode = json.dumps(source_mode)
    safe_material = json.dumps((material_text or "")[:9000])

    components.html(
        f"""
        <div class="berri-root">
            <div class="robot-button" id="activateBerri">
                <div class="robot-head">
                    <span class="eye eye-left"></span>
                    <span class="eye eye-right"></span>
                    <span class="mouth"></span>
                </div>
            </div>
            <div class="panel">
                <strong>BerriBot Live Voice</strong>
                <p id="berriStatus">Press Listen, ask naturally, then pause. BerriBot will answer aloud automatically.</p>
                <div class="controls">
                    <button id="berriListen">Listen</button>
                    <button id="berriPause">Pause</button>
                    <button id="berriResume">Resume</button>
                    <button id="berriStop">Stop</button>
                </div>
            </div>
        </div>
        <style>
        .berri-root {{
            display: grid;
            grid-template-columns: 150px 1fr;
            gap: 18px;
            align-items: center;
            background: linear-gradient(135deg, #020617, #172554 58%, #0f766e);
            color: white;
            border-radius: 22px;
            padding: 18px;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            box-shadow: 0 18px 38px rgba(15, 23, 42, 0.32);
        }}
        .robot-button {{
            min-height: 132px;
            display: grid;
            place-items: center;
            cursor: pointer;
        }}
        .robot-head {{
            width: 106px;
            height: 88px;
            border-radius: 28px;
            background: linear-gradient(145deg, #f8fafc, #bfdbfe);
            position: relative;
            box-shadow: inset 0 -9px 20px rgba(37, 99, 235, 0.25), 0 0 34px rgba(45, 212, 191, 0.42);
            animation: floatBot 3s ease-in-out infinite;
        }}
        .robot-head:before {{
            content: "";
            position: absolute;
            top: -25px;
            left: 51px;
            width: 3px;
            height: 25px;
            background: #67e8f9;
        }}
        .robot-head:after {{
            content: "";
            position: absolute;
            top: -36px;
            left: 43px;
            width: 18px;
            height: 18px;
            border-radius: 999px;
            background: #22d3ee;
            box-shadow: 0 0 22px #22d3ee;
        }}
        .eye {{
            position: absolute;
            top: 32px;
            width: 17px;
            height: 17px;
            border-radius: 50%;
            background: #0f172a;
            box-shadow: 0 0 14px #38bdf8;
        }}
        .eye-left {{ left: 28px; }}
        .eye-right {{ right: 28px; }}
        .mouth {{
            position: absolute;
            left: 35px;
            bottom: 20px;
            width: 36px;
            height: 7px;
            border-radius: 999px;
            background: #2563eb;
        }}
        @keyframes floatBot {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-8px); }}
        }}
        .panel strong {{
            font-size: 22px;
        }}
        .panel p {{
            color: #dbeafe;
            margin: 8px 0 12px;
        }}
        .controls {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 8px;
        }}
        button {{
            border: 1px solid rgba(255,255,255,0.28);
            border-radius: 11px;
            padding: 10px;
            color: white;
            background: rgba(255,255,255,0.10);
            font-weight: 800;
            cursor: pointer;
        }}
        button:hover {{
            background: rgba(255,255,255,0.18);
        }}
        </style>
        <script>
        let answerText = {safe_answer};
        const apiBaseUrl = {safe_base_url};
        const authToken = {safe_token};
        const sourceMode = {safe_source_mode};
        const materialText = {safe_material};
        const status = document.getElementById("berriStatus");
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let utterance = null;
        let recognition = SpeechRecognition ? new SpeechRecognition() : null;
        let receivedSpeech = false;

        function setStatus(message) {{
            status.textContent = message;
        }}

        function speakText(text) {{
            const cleanText = (text || "").trim();
            if (!cleanText) {{
                setStatus("I could not find an answer for that. Please try again.");
                return;
            }}
            window.speechSynthesis.cancel();
            answerText = cleanText;
            utterance = new SpeechSynthesisUtterance(cleanText);
            utterance.rate = 0.94;
            utterance.pitch = 1.05;
            utterance.onend = () => setStatus("Ready. Press Listen for your next question.");
            utterance.onerror = () => setStatus("Speech playback was blocked. Press Listen and ask again.");
            setStatus("Answering aloud now. Say pause, stop, or resume any time.");
            window.speechSynthesis.speak(utterance);
        }}

        function buildTutorQuestion(transcript) {{
            if (sourceMode === "Uploaded material only" && !materialText.trim()) {{
                return null;
            }}

            if (sourceMode === "Universal knowledge") {{
                return transcript;
            }}

            if (sourceMode === "Uploaded material only") {{
                return `SOURCE MODE: Uploaded material only.
Teach and answer using only the reference material below. If the answer is not present, say that it is not available in the uploaded material.

REFERENCE MATERIAL:
${{materialText}}

STUDENT REQUEST:
${{transcript}}`;
            }}

            return `SOURCE MODE: Uploaded material first, then universal knowledge.
Use the uploaded reference material first. If it is incomplete, clearly say what comes from general knowledge.

REFERENCE MATERIAL:
${{materialText || "No uploaded material has been added yet."}}

STUDENT REQUEST:
${{transcript}}`;
        }}

        async function answerTranscript(transcript) {{
            const tutorQuestion = buildTutorQuestion(transcript);
            if (!tutorQuestion) {{
                speakText("Upload study material first, or switch BerriBot to Universal knowledge mode.");
                return;
            }}

            if (!authToken) {{
                speakText("Please log in again so I can answer through the tutor system.");
                return;
            }}

            setStatus("Thinking about: " + transcript);

            try {{
                const response = await fetch(apiBaseUrl + "/ai_tutor", {{
                    method: "POST",
                    headers: {{
                        "Authorization": "Bearer " + authToken,
                        "Content-Type": "application/json"
                    }},
                    body: JSON.stringify({{
                        question: tutorQuestion,
                        subject: "General",
                        difficulty: "medium",
                        task: "answer"
                    }})
                }});

                if (!response.ok) {{
                    throw new Error("Tutor request failed");
                }}

                const data = await response.json();
                speakText(data.answer || "I could not generate an answer for that.");
            }} catch (error) {{
                speakText("I heard you, but I could not reach the tutor service. Please try again.");
            }}
        }}

        function handleVoiceCommand(transcript) {{
            const command = transcript.trim().toLowerCase();
            if (["pause", "stop", "wait", "hold on"].includes(command)) {{
                window.speechSynthesis.pause();
                setStatus("Paused by voice command. Say resume to continue.");
                return true;
            }}
            if (["resume", "continue", "keep going"].includes(command)) {{
                window.speechSynthesis.resume();
                setStatus("Resumed by voice command.");
                return true;
            }}
            if (["cancel", "silence", "be quiet"].includes(command)) {{
                window.speechSynthesis.cancel();
                setStatus("Stopped by voice command.");
                return true;
            }}
            return false;
        }}

        function startListening() {{
            if (!recognition) {{
                setStatus("Voice recognition needs Chrome.");
                return;
            }}
            if (window.speechSynthesis.speaking) {{
                window.speechSynthesis.cancel();
                setStatus("Interrupted. Listening to your new question...");
            }} else {{
                setStatus("Listening...");
            }}
            receivedSpeech = false;
            try {{
                recognition.start();
            }} catch (error) {{
                setStatus("Already listening. Speak now.");
            }}
        }}

        if (recognition) {{
            recognition.lang = "en-US";
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.onresult = (event) => {{
                receivedSpeech = true;
                const transcript = event.results[0][0].transcript;
                if (handleVoiceCommand(transcript)) {{
                    return;
                }}
                answerTranscript(transcript);
            }};
            recognition.onerror = (event) => {{
                setStatus("Voice error: " + event.error);
            }};
            recognition.onend = () => {{
                if (!receivedSpeech && status.textContent === "Listening...") {{
                    setStatus("I did not hear a full question. Press Listen and try again.");
                }}
            }};
        }}

        document.getElementById("activateBerri").onclick = startListening;
        document.getElementById("berriListen").onclick = startListening;
        document.getElementById("berriPause").onclick = () => {{
            window.speechSynthesis.pause();
            setStatus("Paused. Press Resume or say resume.");
        }};
        document.getElementById("berriResume").onclick = () => {{
            window.speechSynthesis.resume();
            setStatus("Resumed.");
        }};
        document.getElementById("berriStop").onclick = () => {{
            window.speechSynthesis.cancel();
            setStatus("Stopped. Press Listen for a new question.");
        }};
        </script>
        """,
        height=238
    )


def ask_tutor(question, subject, difficulty, task):
    return ask_ai_tutor(
        question,
        subject,
        difficulty,
        st.session_state.token,
        task=task
    )


def build_berribot_question(user_question, source_mode, material_text):
    material_text = (material_text or "").strip()

    if source_mode == "Uploaded material only" and not material_text:
        return None

    if source_mode == "Universal knowledge":
        return user_question

    if source_mode == "Uploaded material only":
        return f"""
SOURCE MODE: Uploaded material only.
Teach and answer using only the reference material below. If the answer is not present, say that it is not available in the uploaded material.

REFERENCE MATERIAL:
{material_text[:9000]}

STUDENT REQUEST:
{user_question}
"""

    return f"""
SOURCE MODE: Uploaded material first, then universal knowledge.
Use the uploaded reference material first. If it is incomplete, clearly say what comes from general knowledge.

REFERENCE MATERIAL:
{material_text[:9000] if material_text else "No uploaded material has been added yet."}

STUDENT REQUEST:
{user_question}
"""


require_student()
show_sidebar()
render_styles()


voice_question = st.query_params.get(
    "voice_question",
    ""
)

if isinstance(voice_question, list):
    voice_question = voice_question[0] if voice_question else ""

if "tutor_messages" not in st.session_state:
    st.session_state.tutor_messages = []

if "current_answer" not in st.session_state:
    st.session_state.current_answer = ""

if "last_voice_question_processed" not in st.session_state:
    st.session_state.last_voice_question_processed = ""

if "auto_speak_answer" not in st.session_state:
    st.session_state.auto_speak_answer = False

if "berribot_material_text" not in st.session_state:
    st.session_state.berribot_material_text = ""

if "berribot_material_name" not in st.session_state:
    st.session_state.berribot_material_name = "No material uploaded"

if "berribot_source_mode" not in st.session_state:
    st.session_state.berribot_source_mode = "Universal knowledge"


if (
    voice_question.strip()
    and voice_question != st.session_state.last_voice_question_processed
):
    with st.spinner(
        "BerriBot heard you. Answering now..."
    ):
        berribot_question = build_berribot_question(
            voice_question,
            st.session_state.berribot_source_mode,
            st.session_state.berribot_material_text
        )

        if berribot_question is None:
            result = {
                "answer": "Upload study material first, or switch BerriBot to Universal knowledge mode.",
                "source": "material_required"
            }
        else:
            result = ask_tutor(
                berribot_question,
                "General",
                "medium",
                "answer"
            )

    answer = result.get(
        "answer",
        ""
    )

    st.session_state.current_answer = answer
    st.session_state.last_voice_question_processed = voice_question
    st.session_state.auto_speak_answer = True
    st.session_state.tutor_messages.append(
        {
            "question": voice_question,
            "answer": answer,
            "source": result.get(
                "source",
                "unknown"
            ),
            "task": "voice_answer"
        }
    )


st.markdown(
    """
    <div class="assistant-hero">
        <h1>AI Study Assistant</h1>
        <p>Ask questions, speak to the tutor, summarize notes, find weak topics, and generate a focused improvement plan.</p>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown(
    f"""
    <div class="metric-strip">
        <div class="study-card"><span>Questions Asked</span><strong>{len(st.session_state.tutor_messages)}</strong></div>
        <div class="study-card"><span>Voice Mode</span><strong>Ready</strong></div>
        <div class="study-card"><span>Tutor Mode</span><strong>Answer First</strong></div>
    </div>
    """,
    unsafe_allow_html=True
)

render_berribot_agent(
    st.session_state.current_answer,
    token=st.session_state.token,
    source_mode=st.session_state.berribot_source_mode,
    material_text=st.session_state.berribot_material_text
)


ask_tab, teach_tab, tools_tab, history_tab = st.tabs(
    [
        "Ask Tutor",
        "TeachMeBerriBot",
        "Study Tools",
        "Session History"
    ]
)


with ask_tab:
    source_mode = st.radio(
        "BerriBot knowledge source",
        [
            "Universal knowledge",
            "Uploaded material first",
            "Uploaded material only"
        ],
        horizontal=True,
        index=[
            "Universal knowledge",
            "Uploaded material first",
            "Uploaded material only"
        ].index(st.session_state.berribot_source_mode)
    )
    st.session_state.berribot_source_mode = source_mode

    question = st.text_area(
        "Ask anything",
        value=voice_question,
        height=160,
        placeholder="Type here if you do not want to use voice. Or press Listen on BerriBot above and speak."
    )

    speak_typed_answer = st.checkbox(
        "Speak the answer aloud",
        value=False
    )

    ask_button = st.button(
        "Ask BerriBot",
        use_container_width=True,
        type="primary"
    )

    if ask_button:
        if not question.strip():
            st.warning(
                "Enter or speak a question first."
            )
        else:
            berribot_question = build_berribot_question(
                question,
                st.session_state.berribot_source_mode,
                st.session_state.berribot_material_text
            )

            if berribot_question is None:
                st.warning(
                    "Upload material first, or switch to Universal knowledge."
                )
                st.stop()

            with st.spinner(
                "Thinking..."
            ):
                result = ask_tutor(
                    berribot_question,
                    "General",
                    "medium",
                    "answer"
                )

            answer = result.get(
                "answer",
                ""
            )

            st.session_state.current_answer = answer
            st.session_state.auto_speak_answer = speak_typed_answer
            st.session_state.tutor_messages.append(
                {
                    "question": question,
                    "answer": answer,
                    "source": result.get(
                        "source",
                        "unknown"
                    ),
                    "task": "answer"
                }
            )

    if st.session_state.current_answer:
        st.markdown(
            '<div class="answer-box">',
            unsafe_allow_html=True
        )
        st.markdown(
            '<span class="source-pill">Latest tutor answer</span>',
            unsafe_allow_html=True
        )
        st.write(
            st.session_state.current_answer
        )
        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )
        render_voice_player(
            st.session_state.current_answer,
            auto_speak=st.session_state.auto_speak_answer
        )
        st.session_state.auto_speak_answer = False


with teach_tab:
    st.subheader("TeachMeBerriBot")
    st.caption(
        "Upload notes, PDFs, scans, DOCX, TXT, CSV, or images. Then choose whether BerriBot should teach from universal knowledge or only from your uploaded material."
    )

    upload_col, teach_col = st.columns([1, 1.15])

    with upload_col:
        uploaded_material = st.file_uploader(
            "Upload teaching material",
            type=["pdf", "txt", "docx", "csv", "xlsx", "png", "jpg", "jpeg", "webp"]
        )

        if uploaded_material:
            with st.spinner("Reading uploaded material..."):
                extracted_material = extract_text_from_file(uploaded_material)

            if extracted_material:
                st.session_state.berribot_material_text = extracted_material
                st.session_state.berribot_material_name = uploaded_material.name
                st.success(f"Material loaded: {uploaded_material.name}")
            else:
                st.warning("I could not extract readable text from this file.")

        st.caption(extraction_note())

        current_material = st.text_area(
            "Current reference material",
            value=st.session_state.berribot_material_text,
            height=220,
            placeholder="Upload a file or paste material here."
        )
        st.session_state.berribot_material_text = current_material

    with teach_col:
        teach_source_mode = st.radio(
            "Teaching source",
            [
                "Universal knowledge",
                "Uploaded material first",
                "Uploaded material only"
            ],
            horizontal=True,
            key="teach_source_mode",
            index=[
                "Universal knowledge",
                "Uploaded material first",
                "Uploaded material only"
            ].index(st.session_state.berribot_source_mode)
        )
        st.session_state.berribot_source_mode = teach_source_mode

        teach_topic = st.text_input(
            "What should BerriBot teach?",
            placeholder="Example: teach me normalization, stacks, calculus limits, OS scheduling"
        )

        teaching_style = st.selectbox(
            "Teaching style",
            [
                "Beginner friendly",
                "Exam focused",
                "Step by step",
                "Interview style",
                "Quick revision"
            ]
        )

        lesson_depth = st.selectbox(
            "Lesson depth",
            [
                "Short",
                "Detailed",
                "Deep explanation"
            ],
            index=1
        )

        if st.button("TeachMeBerriBot", type="primary", use_container_width=True):
            if not teach_topic.strip():
                st.warning("Tell BerriBot what topic to teach.")
            else:
                lesson_request = f"""
Teach this topic to me like a live tutor: {teach_topic}
Teaching style: {teaching_style}
Lesson depth: {lesson_depth}

Return:
1. Direct concept explanation
2. Why it matters
3. Step-by-step understanding
4. Example
5. Common mistakes
6. Mini practice question
"""
                berribot_question = build_berribot_question(
                    lesson_request,
                    st.session_state.berribot_source_mode,
                    st.session_state.berribot_material_text
                )

                if berribot_question is None:
                    st.warning(
                        "Upload material first, or switch to Universal knowledge."
                    )
                else:
                    with st.spinner("BerriBot is preparing the lesson..."):
                        result = ask_tutor(
                            berribot_question,
                            "TeachMeBerriBot",
                            "medium",
                            "teach"
                        )

                    output = result.get("answer", "")
                    st.session_state.current_answer = output
                    st.session_state.auto_speak_answer = True
                    st.session_state.tutor_messages.append(
                        {
                            "question": teach_topic,
                            "answer": output,
                            "source": result.get("source", "unknown"),
                            "task": "teach"
                        }
                    )

        if st.session_state.current_answer:
            st.markdown('<div class="answer-box">', unsafe_allow_html=True)
            st.markdown(
                f'<span class="source-pill">Teaching from: {st.session_state.berribot_source_mode} | {st.session_state.berribot_material_name}</span>',
                unsafe_allow_html=True
            )
            st.write(st.session_state.current_answer)
            st.markdown("</div>", unsafe_allow_html=True)
            render_voice_player(
                st.session_state.current_answer,
                auto_speak=st.session_state.auto_speak_answer
            )
            st.session_state.auto_speak_answer = False


with tools_tab:
    tool_text = st.text_area(
        "Paste notes, an answer, or a topic",
        value=st.session_state.current_answer,
        height=170,
        placeholder="Paste study material here, then choose a tool."
    )

    tool_subject = st.text_input(
        "Tool subject",
        value="General"
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        summarize_button = st.button(
            "Summarize",
            use_container_width=True
        )

    with col2:
        weak_button = st.button(
            "My Topics That Need Improvement",
            use_container_width=True
        )

    with col3:
        improve_button = st.button(
            "Improvement Generator",
            use_container_width=True
        )

    selected_task = None

    if summarize_button:
        selected_task = "summarize"
    elif weak_button:
        selected_task = "weak_topics"
    elif improve_button:
        selected_task = "improvement"

    if selected_task:
        if not tool_text.strip():
            st.warning(
                "Add some notes, a topic, or an answer first."
            )
        else:
            with st.spinner(
                "Building your study output..."
            ):
                result = ask_tutor(
                    tool_text,
                    tool_subject,
                    "medium",
                    selected_task
                )

            output = result.get(
                "answer",
                ""
            )

            st.session_state.current_answer = output
            st.session_state.tutor_messages.append(
                {
                    "question": tool_text,
                    "answer": output,
                    "source": result.get(
                        "source",
                        "unknown"
                    ),
                    "task": selected_task
                }
            )

            st.markdown(
                '<div class="answer-box">',
                unsafe_allow_html=True
            )
            st.write(
                output
            )
            st.markdown(
                "</div>",
                unsafe_allow_html=True
            )
            render_voice_player(
                output
            )


with history_tab:
    if st.button(
        "Clear Session",
        use_container_width=True
    ):
        st.session_state.tutor_messages = []
        st.session_state.current_answer = ""
        st.rerun()

    if not st.session_state.tutor_messages:
        st.info(
            "No tutor messages yet."
        )
    else:
        for message in reversed(
            st.session_state.tutor_messages
        ):
            with st.container(
                border=True
            ):
                st.caption(
                    f"Task: {message.get('task', 'answer')} | Source: {message.get('source', 'unknown')}"
                )
                st.write(
                    message["question"]
                )
                st.divider()
                st.write(
                    message["answer"]
                )
