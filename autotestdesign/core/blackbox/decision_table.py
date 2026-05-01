from __future__ import annotations
from itertools import product
from autotestdesign.core.models import Requirement, TestCase


def generate_decision_table_cases(req: Requirement) -> list[TestCase]:
    """按 ISO 29119-4 判定表技术,对 N 个条件穷举 2^N 组合。"""
    # 无条件时返回空列表,无需生成任何测试用例
    if not req.conditions:
        return []

    cases: list[TestCase] = []
    # 用 itertools.product 对每个条件枚举 False/True,生成所有组合
    for i, combo in enumerate(product([False, True], repeat=len(req.conditions)), start=1):
        # 将条件名称与布尔值对应,构建输入字典
        inputs = dict(zip(req.conditions, combo))
        # 取所有为 True 的条件名,用于生成期望结果描述
        true_conditions = [k for k, v in inputs.items() if v]
        expected = (
            "系统应执行以下动作:" + "、".join(req.expected_actions)
            if true_conditions and req.expected_actions
            else "系统不执行动作或应拒绝"
        )
        cases.append(TestCase(
            id=f"{req.id}-DT-{i:03d}",
            requirement_id=req.id,
            technique="DT",
            inputs=inputs,
            steps=[f"给定条件组合 {inputs}"],
            expected_result=expected,
            # 若需求携带风险评分则使用其优先级,否则默认 Medium
            priority=(req.risk.priority if req.risk else "Medium"),
            tags=["DT"] + true_conditions,
        ))
    return cases
