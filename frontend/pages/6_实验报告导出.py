import sys
from pathlib import Path

import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, APIError, cached_datasets, cached_prompts
from ui import apply_base_style, feature_card, hero, info_card, panel_title, status_banner, text_panel

apply_base_style()
hero("实验报告导出", "把两个 Prompt 版本的结果差异收敛成一份可阅读、可下载、可继续复盘的对比报告。", kicker="报告工作台")

client = APIClient()
datasets = cached_datasets(client.base_url)
prompts, version_map = cached_prompts(client.base_url)

if not datasets or not prompts:
    status_banner("warning", "缺少报告生成前置条件", "需要先有数据集、Prompt 版本，并且至少完成一次实验运行。")
    st.stop()

dataset_options = {item["name"]: item for item in datasets}
version_options = {}
for prompt in prompts:
    for version in version_map.get(prompt["id"], []):
        label = "{name} / {version}".format(name=prompt["name"], version=version["version"])
        version_options[label] = {"prompt": prompt, "version": version}

summary_cols = st.columns(3)
with summary_cols[0]:
    info_card("可选数据集", str(len(dataset_options)), "当前可用于报告生成的数据集数。", tone="cobalt")
with summary_cols[1]:
    info_card("Prompt 版本", str(len(version_options)), "可参与对比的 Prompt 版本总数。", tone="cyan")
with summary_cols[2]:
    info_card("导出格式", "2", "支持 Markdown 与 HTML。", tone="emerald")

config_col, note_col = st.columns([1.16, 0.84])
with config_col:
    panel_title("报告配置", "选择数据集与两个 Prompt 版本，生成对比报告。", eyebrow="Report Builder")
    with st.form("export_report_form"):
        dataset_name = st.selectbox("数据集", list(dataset_options.keys()))
        version_a_label = st.selectbox("Prompt 版本 A", list(version_options.keys()), index=0)
        version_b_label = st.selectbox("Prompt 版本 B", list(version_options.keys()), index=min(1, len(version_options) - 1))
        output_format = st.selectbox("导出格式", ["markdown", "html"])
        submitted = st.form_submit_button("生成对比报告", use_container_width=True)
with note_col:
    feature_card("生成条件", "只有当两个 Prompt 版本都已经在当前数据集上完成过至少一次实验运行时，才能形成有效对比。", eyebrow="Requirement", meta="Matched Runs Needed")
    text_panel("适合导出的场景", "Markdown 适合继续编辑和归档；HTML 适合直接分享和展示。", eyebrow="Usage", meta="MD / HTML")

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
        status_banner("success", "对比报告已生成", "摘要指标和完整内容已经返回，可以先预览，再直接下载。")
        col1, col2, col3 = st.columns(3)
        with col1:
            info_card("可对比样本量", str(summary["paired_sample_count"]), "两个 Prompt 版本都覆盖到的样本数量。", tone="cobalt")
        with col2:
            info_card("平均总分差值", "{:+.4f}".format(summary["avg_score_delta"]), "定义为 B 版本减 A 版本。", tone="cyan")
        with col3:
            info_card("重点 category", summary["top_improved_category"], "提升最明显的类别。", tone="emerald")

        panel_title("报告预览", "支持直接预览，也保留原始内容以便继续处理。", eyebrow="Preview")
        preview_tabs = st.tabs(["渲染预览", "原始内容"])
        with preview_tabs[0]:
            if output_format == "markdown":
                st.markdown(report["content"])
            else:
                st.components.v1.html(report["content"], height=720, scrolling=True)
        with preview_tabs[1]:
            language = "markdown" if output_format == "markdown" else "html"
            st.code(report["content"], language=language)

        st.download_button(
            label="下载报告",
            data=report["content"],
            file_name=report["filename"],
            mime=report["content_type"],
            use_container_width=True,
        )
    except APIError as exc:
        st.error(str(exc))
