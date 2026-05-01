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
