from __future__ import annotations

from html import escape
from typing import Any

import streamlit as st


def _safe(value: Any) -> str:
    return escape("" if value is None else str(value)).replace("\n", "<br />")


def apply_base_style() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Saira+Semi+Condensed:wght@500;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;700;800&display=swap');

        :root {
            --bg-0: #04101d;
            --bg-1: #0a1830;
            --bg-2: #11294a;
            --panel: rgba(10, 20, 35, 0.82);
            --panel-strong: rgba(9, 18, 31, 0.94);
            --panel-soft: rgba(17, 31, 51, 0.76);
            --line: rgba(140, 179, 255, 0.18);
            --line-strong: rgba(140, 179, 255, 0.32);
            --ink: #eef6ff;
            --ink-soft: #8ea8c6;
            --cyan: #72e3ff;
            --cobalt: #5f7cff;
            --emerald: #62f2c2;
            --amber: #ffc977;
            --rose: #ff7ea7;
            --shadow: 0 22px 60px rgba(0, 6, 18, 0.42);
        }

        html, body {
            font-family: "Noto Sans SC", sans-serif;
            color: var(--ink);
        }

        body {
            background: linear-gradient(180deg, var(--bg-0) 0%, #071527 36%, #0d1f37 100%);
        }

        .stApp {
            color: var(--ink);
            background:
                radial-gradient(circle at 18% 0%, rgba(95, 124, 255, 0.16), transparent 26%),
                radial-gradient(circle at 88% 16%, rgba(114, 227, 255, 0.14), transparent 22%),
                radial-gradient(circle at 50% 100%, rgba(98, 242, 194, 0.08), transparent 30%),
                linear-gradient(180deg, var(--bg-0) 0%, #071527 36%, #0d1f37 100%);
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        .block-container {
            max-width: 1440px;
            padding-top: 1.1rem;
            padding-bottom: 3rem;
        }

        [data-testid="stSidebar"] {
            background:
                radial-gradient(circle at top left, rgba(95, 124, 255, 0.18), transparent 30%),
                linear-gradient(180deg, rgba(4, 10, 18, 0.96) 0%, rgba(7, 18, 32, 0.95) 52%, rgba(10, 24, 42, 0.92) 100%);
            border-right: 1px solid rgba(136, 174, 255, 0.16);
        }

        [data-testid="stSidebar"] * {
            color: #f3f8ff;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 0.3rem;
        }

        [data-testid="stSidebarNav"] a {
            margin-bottom: 0.42rem;
            padding: 0.58rem 0.72rem;
            border-radius: 16px;
            border: 1px solid transparent;
            background: rgba(14, 28, 47, 0.58);
            transition: transform 0.18s ease, background 0.18s ease, border-color 0.18s ease;
        }

        [data-testid="stSidebarNav"] a:hover {
            transform: translateX(2px);
            background: rgba(20, 40, 68, 0.78);
            border-color: rgba(114, 227, 255, 0.24);
        }

        [data-testid="stSidebarNav"] a[aria-current="page"] {
            background: linear-gradient(135deg, rgba(95, 124, 255, 0.26), rgba(114, 227, 255, 0.16));
            border-color: rgba(114, 227, 255, 0.30);
            box-shadow: 0 16px 32px rgba(0, 10, 30, 0.34);
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            color: var(--ink);
            letter-spacing: 0.01em;
        }

        p, li, label, .stCaption {
            color: #d9e7fb;
        }

        code, pre {
            font-family: "IBM Plex Mono", monospace !important;
        }

        .stButton > button,
        .stDownloadButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            height: 2.9rem;
            border-radius: 16px !important;
            border: 1px solid rgba(166, 208, 255, 0.34) !important;
            background: linear-gradient(135deg, rgba(95, 124, 255, 0.96), rgba(114, 227, 255, 0.86)) !important;
            color: #06111c !important;
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: 0.05em;
            box-shadow: 0 16px 34px rgba(22, 65, 173, 0.30);
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            border-color: rgba(200, 233, 255, 0.44) !important;
            transform: translateY(-1px);
        }

        .stSelectbox label, .stMultiSelect label, .stTextInput label, .stSlider label, .stFileUploader label {
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            font-size: 0.84rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: #a9c7eb;
        }

        .stSelectbox [data-baseweb="select"] > div,
        .stMultiSelect [data-baseweb="select"] > div,
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        div[data-baseweb="base-input"] > div,
        div[data-baseweb="base-input"] input {
            min-height: 48px;
            background: rgba(7, 15, 27, 0.86) !important;
            color: var(--ink) !important;
            border: 1px solid rgba(140, 179, 255, 0.16) !important;
            border-radius: 16px !important;
        }

        div[data-baseweb="tag"] {
            background: rgba(15, 39, 71, 0.88) !important;
            border-radius: 999px !important;
            border: 1px solid rgba(114, 227, 255, 0.22) !important;
        }

        .stSlider [data-baseweb="slider"] > div > div {
            background: rgba(95, 124, 255, 0.62);
        }

        .stAlert,
        div[data-testid="stCodeBlock"],
        div[data-testid="stDataFrame"],
        .stPlotlyChart,
        div[data-testid="stExpander"],
        div[data-testid="stForm"] {
            border: 1px solid var(--line);
            border-radius: 24px;
            background: var(--panel);
            box-shadow: var(--shadow);
        }

        div[data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid var(--line-strong);
            background:
                linear-gradient(180deg, rgba(11, 22, 37, 0.94), rgba(8, 16, 28, 0.92));
        }

        div[data-testid="stDataFrame"] > div,
        div[data-testid="stDataFrame"] section,
        div[data-testid="stDataFrame"] [data-testid="stElementToolbar"] {
            background: transparent !important;
        }

        div[data-testid="stDataFrame"] canvas {
            border-radius: 18px;
        }

        div[data-testid="stTable"] {
            overflow: hidden;
            border: 1px solid var(--line-strong);
            border-radius: 22px;
            background:
                linear-gradient(180deg, rgba(11, 22, 37, 0.94), rgba(8, 16, 28, 0.92));
            box-shadow: var(--shadow);
        }

        div[data-testid="stTable"] table {
            background: transparent;
        }

        div[data-testid="stTable"] th {
            background: rgba(17, 43, 72, 0.96);
            color: #ecf6ff;
            border-bottom: 1px solid rgba(140, 179, 255, 0.16);
        }

        div[data-testid="stTable"] td {
            background: rgba(8, 17, 30, 0.82);
            color: #d7e9fb;
            border-bottom: 1px solid rgba(140, 179, 255, 0.08);
        }

        div[data-testid="stForm"] {
            padding: 1.15rem 1rem 0.95rem;
            background:
                linear-gradient(180deg, rgba(12, 23, 40, 0.92), rgba(11, 20, 34, 0.86));
        }

        .stAlert {
            background: rgba(12, 22, 37, 0.88) !important;
        }

        div[data-testid="stMetric"] {
            padding: 0.88rem 0.96rem;
            border-radius: 20px;
            border: 1px solid var(--line);
            background: linear-gradient(180deg, rgba(13, 24, 40, 0.95), rgba(9, 17, 28, 0.88));
            box-shadow: 0 20px 42px rgba(0, 8, 20, 0.28);
        }

        div[data-testid="stMetric"] label {
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            font-size: 0.78rem;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: #9fc4ea;
        }

        div[data-testid="stMetricValue"] {
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            color: #f5fbff;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 0.52rem;
            margin-bottom: 0.2rem;
        }

        .stTabs [data-baseweb="tab"] {
            height: 44px;
            padding: 0 1rem;
            border-radius: 14px;
            background: rgba(10, 19, 33, 0.78);
            border: 1px solid rgba(140, 179, 255, 0.14);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(95, 124, 255, 0.26), rgba(114, 227, 255, 0.16));
            border-color: rgba(114, 227, 255, 0.26);
        }

        [data-testid="stCodeBlock"] pre,
        [data-testid="stCodeBlock"] code {
            color: #d8eaff !important;
        }

        .hud-hero {
            position: relative;
            overflow: hidden;
            padding: 1.55rem 1.6rem;
            border-radius: 30px;
            border: 1px solid rgba(140, 179, 255, 0.16);
            background:
                radial-gradient(circle at 84% 16%, rgba(114, 227, 255, 0.24), transparent 18%),
                radial-gradient(circle at 12% 0%, rgba(98, 242, 194, 0.14), transparent 20%),
                linear-gradient(135deg, rgba(4, 10, 18, 0.96) 0%, rgba(8, 24, 44, 0.94) 42%, rgba(17, 41, 74, 0.94) 100%);
            box-shadow: var(--shadow);
            margin-bottom: 1rem;
        }

        .hud-hero::before {
            content: "";
            position: absolute;
            inset: 0;
            background:
                linear-gradient(90deg, transparent 0%, rgba(114, 227, 255, 0.10) 49%, transparent 100%);
            opacity: 0.35;
            pointer-events: none;
        }

        .hud-hero-grid {
            position: relative;
            z-index: 1;
            display: grid;
            grid-template-columns: minmax(0, 1.6fr) minmax(240px, 0.8fr);
            gap: 1.2rem;
            align-items: center;
        }

        .hud-kicker {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.34rem 0.68rem;
            border-radius: 999px;
            border: 1px solid rgba(114, 227, 255, 0.22);
            background: rgba(9, 24, 42, 0.62);
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.14em;
            color: #9cd5ff;
        }

        .hud-kicker::before {
            content: "";
            width: 8px;
            height: 8px;
            border-radius: 999px;
            background: var(--cyan);
            box-shadow: 0 0 14px rgba(114, 227, 255, 0.78);
        }

        .hud-hero h1,
        .hud-hero h2 {
            margin: 0.8rem 0 0 0;
            font-size: clamp(2rem, 2.7vw, 3rem);
            line-height: 1.06;
            color: #f5fbff;
        }

        .hud-hero p {
            margin: 0.8rem 0 0 0;
            max-width: 760px;
            font-size: 1rem;
            line-height: 1.8;
            color: #d7e7fb;
        }

        .hud-chip-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 1rem;
        }

        .hud-chip {
            padding: 0.36rem 0.66rem;
            border-radius: 999px;
            background: rgba(10, 22, 37, 0.72);
            border: 1px solid rgba(140, 179, 255, 0.16);
            color: #c8def7;
            font-size: 0.84rem;
        }

        .hud-hero-side {
            position: relative;
            min-height: 180px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .hud-orbit {
            position: absolute;
            width: 180px;
            height: 180px;
            border-radius: 999px;
            border: 1px solid rgba(114, 227, 255, 0.24);
            box-shadow: inset 0 0 0 18px rgba(114, 227, 255, 0.04);
        }

        .hud-orbit::before,
        .hud-orbit::after {
            content: "";
            position: absolute;
            border-radius: 999px;
        }

        .hud-orbit::before {
            inset: 18px;
            border: 1px solid rgba(98, 242, 194, 0.18);
        }

        .hud-orbit::after {
            top: 18px;
            right: 36px;
            width: 18px;
            height: 18px;
            background: rgba(114, 227, 255, 0.88);
            box-shadow: 0 0 22px rgba(114, 227, 255, 0.68);
        }

        .hud-hero-panel {
            position: absolute;
            right: 0;
            bottom: 10px;
            padding: 1rem 1rem 0.95rem;
            width: min(100%, 250px);
            border-radius: 22px;
            border: 1px solid rgba(140, 179, 255, 0.16);
            background: rgba(8, 18, 31, 0.74);
        }

        .hud-hero-panel-label,
        .hud-section-eyebrow,
        .hud-feature-eyebrow,
        .hud-text-eyebrow,
        .hud-banner-label,
        .hud-card-title {
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            font-size: 0.76rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .hud-hero-panel-label {
            color: #8fc9ff;
        }

        .hud-hero-panel strong {
            display: block;
            margin-top: 0.35rem;
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            font-size: 1.08rem;
            color: #f3f9ff;
        }

        .hud-hero-panel small {
            display: block;
            margin-top: 0.42rem;
            line-height: 1.7;
            color: #aac4e4;
        }

        .hud-section-header {
            margin: 0.25rem 0 0.8rem 0;
        }

        .hud-section-eyebrow {
            color: #8fc9ff;
        }

        .hud-section-title {
            margin: 0.18rem 0 0 0;
            font-size: 1.16rem;
            color: #f4f9ff;
        }

        .hud-section-subtitle {
            margin: 0.25rem 0 0 0;
            color: #9eb8d7;
            line-height: 1.7;
        }

        .hud-card,
        .hud-feature,
        .hud-text-panel,
        .hud-banner {
            position: relative;
            overflow: hidden;
            border-radius: 24px;
            border: 1px solid var(--line);
            background:
                linear-gradient(180deg, rgba(13, 24, 40, 0.92), rgba(9, 17, 29, 0.86));
            box-shadow: var(--shadow);
        }

        .hud-card::before,
        .hud-feature::before,
        .hud-text-panel::before,
        .hud-banner::before {
            content: "";
            position: absolute;
            inset: 0 auto auto 0;
            width: 100%;
            height: 3px;
            background: linear-gradient(90deg, rgba(95, 124, 255, 0.0), rgba(114, 227, 255, 0.9), rgba(98, 242, 194, 0.0));
            opacity: 0.88;
        }

        .hud-card,
        .hud-feature,
        .hud-text-panel {
            padding: 1rem 1rem 1.05rem;
        }

        .hud-card--cobalt .hud-card-value { color: #b8cbff; }
        .hud-card--cyan .hud-card-value { color: #9cecff; }
        .hud-card--emerald .hud-card-value { color: #97ffd7; }
        .hud-card--amber .hud-card-value { color: #ffd89a; }
        .hud-card--rose .hud-card-value { color: #ffabc4; }

        .hud-card-title {
            color: #9cbde0;
        }

        .hud-card-value {
            margin-top: 0.42rem;
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            font-size: 2.04rem;
            font-weight: 800;
            line-height: 1.04;
        }

        .hud-card-desc {
            margin-top: 0.5rem;
            color: #a4bedc;
            line-height: 1.7;
            font-size: 0.92rem;
        }

        .hud-feature-eyebrow,
        .hud-text-eyebrow {
            color: #8fc9ff;
        }

        .hud-feature-title,
        .hud-text-title {
            margin-top: 0.28rem;
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            font-size: 1.12rem;
            font-weight: 700;
            color: #f4f9ff;
        }

        .hud-feature-desc,
        .hud-text-body {
            margin-top: 0.48rem;
            color: #a7c0dd;
            line-height: 1.8;
            font-size: 0.94rem;
        }

        .hud-feature-meta,
        .hud-text-meta {
            display: inline-flex;
            margin-top: 0.72rem;
            padding: 0.32rem 0.62rem;
            border-radius: 999px;
            border: 1px solid rgba(114, 227, 255, 0.18);
            background: rgba(14, 32, 54, 0.82);
            color: #d1e6ff;
            font-size: 0.82rem;
        }

        .hud-banner {
            padding: 0.95rem 1rem 1rem;
        }

        .hud-banner--success {
            background:
                linear-gradient(180deg, rgba(8, 27, 27, 0.94), rgba(7, 18, 29, 0.88));
        }

        .hud-banner--warning {
            background:
                linear-gradient(180deg, rgba(40, 22, 8, 0.94), rgba(26, 15, 8, 0.88));
        }

        .hud-banner--info {
            background:
                linear-gradient(180deg, rgba(11, 22, 40, 0.94), rgba(8, 17, 29, 0.88));
        }

        .hud-banner--danger {
            background:
                linear-gradient(180deg, rgba(40, 12, 20, 0.94), rgba(24, 10, 16, 0.88));
        }

        .hud-banner-label {
            color: #9cc6f2;
        }

        .hud-banner-title {
            margin-top: 0.34rem;
            font-family: "Saira Semi Condensed", "Noto Sans SC", sans-serif;
            font-size: 1.04rem;
            font-weight: 700;
            color: #f4f9ff;
        }

        .hud-banner-detail {
            margin-top: 0.35rem;
            color: #b4cbe7;
            line-height: 1.7;
            font-size: 0.92rem;
        }

        @media (max-width: 980px) {
            .hud-hero-grid {
                grid-template-columns: 1fr;
            }

            .hud-hero-side {
                min-height: 140px;
            }

            .hud-hero-panel {
                position: relative;
                right: auto;
                bottom: auto;
                width: 100%;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def hero(title: str, subtitle: str, kicker: str = "LLM Data Eval Lab") -> None:
    st.markdown(
        """
        <section class="hud-hero">
            <div class="hud-hero-grid">
                <div class="hud-hero-copy">
                    <div class="hud-kicker">{kicker}</div>
                    <h1>{title}</h1>
                    <p>{subtitle}</p>
                    <div class="hud-chip-list">
                        <span class="hud-chip">Dataset Ops</span>
                        <span class="hud-chip">Prompt Trials</span>
                        <span class="hud-chip">Eval Intelligence</span>
                        <span class="hud-chip">Actionable Reports</span>
                    </div>
                </div>
                <div class="hud-hero-side">
                    <div class="hud-orbit"></div>
                    <div class="hud-hero-panel">
                        <div class="hud-hero-panel-label">Live Surface</div>
                        <strong>Control, Diagnose, Iterate</strong>
                        <small>把实验配置、样本质量、结果分析和报告导出放进同一条闭环链路里。</small>
                    </div>
                </div>
            </div>
        </section>
        """.format(kicker=_safe(kicker), title=_safe(title), subtitle=_safe(subtitle)),
        unsafe_allow_html=True,
    )


def panel_title(title: str, subtitle: str | None = None, eyebrow: str = "Section") -> None:
    subtitle_html = '<p class="hud-section-subtitle">{}</p>'.format(_safe(subtitle)) if subtitle else ""
    st.markdown(
        """
        <div class="hud-section-header">
            <div class="hud-section-eyebrow">{eyebrow}</div>
            <div class="hud-section-title">{title}</div>
            {subtitle}
        </div>
        """.format(eyebrow=_safe(eyebrow), title=_safe(title), subtitle=subtitle_html),
        unsafe_allow_html=True,
    )


def info_card(title: str, value: str, desc: str, tone: str = "cobalt") -> None:
    tone_class = tone if tone in {"cobalt", "cyan", "emerald", "amber", "rose"} else "cobalt"
    st.markdown(
        """
        <div class="hud-card hud-card--{tone}">
            <div class="hud-card-title">{title}</div>
            <div class="hud-card-value">{value}</div>
            <div class="hud-card-desc">{desc}</div>
        </div>
        """.format(tone=tone_class, title=_safe(title), value=_safe(value), desc=_safe(desc)),
        unsafe_allow_html=True,
    )


def feature_card(title: str, desc: str, eyebrow: str = "Workflow", meta: str = "") -> None:
    meta_html = '<div class="hud-feature-meta">{}</div>'.format(_safe(meta)) if meta else ""
    st.markdown(
        """
        <div class="hud-feature">
            <div class="hud-feature-eyebrow">{eyebrow}</div>
            <div class="hud-feature-title">{title}</div>
            <div class="hud-feature-desc">{desc}</div>
            {meta}
        </div>
        """.format(eyebrow=_safe(eyebrow), title=_safe(title), desc=_safe(desc), meta=meta_html),
        unsafe_allow_html=True,
    )


def text_panel(title: str, body: str, eyebrow: str = "Brief", meta: str = "") -> None:
    meta_html = '<div class="hud-text-meta">{}</div>'.format(_safe(meta)) if meta else ""
    st.markdown(
        """
        <div class="hud-text-panel">
            <div class="hud-text-eyebrow">{eyebrow}</div>
            <div class="hud-text-title">{title}</div>
            <div class="hud-text-body">{body}</div>
            {meta}
        </div>
        """.format(eyebrow=_safe(eyebrow), title=_safe(title), body=_safe(body), meta=meta_html),
        unsafe_allow_html=True,
    )


def status_banner(state: str, title: str, detail: str) -> None:
    tone = state if state in {"success", "warning", "info", "danger"} else "info"
    st.markdown(
        """
        <div class="hud-banner hud-banner--{tone}">
            <div class="hud-banner-label">Status</div>
            <div class="hud-banner-title">{title}</div>
            <div class="hud-banner-detail">{detail}</div>
        </div>
        """.format(tone=tone, title=_safe(title), detail=_safe(detail)),
        unsafe_allow_html=True,
    )


def plotly_style(fig, height: int | None = None):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        plot_bgcolor="rgba(8, 17, 29, 0.78)",
        font=dict(family='"Noto Sans SC", sans-serif', size=13, color="#dbe8fb"),
        title=dict(
            x=0.03,
            xanchor="left",
            font=dict(family='"Saira Semi Condensed", "Noto Sans SC", sans-serif', size=18, color="#f5fbff"),
        ),
        margin=dict(l=26, r=22, t=62, b=28),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            x=0,
            bgcolor="rgba(0,0,0,0)",
            title_text="",
        ),
        colorway=["#72e3ff", "#5f7cff", "#62f2c2", "#ffc977", "#ff7ea7"],
    )
    fig.update_xaxes(
        showgrid=False,
        showline=True,
        linecolor="rgba(140, 179, 255, 0.16)",
        tickfont=dict(color="#bdd1ea"),
        title_font=dict(color="#a6c1e0"),
        zeroline=False,
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(140, 179, 255, 0.12)",
        tickfont=dict(color="#bdd1ea"),
        title_font=dict(color="#a6c1e0"),
        zeroline=False,
    )
    if height is not None:
        fig.update_layout(height=height)
    return fig
