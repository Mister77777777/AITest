from __future__ import annotations
import streamlit as st
from autotestdesign.config import load_config
from autotestdesign.ui.theme import inject_theme, render_hero, render_topbar
from autotestdesign.ui.upload_panel import render_upload_tab
from autotestdesign.ui.risk_panel import render_risk_tab
from autotestdesign.ui.testcase_viewer import render_test_design_tab
from autotestdesign.ui.export_panel import render_export_tab


st.set_page_config(
    page_title="AutoTestDesign",
    layout="wide",
    # 折叠并隐藏侧栏,整页留给主内容
    initial_sidebar_state="collapsed",
)

# 注入 Apple 风格主题
inject_theme()

# 读取配置以便状态条显示;失败不阻塞页面
model_name = ""
api_ok = False
try:
    cfg = load_config()
    model_name = cfg.model
    api_ok = bool(cfg.api_key)
except Exception:
    pass

# 右上浮动毛玻璃状态条
render_topbar(model=model_name, online=api_ok)

# Hero 主视觉
render_hero(api_ok=api_ok)

# 4 段 segmented control + 白色卡片
tab_input, tab_risk, tab_design, tab_export = st.tabs(
    ["需求录入", "风险分析", "测试设计", "导出"]
)

with tab_input:
    render_upload_tab()
with tab_risk:
    render_risk_tab()
with tab_design:
    render_test_design_tab()
with tab_export:
    render_export_tab()
