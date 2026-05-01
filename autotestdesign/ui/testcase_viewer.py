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
    """FR3/FR4/FR5/FR7 面板:配置、运行流水线、按技术分 Tab 展示用例。"""
    session = get_session()
    st.subheader("FR3/FR4/FR5/FR7 · 测试设计")

    if not session.requirements:
        st.info("请先在「需求录入」页载入或输入需求。")
        return

    col1, col2 = st.columns([1, 1])
    with col1:
        use_llm = st.toggle("使用 LLM 生成风险理由与 Oracle", value=True)
        max_cases = st.number_input("优化:最大用例数(0 = 不限)", min_value=0, value=0)
    with col2:
        include_stt = st.checkbox("包含状态转换(FR4)", value=True)

    # 状态机 DSL 编辑与图渲染(可选)
    sm = None
    stt_req_id = None
    if include_stt:
        sm = render_state_diagram_section()
        stt_req_id = st.text_input("将状态机挂到需求 ID", value=session.requirements[0].id)

    if st.button("▶ 运行完整流水线", type="primary"):
        llm = _build_llm_or_none() if use_llm else None
        with st.spinner("正在运行流水线..."):
            suite = run_pipeline(
                session.requirements,
                llm=llm,
                state_machine=sm,
                state_machine_requirement_id=stt_req_id,
                optimize_max_cases=max_cases or None,
            )
        session.suite = suite
        # 触发页面重绘:重新赋值以更新会话状态
        session.requirements = [r for r in session.requirements]
        st.success(f"已生成 {len(suite.cases)} 条测试用例。")

    if not session.suite:
        return

    st.markdown("---")
    # 按生成技术分 Tab 展示用例
    techniques = sorted({c.technique for c in session.suite.cases})
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
                "标签": ",".join(c.tags),
            } for c in rows])
            st.dataframe(df, use_container_width=True)

    # 展示覆盖率汇总
    st.markdown("**覆盖率:**" + ", ".join(f"{k}={v:.2f}" for k, v in session.suite.coverage.items()))
