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
hero("Bad Case 分析", "把低分样本当作故障池，先看风险面，再回到单个案例定位根因。", kicker="差例工作台")

client = APIClient()
df = build_results_dataframe(client.base_url)
if df.empty:
    status_banner("warning", "当前没有可分析的结果数据", "先完成至少一次实验运行，再使用 Bad Case 分析页定位失败模式。")
    st.stop()

panel_title("低分阈值", "通过阈值控制进入故障池的样本范围。", eyebrow="Risk Gate")
threshold = st.slider("低分阈值", 0.0, 1.0, 0.65, 0.05)
bad_df = df[df["overall_score"] <= threshold].copy()
bad_df["badcase_tags_text"] = bad_df["badcase_tags"].apply(lambda tags: ", ".join(tags))

summary_cols = st.columns(4)
with summary_cols[0]:
    info_card("低分样本数", str(len(bad_df)), "当前故障池中的样本数量。", tone="rose")
with summary_cols[1]:
    ratio = 0.0 if df.empty else len(bad_df) / len(df)
    info_card("占比", "{:.1%}".format(ratio), "低分样本占全部结果的比例。", tone="amber")
with summary_cols[2]:
    info_card(
        "平均低分样本分数",
        "{:.3f}".format(bad_df["overall_score"].mean() if not bad_df.empty else 0.0),
        "故障池样本的平均总分。",
        tone="cobalt",
    )
with summary_cols[3]:
    info_card(
        "平均低分样本幻觉率",
        "{:.3f}".format(bad_df["hallucination_risk"].mean() if not bad_df.empty else 0.0),
        "故障池样本的平均 hallucination risk。",
        tone="cyan",
    )

tag_counter = {}
for tags in bad_df["badcase_tags"]:
    for tag in tags:
        tag_counter[tag] = tag_counter.get(tag, 0) + 1

tag_df = pd.DataFrame(
    [{"tag": tag, "count": count} for tag, count in sorted(tag_counter.items(), key=lambda item: item[1], reverse=True)]
)

chart_col, table_col = st.columns([1, 1.4])
with chart_col:
    panel_title("归因标签分布", "看故障池里哪些错误模式最集中。", eyebrow="Failure Signature")
    if not tag_df.empty:
        fig = px.bar(tag_df, x="tag", y="count", title="归因标签统计", color="count", color_continuous_scale="Blues")
        st.plotly_chart(plotly_style(fig, height=420), use_container_width=True)
    else:
        status_banner("info", "低分样本尚未命中 Bad Case 标签", "说明当前规则还没有给这批样本打上归因标签，建议优先检查评分与标签策略。")

with table_col:
    panel_title("低分样本清单", "先看问题文本、得分和标签，再决定深入哪条样本。", eyebrow="Failure Pool")
    st.dataframe(
        bad_df[["run_name", "sample_id", "query", "overall_score", "hallucination_risk", "badcase_tags_text"]].rename(
            columns={
                "run_name": "运行名称",
                "sample_id": "样本 ID",
                "query": "问题",
                "overall_score": "总分",
                "hallucination_risk": "幻觉率",
                "badcase_tags_text": "归因标签",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

panel_title("样例详情", "把典型失败样本拆成问答、标签和上下文三个视角。", eyebrow="Case Drilldown")
if bad_df.empty:
    status_banner("info", "当前阈值下没有低分样本", "可以提高阈值，或者先回到实验页继续跑新的实验。")
else:
    selected_idx = st.selectbox("选择低分样本", bad_df.index.tolist(), format_func=lambda idx: bad_df.loc[idx, "query"])
    row = bad_df.loc[selected_idx]
    detail_tabs = st.tabs(["问答对比", "Bad Case 标签", "上下文"])
    with detail_tabs[0]:
        left, right = st.columns(2)
        with left:
            text_panel("问题", row["query"], eyebrow="Query", meta=row["run_name"])
            text_panel("参考答案", row["reference_answer"], eyebrow="Reference")
        with right:
            text_panel("模型输出", row["generated_answer"], eyebrow="Generated Answer")
            text_panel("总分 / 幻觉率", "{score:.3f} / {risk:.3f}".format(score=row["overall_score"], risk=row["hallucination_risk"]), eyebrow="Signal")
    with detail_tabs[1]:
        text_panel("Bad Case 标签", row["badcase_tags_text"] or "无", eyebrow="Tag Set")
    with detail_tabs[2]:
        st.code(row["context"] or "暂无上下文", language="text")
