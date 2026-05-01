from __future__ import annotations
from typing import Any, Protocol
from pydantic import BaseModel
from autotestdesign.core.models import Requirement, TestCase


class _OracleOut(BaseModel):
    # LLM 返回的结构化 oracle 结果
    expected_result: str


class _LLMLike(Protocol):
    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type) -> Any: ...


def _is_out_of_range(req: Requirement, tc: TestCase) -> tuple[bool, str]:
    """检查 TestCase 的输入是否越界,越界则直接用算法兜底结果。"""
    for field in req.input_fields:
        if field.name not in tc.inputs:
            continue
        v = tc.inputs[field.name]
        if field.type in ("int", "float") and field.min is not None and v < field.min:
            return True, f"{field.name} 低于下限({field.min})"
        if field.type in ("int", "float") and field.max is not None and v > field.max:
            return True, f"{field.name} 高于上限({field.max})"
        if field.type == "enum" and field.allowed and v not in field.allowed:
            return True, f"{field.name} 不在允许的取值集合中"
    return False, ""


def synthesize_oracle(req: Requirement, tc: TestCase, llm: _LLMLike | None) -> TestCase:
    """为 TestCase 合成 Expected Result。先算法兜底,否则调 LLM,失败再回退默认。"""
    out_of_range, reason = _is_out_of_range(req, tc)
    if out_of_range:
        # 输入越界 — 无需 LLM,直接断言系统拒绝
        return tc.model_copy(update={
            "expected_result": f"系统应拒绝该输入:{reason}。"
        })
    if llm is None:
        # 无 LLM 且输入合法 — 使用 expected_actions 构造默认 oracle
        default = (
            f"系统应执行:{'、'.join(req.expected_actions)}。"
            if req.expected_actions else "系统应接受该输入。"
        )
        return tc.model_copy(update={"expected_result": default})
    try:
        # 调用 LLM 生成语义化 oracle
        res = llm.structured_call(
            "synthesize_oracle",
            {
                "raw_text": req.raw_text,
                "expected_actions": req.expected_actions,
                "inputs": tc.inputs,
            },
            _OracleOut,
        )
        return tc.model_copy(update={"expected_result": res.expected_result})
    except Exception:
        # LLM 调用失败 — 回退到基于 expected_actions 的默认 oracle
        default = (
            f"系统应执行:{'、'.join(req.expected_actions)}。"
            if req.expected_actions else "系统应接受该输入。"
        )
        return tc.model_copy(update={"expected_result": default})
