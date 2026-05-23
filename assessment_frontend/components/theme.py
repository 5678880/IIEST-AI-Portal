import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --ink: #0f172a;
            --muted: #64748b;
            --line: #e2e8f0;
            --panel: rgba(255, 255, 255, 0.92);
            --blue: #2563eb;
            --teal: #0f766e;
            --violet: #6d28d9;
            --iiest-purple: #3c348d;
            --iiest-gold: #e7bd24;
        }
        .stApp {
            background:
                radial-gradient(circle at 12% 8%, rgba(60, 52, 141, 0.14), transparent 28%),
                radial-gradient(circle at 88% 8%, rgba(231, 189, 36, 0.12), transparent 28%),
                radial-gradient(circle at 50% 100%, rgba(37, 99, 235, 0.08), transparent 35%),
                #f8fafc;
            color: var(--ink);
        }
        .stApp:before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.18) 40%, transparent 70%);
            animation: surfaceSheen 9s ease-in-out infinite;
            z-index: 0;
        }
        @keyframes surfaceSheen {
            0%, 100% { opacity: 0; transform: translateX(-12%); }
            45% { opacity: 0.72; }
            60% { opacity: 0; transform: translateX(12%); }
        }
        .main .block-container {
            max-width: 1280px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020617 0%, #0f172a 52%, #172554 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }
        section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
            display: none;
        }
        section[data-testid="stSidebar"] * {
            color: #e5e7eb;
        }
        section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: #cbd5e1;
        }
        section[data-testid="stSidebar"] a {
            border-radius: 12px;
            color: #e5e7eb;
            transition: transform 160ms ease, background 160ms ease, box-shadow 160ms ease;
        }
        section[data-testid="stSidebar"] a:hover {
            background: rgba(255,255,255,0.12);
            box-shadow: 0 10px 22px rgba(15, 23, 42, 0.22);
            transform: translateX(4px);
        }
        div[data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 16px 34px rgba(15, 23, 42, 0.07);
            transition: transform 180ms ease, box-shadow 180ms ease;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 22px 42px rgba(15, 23, 42, 0.11);
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 18px;
            border-color: var(--line);
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
        }
        .premium-hero {
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, #0f172a, var(--iiest-purple) 45%, #0f766e);
            color: white;
            padding: 30px;
            border-radius: 24px;
            margin-bottom: 22px;
            box-shadow: 0 22px 48px rgba(15, 23, 42, 0.22);
        }
        .premium-hero:after {
            content: "";
            position: absolute;
            width: 280px;
            height: 280px;
            border-radius: 999px;
            right: -80px;
            top: -120px;
            background: radial-gradient(circle, rgba(231,189,36,0.34), transparent 66%);
            animation: heroPulse 4.8s ease-in-out infinite;
        }
        @keyframes heroPulse {
            0%, 100% { transform: scale(1); opacity: 0.62; }
            50% { transform: scale(1.08); opacity: 0.9; }
        }
        .hero-brand {
            display: flex;
            gap: 18px;
            align-items: center;
            position: relative;
            z-index: 1;
        }
        .hero-logo {
            width: 82px;
            min-width: 82px;
            height: 82px;
            border-radius: 20px;
            background: rgba(255,255,255,0.12);
            display: grid;
            place-items: center;
            border: 1px solid rgba(255,255,255,0.18);
            box-shadow: inset 0 0 18px rgba(255,255,255,0.08);
        }
        .premium-hero h1 {
            margin: 0 0 8px 0;
            font-size: 38px;
            letter-spacing: 0;
        }
        .premium-hero p {
            margin: 0;
            max-width: 920px;
            color: #dbeafe;
            font-size: 16px;
        }
        .ai-card {
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 18px;
            box-shadow: 0 16px 34px rgba(15, 23, 42, 0.07);
            min-height: 150px;
            transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
        }
        .ai-card:hover {
            transform: translateY(-5px);
            border-color: rgba(60,52,141,0.34);
            box-shadow: 0 24px 46px rgba(15, 23, 42, 0.13);
        }
        .ai-card h3 {
            margin: 0 0 8px 0;
            color: var(--ink);
        }
        .ai-card p {
            color: var(--muted);
            margin: 0;
        }
        .pill {
            display: inline-block;
            background: linear-gradient(135deg, #eef2ff, #fff7d6);
            color: #3730a3;
            padding: 5px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            margin-bottom: 8px;
        }
        .stButton > button, .stDownloadButton > button {
            border-radius: 12px;
            border: 1px solid rgba(60, 52, 141, 0.22);
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            transform: translateY(-2px);
            border-color: var(--iiest-gold);
            box-shadow: 0 14px 28px rgba(60, 52, 141, 0.16);
        }
        input, textarea, select {
            border-radius: 12px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def iiest_logo_svg(size=64):
    return f"""
    <svg width="{size}" height="{size}" viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg" aria-label="IIEST Shibpur inspired crest">
        <path d="M19 105C24 74 40 49 64 31C88 49 104 74 109 105" stroke="#e7bd24" stroke-width="10" stroke-linecap="round" stroke-dasharray="10 10"/>
        <path d="M36 43L64 14L92 43H82V105H72V69C72 58 56 58 56 69V105H46V43H36Z" fill="#3c348d"/>
        <circle cx="64" cy="43" r="11" fill="#f8fafc"/>
        <path d="M25 111H103" stroke="#3c348d" stroke-width="8" stroke-linecap="round"/>
        <text x="64" y="124" text-anchor="middle" font-size="12" font-family="Arial, sans-serif" font-weight="800" fill="#3c348d">IIEST</text>
    </svg>
    """


def hero(title, subtitle):
    st.markdown(
        f"""
        <div class="premium-hero">
            <div class="hero-brand">
                <div class="hero-logo">{iiest_logo_svg(66)}</div>
                <div>
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def ai_feature_grid(features):
    columns = st.columns(3)

    for index, feature in enumerate(features):
        with columns[index % 3]:
            st.markdown(
                f"""
                <div class="ai-card">
                    <span class="pill">AI teacher support</span>
                    <h3>{feature["title"]}</h3>
                    <p>{feature["body"]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
