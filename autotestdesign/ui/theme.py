"""编辑类极简主题:注入 Google Fonts + 结构化 CSS。

设计方向:Swiss editorial × architectural 审美。
- 字体:Fraunces(可变衬线,标题)+ IBM Plex Sans(正文)+ IBM Plex Mono(数据/代码)
- 色板:象牙纸面 + 墨黑 + 单一锈红强调色(避免紫色渐变等俗套)
- 细节:左侧 2px 色条代替填充色块、硬朗方形按钮、细分隔线、适度微动效
"""
from __future__ import annotations
import streamlit as st


_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,300;9..144,400;9..144,500;9..144,700&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Serif+SC:wght@400;500;700&family=Noto+Sans+SC:wght@300;400;500&display=swap" rel="stylesheet">

<style>
:root {
  --paper:      #F7F5F0;
  --paper-pure: #FEFDFA;
  --ink:        #1A1A1A;
  --ink-soft:   #5C5852;
  --ink-faint:  #8E8880;
  --rule:       #D5D0C5;
  --accent:     #B5482E;
  --accent-soft:#F0DCD0;
  --amber:      #C69214;
  --font-serif: 'Fraunces', 'Noto Serif SC', 'Songti SC', Georgia, serif;
  --font-sans:  'IBM Plex Sans', 'Noto Sans SC', -apple-system, sans-serif;
  --font-mono:  'IBM Plex Mono', 'SF Mono', 'Menlo', monospace;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background: var(--paper) !important;
  color: var(--ink) !important;
  font-family: var(--font-sans) !important;
  font-weight: 300;
  letter-spacing: 0.005em;
}

#MainMenu, [data-testid="stStatusWidget"], footer, header[data-testid="stHeader"] {
  display: none !important;
}

[data-testid="stMainBlockContainer"] {
  padding-top: 3rem !important;
  max-width: 1180px;
}

h1 {
  font-family: var(--font-serif) !important;
  font-weight: 400 !important;
  font-variation-settings: "opsz" 144, "SOFT" 30;
  letter-spacing: -0.03em !important;
  font-size: 3.25rem !important;
  line-height: 1.05 !important;
  margin-bottom: 0.25rem !important;
  color: var(--ink) !important;
}

h2 {
  font-family: var(--font-serif) !important;
  font-weight: 500 !important;
  font-variation-settings: "opsz" 36;
  letter-spacing: -0.015em !important;
  font-size: 1.75rem !important;
  margin-top: 1.5rem !important;
  color: var(--ink) !important;
}

h3 {
  font-family: var(--font-mono) !important;
  font-weight: 500 !important;
  font-size: 0.78rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: var(--accent) !important;
  margin-top: 1.75rem !important;
  margin-bottom: 1rem !important;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--rule);
}

p, li, label, span, div {
  font-family: var(--font-sans) !important;
}

code, kbd, pre, tt {
  font-family: var(--font-mono) !important;
  font-size: 0.88rem !important;
}

.atd-kicker {
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.25em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 500;
  display: block;
  margin-bottom: 0.5rem;
}

.atd-sub {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  letter-spacing: 0.08em;
  color: var(--ink-soft);
  margin-top: 0.5rem;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--rule);
}

.atd-sub span.sep {
  color: var(--rule);
  margin: 0 0.75rem;
}

[data-baseweb="tab-list"] {
  gap: 0 !important;
  border-bottom: 1px solid var(--rule) !important;
  padding-left: 0 !important;
  margin-bottom: 2rem !important;
}

[data-baseweb="tab"] {
  font-family: var(--font-sans) !important;
  font-size: 0.95rem !important;
  font-weight: 400 !important;
  letter-spacing: 0.02em !important;
  color: var(--ink-soft) !important;
  padding: 0.75rem 1.75rem 1rem 0 !important;
  margin-right: 1.5rem !important;
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  transition: color 0.2s ease, border-color 0.2s ease;
}

[data-baseweb="tab"]:hover {
  color: var(--ink) !important;
}

[data-baseweb="tab"][aria-selected="true"] {
  color: var(--accent) !important;
  border-bottom-color: var(--accent) !important;
  font-weight: 500 !important;
}

[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
  background: transparent !important;
  height: 0 !important;
}

[data-testid="stBaseButton-primary"] {
  background: var(--ink) !important;
  color: var(--paper-pure) !important;
  border: 1px solid var(--ink) !important;
  border-radius: 0 !important;
  font-family: var(--font-mono) !important;
  font-weight: 500 !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.12em !important;
  text-transform: uppercase !important;
  padding: 0.75rem 1.5rem !important;
  transition: all 0.25s ease !important;
  box-shadow: none !important;
}

[data-testid="stBaseButton-primary"]:hover {
  background: var(--accent) !important;
  border-color: var(--accent) !important;
  transform: translateY(-1px);
}

[data-testid="stBaseButton-secondary"] {
  background: transparent !important;
  color: var(--ink) !important;
  border: 1px solid var(--ink) !important;
  border-radius: 0 !important;
  font-family: var(--font-mono) !important;
  font-weight: 400 !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.1em !important;
  padding: 0.6rem 1.25rem !important;
  box-shadow: none !important;
  transition: all 0.2s ease !important;
}

[data-testid="stBaseButton-secondary"]:hover {
  background: var(--ink) !important;
  color: var(--paper-pure) !important;
}

[data-testid="stDownloadButton"] button {
  background: transparent !important;
  color: var(--ink) !important;
  border: 1px solid var(--rule) !important;
  border-radius: 0 !important;
  font-family: var(--font-mono) !important;
  letter-spacing: 0.08em !important;
  text-transform: none !important;
  padding: 0.7rem 1.25rem !important;
  text-align: left !important;
  justify-content: flex-start !important;
}

[data-testid="stDownloadButton"] button:hover {
  border-color: var(--ink) !important;
  background: var(--paper-pure) !important;
}

[data-testid="stSidebar"] {
  background: var(--paper-pure) !important;
  border-right: 1px solid var(--rule) !important;
}

[data-testid="stSidebar"] > div {
  padding-top: 3rem !important;
}

[data-testid="stSidebar"] h2 {
  font-family: var(--font-serif) !important;
  font-size: 1.1rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.01em !important;
  margin-bottom: 1.25rem !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
  font-family: var(--font-mono) !important;
  font-size: 0.78rem !important;
  color: var(--ink-soft) !important;
  letter-spacing: 0.02em;
  line-height: 1.7 !important;
}

[data-testid="stAlert"],
[data-testid="stInfo"],
[data-testid="stSuccess"],
[data-testid="stWarning"],
[data-testid="stError"] {
  background: transparent !important;
  border-radius: 0 !important;
  padding: 0.75rem 0 0.75rem 1rem !important;
  font-family: var(--font-sans) !important;
  box-shadow: none !important;
}

[data-testid="stInfo"] {
  border-left: 2px solid var(--ink-soft) !important;
  color: var(--ink-soft) !important;
}

[data-testid="stSuccess"] {
  border-left: 2px solid var(--accent) !important;
}

[data-testid="stWarning"] {
  border-left: 2px solid var(--amber) !important;
}

[data-testid="stError"] {
  border-left: 2px solid #8B2B1E !important;
}

[data-testid="stDataFrame"] {
  border: 1px solid var(--rule) !important;
  border-radius: 0 !important;
  font-family: var(--font-mono) !important;
}

[data-testid="stDataFrame"] * {
  font-family: var(--font-mono) !important;
  font-size: 0.82rem !important;
}

[data-testid="stDataFrame"] [role="columnheader"] {
  background: var(--paper) !important;
  font-weight: 500 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  font-size: 0.7rem !important;
  color: var(--ink) !important;
  border-bottom: 1px solid var(--ink) !important;
}

div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-baseweb="select"] > div {
  border-radius: 0 !important;
  border: 1px solid var(--rule) !important;
  background: var(--paper-pure) !important;
  font-family: var(--font-mono) !important;
  font-size: 0.88rem !important;
  color: var(--ink) !important;
  transition: border-color 0.2s ease;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--ink) !important;
  box-shadow: none !important;
}

div[role="radiogroup"] > label {
  background: transparent !important;
  border: 1px solid var(--rule) !important;
  border-radius: 0 !important;
  padding: 0.5rem 1rem !important;
  font-family: var(--font-mono) !important;
  font-size: 0.82rem !important;
  letter-spacing: 0.04em !important;
  color: var(--ink-soft) !important;
  transition: all 0.2s ease;
}

div[role="radiogroup"] > label:has(input:checked) {
  border-color: var(--ink) !important;
  background: var(--ink) !important;
  color: var(--paper-pure) !important;
}

[data-testid="stFileUploader"] section {
  background: var(--paper-pure) !important;
  border: 1px dashed var(--ink-faint) !important;
  border-radius: 0 !important;
  padding: 1.5rem !important;
}

[data-testid="stFileUploader"] section:hover {
  border-color: var(--ink) !important;
}

[data-testid="stToggle"] label > div > div {
  background: var(--rule) !important;
}

[data-testid="stCheckbox"] label > div:first-child,
[data-testid="stToggle"] label > div:first-child {
  border-radius: 2px !important;
}

[data-testid="stExpander"] {
  border: 1px solid var(--rule) !important;
  border-radius: 0 !important;
  background: var(--paper-pure) !important;
}

[data-testid="stExpander"] summary {
  font-family: var(--font-mono) !important;
  font-size: 0.85rem !important;
  letter-spacing: 0.04em !important;
  padding: 0.75rem 1rem !important;
}

hr {
  border: none !important;
  border-top: 1px solid var(--rule) !important;
  margin: 2rem 0 !important;
}

[data-testid="stSpinner"] > div > div {
  border-color: var(--ink-faint) !important;
  border-top-color: var(--accent) !important;
}

[data-testid="stSubheader"] {
  font-family: var(--font-mono) !important;
  font-size: 0.72rem !important;
  letter-spacing: 0.2em !important;
  text-transform: uppercase !important;
  color: var(--accent) !important;
  font-weight: 500 !important;
  margin-bottom: 0.75rem !important;
  margin-top: 1.5rem !important;
}

main > div {
  animation: atd-fade 0.5s ease-out;
}

@keyframes atd-fade {
  from { opacity: 0; transform: translateY(6px); }
  to   { opacity: 1; transform: translateY(0); }
}

[data-testid="stTabs"] > div:last-child > div {
  animation: atd-tab-fade 0.35s ease-out;
}

@keyframes atd-tab-fade {
  from { opacity: 0; }
  to   { opacity: 1; }
}

[data-testid="stBarChart"] {
  background: var(--paper-pure);
  padding: 1rem;
  border: 1px solid var(--rule);
}

.atd-footer {
  margin-top: 4rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--rule);
  font-family: var(--font-mono);
  font-size: 0.7rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--ink-faint);
  display: flex;
  justify-content: space-between;
}
</style>
"""


def inject_theme() -> None:
    """在页面顶端注入主题 CSS。放在 app.py 最靠前位置调用。"""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_masthead() -> None:
    """渲染编辑风格刊头:kicker + 大字标题 + 细线分隔的副标题。"""
    st.markdown(
        """
        <span class="atd-kicker">AutoTestDesign · 0.1</span>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("# AI 驱动的测试用例生成器")
    st.markdown(
        """
        <div class="atd-sub">
          FR1 — FR7<span class="sep">·</span>ISO/IEC/IEEE 29119-4<span class="sep">·</span>ISTQB Foundation
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_footer(model: str = "", endpoint: str = "") -> None:
    """编辑风格页脚:左边版本号,右边 LLM 接入点。"""
    st.markdown(
        f"""
        <div class="atd-footer">
          <span>Assignment 2 · Final Project</span>
          <span>{model} {'· ' + endpoint if endpoint else ''}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
