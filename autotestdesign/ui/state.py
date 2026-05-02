from __future__ import annotations
from dataclasses import dataclass, field
import streamlit as st
from autotestdesign.core.models import Requirement, TestSuite


@dataclass
class SessionData:
    """Streamlit 会话内共享的状态:需求、测试套件、运行日志。"""
    requirements: list[Requirement] = field(default_factory=list)
    suite: TestSuite | None = None
    run_log: list[str] = field(default_factory=list)
    source_label: str = ""  # 数据来源标签(内置示例名 / 上传文件名 / 手动输入)


def get_session() -> SessionData:
    """获取或初始化当前 Streamlit 会话的 SessionData。"""
    if "atd" not in st.session_state:
        st.session_state.atd = SessionData()
    return st.session_state.atd


def render_workset_chip() -> None:
    """在每个 Tab 顶部渲染一条紧凑的「当前工作集」状态条,跨页面保持可见。"""
    session = get_session()
    n_req = len(session.requirements)
    n_cases = len(session.suite.cases) if session.suite else 0
    source = session.source_label or "—"

    if n_req == 0:
        chip_html = """
        <div class="atd-workset empty">
          <div class="atd-workset-main">
            <span class="atd-workset-dot empty"></span>
            <span class="atd-workset-label">尚未载入需求</span>
          </div>
          <div class="atd-workset-meta">请前往「需求录入」</div>
        </div>
        """
    else:
        suite_part = (
            f'<span class="atd-workset-pill">{n_cases} 条用例</span>'
            if n_cases else '<span class="atd-workset-pill dim">未生成</span>'
        )
        chip_html = f"""
        <div class="atd-workset">
          <div class="atd-workset-main">
            <span class="atd-workset-dot"></span>
            <span class="atd-workset-label">当前工作集</span>
            <span class="atd-workset-count">{n_req} 条需求</span>
            {suite_part}
          </div>
          <div class="atd-workset-meta">来源 · {source}</div>
        </div>
        """
    st.markdown(chip_html, unsafe_allow_html=True)

