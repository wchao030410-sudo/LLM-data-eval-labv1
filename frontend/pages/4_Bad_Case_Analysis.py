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
hero("Bad Case 分析", "聚焦低分样本，查看归因标签分布与典型失败样例。", kicker="差例工作台")

client = APIClient()
df = build_results_dataframe(client.base_url)
if df.empty:
    st.warning("暂无结果数据。先运行一次实验。")
    st.stop()

threshold = st.slider("低分阈值", 0.0, 1.0, 0.65, 0.05)
bad_df = df[df["overall_score"] <= threshold].copy()
bad_df["badcase_tags_text"] = bad_df["badcase_tags"].apply(lambda tags: ", ".join(tags))

col1, col2, col3 = st.columns(3)
col1.metric("低分样本数", len(bad_df))
col2.metric("平均低分样本分数", "{:.3f}".format(bad_df["overall_score"].mean() if not bad_df.empty else 0.0))
col3.metric("平均低分样本幻觉率", "{:.3f}".format(bad_df["hallucination_risk"].mean() if not bad_df.empty else 0.0))

tag_counter = {}
for tags in bad_df["badcase_tags"]:
    for tag in tags:
        tag_counter[tag] = tag_counter.get(tag, 0) + 1

tag_df = pd.DataFrame(
    [{"tag": tag, "count": count} for tag, count in sorted(tag_counter.items(), key=lambda item: item[1], reverse=True)]
)

chart_col, table_col = st.columns([1, 1.4])
with chart_col:
    if not tag_df.empty:
        fig = px.bar(tag_df, x="tag", y="count", title="归因标签统计", color="count", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("低分样本尚未命中 Bad Case 标签。")

with table_col:
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

panel_title("样例详情")
if not bad_df.empty:
    selected_idx = st.selectbox("选择低分样本", bad_df.index.tolist(), format_func=lambda idx: bad_df.loc[idx, "query"])
    row = bad_df.loc[selected_idx]
    st.markdown("**问题**")
    st.write(row["query"])
    st.markdown("**参考答案**")
    st.write(row["reference_answer"])
    st.markdown("**模型输出**")
    st.write(row["generated_answer"])
    st.markdown("**Bad Case 标签**")
    st.write(row["badcase_tags_text"] or "无")
    st.markdown("**上下文**")
    st.code(row["context"])
