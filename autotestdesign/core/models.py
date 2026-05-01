from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field as PydField, model_validator


class Field(BaseModel):
    name: str
    type: Literal["int", "float", "string", "enum", "bool"]
    min: Any | None = None
    max: Any | None = None
    allowed: list[Any] | None = None


class RiskScore(BaseModel):
    likelihood: int = PydField(ge=1, le=5)
    impact: int = PydField(ge=1, le=5)
    score: int
    priority: Literal["High", "Medium", "Low"]
    rationale: str

    @model_validator(mode="after")
    def _score_matches_product(self) -> "RiskScore":
        # 强制 score = likelihood * impact,防止 LLM 返回自相矛盾的风险分
        expected = self.likelihood * self.impact
        if self.score != expected:
            raise ValueError(f"score must equal likelihood * impact ({expected}), got {self.score}")
        return self


class Requirement(BaseModel):
    id: str
    raw_text: str
    input_fields: list[Field] = []
    conditions: list[str] = []
    expected_actions: list[str] = []
    category: Literal["functional", "non-functional"] = "functional"
    risk: RiskScore | None = None


class TestCase(BaseModel):
    # pytest 会尝试收集以 "Test" 开头的类,通过 pyproject.toml 过滤该警告
    id: str
    requirement_id: str
    technique: Literal["EP", "BVA", "DT", "STT"]
    inputs: dict[str, Any] = {}
    preconditions: list[str] = []
    steps: list[str] = []
    expected_result: str = ""
    priority: Literal["High", "Medium", "Low"] = "Medium"
    tags: list[str] = []


class TestSuite(BaseModel):
    cases: list[TestCase] = []
    coverage: dict[str, float] = {}
