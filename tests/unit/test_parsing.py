import pytest
from pathlib import Path
from autotestdesign.core.parsing import parse_csv, parse_text_block, parse_with_llm
from tests.fixtures.fake_llm import FakeLLM


CSV_SAMPLE = """id,raw_text,category
REQ-001,"Age must be between 18 and 120",functional
REQ-002,"Password must be stored securely",non-functional
"""


def test_parse_csv_returns_requirements(tmp_path: Path):
    p = tmp_path / "r.csv"
    p.write_text(CSV_SAMPLE)
    reqs = parse_csv(p)
    assert len(reqs) == 2
    assert reqs[0].id == "REQ-001"
    assert reqs[0].category == "functional"
    assert reqs[1].category == "non-functional"


def test_parse_text_block_splits_on_blank_lines():
    text = "REQ-001: user can login\n\nREQ-002: session expires after 30 min"
    reqs = parse_text_block(text)
    assert len(reqs) == 2
    assert "login" in reqs[0].raw_text


def test_parse_with_llm_uses_structured_call():
    fake = FakeLLM()
    fake.queue("structure_requirement", {
        "id": "REQ-010",
        "raw_text": "Age must be 18-120",
        "input_fields": [{"name": "age", "type": "int", "min": 18, "max": 120, "allowed": None}],
        "conditions": ["age >= 18"],
        "expected_actions": ["accept"],
        "category": "functional",
    })
    req = parse_with_llm("Age must be 18-120", fake)
    assert req.input_fields[0].name == "age"
    assert req.input_fields[0].min == 18
    assert req.input_fields[0].max == 120
