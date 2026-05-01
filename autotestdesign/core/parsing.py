from __future__ import annotations
from pathlib import Path
from typing import Any, Protocol
import pandas as pd
from autotestdesign.core.models import Requirement


class _LLMLike(Protocol):
    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type) -> Any: ...


def parse_csv(path: Path) -> list[Requirement]:
    """从 CSV 读取需求列表。表头需包含 id / raw_text / category 字段。"""
    df = pd.read_csv(path)
    requirements: list[Requirement] = []
    for i, row in df.iterrows():
        rid = str(row.get("id") or f"REQ-{i+1:03d}")
        category = str(row.get("category", "functional")).strip() or "functional"
        if category not in ("functional", "non-functional"):
            category = "functional"
        requirements.append(Requirement(
            id=rid,
            raw_text=str(row["raw_text"]),
            category=category,  # type: ignore[arg-type]
        ))
    return requirements


def parse_text_block(text: str) -> list[Requirement]:
    """把纯文本按空行拆成多个需求,每段生成一个 Requirement。"""
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    return [
        Requirement(id=f"REQ-{i+1:03d}", raw_text=chunk)
        for i, chunk in enumerate(chunks)
    ]


def parse_with_llm(raw_text: str, llm: _LLMLike) -> Requirement:
    """调用 LLM 把自由文本结构化为 Requirement。"""
    return llm.structured_call(
        "structure_requirement",
        {"raw_text": raw_text},
        Requirement,
    )
