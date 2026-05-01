from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field as PydField


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


class Requirement(BaseModel):
    id: str
    raw_text: str
    input_fields: list[Field] = []
    conditions: list[str] = []
    expected_actions: list[str] = []
    category: Literal["functional", "non-functional"] = "functional"
    risk: RiskScore | None = None


class TestCase(BaseModel):
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
