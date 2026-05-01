from __future__ import annotations
import streamlit as st
from graphviz import Digraph
from autotestdesign.core.whitebox.state_machine import StateMachine, parse_dsl


def render_state_diagram_section() -> StateMachine | None:
    """FR4 状态机 DSL 编辑器 + graphviz 渲染。"""
    st.markdown("**FR4 · 状态机(DSL 编辑)**")
    # 默认 DSL 示例:用户登录流程
    default_dsl = "\n".join([
        "# 格式:SOURCE --event--> TARGET",
        "Guest --login--> LoggedIn",
        "LoggedIn --logout--> Guest",
        "LoggedIn --failedAttempt--> Locked",
        "Locked --reset--> Guest",
    ])
    dsl = st.text_area("状态转换", value=default_dsl, height=160)
    start = st.text_input("起始状态", value="Guest")
    if not dsl.strip():
        return None
    try:
        sm = parse_dsl(dsl, start_state=start)
    except Exception as e:
        st.warning(f"DSL 解析失败:{e}")
        return None
    # 渲染 graphviz 图:起始状态使用双圆圈标注
    g = Digraph()
    for s in sm.states:
        g.node(s, shape="circle" if s != sm.start_state else "doublecircle")
    for t in sm.transitions:
        g.edge(t.source, t.target, label=t.event)
    st.graphviz_chart(g)
    return sm
