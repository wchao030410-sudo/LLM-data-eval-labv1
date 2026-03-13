import sys
from pathlib import Path

import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, APIError, cached_datasets, cached_prompts
from ui import apply_base_style, hero, info_card, panel_title

apply_base_style()
hero("Prompt 实验", "配置数据集、Prompt 版本与模型参数，批量运行离线实验。", kicker="实验工作台")

client = APIClient()
datasets = cached_datasets(client.base_url)
prompts, version_map = cached_prompts(client.base_url)

if not datasets or not prompts:
    st.warning("需要先有数据集和 Prompt。先运行 seed 脚本。")
    st.stop()

dataset_options = {item["name"]: item for item in datasets}
version_options = {}
for prompt in prompts:
    for version in version_map.get(prompt["id"], []):
        label = "{name} / {version}".format(name=prompt["name"], version=version["version"])
        version_options[label] = {"prompt": prompt, "version": version}

panel_title("实验配置")
with st.form("run_experiment_form"):
    dataset_name = st.selectbox("数据集", list(dataset_options.keys()))
    version_label = st.selectbox("Prompt 版本", list(version_options.keys()))
    model_name = st.text_input("模型名", value="glm-4.5-air")
    temperature = st.slider("温度参数", 0.0, 1.0, 0.2, 0.1)
    max_tokens = st.slider("最大输出长度", 64, 1024, 256, 32)
    judge_mode = st.selectbox("评审模式", ["rule", "llm_judge"])
    experiment_name = st.text_input("实验名称", value="search_qa_eval_run")
    experiment_desc = st.text_input("实验描述", value="来自 Streamlit 的批量实验")
    submitted = st.form_submit_button("运行实验", use_container_width=True)

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
        st.success("实验完成")
        summary_cols = st.columns(4)
        with summary_cols[0]:
            info_card("运行 ID", str(run["id"]), "本次 Experiment Run 的唯一标识")
        with summary_cols[1]:
            info_card("运行状态", str(run["run_status"]), "后端返回的最终状态")
        with summary_cols[2]:
            info_card("完成样本数", str(run["sample_completed"]), "本次已完成的样本条数")
        with summary_cols[3]:
            info_card("平均总分", "{:.3f}".format(run["avg_overall_score"]), "本次 Run 的平均 overall score")
        st.json(run)
        st.cache_data.clear()
    except APIError as exc:
        st.error(str(exc))

panel_title("最近实验摘要")
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
