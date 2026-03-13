import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, build_results_dataframe
from ui import apply_base_style, hero, panel_title

apply_base_style()
hero("效果看板", "对比 Prompt 版本、类别表现、幻觉率和近期实验趋势。", kicker="数据看板")

client = APIClient()
df = build_results_dataframe(client.base_url)
if df.empty:
    st.warning("暂无实验结果。先完成一次 Prompt 实验。")
    st.stop()

prompt_df = (
    df.groupby(["prompt_name", "prompt_version"], as_index=False)["overall_score"]
    .mean()
    .sort_values("overall_score", ascending=False)
)

category_df = (
    df.groupby("category", as_index=False)[["overall_score", "hallucination_risk"]]
    .mean()
    .sort_values("overall_score", ascending=False)
)

badcase_counter = {}
for tags in df["badcase_tags"]:
    for tag in tags:
        badcase_counter[tag] = badcase_counter.get(tag, 0) + 1
badcase_df = pd.DataFrame(
    [{"tag": tag, "count": count} for tag, count in sorted(badcase_counter.items(), key=lambda item: item[1], reverse=True)]
)

trend_df = (
    df.groupby(["run_id", "run_name"], as_index=False)["overall_score"]
    .mean()
    .sort_values("run_id")
)

col1, col2, col3 = st.columns(3)
col1.metric("总 Run 数", int(df["run_id"].nunique()))
col2.metric("平均总分", "{:.3f}".format(df["overall_score"].mean()))
col3.metric("平均幻觉率", "{:.3f}".format(df["hallucination_risk"].mean()))

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    fig_prompt = px.bar(
        prompt_df,
        x="prompt_version",
        y="overall_score",
        color="prompt_name",
        title="Prompt 版本对比",
        color_discrete_sequence=["#1d4ed8", "#3b82f6", "#60a5fa", "#93c5fd"],
    )
    st.plotly_chart(fig_prompt, use_container_width=True)

with row1_col2:
    fig_category = px.bar(
        category_df,
        x="category",
        y="overall_score",
        color="overall_score",
        title="类别表现图",
        color_continuous_scale="Blues",
    )
    st.plotly_chart(fig_category, use_container_width=True)

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    fig_hallucination = px.bar(
        category_df,
        x="category",
        y="hallucination_risk",
        color="hallucination_risk",
        title="幻觉率图",
        color_continuous_scale="Reds",
    )
    st.plotly_chart(fig_hallucination, use_container_width=True)

with row2_col2:
    if not badcase_df.empty:
        fig_badcase = px.pie(
            badcase_df,
            names="tag",
            values="count",
            title="Bad Case 分布图",
            color_discrete_sequence=["#0f172a", "#1d4ed8", "#60a5fa", "#bfdbfe", "#e2e8f0"],
        )
        st.plotly_chart(fig_badcase, use_container_width=True)
    else:
        st.info("暂无 Bad Case 分布数据。")

panel_title("最近实验趋势")
fig_trend = px.line(
    trend_df,
    x="run_id",
    y="overall_score",
    markers=True,
    hover_name="run_name",
    title="最近实验趋势",
)
st.plotly_chart(fig_trend, use_container_width=True)

panel_title("明细列表")
display_df = df.copy()
display_df["badcase_tags"] = display_df["badcase_tags"].apply(lambda tags: ", ".join(tags))
st.dataframe(
    display_df[
        [
            "run_name",
            "query",
            "prompt_name",
            "prompt_version",
            "category",
            "overall_score",
            "hallucination_risk",
            "badcase_tags",
        ]
    ].rename(
        columns={
            "run_name": "运行名称",
            "query": "问题",
            "prompt_name": "Prompt 名称",
            "prompt_version": "Prompt 版本",
            "category": "类别",
            "overall_score": "总分",
            "hallucination_risk": "幻觉率",
            "badcase_tags": "差例标签",
        }
    ),
    use_container_width=True,
    hide_index=True,
)
