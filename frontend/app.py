from pathlib import Path

import pandas as pd
import streamlit as st

from bootstrap import ensure_frontend_paths

ensure_frontend_paths()

from api_client import APIClient, APIError
from ui import apply_base_style, feature_card, hero, info_card, panel_title, status_banner, text_panel

ROOT_DIR = Path(__file__).resolve().parents[1]


def render_home() -> None:
    client = APIClient()
    hero("Search QA 评测控制台", "把数据集、Prompt 实验、逐样本分析、Bad Case 归因和报告导出组织成一块连续的评测操作面板。")

    overview = {}
    runs = []
    status_state = "success"
    status_title = "后端链路已连通"
    status_detail = "API 服务在线，首页摘要与历史实验可实时读取。"
    try:
        client.health()
        overview = client.analysis_overview()
        runs = client.analysis_runs()
    except APIError as exc:
        status_state = "danger"
        status_title = "后端链路暂不可用"
        status_detail = "当前无法读取 API：{error}".format(error=exc)
        overview = {"total_runs": 0, "total_results": 0, "avg_overall_score": 0.0, "avg_hallucination_risk": 0.0}
        runs = []

    with st.sidebar:
        panel_title("系统面板", "快速查看连接与缓存状态。", eyebrow="System")
        status_banner(status_state, "API Endpoint", client.base_url)
        if st.button("刷新页面缓存", use_container_width=True):
            st.cache_data.clear()
        text_panel("工程目录", str(ROOT_DIR), eyebrow="Workspace", meta="Local Project")

    status_banner(status_state, status_title, status_detail)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        info_card("实验总数", str(overview["total_runs"]), "累计完成的实验运行数量。", tone="cobalt")
    with col2:
        info_card("结果总数", str(overview["total_results"]), "已落库的评测结果条数。", tone="cyan")
    with col3:
        info_card("平均总分", "{:.3f}".format(overview["avg_overall_score"]), "当前全量结果的平均总分。", tone="emerald")
    with col4:
        info_card("平均幻觉率", "{:.3f}".format(overview["avg_hallucination_risk"]), "当前全量结果的平均幻觉率。", tone="amber")

    left_col, right_col = st.columns([1.28, 0.92])
    with left_col:
        panel_title("评测闭环", "围绕数据、实验、结果、诊断和导出做统一的信息组织。", eyebrow="Workflow")
        feature_row_1 = st.columns(2)
        with feature_row_1[0]:
            feature_card("数据集工作台", "导入 CSV / JSON，按类别、难度和标签筛样本，快速定位具体问题样本。", eyebrow="Dataset", meta="Import / Filter / Inspect")
        with feature_row_1[1]:
            feature_card("Prompt 批量实验", "把 Prompt 版本、模型参数和评审模式收敛到同一份运行配置里。", eyebrow="Experiment", meta="Run / Compare / Persist")
        feature_row_2 = st.columns(2)
        with feature_row_2[0]:
            feature_card("逐样本结果追踪", "直接对照问题、参考答案、模型输出和分项评分，缩短问题定位路径。", eyebrow="Result Analysis", meta="Trace / Explain / Slice")
        with feature_row_2[1]:
            feature_card("差例与趋势复盘", "聚合幻觉、低分、Bad Case 标签和近期 Run 趋势，辅助持续迭代。", eyebrow="Diagnostics", meta="Dashboard / Bad Case / Report")
    with right_col:
        panel_title("操作台", "把常用动作和启动路径放在一处，首页就能完成状态判断。", eyebrow="Ops")
        text_panel("当前展示模式", "这版界面采用深色控制台视觉，强调实验状态、信号强弱和信息层级，适合持续做离线评测。", eyebrow="Direction", meta="Distinctive / Practical")
        text_panel("启动路径", "1. 激活虚拟环境\n2. Seed 演示数据\n3. 启动 FastAPI\n4. 启动 Streamlit", eyebrow="Quick Start", meta="Local Boot")
        st.code(
            "\n".join(
                [
                    "source .venv/bin/activate",
                    "python scripts/seed_demo_data.py",
                    "uvicorn app.main:app --reload",
                    "streamlit run frontend/app.py",
                ]
            ),
            language="bash",
        )

    panel_title("最近实验概览", "优先暴露最近的 run 名称、得分与状态，方便继续追踪。", eyebrow="Telemetry")
    if runs:
        run_df = pd.DataFrame(runs)
        st.dataframe(
            run_df.rename(
                columns={
                    "run_id": "运行 ID",
                    "run_name": "运行名称",
                    "experiment_id": "实验 ID",
                    "sample_total": "样本总数",
                    "avg_overall_score": "平均总分",
                    "avg_hallucination_risk": "平均幻觉率",
                    "status": "状态",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning("暂无实验记录。先运行 `python scripts/seed_demo_data.py`，再进入 Prompt 实验页面启动一次实验。")
    footer_cols = st.columns(2)
    with footer_cols[0]:
        text_panel("适合的使用方式", "先在数据集页确认样本质量，再切到 Prompt 实验页发起批量运行，最后在结果页与 Bad Case 页做复盘。", eyebrow="Playbook", meta="Inspect -> Run -> Diagnose")
    with footer_cols[1]:
        text_panel("工程目录", str(ROOT_DIR), eyebrow="Workspace", meta="Shared Local Path")


st.set_page_config(
    page_title="Search QA 评测控制台",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_base_style()

navigation = st.navigation(
    [
        st.Page(render_home, title="首页", icon="🏠", default=True),
        st.Page("pages/1_Dataset_Management.py", title="数据集管理", icon="🗂️"),
        st.Page("pages/2_Prompt_Experiments.py", title="Prompt 实验", icon="🧪"),
        st.Page("pages/3_Experiment_Results.py", title="实验结果", icon="📋"),
        st.Page("pages/4_Bad_Case_Analysis.py", title="Bad Case 分析", icon="🔎"),
        st.Page("pages/5_Dashboard.py", title="效果看板", icon="📈"),
        st.Page("pages/6_实验报告导出.py", title="实验报告导出", icon="📝"),
    ],
    position="sidebar",
    expanded=True,
)
navigation.run()
