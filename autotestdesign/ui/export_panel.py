from __future__ import annotations
import tempfile
from pathlib import Path
import streamlit as st
from autotestdesign.core.export import to_json, to_csv, to_xlsx
from autotestdesign.ui.state import get_session


def render_export_tab() -> None:
    """FR6 导出面板:JSON / CSV / Excel + 预览。"""
    session = get_session()
    st.subheader("FR6 · 导出")
    if not session.suite:
        st.info("请先在「测试设计」页运行流水线以生成测试套件。")
        return

    # 下载 JSON 格式
    st.download_button(
        "⬇ 下载 JSON",
        data=to_json(session.suite).encode("utf-8"),
        file_name="testsuite.json",
        mime="application/json",
    )

    # 下载 CSV 格式
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        to_csv(session.suite, Path(tmp.name))
        csv_bytes = Path(tmp.name).read_bytes()
    st.download_button(
        "⬇ 下载 CSV",
        data=csv_bytes,
        file_name="testsuite.csv",
        mime="text/csv",
    )

    # 下载 Excel 格式
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        to_xlsx(session.suite, Path(tmp.name))
        xlsx_bytes = Path(tmp.name).read_bytes()
    st.download_button(
        "⬇ 下载 Excel",
        data=xlsx_bytes,
        file_name="testsuite.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # 前 5 条用例预览
    st.markdown("**前 5 条用例预览:**")
    for c in session.suite.cases[:5]:
        with st.expander(f"{c.id} — {c.technique} — {c.priority}"):
            st.json(c.model_dump())
