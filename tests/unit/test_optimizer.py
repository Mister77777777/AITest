from autotestdesign.core.models import TestCase, TestSuite
from autotestdesign.core.optimizer import dedup_and_prioritize, weighted_cover


def _tc(id_: str, req: str, tech: str, inputs: dict, priority: str = "Medium") -> TestCase:
    # 快捷构造 TestCase 辅助函数
    return TestCase(id=id_, requirement_id=req, technique=tech, inputs=inputs, priority=priority)


def test_dedup_removes_identical_inputs_same_technique():
    # 验证相同 (req, technique, inputs) 指纹只保留一条
    cases = [
        _tc("A", "R1", "EP", {"age": 10}),
        _tc("B", "R1", "EP", {"age": 10}),  # 重复
        _tc("C", "R1", "EP", {"age": 11}),
    ]
    out = dedup_and_prioritize(cases)
    ids = [c.id for c in out]
    assert len(out) == 2
    assert ids[0] in ("A", "B")
    assert "C" in ids


def test_priority_sort_high_first():
    # 验证去重后按 High > Medium > Low 排序
    cases = [
        _tc("L", "R1", "EP", {"x": 1}, priority="Low"),
        _tc("H", "R1", "EP", {"x": 2}, priority="High"),
        _tc("M", "R1", "EP", {"x": 3}, priority="Medium"),
    ]
    out = dedup_and_prioritize(cases)
    assert [c.id for c in out] == ["H", "M", "L"]


def test_weighted_cover_drops_redundant_low_priority():
    # 验证加权覆盖在 max_cases 限制下保留高优先级并覆盖所有需求
    cases = [
        _tc("H1", "R1", "BVA", {"a": 1}, priority="High"),
        _tc("L1", "R1", "BVA", {"a": 1}, priority="Low"),
        _tc("M1", "R2", "EP", {"a": 2}, priority="Medium"),
    ]
    suite: TestSuite = weighted_cover(cases, max_cases=2)
    assert len(suite.cases) == 2
    reqs = {c.requirement_id for c in suite.cases}
    assert reqs == {"R1", "R2"}
