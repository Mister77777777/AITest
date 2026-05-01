from __future__ import annotations
import re
from dataclasses import dataclass
import networkx as nx
from autotestdesign.core.models import TestCase


@dataclass(frozen=True)
class Transition:
    source: str
    event: str
    target: str


@dataclass
class StateMachine:
    start_state: str
    states: list[str]
    transitions: list[Transition]

    def to_digraph(self) -> nx.MultiDiGraph:
        """构建允许多重边的有向图(同一对节点可以有多个事件)。"""
        g = nx.MultiDiGraph()
        for s in self.states:
            g.add_node(s)
        for t in self.transitions:
            g.add_edge(t.source, t.target, event=t.event)
        return g


# DSL 行格式:SOURCE --event--> TARGET
_DSL_LINE = re.compile(r"^\s*(\w+)\s*--\s*([^-\s][^-]*?)\s*-->\s*(\w+)\s*$")


def parse_dsl(text: str, start_state: str) -> StateMachine:
    """解析 DSL 文本。以 # 开头的行视为注释。至少 1 条转换,否则抛 ValueError。"""
    transitions: list[Transition] = []
    states: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = _DSL_LINE.match(line)
        if not m:
            continue
        src, event, tgt = m.group(1), m.group(2).strip(), m.group(3)
        transitions.append(Transition(src, event, tgt))
        states.add(src)
        states.add(tgt)
    if not transitions:
        raise ValueError("DSL produced no transitions")
    if start_state not in states:
        states.add(start_state)
    return StateMachine(start_state=start_state, states=sorted(states), transitions=transitions)


def _path_steps(path: list[tuple[str, str, str]]) -> list[str]:
    """把 (src, event, tgt) 三元组列表转成人类可读的步骤字符串。"""
    steps = []
    for src, ev, tgt in path:
        steps.append(f"{src} --{ev}--> {tgt}")
    return steps


def generate_all_states_cases(sm: StateMachine, requirement_id: str) -> list[TestCase]:
    """All-States 覆盖:为每个未到达的状态生成最短到达路径对应的用例。"""
    g = sm.to_digraph()
    reached = {sm.start_state}
    cases: list[TestCase] = []
    counter = 1
    for target in sm.states:
        if target in reached:
            continue
        try:
            node_path = nx.shortest_path(g, sm.start_state, target)
        except nx.NetworkXNoPath:
            continue
        edges: list[tuple[str, str, str]] = []
        for a, b in zip(node_path, node_path[1:]):
            data = g.get_edge_data(a, b)
            first_event = next(iter(data.values()))["event"]
            edges.append((a, first_event, b))
        steps = _path_steps(edges)
        steps.insert(0, f"初始状态:{sm.start_state}")
        steps.append(f"-> {target}")
        reached.update(node_path)
        cases.append(TestCase(
            id=f"{requirement_id}-STT-AS-{counter:03d}",
            requirement_id=requirement_id,
            technique="STT",
            inputs={"target_state": target},
            steps=steps,
            expected_result=f"系统应到达状态 {target}",
            priority="High",
            tags=["STT", "all_states"],
        ))
        counter += 1
    return cases


def generate_all_transitions_cases(sm: StateMachine, requirement_id: str) -> list[TestCase]:
    """All-Transitions 覆盖:为每条转换生成 '从起点走到源态 + 触发该转换' 的用例。"""
    g = sm.to_digraph()
    cases: list[TestCase] = []
    counter = 1
    for t in sm.transitions:
        try:
            node_path = nx.shortest_path(g, sm.start_state, t.source)
        except nx.NetworkXNoPath:
            continue
        edges: list[tuple[str, str, str]] = []
        for a, b in zip(node_path, node_path[1:]):
            data = g.get_edge_data(a, b)
            first_event = next(iter(data.values()))["event"]
            edges.append((a, first_event, b))
        edges.append((t.source, t.event, t.target))
        steps = [f"初始状态:{sm.start_state}"] + _path_steps(edges)
        cases.append(TestCase(
            id=f"{requirement_id}-STT-AT-{counter:03d}",
            requirement_id=requirement_id,
            technique="STT",
            inputs={"transition": f"{t.source} --{t.event}--> {t.target}"},
            steps=steps,
            expected_result=f"系统应在事件 '{t.event}' 触发下从 {t.source} 转移到 {t.target}",
            priority="High",
            tags=["STT", "all_transitions", t.event],
        ))
        counter += 1
    return cases
