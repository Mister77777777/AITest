from __future__ import annotations
from autotestdesign.core.models import Field, Requirement, TestCase

# 浮点数边界微小扰动量
_FLOAT_EPS = 0.01


def _boundary_values(f: Field) -> list[object]:
    """返回 6 个边界值:下界-1,下界,下界+1,上界-1,上界,上界+1。无区间字段返回空。"""
    if f.min is None or f.max is None:
        return []
    if f.type == "int":
        lo, hi = int(f.min), int(f.max)
        return [lo - 1, lo, lo + 1, hi - 1, hi, hi + 1]
    if f.type == "float":
        lo, hi = float(f.min), float(f.max)
        return [lo - _FLOAT_EPS, lo, lo + _FLOAT_EPS, hi - _FLOAT_EPS, hi, hi + _FLOAT_EPS]
    if f.type == "string":
        # string 的 min/max 视为长度约束
        lo, hi = int(f.min), int(f.max)
        return ["x" * n for n in [lo - 1, lo, lo + 1, hi - 1, hi, hi + 1]]
    return []


def generate_boundary_cases(req: Requirement) -> list[TestCase]:
    """按 ISO 29119-4 边界值分析技术生成测试用例。"""
    cases: list[TestCase] = []
    counter = 1
    for field in req.input_fields:
        values = _boundary_values(field)
        for v in values:
            if field.type == "string":
                length = len(v)  # type: ignore[arg-type]
                is_invalid = length < (field.min or 0) or length > (field.max or 0)
            else:
                is_invalid = v < field.min or v > field.max  # type: ignore[operator]
            cases.append(TestCase(
                id=f"{req.id}-BVA-{counter:03d}",
                requirement_id=req.id,
                technique="BVA",
                inputs={field.name: v},
                steps=[f"Submit with {field.name}={v!r}"],
                expected_result=(
                    f"System rejects ({field.name} out of range)"
                    if is_invalid else f"System accepts ({field.name} within range)"
                ),
                priority=(req.risk.priority if req.risk else "Medium"),
                tags=["BVA", field.name],
            ))
            counter += 1
    return cases
