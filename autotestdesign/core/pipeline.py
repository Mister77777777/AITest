from __future__ import annotations
from typing import Any, Protocol
from autotestdesign.core.models import Requirement, TestCase, TestSuite
from autotestdesign.core.risk import attach_risk
from autotestdesign.core.blackbox.equivalence import generate_equivalence_cases
from autotestdesign.core.blackbox.boundary import generate_boundary_cases
from autotestdesign.core.blackbox.decision_table import generate_decision_table_cases
from autotestdesign.core.oracle import synthesize_oracle
from autotestdesign.core.optimizer import weighted_cover
from autotestdesign.core.whitebox.state_machine import (
    StateMachine, generate_all_states_cases, generate_all_transitions_cases,
)


class _LLMLike(Protocol):
    # LLM 协议接口:接受 prompt 名、变量字典、输出 schema,返回结构化实例
    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type) -> Any: ...


def run_pipeline(
    requirements: list[Requirement],
    llm: _LLMLike | None,
    state_machine: StateMachine | None = None,
    state_machine_requirement_id: str | None = None,
    optimize_max_cases: int | None = None,
) -> TestSuite:
    """FR1-FR7 整链路:风险打分 → 三种黑盒生成 → (可选) 状态图 → Oracle → 优化。"""
    # 1) FR2:给每条需求打风险分并合并 rationale
    risked: list[Requirement] = []
    for r in requirements:
        risked.append(attach_risk(r, llm) if llm else r.model_copy(update={"risk": None}))

    # 2) FR3:三种黑盒测试用例
    all_cases: list[TestCase] = []
    for r in risked:
        all_cases.extend(generate_equivalence_cases(r))
        all_cases.extend(generate_boundary_cases(r))
        all_cases.extend(generate_decision_table_cases(r))

    # 3) FR4:可选的状态图用例
    if state_machine is not None and state_machine_requirement_id is not None:
        all_cases.extend(generate_all_states_cases(state_machine, state_machine_requirement_id))
        all_cases.extend(generate_all_transitions_cases(state_machine, state_machine_requirement_id))

    # 4) FR5:为每条用例合成 Expected Result
    req_map = {r.id: r for r in risked}
    all_cases = [
        synthesize_oracle(req_map[c.requirement_id], c, llm)
        if c.requirement_id in req_map else c
        for c in all_cases
    ]

    # 5) FR7:去重 + 加权覆盖优化
    return weighted_cover(all_cases, max_cases=optimize_max_cases)
