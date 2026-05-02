from __future__ import annotations
import tempfile
from pathlib import Path
import streamlit as st
import pandas as pd
from autotestdesign.core.parsing import parse_csv, parse_text_block
from autotestdesign.examples.loader import list_examples, load_example
from autotestdesign.ui.state import get_session, render_workset_chip


def render_upload_tab() -> None:
    """FR1 需求录入面板:左栏录入控件,右栏当前需求表,充分占满横向空间。"""
    session = get_session()
    # 顶部持久状态条 — 切换到其他 tab 依然能看到
    render_workset_chip()

    # 左 2 : 右 3,左控件区紧凑,右侧展示占大头
    col_ctrl, col_view = st.columns([2, 3], gap="large")

    with col_ctrl:
        st.markdown(
            '<div class="atd-section">FR1 · 需求录入</div>'
            '<h2>选择需求来源</h2>',
            unsafe_allow_html=True,
        )

        mode = st.radio(
            "录入方式",
            options=["内置示例", "上传文件", "手动输入"],
            horizontal=True,
            label_visibility="collapsed",
        )

        st.write("")  # 小间隔

        if mode == "内置示例":
            choice = st.selectbox("示例集", list_examples(), label_visibility="collapsed")
            if st.button("载入示例", type="primary", use_container_width=True):
                session.requirements = load_example(choice)
                session.source_label = f"内置示例 · {choice}"
                session.suite = None  # 新数据源,清空旧套件避免串场
                st.success(f"已从 {choice} 载入 {len(session.requirements)} 条需求")
                st.rerun()

        elif mode == "上传文件":
            up = st.file_uploader(
                "拖拽 CSV / TXT / MD 文件",
                type=["csv", "txt", "md"],
                label_visibility="collapsed",
            )
            if up is not None and st.button("解析文件", type="primary", use_container_width=True):
                suffix = Path(up.name).suffix
                with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=suffix) as tmp:
                    tmp.write(up.read())
                    tmp_path = Path(tmp.name)
                if suffix == ".csv":
                    session.requirements = parse_csv(tmp_path)
                else:
                    session.requirements = parse_text_block(tmp_path.read_text())
                session.source_label = f"上传 · {up.name}"
                session.suite = None
                st.success(f"已解析 {len(session.requirements)} 条需求")
                st.rerun()

        else:
            text = st.text_area(
                "需求文本",
                placeholder="粘贴需求,空行分隔多条",
                height=260,
                label_visibility="collapsed",
            )
            if st.button("解析文本", type="primary", use_container_width=True):
                session.requirements = parse_text_block(text)
                session.source_label = "手动输入"
                session.suite = None
                st.success(f"已解析 {len(session.requirements)} 条需求")
                st.rerun()

    with col_view:
        st.markdown(
            '<div class="atd-section">当前工作集</div>'
            f'<h2>已载入 {len(session.requirements)} 条需求</h2>',
            unsafe_allow_html=True,
        )
        if session.requirements:
            df = pd.DataFrame([
                {
                    "ID": r.id,
                    "需求原文": r.raw_text,
                    "类别": r.category,
                    "字段": len(r.input_fields),
                    "条件": len(r.conditions),
                }
                for r in session.requirements
            ])
            st.dataframe(df, use_container_width=True, height=420, hide_index=True)
        else:
            st.info("尚未载入任何需求。请在左侧选择来源并提交。")
