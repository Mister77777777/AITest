from __future__ import annotations
from typing import Any, Protocol
from autotestdesign.core.models import Requirement, TestCase, TestSuite
from autotestdesign.core.parsing import parse_with_llm
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


def _needs_structuring(r: Requirement) -> bool:
    """如果需求未填 input_fields 也没 conditions,就需要 LLM 辅助结构化。"""
    return not r.input_fields and not r.conditions


def _structure_with_llm(req: Requirement, llm: _LLMLike) -> Requirement:
    """调 LLM 把自由文本需求结构化(FR1.1),保留原 id 不被 LLM 覆盖。失败返回原需求。"""
    try:
        structured = parse_with_llm(req.raw_text, llm)
        # 保留原 id 与原 category,仅合并 LLM 补充的 input_fields/conditions/expected_actions
        return req.model_copy(update={
            "input_fields": structured.input_fields or req.input_fields,
            "conditions": structured.conditions or req.conditions,
            "expected_actions": structured.expected_actions or req.expected_actions,
        })
    except Exception:
        return req


def run_pipeline(
    requirements: list[Requirement],
    llm: _LLMLike | None,
    state_machine: StateMachine | None = None,
    state_machine_requirement_id: str | None = None,
    optimize_max_cases: int | None = None,
    auto_structure: bool = True,
) -> TestSuite:
    """FR1-FR7 整链路:(可选)LLM 结构化 → 风险打分 → 黑盒生成 → (可选)状态图 → Oracle → 优化。

    auto_structure:当需求缺 input_fields/conditions 时,是否用 LLM 自动补齐。默认 True;
    仅在 llm 可用且对应需求确实为空时才触发,不影响已结构化的需求。
    """
    # 1) FR1.1:按需对未结构化的需求调用 LLM 补齐字段
    if llm is not None and auto_structure:
        requirements = [
            _structure_with_llm(r, llm) if _needs_structuring(r) else r
            for r in requirements
        ]

    # 2) FR2:给每条需求打风险分并合并 rationale
    risked: list[Requirement] = []
    for r in requirements:
        risked.append(attach_risk(r, llm) if llm else r.model_copy(update={"risk": None}))

    # 3) FR3:三种黑盒测试用例
    all_cases: list[TestCase] = []
    for r in risked:
        all_cases.extend(generate_equivalence_cases(r))
        all_cases.extend(generate_boundary_cases(r))
        all_cases.extend(generate_decision_table_cases(r))

    # 4) FR4:可选的状态图用例
    if state_machine is not None and state_machine_requirement_id is not None:
        all_cases.extend(generate_all_states_cases(state_machine, state_machine_requirement_id))
        all_cases.extend(generate_all_transitions_cases(state_machine, state_machine_requirement_id))

    # 5) FR5:为每条用例合成 Expected Result
    req_map = {r.id: r for r in risked}
    all_cases = [
        synthesize_oracle(req_map[c.requirement_id], c, llm)
        if c.requirement_id in req_map else c
        for c in all_cases
    ]

    # 6) FR7:去重 + 加权覆盖优化
    return weighted_cover(all_cases, max_cases=optimize_max_cases)
