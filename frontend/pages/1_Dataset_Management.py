import sys
from pathlib import Path

import pandas as pd
import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, APIError, cached_datasets, save_uploaded_file
from ui import apply_base_style, feature_card, hero, info_card, panel_title, status_banner, text_panel

apply_base_style()
hero("数据集管理", "围绕样本导入、切片筛选和逐条检查，建立一个更适合评测任务的数据操作面板。", kicker="数据工作台")

client = APIClient()
datasets = cached_datasets(client.base_url)

if not datasets:
    status_banner("warning", "当前没有可用数据集", "先执行 seed 脚本，或者在本页上传 CSV / JSON 建一个新的数据集。")
    st.stop()

dataset_options = {item["name"]: item for item in datasets}
toolbar_left, toolbar_right = st.columns([1.35, 0.65])
with toolbar_left:
    default_dataset = st.selectbox("选择数据集", list(dataset_options.keys()))
with toolbar_right:
    st.write("")
    st.write("")
    if st.button("刷新数据集缓存", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

selected_dataset = dataset_options[default_dataset]

panel_title("数据入口", "把上传动作和当前选中数据集信息放在同一层，减少来回跳转。", eyebrow="Ingest")
intake_col, meta_col = st.columns([1.2, 0.8])
with intake_col:
    with st.form("dataset_upload_form"):
        uploaded_file = st.file_uploader("上传样本文件", type=["csv", "json"])
        dataset_name = st.text_input("新数据集名称", value="uploaded_search_qa")
        upload_submitted = st.form_submit_button("创建并导入数据集", use_container_width=True)
with meta_col:
    feature_card(
        "当前选中数据集",
        selected_dataset.get("description") or "当前数据集可用于样本检索、实验运行和报告导出。",
        eyebrow="Selected Dataset",
        meta="{name} / {status}".format(
            name=selected_dataset.get("name", "unknown"),
            status=selected_dataset.get("status", "active"),
        ),
    )
    text_panel(
        "导入建议",
        "CSV 更适合快速批量整理；JSON 更适合保留结构化字段。上传后会自动写入项目本地数据目录。",
        eyebrow="Import Notes",
        meta="CSV / JSON",
    )

if upload_submitted and uploaded_file is not None:
    try:
        dataset = client.create_dataset(
            {
                "name": dataset_name,
                "description": "来自 Streamlit 上传",
                "source_type": uploaded_file.name.rsplit(".", 1)[-1].lower(),
                "source_path": "",
                "status": "active",
            }
        )
        saved_path = save_uploaded_file(uploaded_file, "data/uploads")
        client.import_samples(dataset["id"], saved_path)
        st.success("数据集已导入。")
        st.cache_data.clear()
        st.rerun()
    except APIError as exc:
        st.error(str(exc))

samples = client.list_samples(selected_dataset["id"])
df = pd.DataFrame(samples)
if df.empty:
    status_banner("info", "当前数据集还没有样本", "可以直接在上方上传 CSV / JSON，或者先执行演示数据 seed。")
    st.stop()

df["标签"] = df["tags"].apply(lambda items: ", ".join(items))
all_tags = sorted({tag for tags in df["tags"] for tag in tags})

summary_cols = st.columns(4)
with summary_cols[0]:
    info_card("样本总数", str(len(df)), "当前数据集内的样本条数。", tone="cobalt")
with summary_cols[1]:
    info_card("类别数", str(df["category"].nunique()), "可用于切片分析的类别数量。", tone="cyan")
with summary_cols[2]:
    info_card("难度层级", str(df["difficulty"].nunique()), "当前数据集覆盖的难度层级。", tone="emerald")
with summary_cols[3]:
    info_card("标签种类", str(len(all_tags)), "当前数据集包含的标签总类数。", tone="amber")

panel_title("筛选条件", "用关键词、类别、难度和标签快速收窄样本范围。", eyebrow="Filter")
filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)
query_keyword = filter_col1.text_input("关键词检索")
selected_category = filter_col2.selectbox("类别", ["全部"] + sorted(df["category"].dropna().unique().tolist()))
selected_difficulty = filter_col3.selectbox("难度", ["全部"] + sorted(df["difficulty"].dropna().unique().tolist()))
selected_tags = filter_col4.multiselect("标签", all_tags)

filtered = df.copy()
if query_keyword:
    filtered = filtered[filtered["query"].str.contains(query_keyword, case=False, na=False)]
if selected_category != "全部":
    filtered = filtered[filtered["category"] == selected_category]
if selected_difficulty != "全部":
    filtered = filtered[filtered["difficulty"] == selected_difficulty]
if selected_tags:
    filtered = filtered[filtered["tags"].apply(lambda tags: set(selected_tags).issubset(set(tags)))]

panel_title("样本视图", "默认展示问题文本、类别、难度和标签，方便直接决定下一步实验切片。", eyebrow="Dataset Table")
st.dataframe(
    filtered[["id", "query", "category", "difficulty", "标签", "created_at"]].rename(
        columns={
            "id": "样本 ID",
            "query": "问题",
            "category": "类别",
            "difficulty": "难度",
            "created_at": "创建时间",
        }
    ),
    use_container_width=True,
    hide_index=True,
)

panel_title("样本详情", "把问答主体和上下文拆开看，减少信息互相挤压。", eyebrow="Inspect")
sample_ids = filtered["id"].tolist()
if not sample_ids:
    status_banner("info", "筛选后没有命中样本", "放宽关键词、难度或标签条件后，再查看样本详情。")
    st.stop()

sample_id = st.selectbox("选择样本", sample_ids)
detail = next(item for item in samples if item["id"] == sample_id)
detail_tabs = st.tabs(["问答结构", "上下文"])
with detail_tabs[0]:
    left, right = st.columns([1, 1])
    with left:
        text_panel("问题", detail["query"], eyebrow="Query", meta="Sample #{sample_id}".format(sample_id=detail["id"]))
        text_panel("参考答案", detail["reference_answer"], eyebrow="Reference", meta=detail.get("category", "unknown"))
    with right:
        text_panel("标签", ", ".join(detail["tags"]) or "无", eyebrow="Tags", meta=detail.get("difficulty", "unknown"))
        text_panel("备注", detail["notes"] or "暂无备注", eyebrow="Notes")
with detail_tabs[1]:
    st.code(detail["context"] or "暂无上下文", language="text")
