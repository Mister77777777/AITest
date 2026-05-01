from __future__ import annotations
import tempfile
from pathlib import Path
import streamlit as st
from autotestdesign.core.parsing import parse_csv, parse_text_block
from autotestdesign.examples.loader import list_examples, load_example
from autotestdesign.ui.state import get_session


def render_upload_tab() -> None:
    """FR1 需求录入面板:支持内置示例、上传文件、手动输入三种方式。"""
    session = get_session()
    st.subheader("FR1 · 需求录入")

    mode = st.radio(
        "录入方式",
        options=["内置示例", "上传文件", "手动输入"],
        horizontal=True,
    )

    if mode == "内置示例":
        choice = st.selectbox("选择示例", list_examples())
        if st.button("载入示例", type="primary"):
            session.requirements = load_example(choice)
            st.success(f"已从 `{choice}` 载入 {len(session.requirements)} 条需求。")

    elif mode == "上传文件":
        up = st.file_uploader("选择 CSV / TXT / MD 文件", type=["csv", "txt", "md"])
        if up is not None and st.button("解析上传文件"):
            suffix = Path(up.name).suffix
            with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=suffix) as tmp:
                tmp.write(up.read())
                tmp_path = Path(tmp.name)
            if suffix == ".csv":
                session.requirements = parse_csv(tmp_path)
            else:
                session.requirements = parse_text_block(tmp_path.read_text())
            st.success(f"已解析 {len(session.requirements)} 条需求。")

    else:
        text = st.text_area("粘贴需求文本(空行分隔多条需求)", height=220)
        if st.button("解析文本"):
            session.requirements = parse_text_block(text)
            st.success(f"已解析 {len(session.requirements)} 条需求。")

    if session.requirements:
        import pandas as pd
        # 用 DataFrame 展示解析后的需求概览
        df = pd.DataFrame([
            {
                "ID": r.id,
                "需求原文": r.raw_text,
                "类别": r.category,
                "字段数": len(r.input_fields),
                "条件数": len(r.conditions),
            }
            for r in session.requirements
        ])
        st.dataframe(df, use_container_width=True)
