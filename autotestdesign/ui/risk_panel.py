from __future__ import annotations
import pandas as pd
import streamlit as st
from autotestdesign.ui.state import get_session


def render_risk_tab() -> None:
    """FR2 风险分析面板:表格 + 优先级分布柱状图。"""
    session = get_session()
    st.subheader("FR2 · 风险分析与优先级")
    reqs_with_risk = [r for r in session.requirements if r.risk]
    if not reqs_with_risk:
        st.info("暂无风险数据。请先在「测试设计」页运行流水线。")
        return

    # 构建风险数据表格
    df = pd.DataFrame([
        {
            "ID": r.id,
            "需求摘要": r.raw_text[:80],
            "可能性": r.risk.likelihood,
            "影响": r.risk.impact,
            "得分": r.risk.score,
            "优先级": r.risk.priority,
            "理由": r.risk.rationale,
        }
        for r in reqs_with_risk
    ])
    st.dataframe(df, use_container_width=True)

    # 优先级分布柱状图
    counts = df["优先级"].value_counts().reindex(["High", "Medium", "Low"]).fillna(0)
    st.bar_chart(counts)
