import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, build_results_dataframe
from ui import apply_base_style, hero, info_card, panel_title, plotly_style, status_banner, text_panel

apply_base_style()
hero("效果看板", "从 Prompt 版本、类别表现、风险分布到近期趋势，把关键评测信号集中在一屏。", kicker="数据看板")

client = APIClient()
df = build_results_dataframe(client.base_url)
if df.empty:
    status_banner("warning", "当前没有可视化数据", "先完成至少一次 Prompt 实验，仪表盘才会生成版本对比和趋势图。")
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

summary_cols = st.columns(4)
with summary_cols[0]:
    info_card("总 Run 数", str(int(df["run_id"].nunique())), "参与汇总的实验运行数量。", tone="cobalt")
with summary_cols[1]:
    info_card("平均总分", "{:.3f}".format(df["overall_score"].mean()), "全部结果的 overall score 均值。", tone="cyan")
with summary_cols[2]:
    info_card("平均幻觉率", "{:.3f}".format(df["hallucination_risk"].mean()), "全部结果的 hallucination risk 均值。", tone="amber")
with summary_cols[3]:
    info_card("Prompt 组合数", str(prompt_df.shape[0]), "参与比较的 Prompt 版本组合数量。", tone="emerald")

insight_cols = st.columns(2)
with insight_cols[0]:
    best_row = category_df.iloc[0]
    text_panel(
        "当前最佳类别",
        "{category} 的平均总分目前最高，为 {score:.3f}。".format(category=best_row["category"], score=best_row["overall_score"]),
        eyebrow="Highlight",
        meta="Category Leader",
    )
with insight_cols[1]:
    if not badcase_df.empty:
        top_tag = badcase_df.iloc[0]
        text_panel(
            "最常见差例标签",
            "{tag} 出现了 {count} 次，是当前最主要的 Bad Case 模式。".format(tag=top_tag["tag"], count=int(top_tag["count"])),
            eyebrow="Risk Signal",
            meta="Dominant Failure Mode",
        )
    else:
        text_panel("最常见差例标签", "当前结果尚未产生 Bad Case 分布数据。", eyebrow="Risk Signal", meta="No Labels Yet")

row1_col1, row1_col2 = st.columns(2)
with row1_col1:
    panel_title("Prompt 版本对比", "观察不同 Prompt 版本的平均得分差异。", eyebrow="Version View")
    fig_prompt = px.bar(
        prompt_df,
        x="prompt_version",
        y="overall_score",
        color="prompt_name",
        title="Prompt 版本对比",
        color_discrete_sequence=["#72e3ff", "#5f7cff", "#62f2c2", "#ffc977", "#ff7ea7"],
    )
    st.plotly_chart(plotly_style(fig_prompt, height=420), use_container_width=True)

with row1_col2:
    panel_title("类别表现图", "按类别比较平均总分，找出更稳定或更脆弱的题型。", eyebrow="Category View")
    fig_category = px.bar(
        category_df,
        x="category",
        y="overall_score",
        color="overall_score",
        title="类别表现图",
        color_continuous_scale=["#11294a", "#2d63ff", "#72e3ff"],
    )
    st.plotly_chart(plotly_style(fig_category, height=420), use_container_width=True)

row2_col1, row2_col2 = st.columns(2)
with row2_col1:
    panel_title("幻觉率图", "按类别看 hallucination risk 的差异。", eyebrow="Risk View")
    fig_hallucination = px.bar(
        category_df,
        x="category",
        y="hallucination_risk",
        color="hallucination_risk",
        title="幻觉率图",
        color_continuous_scale=["#2a0e18", "#ff7ea7", "#ffc977"],
    )
    st.plotly_chart(plotly_style(fig_hallucination, height=420), use_container_width=True)

with row2_col2:
    panel_title("Bad Case 分布图", "查看差例标签在全部结果中的构成。", eyebrow="Distribution")
    if not badcase_df.empty:
        fig_badcase = px.pie(
            badcase_df,
            names="tag",
            values="count",
            title="Bad Case 分布图",
            color_discrete_sequence=["#72e3ff", "#5f7cff", "#62f2c2", "#ffc977", "#ff7ea7"],
        )
        st.plotly_chart(plotly_style(fig_badcase, height=420), use_container_width=True)
    else:
        status_banner("info", "暂无 Bad Case 分布数据", "说明当前结果还没有归因标签，或者样本尚未完成标注。")

panel_title("最近实验趋势", "按 Run 观察平均总分的波动。", eyebrow="Trend")
fig_trend = px.line(
    trend_df,
    x="run_id",
    y="overall_score",
    markers=True,
    hover_name="run_name",
    title="最近实验趋势",
)
st.plotly_chart(plotly_style(fig_trend, height=420), use_container_width=True)

panel_title("明细列表", "表格保留到样本粒度，方便二次筛选和导出。", eyebrow="Detailed View")
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
