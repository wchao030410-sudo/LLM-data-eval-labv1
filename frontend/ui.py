import streamlit as st


def apply_base_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap');

        :root {
            --bg-top: #f7f1e7;
            --bg-bottom: #eef3f8;
            --ink: #102033;
            --ink-soft: #526174;
            --line: rgba(16, 32, 51, 0.10);
            --panel: rgba(255, 255, 255, 0.82);
            --panel-strong: rgba(255, 255, 255, 0.96);
            --accent: #14532d;
            --accent-2: #b45309;
            --accent-3: #1d4ed8;
        }

        html, body, [class*="css"]  {
            font-family: "Noto Sans SC", sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 8% 0%, rgba(180, 83, 9, 0.12), transparent 22%),
                radial-gradient(circle at 92% 0%, rgba(29, 78, 216, 0.12), transparent 24%),
                linear-gradient(180deg, var(--bg-top) 0%, var(--bg-bottom) 100%);
        }

        .block-container {
            max-width: 1380px;
            padding-top: 1.2rem;
            padding-bottom: 2.8rem;
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, rgba(59, 130, 246, 0.18), transparent 28%),
                linear-gradient(180deg, #0f172a 0%, #172554 52%, #1e293b 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        [data-testid="stSidebar"] * {
            color: #f8fafc;
        }

        .lab-hero {
            position: relative;
            overflow: hidden;
            padding: 1.65rem 1.7rem;
            border-radius: 26px;
            background:
                radial-gradient(circle at 85% 15%, rgba(245, 158, 11, 0.24), transparent 18%),
                linear-gradient(135deg, #0f172a 0%, #172554 48%, #1d4ed8 100%);
            color: #f8fafc;
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 24px 54px rgba(15, 23, 42, 0.18);
            margin-bottom: 1.15rem;
        }
        .lab-hero::after {
            content: "";
            position: absolute;
            right: -40px;
            top: -50px;
            width: 220px;
            height: 220px;
            border-radius: 999px;
            background: rgba(255,255,255,0.06);
            filter: blur(2px);
        }
        .lab-hero h1, .lab-hero h2, .lab-hero h3, .lab-hero p {
            color: #f8fafc;
            margin: 0;
        }
        .lab-kicker {
            display: inline-block;
            font-family: "Space Grotesk", sans-serif;
            font-size: 0.78rem;
            color: #dbeafe;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            margin-bottom: 0.55rem;
            padding: 0.22rem 0.5rem;
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 999px;
            background: rgba(255,255,255,0.05);
        }

        .lab-card {
            position: relative;
            overflow: hidden;
            background: linear-gradient(180deg, var(--panel-strong) 0%, rgba(255,255,255,0.86) 100%);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 1rem 1rem 1.05rem 1rem;
            min-height: 132px;
            box-shadow: 0 16px 34px rgba(15, 23, 42, 0.07);
        }
        .lab-card::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--accent-2), var(--accent-3), var(--accent));
        }
        .lab-card-title {
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--ink-soft);
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.65rem;
        }
        .lab-card-value {
            font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
            font-size: 1.9rem;
            font-weight: 700;
            color: var(--ink);
            line-height: 1.1;
        }
        .lab-card-desc {
            font-size: 0.92rem;
            color: var(--ink-soft);
            margin-top: 0.45rem;
            line-height: 1.6;
        }

        .lab-section-title {
            margin: 0.18rem 0 0.72rem 0;
            font-size: 1.02rem;
            font-weight: 800;
            color: var(--ink);
        }

        .stAlert, .stCodeBlock, .stDataFrame, .stPlotlyChart {
            border-radius: 18px;
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.88) 100%);
            border: 1px solid var(--line);
            border-radius: 18px;
            padding: 0.8rem 0.95rem;
            box-shadow: 0 12px 28px rgba(15, 23, 42, 0.06);
        }

        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            border-radius: 14px !important;
            border: 1px solid rgba(29, 78, 216, 0.12) !important;
            background: linear-gradient(180deg, #ffffff 0%, #eef4ff 100%) !important;
            color: var(--ink) !important;
            font-weight: 700 !important;
            box-shadow: 0 10px 20px rgba(29, 78, 216, 0.08);
        }

        .stSelectbox > div > div,
        .stTextInput > div > div > input,
        .stTextArea textarea {
            border-radius: 14px !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.35rem;
        }
        .stTabs [data-baseweb="tab"] {
            height: 42px;
            background: rgba(255,255,255,0.65);
            border: 1px solid var(--line);
            border-radius: 12px 12px 0 0;
            padding: 0 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, kicker: str = "LLM Data Eval Lab") -> None:
    st.markdown(
        """
        <div class="lab-hero">
            <div class="lab-kicker">{kicker}</div>
            <h2 style="font-size:2rem;font-weight:800;line-height:1.2;">{title}</h2>
            <p style="margin-top:0.7rem;font-size:1rem;opacity:0.94;max-width:760px;line-height:1.75;">{subtitle}</p>
        </div>
        """.format(kicker=kicker, title=title, subtitle=subtitle),
        unsafe_allow_html=True,
    )


def panel_title(title: str) -> None:
    st.markdown('<div class="lab-section-title">{}</div>'.format(title), unsafe_allow_html=True)


def info_card(title: str, value: str, desc: str) -> None:
    st.markdown(
        """
        <div class="lab-card">
            <div class="lab-card-title">{title}</div>
            <div class="lab-card-value">{value}</div>
            <div class="lab-card-desc">{desc}</div>
        </div>
        """.format(title=title, value=value, desc=desc),
        unsafe_allow_html=True,
    )
