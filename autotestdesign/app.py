from __future__ import annotations
import streamlit as st
from autotestdesign.config import load_config
from autotestdesign.ui.theme import inject_theme, render_masthead, render_footer
from autotestdesign.ui.upload_panel import render_upload_tab
from autotestdesign.ui.risk_panel import render_risk_tab
from autotestdesign.ui.testcase_viewer import render_test_design_tab
from autotestdesign.ui.export_panel import render_export_tab


st.set_page_config(
    page_title="AutoTestDesign",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 注入编辑风格主题(字体 + 细节 CSS)
inject_theme()

# 刊头:kicker + 衬线大字 + 细线副标题
render_masthead()

# 侧边栏:只保留必要元数据,全部用 mono 字体呈现
model_name = ""
endpoint = ""
with st.sidebar:
    st.header("运行时")
    try:
        cfg = load_config()
        model_name = cfg.model
        endpoint = cfg.base_url or "—"
        st.caption(f"MODEL   {cfg.model}")
        st.caption(f"HOST    {cfg.base_url or '—'}")
        st.caption(f"TEMP    {cfg.temperature}")
        st.caption(f"API     {'已配置' if cfg.api_key else '未配置 · 降级规则'}")
        if not cfg.api_key:
            st.warning("未配置 API Key,LLM 相关功能会降级为规则/算法兜底。")
    except Exception as e:
        st.error(f"加载配置失败:{e}")

# 四个主功能 Tab:数字序号 + 细点分隔,替代 emoji
tab_input, tab_risk, tab_design, tab_export = st.tabs(
    [
        "01  需求录入",
        "02  风险分析",
        "03  测试设计",
        "04  导出",
    ]
)

with tab_input:
    render_upload_tab()
with tab_risk:
    render_risk_tab()
with tab_design:
    render_test_design_tab()
with tab_export:
    render_export_tab()

render_footer(model=model_name, endpoint=endpoint)
