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


def get_session() -> SessionData:
    """获取或初始化当前 Streamlit 会话的 SessionData。"""
    if "atd" not in st.session_state:
        st.session_state.atd = SessionData()
    return st.session_state.atd
