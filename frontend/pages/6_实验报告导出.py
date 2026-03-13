import sys
from pathlib import Path

import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, APIError, cached_datasets, cached_prompts
from ui import apply_base_style, hero, info_card, panel_title

apply_base_style()
hero("实验报告导出", "选择两个 Prompt 版本，自动生成对比报告，并导出为 Markdown 或 HTML。", kicker="报告工作台")

client = APIClient()
datasets = cached_datasets(client.base_url)
prompts, version_map = cached_prompts(client.base_url)

if not datasets or not prompts:
    st.warning("需要先有数据集和 Prompt，并完成至少一次实验运行。")
    st.stop()

dataset_options = {item["name"]: item for item in datasets}
version_options = {}
for prompt in prompts:
    for version in version_map.get(prompt["id"], []):
        label = "{name} / {version}".format(name=prompt["name"], version=version["version"])
        version_options[label] = {"prompt": prompt, "version": version}

panel_title("报告配置")
st.caption("说明：只有当两个 Prompt 版本都已经在当前数据集上完成过至少一次实验运行时，才能生成对比报告。")
with st.form("export_report_form"):
    dataset_name = st.selectbox("数据集", list(dataset_options.keys()))
    version_a_label = st.selectbox("Prompt 版本 A", list(version_options.keys()), index=0)
    version_b_label = st.selectbox("Prompt 版本 B", list(version_options.keys()), index=min(1, len(version_options) - 1))
    output_format = st.selectbox("导出格式", ["markdown", "html"])
    submitted = st.form_submit_button("生成对比报告", use_container_width=True)

if submitted:
    try:
        dataset = dataset_options[dataset_name]
        version_a = version_options[version_a_label]["version"]
        version_b = version_options[version_b_label]["version"]
        report = client.export_prompt_comparison_report(
            {
                "dataset_id": dataset["id"],
                "prompt_version_a_id": version_a["id"],
                "prompt_version_b_id": version_b["id"],
                "output_format": output_format,
            }
        )

        summary = report["summary"]
        col1, col2, col3 = st.columns(3)
        with col1:
            info_card("可对比样本量", str(summary["paired_sample_count"]), "两个 Prompt 版本都覆盖到的样本数量")
        with col2:
            info_card("平均总分差值", "{:+.4f}".format(summary["avg_score_delta"]), "定义为 B 版本减 A 版本")
        with col3:
            info_card("重点 category", summary["top_improved_category"], "提升最明显的类别")

        panel_title("报告预览")
        if output_format == "markdown":
            st.code(report["content"], language="markdown")
        else:
            st.components.v1.html(report["content"], height=720, scrolling=True)

        st.download_button(
            label="下载报告",
            data=report["content"],
            file_name=report["filename"],
            mime=report["content_type"],
            use_container_width=True,
        )
    except APIError as exc:
        st.error(str(exc))
