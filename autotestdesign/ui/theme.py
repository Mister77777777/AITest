"""苹果生态风格主题:SF Pro / PingFang SC、云白底、系统蓝、圆角卡片、无分隔线。

设计原则:
- 无侧栏、无横线、无页脚小字
- Hero 大字标题 + 柔和副标题,集中视觉
- 内容区用白色圆角卡片,20px radius + 柔和多层阴影
- Tabs 作为 segmented control:药丸式胶囊背景 + 白色活动态
- 16-18px 基础字号,提升可读性
- 两种深浅状态:主文 #1D1D1F,次文 #6E6E73;仅在强调态用系统蓝
"""
from __future__ import annotations
import streamlit as st


_CSS = """
<style>
:root {
  --bg:          #F5F5F7;
  --card:        #FFFFFF;
  --ink:         #1D1D1F;
  --ink-2:       #424245;
  --ink-3:       #6E6E73;
  --hair:        #E8E8ED;
  --blue:        #0071E3;
  --blue-hover:  #0077ED;
  --blue-deep:   #0060C0;
  --green:       #34C759;
  --orange:      #FF9500;
  --red:         #FF3B30;
  --font-sf:     -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text",
                 "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei",
                 sans-serif;
  --font-mono:   "SF Mono", ui-monospace, "Menlo", "JetBrains Mono", monospace;
  --shadow-sm:   0 1px 2px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.02);
  --shadow-md:   0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.05);
  --shadow-lg:   0 4px 16px rgba(0,0,0,0.06), 0 16px 48px rgba(0,0,0,0.08);
  --radius-sm:   8px;
  --radius-md:   14px;
  --radius-lg:   20px;
  --radius-xl:   28px;
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
  background: var(--bg) !important;
  color: var(--ink) !important;
  font-family: var(--font-sf) !important;
  font-size: 17px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  letter-spacing: -0.003em;
}

/* 彻底隐藏侧栏、顶栏菜单、状态条、页脚 */
#MainMenu,
[data-testid="stStatusWidget"],
[data-testid="stToolbar"],
footer,
header[data-testid="stHeader"],
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"],
[data-testid="stSidebarNav"],
[data-testid="stSidebarHeader"] {
  display: none !important;
  visibility: hidden !important;
  width: 0 !important;
}

/* 主容器居中,两边均匀留白 */
[data-testid="stAppViewContainer"] > section {
  padding-left: 0 !important;
}

[data-testid="stMainBlockContainer"] {
  max-width: 1600px !important;
  width: 94vw !important;
  margin: 0 auto !important;
  padding-top: 3rem !important;
  padding-bottom: 5rem !important;
  padding-left: 2.5rem !important;
  padding-right: 2.5rem !important;
}

/* Hero 区:大字标题 + 柔和副标题 */
.atd-hero {
  text-align: center;
  margin-bottom: 2.5rem;
  padding: 0.5rem 0 1.5rem 0;
}

.atd-hero h1 {
  font-family: var(--font-sf) !important;
  font-weight: 700 !important;
  font-size: 3.75rem !important;
  letter-spacing: -0.035em !important;
  line-height: 1.05 !important;
  margin: 0 0 0.75rem 0 !important;
  color: var(--ink) !important;
  background: linear-gradient(180deg, #1D1D1F 0%, #424245 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.atd-hero .sub {
  font-size: 1.2rem !important;
  font-weight: 400 !important;
  color: var(--ink-3) !important;
  letter-spacing: -0.01em;
  line-height: 1.4;
  max-width: 780px;
  margin: 0 auto;
}

.atd-hero .badge {
  display: inline-block;
  margin-top: 1.5rem;
  padding: 6px 14px;
  background: rgba(0, 113, 227, 0.08);
  color: var(--blue);
  font-size: 0.85rem;
  font-weight: 500;
  border-radius: 100px;
  letter-spacing: 0;
}

.atd-hero .badge .dot {
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--green);
  margin-right: 6px;
  transform: translateY(-1px);
  box-shadow: 0 0 8px rgba(52, 199, 89, 0.5);
}

.atd-hero .badge.offline .dot {
  background: var(--orange);
  box-shadow: 0 0 8px rgba(255, 149, 0, 0.5);
}

/* 强制隐藏 Streamlit 自动生成的锚点链接 icon */
h1 a, h2 a, h3 a, h4 a {
  display: none !important;
}

/* 全局 headings 复位,避免被 Streamlit 默认样式覆盖 */
h1, h2, h3, h4, p, div, span, label {
  color: var(--ink) !important;
}

h2 {
  font-family: var(--font-sf) !important;
  font-weight: 600 !important;
  font-size: 1.9rem !important;
  letter-spacing: -0.02em !important;
  margin-top: 0 !important;
  margin-bottom: 1rem !important;
}

h3 {
  font-family: var(--font-sf) !important;
  font-weight: 600 !important;
  font-size: 1.15rem !important;
  letter-spacing: -0.01em !important;
  color: var(--ink) !important;
  text-transform: none !important;
  border: none !important;
  margin-top: 0 !important;
  margin-bottom: 0.75rem !important;
  padding-bottom: 0 !important;
}

/* 段落与标签 */
p, li, label, span, div {
  font-family: var(--font-sf) !important;
}

p {
  line-height: 1.55;
}

code, pre, kbd {
  font-family: var(--font-mono) !important;
  font-size: 0.92em !important;
}

/* Tabs:药丸式 segmented control */
[data-testid="stTabs"] {
  margin-top: 0;
}

[data-baseweb="tab-list"] {
  background: rgba(120, 120, 128, 0.08) !important;
  padding: 5px !important;
  border-radius: 14px !important;
  gap: 0 !important;
  width: fit-content !important;
  margin: 0 auto 2.5rem auto !important;
  border: none !important;
  display: inline-flex !important;
  position: relative;
  justify-content: center;
}

/* 让 tab-list 的父容器居中 */
[data-testid="stTabs"] > div:first-child {
  display: flex !important;
  justify-content: center !important;
}

[data-baseweb="tab"] {
  font-family: var(--font-sf) !important;
  font-size: 0.97rem !important;
  font-weight: 500 !important;
  letter-spacing: -0.005em !important;
  color: var(--ink-2) !important;
  background: transparent !important;
  border: none !important;
  padding: 8px 20px !important;
  border-radius: 10px !important;
  margin: 0 !important;
  transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
  min-height: 36px !important;
  height: 36px !important;
}

[data-baseweb="tab"]:hover {
  color: var(--ink) !important;
}

[data-baseweb="tab"][aria-selected="true"] {
  background: var(--card) !important;
  color: var(--ink) !important;
  box-shadow: var(--shadow-sm), 0 0 0 0.5px rgba(0,0,0,0.04) !important;
  font-weight: 600 !important;
}

/* 隐藏 Streamlit 默认的 tab 下划线动画条 */
[data-baseweb="tab-highlight"],
[data-baseweb="tab-border"] {
  display: none !important;
}

/* Tab 内容区:白色圆角卡片 */
[data-testid="stTabs"] > div:last-child > div {
  background: var(--card);
  border-radius: var(--radius-lg);
  padding: 2.5rem 2.5rem 2rem 2.5rem;
  box-shadow: var(--shadow-md);
  animation: atd-card-in 0.35s cubic-bezier(0.25, 0.1, 0.25, 1);
}

@keyframes atd-card-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 主按钮:系统蓝圆角胶囊 */
[data-testid="stBaseButton-primary"] {
  background: var(--blue) !important;
  color: #FFFFFF !important;
  border: none !important;
  border-radius: 980px !important;
  font-family: var(--font-sf) !important;
  font-weight: 500 !important;
  font-size: 0.98rem !important;
  letter-spacing: -0.005em !important;
  text-transform: none !important;
  padding: 11px 24px !important;
  height: auto !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all 0.2s cubic-bezier(0.25, 0.1, 0.25, 1) !important;
}

[data-testid="stBaseButton-primary"]:hover {
  background: var(--blue-hover) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 113, 227, 0.25) !important;
}

[data-testid="stBaseButton-primary"]:active {
  transform: translateY(0);
  background: var(--blue-deep) !important;
}

/* 次级按钮:灰底胶囊 */
[data-testid="stBaseButton-secondary"] {
  background: rgba(120, 120, 128, 0.12) !important;
  color: var(--ink) !important;
  border: none !important;
  border-radius: 980px !important;
  font-family: var(--font-sf) !important;
  font-weight: 500 !important;
  font-size: 0.95rem !important;
  padding: 10px 20px !important;
  box-shadow: none !important;
  transition: all 0.2s ease !important;
}

[data-testid="stBaseButton-secondary"]:hover {
  background: rgba(120, 120, 128, 0.18) !important;
}

/* 下载按钮:边框胶囊 */
[data-testid="stDownloadButton"] button {
  background: var(--card) !important;
  color: var(--blue) !important;
  border: 1.5px solid rgba(0, 113, 227, 0.25) !important;
  border-radius: 980px !important;
  font-family: var(--font-sf) !important;
  font-weight: 500 !important;
  font-size: 0.95rem !important;
  text-transform: none !important;
  letter-spacing: -0.005em !important;
  padding: 10px 20px !important;
  justify-content: center !important;
  text-align: center !important;
  transition: all 0.2s ease !important;
}

[data-testid="stDownloadButton"] button:hover {
  background: rgba(0, 113, 227, 0.06) !important;
  border-color: var(--blue) !important;
}

/* 表单输入:圆角、柔和边框 */
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input,
div[data-testid="stTextArea"] textarea {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--hair) !important;
  background: var(--card) !important;
  font-family: var(--font-sf) !important;
  font-size: 1rem !important;
  color: var(--ink) !important;
  padding: 10px 14px !important;
  transition: all 0.15s ease !important;
  box-shadow: none !important;
}

div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextArea"] textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px rgba(0, 113, 227, 0.15) !important;
  outline: none !important;
}

/* Selectbox */
div[data-baseweb="select"] > div {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--hair) !important;
  background: var(--card) !important;
  font-family: var(--font-sf) !important;
  font-size: 1rem !important;
  min-height: 44px !important;
  padding: 2px 8px !important;
}

/* Radio — segmented style */
div[role="radiogroup"] {
  background: rgba(120, 120, 128, 0.08);
  padding: 4px;
  border-radius: 12px;
  gap: 0 !important;
  display: inline-flex !important;
}

div[role="radiogroup"] > label {
  background: transparent !important;
  border: none !important;
  border-radius: 8px !important;
  padding: 8px 16px !important;
  font-family: var(--font-sf) !important;
  font-size: 0.95rem !important;
  font-weight: 500 !important;
  color: var(--ink-2) !important;
  margin: 0 !important;
  cursor: pointer;
  transition: all 0.2s ease;
}

div[role="radiogroup"] > label:has(input:checked) {
  background: var(--card) !important;
  color: var(--ink) !important;
  box-shadow: var(--shadow-sm), 0 0 0 0.5px rgba(0,0,0,0.04) !important;
}

/* 提示框:柔和填色 + 圆角,无左边框 */
[data-testid="stAlert"],
[data-testid="stInfo"],
[data-testid="stSuccess"],
[data-testid="stWarning"],
[data-testid="stError"] {
  border-radius: var(--radius-md) !important;
  padding: 14px 18px !important;
  border: none !important;
  box-shadow: none !important;
  font-size: 0.97rem !important;
}

[data-testid="stInfo"] {
  background: rgba(0, 113, 227, 0.06) !important;
  color: var(--blue-deep) !important;
}

[data-testid="stSuccess"] {
  background: rgba(52, 199, 89, 0.10) !important;
  color: #1A7F37 !important;
}

[data-testid="stWarning"] {
  background: rgba(255, 149, 0, 0.12) !important;
  color: #AD5A00 !important;
}

[data-testid="stError"] {
  background: rgba(255, 59, 48, 0.10) !important;
  color: #B00020 !important;
}

[data-testid="stInfo"] *,
[data-testid="stSuccess"] *,
[data-testid="stWarning"] *,
[data-testid="stError"] * {
  color: inherit !important;
}

/* DataFrame:圆角卡片、删除 Streamlit 默认顶格边框 */
[data-testid="stDataFrame"] {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--hair) !important;
  overflow: hidden !important;
}

[data-testid="stDataFrame"] [role="columnheader"] {
  background: #FAFAFC !important;
  font-weight: 600 !important;
  font-size: 0.85rem !important;
  color: var(--ink-2) !important;
  text-transform: none !important;
  letter-spacing: -0.005em !important;
  border-bottom: 1px solid var(--hair) !important;
}

[data-testid="stDataFrame"] * {
  font-family: var(--font-sf) !important;
  font-size: 0.92rem !important;
}

/* File uploader — 更大的 padding + 各元素垂直间隔,避免字号重合 */
[data-testid="stFileUploader"] section {
  background: rgba(120, 120, 128, 0.05) !important;
  border: 1.5px dashed rgba(120, 120, 128, 0.3) !important;
  border-radius: var(--radius-md) !important;
  padding: 2.25rem 1.75rem !important;
  transition: all 0.2s ease;
  min-height: 170px;
}

[data-testid="stFileUploader"] section:hover {
  border-color: var(--blue) !important;
  background: rgba(0, 113, 227, 0.03) !important;
}

/* 上传组件内部:主提示、副提示、按钮 三个层次拉开 */
[data-testid="stFileUploader"] section > div {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  gap: 0.6rem !important;
  text-align: center !important;
}

[data-testid="stFileUploader"] section small,
[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"] span {
  display: block !important;
  font-size: 0.82rem !important;
  color: var(--ink-3) !important;
  line-height: 1.5 !important;
  margin: 0 !important;
}

[data-testid="stFileUploader"] section [data-testid="stFileUploaderDropzoneInstructions"] {
  line-height: 1.6 !important;
}

[data-testid="stFileUploader"] button {
  margin-top: 0.75rem !important;
}

/* Expander — 白色卡片 */
[data-testid="stExpander"] {
  border: 1px solid var(--hair) !important;
  border-radius: var(--radius-md) !important;
  background: var(--card) !important;
  box-shadow: none !important;
  margin-bottom: 0.5rem !important;
}

[data-testid="stExpander"] summary {
  font-family: var(--font-sf) !important;
  font-weight: 500 !important;
  font-size: 0.97rem !important;
  padding: 12px 18px !important;
  color: var(--ink) !important;
}

/* 彻底隐藏 <hr> */
hr {
  display: none !important;
}

/* Spinner */
[data-testid="stSpinner"] > div > div {
  border-color: var(--hair) !important;
  border-top-color: var(--blue) !important;
}

/* 子标题容器:保持自然排版,不加装饰线 */
[data-testid="stHeadingWithActionElements"] {
  margin-bottom: 1rem !important;
}

/* Caption:次要灰 */
[data-testid="stCaptionContainer"] {
  color: var(--ink-3) !important;
  font-size: 0.9rem !important;
}

/* 整体淡入 */
main > div {
  animation: atd-fade 0.5s cubic-bezier(0.25, 0.1, 0.25, 1);
}

@keyframes atd-fade {
  from { opacity: 0; transform: translateY(4px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Toggle 小开关 */
[data-testid="stToggle"] label > div:first-child > div {
  background: var(--hair) !important;
  border-radius: 100px !important;
}

/* 顶栏状态:一个浮动的小圆角条,右上角 */
.atd-topbar {
  position: fixed;
  top: 18px;
  right: 24px;
  z-index: 999;
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255,255,255,0.72);
  backdrop-filter: saturate(180%) blur(20px);
  -webkit-backdrop-filter: saturate(180%) blur(20px);
  border: 0.5px solid rgba(0,0,0,0.06);
  padding: 7px 14px;
  border-radius: 100px;
  font-family: var(--font-sf);
  font-size: 0.82rem;
  color: var(--ink-2);
  box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

.atd-topbar .model {
  font-weight: 500;
  color: var(--ink);
}

.atd-topbar .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 8px rgba(52, 199, 89, 0.4);
}

.atd-topbar.offline .dot {
  background: var(--orange);
  box-shadow: 0 0 8px rgba(255, 149, 0, 0.4);
}

.atd-topbar .sep {
  color: var(--hair);
}

/* 段落式模块副标 */
.atd-section {
  font-size: 0.88rem;
  font-weight: 500;
  color: var(--blue);
  text-transform: none;
  letter-spacing: 0.01em;
  margin-bottom: 0.4rem;
}

/* 风险指标卡(大) */
.atd-metric {
  display: flex;
  align-items: stretch;
  background: var(--card);
  border-radius: var(--radius-md);
  border: 1px solid var(--hair);
  overflow: hidden;
  height: 92px;
  box-shadow: var(--shadow-sm);
}

.atd-metric-bar {
  width: 5px;
  background: var(--blue);
  flex-shrink: 0;
}

.atd-metric-body {
  padding: 14px 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 4px;
  flex: 1;
}

.atd-metric-label {
  font-size: 0.82rem;
  color: var(--ink-3);
  font-weight: 500;
  letter-spacing: -0.005em;
}

.atd-metric-value {
  font-size: 1.9rem;
  color: var(--ink);
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

/* 覆盖率紧凑指标卡 */
.atd-minicard {
  background: var(--card);
  border: 1px solid var(--hair);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  box-shadow: var(--shadow-sm);
}

.atd-minicard-label {
  font-size: 0.76rem;
  color: var(--ink-3);
  font-weight: 500;
}

.atd-minicard-value {
  font-size: 1.35rem;
  font-weight: 600;
  letter-spacing: -0.015em;
  line-height: 1.1;
}

/* 导出下载卡(FR6) */
.atd-dlcard {
  background: linear-gradient(135deg, #FFFFFF 0%, #FAFAFC 100%);
  border: 1px solid var(--hair);
  border-radius: var(--radius-lg);
  padding: 28px 24px 20px 24px;
  margin-bottom: 12px;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.atd-dlcard:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.atd-dlcard-icon {
  font-family: var(--font-mono);
  font-size: 1.5rem;
  color: var(--blue);
  font-weight: 600;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}

.atd-dlcard-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.02em;
  margin-bottom: 6px;
}

.atd-dlcard-desc {
  font-size: 0.9rem;
  color: var(--ink-3);
  line-height: 1.45;
  margin-bottom: 4px;
}
</style>
"""


def inject_theme() -> None:
    """在页面顶端注入主题 CSS。放在 app.py 最靠前位置调用。"""
    st.markdown(_CSS, unsafe_allow_html=True)


def render_hero(api_ok: bool) -> None:
    """Apple 风格 Hero:大字标题 + 柔和副标题 + 状态 badge。"""
    badge_cls = "" if api_ok else "offline"
    badge_label = "就绪 · LLM 已连接" if api_ok else "离线 · 规则兜底模式"
    st.markdown(
        f"""
        <div class="atd-hero">
          <h1>AutoTestDesign</h1>
          <div class="sub">AI 驱动的测试用例生成器 · 从需求到黑盒/白盒测试套件</div>
          <div class="badge {badge_cls}"><span class="dot"></span>{badge_label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_topbar(model: str, online: bool) -> None:
    """右上浮动的毛玻璃状态条:显示 LLM 模型名与在线状态。"""
    cls = "" if online else "offline"
    display = model if model else "—"
    state = "Live" if online else "Offline"
    st.markdown(
        f"""
        <div class="atd-topbar {cls}">
          <span class="dot"></span>
          <span>{state}</span>
          <span class="sep">·</span>
          <span class="model">{display}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
