from autotestdesign.core.models import Requirement
from autotestdesign.core.blackbox.decision_table import generate_decision_table_cases


def test_two_conditions_produce_four_rows():
    req = Requirement(
        id="REQ-001", raw_text="x",
        conditions=["is_member", "over_18"],
        expected_actions=["allow checkout"],
    )
    cases = generate_decision_table_cases(req)
    assert len(cases) == 4
    for c in cases:
        assert c.technique == "DT"
        assert set(c.inputs.keys()) == {"is_member", "over_18"}
    combos = {tuple(sorted(c.inputs.items())) for c in cases}
    assert len(combos) == 4


def test_zero_conditions_yields_empty():
    req = Requirement(id="REQ-002", raw_text="x", conditions=[])
    assert generate_decision_table_cases(req) == []


def test_three_conditions_produce_eight_rows():
    req = Requirement(
        id="REQ-003", raw_text="x",
        conditions=["A", "B", "C"],
    )
    cases = generate_decision_table_cases(req)
    assert len(cases) == 8


def test_every_case_has_unique_id():
    req = Requirement(
        id="REQ-004", raw_text="x",
        conditions=["p", "q"],
    )
    cases = generate_decision_table_cases(req)
    assert len({c.id for c in cases}) == 4


def test_one_condition_with_expected_actions_emits_both_branches():
    """TC-DT-BVA-02 by Detailed Test Design review:N=1 相邻边界情况。"""
    req = Requirement(
        id="REQ-DT01", raw_text="x",
        conditions=["isPremium"],
        expected_actions=["grant discount"],
    )
    cases = generate_decision_table_cases(req)
    assert len(cases) == 2
    premium = [c for c in cases if c.inputs["isPremium"]]
    not_premium = [c for c in cases if not c.inputs["isPremium"]]
    assert "grant discount" in premium[0].expected_result
    assert (
        "拒绝" in not_premium[0].expected_result
        or "不执行" in not_premium[0].expected_result
    )
