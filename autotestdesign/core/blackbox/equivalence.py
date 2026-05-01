from __future__ import annotations
from autotestdesign.core.models import Field, Requirement, TestCase


def _partitions_for_field(f: Field) -> list[tuple[str, object]]:
    """按字段类型返回等价类 (标签, 代表值) 对。"""
    if f.type == "int":
        lo = f.min if f.min is not None else -1_000_000
        hi = f.max if f.max is not None else 1_000_000
        mid = (lo + hi) // 2 if lo < hi else lo
        parts: list[tuple[str, object]] = []
        if f.min is not None:
            parts.append(("below_min", lo - 1))
        parts.append(("valid", mid))
        if f.max is not None:
            parts.append(("above_max", hi + 1))
        return parts
    if f.type == "float":
        lo = float(f.min) if f.min is not None else -1e6
        hi = float(f.max) if f.max is not None else 1e6
        mid = (lo + hi) / 2 if lo < hi else lo
        parts = []
        if f.min is not None:
            parts.append(("below_min", lo - 0.01))
        parts.append(("valid", mid))
        if f.max is not None:
            parts.append(("above_max", hi + 0.01))
        return parts
    if f.type == "enum":
        allowed = f.allowed or []
        parts = [(f"valid_{v}", v) for v in allowed]
        parts.append(("invalid_enum", "__INVALID__"))
        return parts
    if f.type == "string":
        return [("empty", ""), ("normal", "valid_value"), ("too_long", "x" * 1024)]
    if f.type == "bool":
        return [("true", True), ("false", False)]
    return [("default", None)]


def generate_equivalence_cases(req: Requirement) -> list[TestCase]:
    """按 ISO 29119-4 等价类划分技术为需求生成测试用例。"""
    cases: list[TestCase] = []
    counter = 1
    for field in req.input_fields:
        for label, value in _partitions_for_field(field):
            # 非法分区名约定前缀
            is_invalid = label.startswith(("below", "above", "invalid", "empty", "too_long"))
            cases.append(TestCase(
                id=f"{req.id}-EP-{counter:03d}",
                requirement_id=req.id,
                technique="EP",
                inputs={field.name: value},
                steps=[f"Submit with {field.name}={value!r}"],
                expected_result=(
                    f"System rejects input ({label})" if is_invalid
                    else f"System accepts input ({label})"
                ),
                priority=(req.risk.priority if req.risk else "Medium"),
                tags=["EP", field.name, label],
            ))
            counter += 1
    return cases
