import sys
from pathlib import Path

import pandas as pd
import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, APIError, cached_runs
from ui import apply_base_style, hero, panel_title

apply_base_style()
hero("实验结果", "查看逐样本模型输出、参考答案、评分结果，并按低分或差例标签筛选。", kicker="结果工作台")

client = APIClient()
runs = cached_runs(client.base_url)
if not runs:
    st.warning("暂无实验运行记录。")
    st.stop()

run_options = {
    "{run_id} | {run_name}".format(run_id=item["id"], run_name=item["run_name"]): item
    for item in runs
}
selected_label = st.selectbox("选择实验 Run", list(run_options.keys()))
selected_run = run_options[selected_label]

try:
    experiment = client.get_experiment(selected_run["experiment_id"])
    samples = {item["id"]: item for item in client.list_samples(experiment["dataset_id"])}
    results = client.get_run_results(selected_run["id"])
except APIError as exc:
    st.error(str(exc))
    st.stop()

rows = []
for result in results:
    sample = samples.get(result["sample_id"], {})
    rows.append(
        {
            "sample_id": result["sample_id"],
            "query": sample.get("query", ""),
            "reference_answer": sample.get("reference_answer", ""),
            "generated_answer": result["generated_answer"],
            "overall_score": result["overall_score"],
            "correctness": result["correctness"],
            "completeness": result["completeness"],
            "groundedness": result["groundedness"],
            "format_compliance": result["format_compliance"],
            "hallucination_risk": result["hallucination_risk"],
            "badcase_tags": result.get("badcase_tags", []),
            "rendered_prompt": result["rendered_prompt"],
            "context": sample.get("context", ""),
        }
    )

df = pd.DataFrame(rows)
if df.empty:
    st.info("该 Run 暂无结果。")
    st.stop()

filter_col1, filter_col2 = st.columns(2)
score_threshold = filter_col1.slider("仅显示低于该分数的样本", 0.0, 1.0, 1.0, 0.05)
all_badcase_tags = sorted({tag for tags in df["badcase_tags"] for tag in tags})
selected_badcase_tags = filter_col2.multiselect("Bad Case 标签筛选", all_badcase_tags)

filtered = df[df["overall_score"] <= score_threshold].copy()
if selected_badcase_tags:
    filtered = filtered[filtered["badcase_tags"].apply(lambda tags: bool(set(selected_badcase_tags) & set(tags)))]

filtered = filtered.sort_values("overall_score", ascending=True)
if filtered.empty:
    st.info("当前筛选条件下没有结果。")
    st.stop()

filtered["badcase_tags_text"] = filtered["badcase_tags"].apply(lambda tags: ", ".join(tags))

panel_title("结果列表")
st.dataframe(
    filtered[["sample_id", "query", "overall_score", "hallucination_risk", "badcase_tags_text"]].rename(
        columns={
            "sample_id": "样本 ID",
            "query": "问题",
            "overall_score": "总分",
            "hallucination_risk": "幻觉率",
            "badcase_tags_text": "差例标签",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

panel_title("结果详情")
sample_id = st.selectbox("选择样本 ID", filtered["sample_id"].tolist())
detail = filtered[filtered["sample_id"] == sample_id].iloc[0]
left, right = st.columns(2)
with left:
    st.markdown("**问题**")
    st.write(detail["query"])
    st.markdown("**参考答案**")
    st.write(detail["reference_answer"])
    st.markdown("**模型输出**")
    st.write(detail["generated_answer"])
with right:
    st.markdown("**评分结果**")
    st.json(
        {
            "overall_score": detail["overall_score"],
            "correctness": detail["correctness"],
            "completeness": detail["completeness"],
            "groundedness": detail["groundedness"],
            "format_compliance": detail["format_compliance"],
            "hallucination_risk": detail["hallucination_risk"],
            "badcase_tags": detail["badcase_tags"],
        }
    )
st.markdown("**上下文**")
st.code(detail["context"])
st.markdown("**渲染后的 Prompt**")
st.code(detail["rendered_prompt"])
