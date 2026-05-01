from __future__ import annotations
import json
from autotestdesign.core.models import TestCase, TestSuite

# 优先级排序键:数字越小越靠前
PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}
# 加权集合覆盖用的权重
PRIORITY_WEIGHT = {"High": 5, "Medium": 3, "Low": 1}


def _signature(tc: TestCase) -> tuple:
    """(需求 ID, 技术, 规范化后的输入) 作为去重指纹。"""
    return (tc.requirement_id, tc.technique, json.dumps(tc.inputs, sort_keys=True, default=str))


def dedup_and_prioritize(cases: list[TestCase]) -> list[TestCase]:
    """按 (req_id, technique, inputs) 指纹去重,相同指纹保留优先级最高的,再按优先级排序。"""
    seen: dict[tuple, TestCase] = {}
    for tc in cases:
        sig = _signature(tc)
        existing = seen.get(sig)
        if existing is None or PRIORITY_ORDER[tc.priority] < PRIORITY_ORDER[existing.priority]:
            seen[sig] = tc
    return sorted(seen.values(), key=lambda c: (PRIORITY_ORDER[c.priority], c.id))


def weighted_cover(cases: list[TestCase], max_cases: int | None = None) -> TestSuite:
    """加权集合覆盖优化:先保证每个需求至少一条用例,剩余空间按优先级权重填。"""
    deduped = dedup_and_prioritize(cases)
    selected: list[TestCase] = []
    covered_reqs: set[str] = set()
    # 优先保证需求覆盖
    for tc in deduped:
        if tc.requirement_id not in covered_reqs:
            selected.append(tc)
            covered_reqs.add(tc.requirement_id)
    # 剩余按权重补齐
    remaining = [c for c in deduped if c not in selected]
    remaining.sort(key=lambda c: -PRIORITY_WEIGHT[c.priority])
    for tc in remaining:
        if max_cases is not None and len(selected) >= max_cases:
            break
        selected.append(tc)
    if max_cases is not None:
        selected = selected[:max_cases]
    total_reqs = len({c.requirement_id for c in cases})
    coverage = {
        "requirement_coverage": len({c.requirement_id for c in selected}) / total_reqs if total_reqs else 0.0,
    }
    return TestSuite(cases=selected, coverage=coverage)
