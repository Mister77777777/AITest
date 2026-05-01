import pytest
from pydantic import ValidationError
from autotestdesign.core.models import (
    Field, Requirement, RiskScore, TestCase, TestSuite,
)


def test_field_numeric_with_range():
    f = Field(name="age", type="int", min=0, max=120)
    assert f.min == 0
    assert f.max == 120


def test_field_enum_allowed():
    f = Field(name="role", type="enum", allowed=["admin", "user"])
    assert f.allowed == ["admin", "user"]


def test_requirement_builds():
    req = Requirement(
        id="REQ-001",
        raw_text="User can register with email and age 18-120",
        input_fields=[
            Field(name="email", type="string"),
            Field(name="age", type="int", min=18, max=120),
        ],
        conditions=["age >= 18"],
        expected_actions=["create account", "send verification email"],
        category="functional",
    )
    assert req.id == "REQ-001"
    assert len(req.input_fields) == 2
    assert req.risk is None


def test_risk_score_priority_literal():
    rs = RiskScore(likelihood=4, impact=5, score=20, priority="High", rationale="auth path")
    assert rs.priority == "High"


def test_risk_score_rejects_bad_priority():
    with pytest.raises(ValidationError):
        RiskScore(likelihood=4, impact=5, score=20, priority="Critical", rationale="x")


def test_testcase_technique_enum():
    tc = TestCase(
        id="TC-001",
        requirement_id="REQ-001",
        technique="BVA",
        inputs={"age": 17},
        preconditions=[],
        steps=["submit form with age=17"],
        expected_result="system rejects: age below minimum",
        priority="High",
        tags=["boundary", "age"],
    )
    assert tc.technique == "BVA"


def test_testsuite_coverage_dict():
    ts = TestSuite(cases=[], coverage={"all_states": 1.0, "all_transitions": 0.83})
    assert ts.coverage["all_transitions"] == 0.83
