import sys
from pathlib import Path

import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, APIError, cached_datasets, cached_prompts
from ui import apply_base_style, feature_card, hero, info_card, panel_title, status_banner, text_panel

apply_base_style()
hero("Prompt 实验", "把数据集、Prompt 版本和模型参数收束成一份实验任务单，便于连续发起离线评测。", kicker="实验工作台")

client = APIClient()
datasets = cached_datasets(client.base_url)
prompts, version_map = cached_prompts(client.base_url)

if not datasets or not prompts:
    status_banner("warning", "缺少实验前置资源", "当前没有可用的数据集或 Prompt 版本。先运行 seed 脚本补齐基础数据。")
    st.stop()

dataset_options = {item["name"]: item for item in datasets}
version_options = {}
for prompt in prompts:
    for version in version_map.get(prompt["id"], []):
        label = "{name} / {version}".format(name=prompt["name"], version=version["version"])
        version_options[label] = {"prompt": prompt, "version": version}

summary_cols = st.columns(3)
with summary_cols[0]:
    info_card("可选数据集", str(len(dataset_options)), "当前可用于实验的数据集数量。", tone="cobalt")
with summary_cols[1]:
    info_card("Prompt 版本", str(len(version_options)), "可直接选用的 Prompt 版本总数。", tone="cyan")
with summary_cols[2]:
    info_card("评审模式", "2", "当前支持规则评审与 LLM Judge。", tone="emerald")

setup_left, setup_right = st.columns([1.14, 0.86])
with setup_left:
    panel_title("实验配置", "按数据集、Prompt、模型参数和评审模式组织任务。", eyebrow="Run Builder")
    with st.form("run_experiment_form"):
        top_left, top_right = st.columns(2)
        dataset_name = top_left.selectbox("数据集", list(dataset_options.keys()))
        version_label = top_right.selectbox("Prompt 版本", list(version_options.keys()))

        model_left, model_right = st.columns(2)
        model_name = model_left.text_input("模型名", value="glm-4.5-air")
        judge_mode = model_right.selectbox("评审模式", ["rule", "llm_judge"])

        param_left, param_right = st.columns(2)
        temperature = param_left.slider("温度参数", 0.0, 1.0, 0.2, 0.1)
        max_tokens = param_right.slider("最大输出长度", 64, 1024, 256, 32)

        name_left, name_right = st.columns(2)
        experiment_name = name_left.text_input("实验名称", value="search_qa_eval_run")
        experiment_desc = name_right.text_input("实验描述", value="来自 Streamlit 的批量实验")
        submitted = st.form_submit_button("运行实验", use_container_width=True)
with setup_right:
    feature_card("配置逻辑", "优先选定数据集和 Prompt 版本，再控制模型参数和评审方式，最后统一发起单次离线 Run。", eyebrow="Execution Pattern", meta="Dataset -> Prompt -> Model")
    text_panel("推荐做法", "先用较小数据集验证 Prompt 方向，再扩大样本量做更稳定的均值比较。", eyebrow="Advice", meta="Small Slice First")
    text_panel("结果去向", "实验完成后会把运行摘要、逐样本结果和 Bad Case 标签写入后端，后续页面可直接复用。", eyebrow="Output", meta="Persisted Analysis")

if submitted:
    try:
        dataset = dataset_options[dataset_name]
        version_meta = version_options[version_label]["version"]
        experiment = client.create_experiment(
            {
                "name": experiment_name,
                "description": experiment_desc,
                "dataset_id": dataset["id"],
                "prompt_version_id": version_meta["id"],
                "target_model": model_name,
                "temperature": temperature,
                "top_p": 1.0,
                "max_tokens": max_tokens,
                "judge_mode": judge_mode,
                "status": "draft",
            }
        )
        with st.spinner("实验运行中..."):
            run = client.run_experiment(experiment["id"], run_name="{name}-run".format(name=experiment_name))
        status_banner("success", "实验执行完成", "本次实验已返回运行摘要，后续可以直接切换到结果页或 Bad Case 页继续分析。")
        summary_cols = st.columns(4)
        with summary_cols[0]:
            info_card("运行 ID", str(run["id"]), "本次 Experiment Run 的唯一标识。", tone="cobalt")
        with summary_cols[1]:
            info_card("运行状态", str(run["run_status"]), "后端返回的最终状态。", tone="cyan")
        with summary_cols[2]:
            info_card("完成样本数", str(run["sample_completed"]), "本次已完成的样本条数。", tone="emerald")
        with summary_cols[3]:
            info_card("平均总分", "{:.3f}".format(run["avg_overall_score"]), "本次 Run 的平均 overall score。", tone="amber")
        with st.expander("查看原始 Run 返回"):
            st.json(run)
        st.cache_data.clear()
    except APIError as exc:
        st.error(str(exc))

panel_title("最近实验摘要", "把最近 run 的名称、状态和均值集中在一张表里。", eyebrow="Recent Runs")
try:
    runs = client.list_runs()
    if runs:
        st.dataframe(
            [
                {
                    "运行 ID": item["id"],
                    "实验 ID": item["experiment_id"],
                    "名称": item["run_name"],
                    "状态": item["run_status"],
                    "样本总数": item["sample_total"],
                    "平均总分": item["avg_overall_score"],
                    "平均幻觉率": item["avg_hallucination_risk"],
                }
                for item in runs
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("暂无实验记录。")
except APIError as exc:
    st.error(str(exc))
