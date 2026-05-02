from __future__ import annotations
import pandas as pd
import streamlit as st
from autotestdesign.config import load_config
from autotestdesign.llm.client import LLMClient
from autotestdesign.core.pipeline import run_pipeline
from autotestdesign.ui.state import get_session
from autotestdesign.ui.state_diagram import render_state_diagram_section


def _build_llm_or_none():
    """构建 LLM 客户端,无 API Key 时返回 None(退化到规则/算法兜底)。"""
    try:
        cfg = load_config()
        if not cfg.api_key:
            return None
        return LLMClient(cfg)
    except Exception:
        return None


def render_test_design_tab() -> None:
    """FR3/FR4/FR5/FR7 面板:顶部配置栏 + 左状态机/右结果 两栏填满页面。"""
    session = get_session()
    st.markdown(
        '<div class="atd-section">FR3 · FR4 · FR5 · FR7 · 测试设计</div>'
        '<h2>流水线配置与结果</h2>',
        unsafe_allow_html=True,
    )

    if not session.requirements:
        st.info("请先在「需求录入」页载入或输入需求。")
        return

    # 顶部配置栏:四个等宽控件
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1], gap="medium")
    with c1:
        use_llm = st.toggle("启用 LLM", value=True, help="用 LLM 生成风险理由与 Oracle")
    with c2:
        include_stt = st.checkbox("状态转换 (FR4)", value=True)
    with c3:
        max_cases = st.number_input("最大用例数", min_value=0, value=0, help="0 = 不限")
    with c4:
        stt_req_id = st.selectbox(
            "状态机挂载 ID",
            options=[r.id for r in session.requirements],
            disabled=not include_stt,
        )

    st.write("")

    # 左状态机 / 右运行按钮与进度区
    if include_stt:
        col_sm, col_go = st.columns([3, 2], gap="large")
        with col_sm:
            sm = render_state_diagram_section()
        with col_go:
            st.markdown('<div class="atd-section">流水线</div>', unsafe_allow_html=True)
            st.markdown(
                """
                <div style="color:#6E6E73; font-size:0.95rem; line-height:1.6;">
                  将执行:LLM 自动结构化 → 风险打分 → 等价类 / 边界值 / 判定表 →
                  状态转换 → Oracle 合成 → 加权覆盖优化。
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.write("")
            run = st.button("运行完整流水线", type="primary", use_container_width=True)
    else:
        sm = None
        st.markdown(
            """
            <div style="color:#6E6E73; font-size:0.95rem; line-height:1.6;">
              将执行:LLM 自动结构化 → 风险打分 → 等价类 / 边界值 / 判定表 →
              Oracle 合成 → 加权覆盖优化。
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")
        run = st.button("运行完整流水线", type="primary", use_container_width=True)

    if run:
        llm = _build_llm_or_none() if use_llm else None
        with st.spinner("正在运行流水线..."):
            suite = run_pipeline(
                session.requirements,
                llm=llm,
                state_machine=sm,
                state_machine_requirement_id=stt_req_id if include_stt else None,
                optimize_max_cases=max_cases or None,
            )
        session.suite = suite
        session.requirements = [r for r in session.requirements]
        st.success(f"已生成 {len(suite.cases)} 条测试用例")

    if not session.suite:
        return

    # 结果区:顶部覆盖率指标卡 + 下方按技术分 Tab 的大表
    st.write("")
    st.markdown('<div class="atd-section">生成结果</div>', unsafe_allow_html=True)

    # 覆盖率卡片 + 各技术用例数
    by_tech: dict[str, int] = {}
    for c in session.suite.cases:
        by_tech[c.technique] = by_tech.get(c.technique, 0) + 1

    cov_cols = st.columns(5, gap="small")
    with cov_cols[0]:
        req_cov = session.suite.coverage.get("requirement_coverage", 0.0)
        _mini_metric("需求覆盖", f"{req_cov * 100:.0f}%", "#0071E3")
    for i, (tech, label, color) in enumerate(
        [
            ("EP", "等价类", "#34C759"),
            ("BVA", "边界值", "#FF9500"),
            ("DT", "判定表", "#AF52DE"),
            ("STT", "状态转换", "#FF2D55"),
        ]
    ):
        with cov_cols[i + 1]:
            _mini_metric(label, str(by_tech.get(tech, 0)), color)

    st.write("")

    techniques = sorted(by_tech.keys())
    tech_tabs = st.tabs(techniques)
    for tab, tech in zip(tech_tabs, techniques):
        with tab:
            rows = [c for c in session.suite.cases if c.technique == tech]
            df = pd.DataFrame([{
                "ID": c.id,
                "需求": c.requirement_id,
                "优先级": c.priority,
                "输入": str(c.inputs),
                "预期结果": c.expected_result,
                "标签": ", ".join(c.tags),
            } for c in rows])
            st.dataframe(df, use_container_width=True, height=460, hide_index=True)


def _mini_metric(label: str, value: str, color: str) -> None:
    """紧凑指标卡(覆盖率栏用)。"""
    st.markdown(
        f"""
        <div class="atd-minicard">
          <div class="atd-minicard-label">{label}</div>
          <div class="atd-minicard-value" style="color:{color}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
