from __future__ import annotations
import tempfile
from pathlib import Path
import streamlit as st
from autotestdesign.core.export import to_json, to_csv, to_xlsx
from autotestdesign.ui.state import get_session


def render_export_tab() -> None:
    """FR6 导出面板:3 列下载 + 右侧预览,充满横向。"""
    session = get_session()
    st.markdown(
        '<div class="atd-section">FR6 · 导出</div>'
        '<h2>下载与预览</h2>',
        unsafe_allow_html=True,
    )

    if not session.suite:
        st.info("请先在「测试设计」页运行流水线以生成测试套件。")
        return

    # 准备三种导出产物(懒加载一次)
    json_bytes = to_json(session.suite).encode("utf-8")
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        to_csv(session.suite, Path(tmp.name))
        csv_bytes = Path(tmp.name).read_bytes()
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        to_xlsx(session.suite, Path(tmp.name))
        xlsx_bytes = Path(tmp.name).read_bytes()

    # 下载卡片:三列等宽,占满横向
    c1, c2, c3 = st.columns(3, gap="large")
    with c1:
        _download_card(
            icon="{ }",
            title="JSON",
            desc="适用于 Test Management Tool、自动化脚本直接消费。",
            data=json_bytes,
            file_name="testsuite.json",
            mime="application/json",
        )
    with c2:
        _download_card(
            icon="━━━",
            title="CSV",
            desc="表格导入 Excel / Numbers / Google Sheets,便于人工审阅。",
            data=csv_bytes,
            file_name="testsuite.csv",
            mime="text/csv",
        )
    with c3:
        _download_card(
            icon="▦",
            title="Excel",
            desc="Excel 原生格式,样式与公式可继续加工。",
            data=xlsx_bytes,
            file_name="testsuite.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    st.write("")
    st.markdown('<div class="atd-section">预览</div>', unsafe_allow_html=True)

    preview_rows = session.suite.cases[:6]
    if not preview_rows:
        st.info("测试套件为空。")
        return

    # 2 列 × 3 行的小卡预览
    for row_idx in range(0, len(preview_rows), 2):
        cols = st.columns(2, gap="medium")
        for col, c in zip(cols, preview_rows[row_idx : row_idx + 2]):
            with col:
                with st.expander(f"{c.id}  ·  {c.technique}  ·  {c.priority}", expanded=False):
                    st.json(c.model_dump())


def _download_card(
    icon: str,
    title: str,
    desc: str,
    data: bytes,
    file_name: str,
    mime: str,
) -> None:
    """带图标、标题、描述、下载按钮的导出卡片。"""
    st.markdown(
        f"""
        <div class="atd-dlcard">
          <div class="atd-dlcard-icon">{icon}</div>
          <div class="atd-dlcard-title">{title}</div>
          <div class="atd-dlcard-desc">{desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.download_button(
        f"下载 {title}",
        data=data,
        file_name=file_name,
        mime=mime,
        use_container_width=True,
    )
