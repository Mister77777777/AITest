from autotestdesign.core.models import Field, Requirement
from autotestdesign.core.blackbox.equivalence import generate_equivalence_cases


def _req_with_field(f: Field) -> Requirement:
    return Requirement(id="REQ-001", raw_text="x", input_fields=[f])


def test_int_field_produces_valid_and_two_invalid_partitions():
    req = _req_with_field(Field(name="age", type="int", min=18, max=120))
    cases = generate_equivalence_cases(req)
    assert len(cases) == 3
    ages = sorted(c.inputs["age"] for c in cases)
    assert ages[0] < 18 and ages[1] >= 18 and ages[2] > 120
    assert all(c.technique == "EP" for c in cases)


def test_enum_field_one_case_per_value_plus_one_invalid():
    req = _req_with_field(Field(name="role", type="enum", allowed=["admin", "user", "guest"]))
    cases = generate_equivalence_cases(req)
    assert len(cases) == 4
    roles = [c.inputs["role"] for c in cases]
    for allowed in ["admin", "user", "guest"]:
        assert allowed in roles
    invalid = [r for r in roles if r not in ("admin", "user", "guest")]
    assert len(invalid) == 1


def test_string_field_three_classes():
    req = _req_with_field(Field(name="name", type="string"))
    cases = generate_equivalence_cases(req)
    assert len(cases) == 3


def test_bool_field_two_cases():
    req = _req_with_field(Field(name="active", type="bool"))
    cases = generate_equivalence_cases(req)
    assert len(cases) == 2
    assert {c.inputs["active"] for c in cases} == {True, False}


def test_each_case_has_unique_id_and_requirement_link():
    req = Requirement(
        id="REQ-007", raw_text="x",
        input_fields=[Field(name="age", type="int", min=0, max=10)],
    )
    cases = generate_equivalence_cases(req)
    ids = [c.id for c in cases]
    assert len(set(ids)) == len(ids)
    assert all(c.requirement_id == "REQ-007" for c in cases)


def test_float_field_produces_below_valid_above_partitions():
    """TC-EP-03 by Detailed Test Design review:覆盖 float 分支。"""
    req = _req_with_field(Field(name="rate", type="float", min=0.0, max=1.0))
    cases = generate_equivalence_cases(req)
    assert len(cases) == 3
    labels = [c.tags[-1] for c in cases]
    assert labels == ["below_min", "valid", "above_max"]
