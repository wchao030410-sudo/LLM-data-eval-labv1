import sys
from pathlib import Path

import pandas as pd
import streamlit as st

FRONTEND_DIR = Path(__file__).resolve().parents[1]
if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

from api_client import APIClient, APIError, cached_datasets, save_uploaded_file
from ui import apply_base_style, hero, info_card, panel_title

apply_base_style()
hero("数据集管理", "查看 Search QA 样本、按类别筛选，并支持本地 CSV 或 JSON 导入。", kicker="数据工作台")

client = APIClient()
datasets = cached_datasets(client.base_url)

if not datasets:
    st.warning("暂无数据集，请先执行 seed 脚本或创建数据集。")
    default_dataset = None
else:
    dataset_options = {item["name"]: item for item in datasets}
    default_dataset = st.selectbox("选择数据集", list(dataset_options.keys()))

if st.button("刷新数据集缓存"):
    st.cache_data.clear()
    st.rerun()

panel_title("上传 CSV / JSON")
col1, col2 = st.columns([2, 1])
with col1:
    uploaded_file = st.file_uploader("上传样本文件", type=["csv", "json"])
with col2:
    dataset_name = st.text_input("新数据集名称", value="uploaded_search_qa")

if uploaded_file is not None and st.button("创建并导入数据集", use_container_width=True):
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

if default_dataset:
    selected_dataset = dataset_options[default_dataset]
    samples = client.list_samples(selected_dataset["id"])
    df = pd.DataFrame(samples)
    if not df.empty:
        stat1, stat2, stat3 = st.columns(3)
        with stat1:
            info_card("样本总数", str(len(df)), "当前数据集内的样本条数")
        with stat2:
            info_card("类别数", str(df["category"].nunique()), "可用于切片分析的类别数量")
        with stat3:
            info_card("难度层级", str(df["difficulty"].nunique()), "当前数据集覆盖的难度层级")

        df["标签"] = df["tags"].apply(lambda items: ", ".join(items))
        category_options = ["全部"] + sorted(df["category"].dropna().unique().tolist())
        difficulty_options = ["全部"] + sorted(df["difficulty"].dropna().unique().tolist())
        all_tags = sorted({tag for tags in df["tags"] for tag in tags})

        panel_title("筛选条件")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        selected_category = filter_col1.selectbox("类别", category_options)
        selected_difficulty = filter_col2.selectbox("难度", difficulty_options)
        selected_tags = filter_col3.multiselect("标签", all_tags)

        filtered = df.copy()
        if selected_category != "全部":
            filtered = filtered[filtered["category"] == selected_category]
        if selected_difficulty != "全部":
            filtered = filtered[filtered["difficulty"] == selected_difficulty]
        if selected_tags:
            filtered = filtered[filtered["tags"].apply(lambda tags: set(selected_tags).issubset(set(tags)))]

        panel_title("样本列表")
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

        panel_title("样本详情")
        sample_ids = filtered["id"].tolist()
        if sample_ids:
            sample_id = st.selectbox("选择样本", sample_ids)
            detail = next(item for item in samples if item["id"] == sample_id)
            left, right = st.columns([1.1, 1])
            with left:
                st.markdown("**问题**")
                st.write(detail["query"])
                st.markdown("**参考答案**")
                st.write(detail["reference_answer"])
                st.markdown("**标签 / 备注**")
                st.write(", ".join(detail["tags"]))
                st.caption(detail["notes"] or "暂无备注")
            with right:
                st.markdown("**上下文**")
                st.code(detail["context"])
        else:
            st.info("筛选后暂无样本。")
    else:
        st.info("该数据集没有样本。")
