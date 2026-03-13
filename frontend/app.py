from pathlib import Path

import pandas as pd
import streamlit as st

from bootstrap import ensure_frontend_paths

ensure_frontend_paths()

from api_client import APIClient, APIError
from ui import apply_base_style, hero, info_card, panel_title

ROOT_DIR = Path(__file__).resolve().parents[1]


def render_home() -> None:
    apply_base_style()
    hero("面向 Search QA 的大模型数据评测平台", "围绕数据集、Prompt、实验运行、自动评测与差例分析构建完整闭环。")

    client = APIClient()

    with st.sidebar:
        st.subheader("连接状态")
        st.code(client.base_url)
        if st.button("刷新页面缓存", use_container_width=True):
            st.cache_data.clear()

    try:
        client.health()
        st.success("后端已连接：正常")
    except APIError as exc:
        st.error("后端不可用：{error}".format(error=exc))

    overview = {}
    runs = []
    try:
        overview = client.analysis_overview()
        runs = client.analysis_runs()
    except APIError:
        overview = {"total_runs": 0, "total_results": 0, "avg_overall_score": 0.0, "avg_hallucination_risk": 0.0}
        runs = []

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        info_card("实验总数", str(overview["total_runs"]), "累计完成的实验运行数量")
    with col2:
        info_card("结果总数", str(overview["total_results"]), "已落库的评测结果条数")
    with col3:
        info_card("平均总分", "{:.3f}".format(overview["avg_overall_score"]), "当前全量结果的平均总分")
    with col4:
        info_card("平均幻觉率", "{:.3f}".format(overview["avg_hallucination_risk"]), "当前全量结果的平均幻觉率")

    panel_title("项目介绍")
    st.markdown(
        """
        这个项目模拟 AI 模型数据平台常见的离线评测流程：

        - 评测数据集管理与样本筛选
        - Prompt 版本管理与实验配置
        - 批量运行实验并记录结果
        - 自动评测与 Bad Case 归因
        - 数据看板与趋势复盘
        """
    )

    panel_title("核心能力")
    capability_cols = st.columns(3)
    with capability_cols[0]:
        info_card("数据集管理", "CSV / JSON", "支持样本导入、筛选、标签查看与详情检索。")
    with capability_cols[1]:
        info_card("Prompt 实验", "批量运行", "支持 Prompt 版本选择、模型参数设置和一次性批量评测。")
    with capability_cols[2]:
        info_card("结果分析", "差例归因", "支持多维评分、Bad Case 标签统计和趋势看板。")

    panel_title("最近实验概览")
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

    panel_title("启动方式")
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

    st.caption("项目目录：{path}".format(path=ROOT_DIR))


st.set_page_config(
    page_title="大模型数据评测平台",
    page_icon="📊",
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
