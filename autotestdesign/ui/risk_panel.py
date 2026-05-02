from __future__ import annotations
import pandas as pd
import streamlit as st
from autotestdesign.ui.state import get_session


def render_risk_tab() -> None:
    """FR2 风险分析面板:顶部四个指标卡 + 主表 + 右侧优先级分布。"""
    session = get_session()
    st.markdown(
        '<div class="atd-section">FR2 · 风险分析与优先级</div>'
        '<h2>风险画像</h2>',
        unsafe_allow_html=True,
    )

    reqs_with_risk = [r for r in session.requirements if r.risk]
    if not reqs_with_risk:
        st.info("暂无风险数据,请先在「测试设计」页运行流水线。")
        return

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

    # 顶部 4 个指标卡
    total = len(df)
    high = int((df["优先级"] == "High").sum())
    medium = int((df["优先级"] == "Medium").sum())
    low = int((df["优先级"] == "Low").sum())
    avg_score = float(df["得分"].mean())

    m1, m2, m3, m4 = st.columns(4, gap="medium")
    with m1:
        _metric("总需求数", str(total), accent="#0071E3")
    with m2:
        _metric("高风险", str(high), accent="#FF3B30")
    with m3:
        _metric("中风险", str(medium), accent="#FF9500")
    with m4:
        _metric("平均得分", f"{avg_score:.1f}", accent="#34C759")

    st.write("")  # 呼吸

    # 主表 + 右侧分布图
    col_tbl, col_chart = st.columns([3, 2], gap="large")
    with col_tbl:
        st.markdown('<div class="atd-section">明细</div>', unsafe_allow_html=True)
        st.dataframe(df, use_container_width=True, height=420, hide_index=True)
    with col_chart:
        st.markdown('<div class="atd-section">优先级分布</div>', unsafe_allow_html=True)
        counts = df["优先级"].value_counts().reindex(["High", "Medium", "Low"]).fillna(0)
        st.bar_chart(counts, height=420, use_container_width=True)


def _metric(label: str, value: str, accent: str) -> None:
    """Apple 风指标小卡:标签上、数值下、左侧竖条强调色。"""
    st.markdown(
        f"""
        <div class="atd-metric">
          <div class="atd-metric-bar" style="background:{accent}"></div>
          <div class="atd-metric-body">
            <div class="atd-metric-label">{label}</div>
            <div class="atd-metric-value">{value}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
