import sys
from pathlib import Path

import pandas as pd
import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, APIError, cached_runs
from ui import apply_base_style, hero, info_card, panel_title, status_banner, text_panel

apply_base_style()
hero("实验结果", "先看一次 Run 的整体信号，再向下钻取到单个样本、分项评分和渲染后的 Prompt。", kicker="结果工作台")

client = APIClient()
runs = cached_runs(client.base_url)
if not runs:
    status_banner("warning", "当前没有实验运行记录", "先在 Prompt 实验页发起至少一次运行，再回到这里做逐样本分析。")
    st.stop()

run_options = {
    "{run_id} | {run_name}".format(run_id=item["id"], run_name=item["run_name"]): item
    for item in runs
}
panel_title("运行选择", "先锁定一个 Run，再对低分和差例标签做切片。", eyebrow="Run Selector")
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
    status_banner("info", "该 Run 暂无结果", "当前运行还没有逐样本结果，稍后重试或检查后端执行状态。")
    st.stop()

summary_cols = st.columns(4)
with summary_cols[0]:
    info_card("运行 ID", str(selected_run["id"]), "当前查看的 Experiment Run 编号。", tone="cobalt")
with summary_cols[1]:
    info_card("样本量", str(len(df)), "该 Run 的结果条数。", tone="cyan")
with summary_cols[2]:
    info_card("平均总分", "{:.3f}".format(df["overall_score"].mean()), "当前 Run 的 overall score 均值。", tone="emerald")
with summary_cols[3]:
    info_card("平均幻觉率", "{:.3f}".format(df["hallucination_risk"].mean()), "当前 Run 的 hallucination risk 均值。", tone="amber")

panel_title("切片筛选", "可以按分数阈值或 Bad Case 标签快速缩小需要复盘的样本范围。", eyebrow="Slice")
filter_col1, filter_col2 = st.columns(2)
score_threshold = filter_col1.slider("仅显示低于该分数的样本", 0.0, 1.0, 1.0, 0.05)
all_badcase_tags = sorted({tag for tags in df["badcase_tags"] for tag in tags})
selected_badcase_tags = filter_col2.multiselect("Bad Case 标签筛选", all_badcase_tags)

filtered = df[df["overall_score"] <= score_threshold].copy()
if selected_badcase_tags:
    filtered = filtered[filtered["badcase_tags"].apply(lambda tags: bool(set(selected_badcase_tags) & set(tags)))]

filtered = filtered.sort_values("overall_score", ascending=True)
if filtered.empty:
    status_banner("info", "当前筛选条件下没有结果", "放宽分数阈值或取消标签条件后，再继续查看样本详情。")
    st.stop()

filtered["badcase_tags_text"] = filtered["badcase_tags"].apply(lambda tags: ", ".join(tags))

panel_title("结果列表", "默认按总分升序排列，优先把最需要关注的样本放在前面。", eyebrow="Result Table")
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

panel_title("结果详情", "把答案对比、分项评分、上下文和渲染 Prompt 分开查看。", eyebrow="Drill Down")
sample_id = st.selectbox("选择样本 ID", filtered["sample_id"].tolist())
detail = filtered[filtered["sample_id"] == sample_id].iloc[0]
detail_tabs = st.tabs(["答案对比", "评分与标签", "上下文", "渲染 Prompt"])
with detail_tabs[0]:
    left, right = st.columns(2)
    with left:
        text_panel("问题", detail["query"], eyebrow="Query", meta="Sample #{sample_id}".format(sample_id=detail["sample_id"]))
        text_panel("参考答案", detail["reference_answer"], eyebrow="Reference")
    with right:
        text_panel("模型输出", detail["generated_answer"], eyebrow="Generated Answer")
        text_panel("差例标签", detail["badcase_tags_text"] or "无", eyebrow="Bad Case Tags")
with detail_tabs[1]:
    score_cols = st.columns(5)
    with score_cols[0]:
        info_card("总分", "{:.3f}".format(detail["overall_score"]), "overall score。", tone="cobalt")
    with score_cols[1]:
        info_card("正确性", "{:.3f}".format(detail["correctness"]), "correctness。", tone="cyan")
    with score_cols[2]:
        info_card("完整性", "{:.3f}".format(detail["completeness"]), "completeness。", tone="emerald")
    with score_cols[3]:
        info_card("贴合度", "{:.3f}".format(detail["groundedness"]), "groundedness。", tone="amber")
    with score_cols[4]:
        info_card("格式合规", "{:.3f}".format(detail["format_compliance"]), "format compliance。", tone="rose")
    info_card("幻觉率", "{:.3f}".format(detail["hallucination_risk"]), "hallucination risk。", tone="amber")
with detail_tabs[2]:
    st.code(detail["context"] or "暂无上下文", language="text")
with detail_tabs[3]:
    st.code(detail["rendered_prompt"], language="text")
