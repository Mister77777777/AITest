from __future__ import annotations
import streamlit as st
from autotestdesign.config import load_config
from autotestdesign.ui.upload_panel import render_upload_tab
from autotestdesign.ui.risk_panel import render_risk_tab
from autotestdesign.ui.testcase_viewer import render_test_design_tab
from autotestdesign.ui.export_panel import render_export_tab


st.set_page_config(page_title="AutoTestDesign · AI 测试用例生成", layout="wide", page_icon="🧪")
st.title("🧪 AutoTestDesign · AI 驱动的测试用例生成器")

# 侧边栏展示配置信息
with st.sidebar:
    st.header("配置信息")
    try:
        cfg = load_config()
        st.caption(f"模型:`{cfg.model}`")
        st.caption(f"接入点:`{cfg.base_url or '—'}`")
        st.caption(f"温度:{cfg.temperature}")
        if not cfg.api_key:
            st.warning("未配置 API Key,LLM 相关功能会降级为规则/算法兜底。")
    except Exception as e:
        st.error(f"加载配置失败:{e}")

# 四个主功能 Tab
tab_input, tab_risk, tab_design, tab_export = st.tabs(
    ["📥 需求录入", "📊 风险分析", "🧪 测试设计", "📤 导出"]
)

with tab_input:
    render_upload_tab()
with tab_risk:
    render_risk_tab()
with tab_design:
    render_test_design_tab()
with tab_export:
    render_export_tab()
