from autotestdesign.core.models import Field, Requirement
from autotestdesign.core.blackbox.boundary import generate_boundary_cases


def test_int_range_produces_six_boundary_cases():
    req = Requirement(
        id="REQ-001", raw_text="x",
        input_fields=[Field(name="age", type="int", min=0, max=100)],
    )
    cases = generate_boundary_cases(req)
    values = sorted(c.inputs["age"] for c in cases)
    assert values == [-1, 0, 1, 99, 100, 101]
    assert all(c.technique == "BVA" for c in cases)


def test_float_range_produces_six_cases_with_epsilon():
    req = Requirement(
        id="REQ-002", raw_text="x",
        input_fields=[Field(name="rate", type="float", min=0.0, max=1.0)],
    )
    cases = generate_boundary_cases(req)
    assert len(cases) == 6


def test_float_range_boundary_values_have_epsilon_perturbation():
    """TC-BVA-03 by Detailed Test Design review:验证 float 边界 ±0.01 ε 扰动。"""
    req = Requirement(
        id="REQ-F01", raw_text="x",
        input_fields=[Field(name="rate", type="float", min=0.0, max=1.0)],
    )
    cases = generate_boundary_cases(req)
    values = sorted(round(c.inputs["rate"], 2) for c in cases)
    assert values == [-0.01, 0.0, 0.01, 0.99, 1.0, 1.01]


def test_field_without_range_is_skipped():
    req = Requirement(
        id="REQ-003", raw_text="x",
        input_fields=[Field(name="name", type="string")],
    )
    cases = generate_boundary_cases(req)
    assert cases == []


def test_string_field_with_min_max_length_uses_length_boundaries():
    req = Requirement(
        id="REQ-004", raw_text="x",
        input_fields=[Field(name="username", type="string", min=3, max=12)],
    )
    cases = generate_boundary_cases(req)
    lengths = sorted(len(c.inputs["username"]) for c in cases)
    assert lengths == [2, 3, 4, 11, 12, 13]
