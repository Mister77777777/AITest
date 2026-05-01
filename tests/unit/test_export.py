import json
from pathlib import Path
import pandas as pd
from autotestdesign.core.models import TestCase, TestSuite
from autotestdesign.core.export import to_json, to_csv, to_xlsx


def _sample_suite() -> TestSuite:
    return TestSuite(
        cases=[
            TestCase(
                id="TC-001", requirement_id="REQ-001", technique="BVA",
                inputs={"age": 17}, steps=["submit age=17"],
                expected_result="reject", priority="High", tags=["boundary"],
            ),
            TestCase(
                id="TC-002", requirement_id="REQ-001", technique="BVA",
                inputs={"age": 18}, steps=["submit age=18"],
                expected_result="accept", priority="High",
            ),
        ],
        coverage={"all_transitions": 0.5},
    )


def test_to_json_roundtrip():
    suite = _sample_suite()
    data = json.loads(to_json(suite))
    assert len(data["cases"]) == 2
    assert data["coverage"]["all_transitions"] == 0.5


def test_to_csv_flattens_cases(tmp_path: Path):
    suite = _sample_suite()
    out = tmp_path / "out.csv"
    to_csv(suite, out)
    df = pd.read_csv(out)
    assert list(df["id"]) == ["TC-001", "TC-002"]
    assert "inputs" in df.columns
    assert "expected_result" in df.columns


def test_to_xlsx_creates_file(tmp_path: Path):
    suite = _sample_suite()
    out = tmp_path / "out.xlsx"
    to_xlsx(suite, out)
    assert out.exists() and out.stat().st_size > 0
    df = pd.read_excel(out)
    assert len(df) == 2
