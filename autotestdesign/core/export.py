from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from autotestdesign.core.models import TestSuite


def to_json(suite: TestSuite) -> str:
    """序列化为 JSON 字符串,带缩进便于人工查看。"""
    return suite.model_dump_json(indent=2)


def _suite_to_dataframe(suite: TestSuite) -> pd.DataFrame:
    """把 TestSuite 扁平化为 DataFrame,列映射对齐常见 TMS(如 Jira Xray)。"""
    rows = []
    for c in suite.cases:
        rows.append({
            "id": c.id,
            "requirement_id": c.requirement_id,
            "technique": c.technique,
            "priority": c.priority,
            "inputs": json.dumps(c.inputs, ensure_ascii=False),
            "preconditions": " | ".join(c.preconditions),
            "steps": " | ".join(c.steps),
            "expected_result": c.expected_result,
            "tags": ",".join(c.tags),
        })
    return pd.DataFrame(rows)


def to_csv(suite: TestSuite, path: Path) -> None:
    """导出 CSV(UTF-8)。"""
    _suite_to_dataframe(suite).to_csv(path, index=False)


def to_xlsx(suite: TestSuite, path: Path) -> None:
    """导出 Excel(openpyxl 引擎)。"""
    _suite_to_dataframe(suite).to_excel(path, index=False, engine="openpyxl")
