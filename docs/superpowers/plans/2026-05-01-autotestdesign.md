# AutoTestDesign Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an AI-driven AutoTestDesign tool implementing all 7 FRs (ISO 29119-4 aligned) with a Streamlit UI, deterministic algorithms for test generation, and an OpenAI-compatible LLM layer for structured parsing / risk rationale / oracle synthesis.

**Architecture:** Layered: `core/` (pure algorithms + pydantic models, no I/O), `llm/` (OpenAI-compatible client + `.md` prompts), `ui/` (Streamlit panels), `tests/` (pytest). Hybrid approach — algorithms drive test generation for reproducibility; LLM augments with semantic fields and falls back to rule-based defaults on failure.

**Tech Stack:** Python 3.11+, Streamlit, OpenAI Python SDK (compatible endpoint), pydantic v2, pandas, openpyxl, networkx, graphviz, Jinja2, pytest, pytest-cov.

**Reference spec:** `docs/superpowers/specs/2026-05-01-autotestdesign-design.md`

**Implementation order:** Foundation → FR1 → FR2 → FR6 → FR3 (EP/BVA/DT) → FR5 → FR7 → FR4 → UI → Examples → README. This order keeps every intermediate state demo-ready.

---

## Task 1: Project scaffolding and config

**Files:**
- Create: `requirements.txt`
- Create: `pyproject.toml`
- Create: `.gitignore` (update existing)
- Create: `autotestdesign/__init__.py`
- Create: `autotestdesign/config.py`
- Create: `tests/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/unit/test_config.py`
- Create: `tests/fixtures/__init__.py`

- [ ] **Step 1: Create `requirements.txt`**

```text
streamlit>=1.30
openai>=1.40
pydantic>=2.5
pandas>=2.2
openpyxl>=3.1
networkx>=3.2
graphviz>=0.20
Jinja2>=3.1
pytest>=8.0
pytest-cov>=5.0
ruff>=0.5
```

- [ ] **Step 2: Create `pyproject.toml`**

```toml
[project]
name = "autotestdesign"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]

[tool.coverage.run]
source = ["autotestdesign/core"]
omit = ["autotestdesign/llm/*", "autotestdesign/ui/*", "autotestdesign/app.py"]

[tool.ruff]
line-length = 100
```

- [ ] **Step 3: Update `.gitignore`**

Append to existing `.gitignore`:

```text
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
.venv/
venv/
*.egg-info/
dist/
build/
.ruff_cache/
```

- [ ] **Step 4: Install deps**

Run: `python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
Expected: all packages install without errors.

- [ ] **Step 5: Create `autotestdesign/__init__.py` and `tests/__init__.py` (both empty)**

```python
```

Also create `tests/unit/__init__.py` and `tests/fixtures/__init__.py` as empty files.

- [ ] **Step 6: Write failing test for config loader**

Create `tests/unit/test_config.py`:

```python
import json
from pathlib import Path
import pytest
from autotestdesign.config import load_config, Config


def test_load_config_reads_json(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "base_url": "https://api.example.com/v1",
        "api_key": "sk-test",
        "model": "gpt-4o-mini",
    }))
    cfg = load_config(cfg_file)
    assert isinstance(cfg, Config)
    assert cfg.base_url == "https://api.example.com/v1"
    assert cfg.api_key == "sk-test"
    assert cfg.model == "gpt-4o-mini"
    assert cfg.temperature == 0.2


def test_load_config_supports_legacy_anthropic_keys(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "ANTHROPIC_BASE_URL": "https://hub.fishriceai.com",
        "ANTHROPIC_AUTH_TOKEN": "token-abc",
    }))
    cfg = load_config(cfg_file)
    assert cfg.base_url == "https://hub.fishriceai.com"
    assert cfg.api_key == "token-abc"


def test_load_config_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "missing.json")
```

- [ ] **Step 7: Run test, expect failure**

Run: `pytest tests/unit/test_config.py -v`
Expected: FAIL (ModuleNotFoundError: autotestdesign.config).

- [ ] **Step 8: Implement `autotestdesign/config.py`**

```python
from __future__ import annotations
import json
from pathlib import Path
from pydantic import BaseModel, Field

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / ".env" / "config.json"


class Config(BaseModel):
    base_url: str
    api_key: str
    model: str = "gpt-4o-mini"
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_retries: int = 3


def load_config(path: Path | None = None) -> Config:
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    raw = json.loads(path.read_text())
    normalized = {
        "base_url": raw.get("base_url") or raw.get("ANTHROPIC_BASE_URL") or raw.get("OPENAI_BASE_URL", ""),
        "api_key": raw.get("api_key") or raw.get("ANTHROPIC_AUTH_TOKEN") or raw.get("OPENAI_API_KEY", ""),
        "model": raw.get("model", "gpt-4o-mini"),
        "temperature": raw.get("temperature", 0.2),
        "max_retries": raw.get("max_retries", 3),
    }
    return Config(**normalized)
```

- [ ] **Step 9: Run tests, expect pass**

Run: `pytest tests/unit/test_config.py -v`
Expected: 3 passed.

- [ ] **Step 10: Commit**

```bash
git add requirements.txt pyproject.toml .gitignore autotestdesign/__init__.py autotestdesign/config.py tests/
git commit -m "feat: scaffold project with config loader"
```

---

## Task 2: Data models (pydantic)

**Files:**
- Create: `autotestdesign/core/__init__.py`
- Create: `autotestdesign/core/models.py`
- Create: `tests/unit/test_models.py`

- [ ] **Step 1: Create empty `autotestdesign/core/__init__.py`**

```python
```

- [ ] **Step 2: Write failing test for models**

Create `tests/unit/test_models.py`:

```python
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
```

- [ ] **Step 3: Run test, expect failure**

Run: `pytest tests/unit/test_models.py -v`
Expected: FAIL (ModuleNotFoundError).

- [ ] **Step 4: Implement `autotestdesign/core/models.py`**

```python
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
```

- [ ] **Step 5: Run tests, expect pass**

Run: `pytest tests/unit/test_models.py -v`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add autotestdesign/core/__init__.py autotestdesign/core/models.py tests/unit/test_models.py
git commit -m "feat: add pydantic data models (Requirement, TestCase, TestSuite)"
```

---

## Task 3: LLM client abstraction with fake fixture

**Files:**
- Create: `autotestdesign/llm/__init__.py`
- Create: `autotestdesign/llm/client.py`
- Create: `autotestdesign/llm/prompts/__init__.py`
- Create: `tests/fixtures/fake_llm.py`
- Create: `tests/unit/test_llm_client.py`

- [ ] **Step 1: Create `autotestdesign/llm/__init__.py` and `autotestdesign/llm/prompts/__init__.py` (empty)**

```python
```

- [ ] **Step 2: Create `tests/fixtures/fake_llm.py`**

```python
from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class FakeLLM:
    """Deterministic in-memory LLM for tests.

    Usage: preload responses by prompt_name, then inject in place of LLMClient.
    """

    def __init__(self, responses: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def queue(self, prompt_name: str, payload: dict[str, Any]) -> None:
        self.responses.setdefault(prompt_name, []).append(payload)

    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type[BaseModel]) -> BaseModel:
        self.calls.append((prompt_name, variables))
        queue = self.responses.get(prompt_name)
        if not queue:
            raise AssertionError(f"FakeLLM has no response queued for prompt '{prompt_name}'")
        payload = queue.pop(0)
        return schema.model_validate(payload)
```

- [ ] **Step 3: Write failing test for LLM client**

Create `tests/unit/test_llm_client.py`:

```python
import pytest
from pydantic import BaseModel
from autotestdesign.config import Config
from autotestdesign.llm.client import LLMClient, LLMOutputError


class _Demo(BaseModel):
    name: str
    score: int


class _StubCompletion:
    def __init__(self, content: str) -> None:
        self.choices = [type("C", (), {"message": type("M", (), {"content": content})()})()]


class _StubOpenAI:
    def __init__(self, contents: list[str]) -> None:
        self._contents = contents
        self.chat = type("Chat", (), {"completions": self})()
        self.calls = 0

    def create(self, **kwargs):
        content = self._contents[self.calls]
        self.calls += 1
        return _StubCompletion(content)


def _make_client(stub: _StubOpenAI, tmp_path) -> LLMClient:
    prompt = tmp_path / "p.md"
    prompt.write_text("Hello {{ who }}. Return JSON.")
    cfg = Config(base_url="x", api_key="y", model="m", max_retries=3)
    c = LLMClient(cfg, prompt_dir=tmp_path, openai_client=stub)
    return c


def test_structured_call_parses_valid_json(tmp_path):
    stub = _StubOpenAI(['{"name": "a", "score": 1}'])
    client = _make_client(stub, tmp_path)
    out = client.structured_call("p", {"who": "world"}, _Demo)
    assert out.name == "a" and out.score == 1
    assert stub.calls == 1


def test_structured_call_retries_on_bad_json(tmp_path):
    stub = _StubOpenAI(["not json", '{"name": "b", "score": 2}'])
    client = _make_client(stub, tmp_path)
    out = client.structured_call("p", {"who": "x"}, _Demo)
    assert out.score == 2
    assert stub.calls == 2


def test_structured_call_raises_after_max_retries(tmp_path):
    stub = _StubOpenAI(["bad", "still bad", "nope"])
    client = _make_client(stub, tmp_path)
    with pytest.raises(LLMOutputError):
        client.structured_call("p", {"who": "x"}, _Demo)
```

- [ ] **Step 4: Run test, expect failure**

Run: `pytest tests/unit/test_llm_client.py -v`
Expected: FAIL (ModuleNotFoundError).

- [ ] **Step 5: Implement `autotestdesign/llm/client.py`**

```python
from __future__ import annotations
from pathlib import Path
from typing import Any, Protocol
from jinja2 import Template
from pydantic import BaseModel, ValidationError
from autotestdesign.config import Config


class LLMOutputError(RuntimeError):
    pass


class _OpenAILike(Protocol):
    chat: Any


DEFAULT_PROMPT_DIR = Path(__file__).parent / "prompts"


class LLMClient:
    def __init__(
        self,
        config: Config,
        prompt_dir: Path | None = None,
        openai_client: _OpenAILike | None = None,
    ) -> None:
        self.config = config
        self.prompt_dir = prompt_dir or DEFAULT_PROMPT_DIR
        if openai_client is None:
            from openai import OpenAI
            openai_client = OpenAI(base_url=config.base_url, api_key=config.api_key)
        self._client = openai_client

    def _render(self, prompt_name: str, variables: dict[str, Any]) -> str:
        path = self.prompt_dir / f"{prompt_name}.md"
        template = Template(path.read_text())
        return template.render(**variables)

    def structured_call(
        self,
        prompt_name: str,
        variables: dict[str, Any],
        schema: type[BaseModel],
    ) -> BaseModel:
        prompt = self._render(prompt_name, variables)
        last_err: Exception | None = None
        for _ in range(self.config.max_retries):
            resp = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=self.config.temperature,
            )
            content = resp.choices[0].message.content
            try:
                return schema.model_validate_json(content)
            except ValidationError as e:
                last_err = e
                continue
            except Exception as e:
                last_err = e
                continue
        raise LLMOutputError(f"Failed to get valid response for '{prompt_name}': {last_err}")
```

- [ ] **Step 6: Run tests, expect pass**

Run: `pytest tests/unit/test_llm_client.py -v`
Expected: 3 passed.

- [ ] **Step 7: Commit**

```bash
git add autotestdesign/llm/ tests/fixtures/fake_llm.py tests/unit/test_llm_client.py
git commit -m "feat: add LLM client with jinja prompts, retries, and fake fixture"
```

---

## Task 4: FR1 — Requirement parsing (CSV + plain text via LLM)

**Files:**
- Create: `autotestdesign/core/parsing.py`
- Create: `autotestdesign/llm/prompts/structure_requirement.md`
- Create: `tests/unit/test_parsing.py`

- [ ] **Step 1: Create prompt template `autotestdesign/llm/prompts/structure_requirement.md`**

```markdown
You are a requirements analyst. Extract a structured Requirement from the raw text below.

Raw requirement text:
---
{{ raw_text }}
---

Return STRICTLY a JSON object with this exact schema (no prose, no markdown fences):

{
  "id": "<assign sequential like REQ-001 if none given>",
  "raw_text": "<copy of the input>",
  "input_fields": [
    {"name": "<field>", "type": "int|float|string|enum|bool", "min": null, "max": null, "allowed": null}
  ],
  "conditions": ["<precondition or business rule>"],
  "expected_actions": ["<action the system should perform>"],
  "category": "functional"
}

Guidance:
- Extract numeric ranges into min/max. Use null when unbounded.
- Extract enum values into allowed; otherwise null.
- If the requirement talks about performance, security, or usability without a concrete input, set category="non-functional".
```

- [ ] **Step 2: Write failing test for parsing**

Create `tests/unit/test_parsing.py`:

```python
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
```

- [ ] **Step 3: Run test, expect failure**

Run: `pytest tests/unit/test_parsing.py -v`
Expected: FAIL (ModuleNotFoundError).

- [ ] **Step 4: Implement `autotestdesign/core/parsing.py`**

```python
from __future__ import annotations
from pathlib import Path
from typing import Any, Protocol
import pandas as pd
from autotestdesign.core.models import Requirement


class _LLMLike(Protocol):
    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type) -> Any: ...


def parse_csv(path: Path) -> list[Requirement]:
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
    chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
    return [
        Requirement(id=f"REQ-{i+1:03d}", raw_text=chunk)
        for i, chunk in enumerate(chunks)
    ]


def parse_with_llm(raw_text: str, llm: _LLMLike) -> Requirement:
    return llm.structured_call(
        "structure_requirement",
        {"raw_text": raw_text},
        Requirement,
    )
```

- [ ] **Step 5: Run tests, expect pass**

Run: `pytest tests/unit/test_parsing.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add autotestdesign/core/parsing.py autotestdesign/llm/prompts/structure_requirement.md tests/unit/test_parsing.py
git commit -m "feat(fr1): requirement parsing from CSV, text block, and LLM"
```

---

## Task 5: FR2 — Risk scoring (rule-based + LLM rationale)

**Files:**
- Create: `autotestdesign/core/risk.py`
- Create: `autotestdesign/llm/prompts/score_risk.md`
- Create: `tests/unit/test_risk.py`

- [ ] **Step 1: Create prompt `autotestdesign/llm/prompts/score_risk.md`**

```markdown
You are a software QA risk analyst. Given the requirement below and a pre-computed rule-based risk score, produce a short rationale (1-2 sentences) explaining why this score is appropriate.

Requirement: {{ raw_text }}
Pre-computed likelihood: {{ likelihood }}
Pre-computed impact: {{ impact }}
Score: {{ score }}
Priority: {{ priority }}

Return STRICTLY a JSON object:
{"rationale": "<1-2 sentences>"}
```

- [ ] **Step 2: Write failing test**

Create `tests/unit/test_risk.py`:

```python
import pytest
from autotestdesign.core.models import Requirement
from autotestdesign.core.risk import compute_risk_rule_based, attach_risk
from tests.fixtures.fake_llm import FakeLLM


def _req(text: str) -> Requirement:
    return Requirement(id="REQ-001", raw_text=text)


def test_payment_keyword_raises_likelihood():
    rs = compute_risk_rule_based(_req("handle credit card payment securely"))
    assert rs.likelihood >= 4
    assert rs.priority in ("High",)


def test_generic_requirement_is_medium_or_low():
    rs = compute_risk_rule_based(_req("display the user profile picture on the homepage"))
    assert rs.priority in ("Medium", "Low")


def test_score_is_product_of_factors():
    rs = compute_risk_rule_based(_req("auth system"))
    assert rs.score == rs.likelihood * rs.impact


def test_attach_risk_populates_rationale_from_llm():
    fake = FakeLLM()
    fake.queue("score_risk", {"rationale": "Payment flow carries financial and reputational risk."})
    req = _req("process customer payment via Stripe")
    out = attach_risk(req, fake)
    assert out.risk is not None
    assert out.risk.rationale.startswith("Payment flow")
    assert out.risk.score == out.risk.likelihood * out.risk.impact


def test_attach_risk_falls_back_on_llm_failure():
    class _BoomLLM:
        def structured_call(self, *a, **kw):
            raise RuntimeError("network down")
    req = _req("login with password")
    out = attach_risk(req, _BoomLLM())
    assert out.risk is not None
    assert "rule-based" in out.risk.rationale.lower()
```

- [ ] **Step 3: Run test, expect failure**

Run: `pytest tests/unit/test_risk.py -v`
Expected: FAIL.

- [ ] **Step 4: Implement `autotestdesign/core/risk.py`**

```python
from __future__ import annotations
from typing import Any, Protocol
from pydantic import BaseModel
from autotestdesign.core.models import Requirement, RiskScore

HIGH_IMPACT_KEYWORDS = {
    "payment", "credit card", "billing", "auth", "login", "password",
    "security", "encrypt", "token", "admin", "permission", "privacy",
    "personal data", "pii", "compliance",
}
HIGH_LIKELIHOOD_KEYWORDS = {
    "concurrent", "real-time", "external api", "network", "integration",
    "migration", "async", "parallel",
}


class _Rationale(BaseModel):
    rationale: str


class _LLMLike(Protocol):
    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type) -> Any: ...


def _priority_from_score(score: int) -> str:
    if score >= 15:
        return "High"
    if score >= 8:
        return "Medium"
    return "Low"


def compute_risk_rule_based(req: Requirement) -> RiskScore:
    text = req.raw_text.lower()
    impact = 2
    likelihood = 2
    for kw in HIGH_IMPACT_KEYWORDS:
        if kw in text:
            impact = min(5, impact + 2)
            break
    for kw in HIGH_LIKELIHOOD_KEYWORDS:
        if kw in text:
            likelihood = min(5, likelihood + 2)
            break
    if req.category == "non-functional":
        impact = max(impact, 3)
    score = likelihood * impact
    return RiskScore(
        likelihood=likelihood,
        impact=impact,
        score=score,
        priority=_priority_from_score(score),  # type: ignore[arg-type]
        rationale="Rule-based baseline.",
    )


def attach_risk(req: Requirement, llm: _LLMLike) -> Requirement:
    rs = compute_risk_rule_based(req)
    try:
        rationale = llm.structured_call(
            "score_risk",
            {
                "raw_text": req.raw_text,
                "likelihood": rs.likelihood,
                "impact": rs.impact,
                "score": rs.score,
                "priority": rs.priority,
            },
            _Rationale,
        )
        rs = rs.model_copy(update={"rationale": rationale.rationale})
    except Exception:
        rs = rs.model_copy(update={"rationale": f"{rs.rationale} (LLM unavailable; used rule-based only.)"})
    return req.model_copy(update={"risk": rs})
```

- [ ] **Step 5: Run tests, expect pass**

Run: `pytest tests/unit/test_risk.py -v`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add autotestdesign/core/risk.py autotestdesign/llm/prompts/score_risk.md tests/unit/test_risk.py
git commit -m "feat(fr2): rule-based risk scoring with LLM rationale + fallback"
```

---

## Task 6: FR6 — Export to JSON / CSV / Excel

**Files:**
- Create: `autotestdesign/core/export.py`
- Create: `tests/unit/test_export.py`

- [ ] **Step 1: Write failing test**

Create `tests/unit/test_export.py`:

```python
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
```

- [ ] **Step 2: Run test, expect failure**

Run: `pytest tests/unit/test_export.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `autotestdesign/core/export.py`**

```python
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from autotestdesign.core.models import TestSuite


def to_json(suite: TestSuite) -> str:
    return suite.model_dump_json(indent=2)


def _suite_to_dataframe(suite: TestSuite) -> pd.DataFrame:
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
    _suite_to_dataframe(suite).to_csv(path, index=False)


def to_xlsx(suite: TestSuite, path: Path) -> None:
    _suite_to_dataframe(suite).to_excel(path, index=False, engine="openpyxl")
```

- [ ] **Step 4: Run tests, expect pass**

Run: `pytest tests/unit/test_export.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add autotestdesign/core/export.py tests/unit/test_export.py
git commit -m "feat(fr6): export TestSuite to JSON, CSV, Excel"
```

---

## Task 7: FR3 — Equivalence Partitioning

**Files:**
- Create: `autotestdesign/core/blackbox/__init__.py`
- Create: `autotestdesign/core/blackbox/equivalence.py`
- Create: `tests/unit/test_equivalence.py`

- [ ] **Step 1: Create empty `autotestdesign/core/blackbox/__init__.py`**

- [ ] **Step 2: Write failing test**

Create `tests/unit/test_equivalence.py`:

```python
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
```

- [ ] **Step 3: Run test, expect failure**

Run: `pytest tests/unit/test_equivalence.py -v`
Expected: FAIL.

- [ ] **Step 4: Implement `autotestdesign/core/blackbox/equivalence.py`**

```python
from __future__ import annotations
from autotestdesign.core.models import Field, Requirement, TestCase


def _partitions_for_field(f: Field) -> list[tuple[str, object]]:
    """Return (label, value) pairs for equivalence classes."""
    if f.type == "int":
        lo = f.min if f.min is not None else -1_000_000
        hi = f.max if f.max is not None else 1_000_000
        mid = (lo + hi) // 2 if lo < hi else lo
        parts: list[tuple[str, object]] = []
        if f.min is not None:
            parts.append(("below_min", lo - 1))
        parts.append(("valid", mid))
        if f.max is not None:
            parts.append(("above_max", hi + 1))
        return parts
    if f.type == "float":
        lo = float(f.min) if f.min is not None else -1e6
        hi = float(f.max) if f.max is not None else 1e6
        mid = (lo + hi) / 2 if lo < hi else lo
        parts = []
        if f.min is not None:
            parts.append(("below_min", lo - 0.01))
        parts.append(("valid", mid))
        if f.max is not None:
            parts.append(("above_max", hi + 0.01))
        return parts
    if f.type == "enum":
        allowed = f.allowed or []
        parts = [(f"valid_{v}", v) for v in allowed]
        parts.append(("invalid_enum", "__INVALID__"))
        return parts
    if f.type == "string":
        return [("empty", ""), ("normal", "valid_value"), ("too_long", "x" * 1024)]
    if f.type == "bool":
        return [("true", True), ("false", False)]
    return [("default", None)]


def generate_equivalence_cases(req: Requirement) -> list[TestCase]:
    cases: list[TestCase] = []
    counter = 1
    for field in req.input_fields:
        for label, value in _partitions_for_field(field):
            is_invalid = label.startswith(("below", "above", "invalid", "empty", "too_long"))
            cases.append(TestCase(
                id=f"{req.id}-EP-{counter:03d}",
                requirement_id=req.id,
                technique="EP",
                inputs={field.name: value},
                steps=[f"Submit with {field.name}={value!r}"],
                expected_result=(
                    f"System rejects input ({label})" if is_invalid
                    else f"System accepts input ({label})"
                ),
                priority=(req.risk.priority if req.risk else "Medium"),
                tags=["EP", field.name, label],
            ))
            counter += 1
    return cases
```

- [ ] **Step 5: Run tests, expect pass**

Run: `pytest tests/unit/test_equivalence.py -v`
Expected: 5 passed.

- [ ] **Step 6: Commit**

```bash
git add autotestdesign/core/blackbox/ tests/unit/test_equivalence.py
git commit -m "feat(fr3): equivalence partitioning test generator"
```

---

## Task 8: FR3 — Boundary Value Analysis

**Files:**
- Create: `autotestdesign/core/blackbox/boundary.py`
- Create: `tests/unit/test_boundary.py`

- [ ] **Step 1: Write failing test**

Create `tests/unit/test_boundary.py`:

```python
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
```

- [ ] **Step 2: Run test, expect failure**

Run: `pytest tests/unit/test_boundary.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `autotestdesign/core/blackbox/boundary.py`**

```python
from __future__ import annotations
from autotestdesign.core.models import Field, Requirement, TestCase

_FLOAT_EPS = 0.01


def _boundary_values(f: Field) -> list[object]:
    if f.min is None or f.max is None:
        return []
    if f.type == "int":
        lo, hi = int(f.min), int(f.max)
        return [lo - 1, lo, lo + 1, hi - 1, hi, hi + 1]
    if f.type == "float":
        lo, hi = float(f.min), float(f.max)
        return [lo - _FLOAT_EPS, lo, lo + _FLOAT_EPS, hi - _FLOAT_EPS, hi, hi + _FLOAT_EPS]
    if f.type == "string":
        lo, hi = int(f.min), int(f.max)
        return ["x" * n for n in [lo - 1, lo, lo + 1, hi - 1, hi, hi + 1]]
    return []


def generate_boundary_cases(req: Requirement) -> list[TestCase]:
    cases: list[TestCase] = []
    counter = 1
    for field in req.input_fields:
        values = _boundary_values(field)
        for v in values:
            if field.type == "string":
                length = len(v)  # type: ignore[arg-type]
                is_invalid = length < (field.min or 0) or length > (field.max or 0)
            else:
                is_invalid = v < field.min or v > field.max  # type: ignore[operator]
            cases.append(TestCase(
                id=f"{req.id}-BVA-{counter:03d}",
                requirement_id=req.id,
                technique="BVA",
                inputs={field.name: v},
                steps=[f"Submit with {field.name}={v!r}"],
                expected_result=(
                    f"System rejects ({field.name} out of range)"
                    if is_invalid else f"System accepts ({field.name} within range)"
                ),
                priority=(req.risk.priority if req.risk else "Medium"),
                tags=["BVA", field.name],
            ))
            counter += 1
    return cases
```

- [ ] **Step 4: Run tests, expect pass**

Run: `pytest tests/unit/test_boundary.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add autotestdesign/core/blackbox/boundary.py tests/unit/test_boundary.py
git commit -m "feat(fr3): boundary value analysis generator"
```

---

## Task 9: FR3 — Decision Table

**Files:**
- Create: `autotestdesign/core/blackbox/decision_table.py`
- Create: `tests/unit/test_decision_table.py`

- [ ] **Step 1: Write failing test**

Create `tests/unit/test_decision_table.py`:

```python
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
```

- [ ] **Step 2: Run test, expect failure**

Run: `pytest tests/unit/test_decision_table.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `autotestdesign/core/blackbox/decision_table.py`**

```python
from __future__ import annotations
from itertools import product
from autotestdesign.core.models import Requirement, TestCase


def generate_decision_table_cases(req: Requirement) -> list[TestCase]:
    if not req.conditions:
        return []
    cases: list[TestCase] = []
    for i, combo in enumerate(product([False, True], repeat=len(req.conditions)), start=1):
        inputs = dict(zip(req.conditions, combo))
        true_conditions = [k for k, v in inputs.items() if v]
        expected = (
            "Execute actions: " + ", ".join(req.expected_actions)
            if true_conditions and req.expected_actions
            else "No action / reject"
        )
        cases.append(TestCase(
            id=f"{req.id}-DT-{i:03d}",
            requirement_id=req.id,
            technique="DT",
            inputs=inputs,
            steps=[f"Given conditions {inputs}"],
            expected_result=expected,
            priority=(req.risk.priority if req.risk else "Medium"),
            tags=["DT"] + true_conditions,
        ))
    return cases
```

- [ ] **Step 4: Run tests, expect pass**

Run: `pytest tests/unit/test_decision_table.py -v`
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add autotestdesign/core/blackbox/decision_table.py tests/unit/test_decision_table.py
git commit -m "feat(fr3): decision table generator (2^N truth table)"
```

---

## Task 10: FR5 — Test oracle synthesis

**Files:**
- Create: `autotestdesign/core/oracle.py`
- Create: `autotestdesign/llm/prompts/synthesize_oracle.md`
- Create: `tests/unit/test_oracle.py`

- [ ] **Step 1: Create prompt `autotestdesign/llm/prompts/synthesize_oracle.md`**

```markdown
You are a test oracle generator. Given a requirement and a concrete test input, produce the expected system behavior in one sentence.

Requirement: {{ raw_text }}
Expected actions declared: {{ expected_actions }}
Test inputs: {{ inputs }}

Return STRICTLY a JSON object:
{"expected_result": "<one-sentence expected behavior>"}
```

- [ ] **Step 2: Write failing test**

Create `tests/unit/test_oracle.py`:

```python
from autotestdesign.core.models import Field, Requirement, TestCase
from autotestdesign.core.oracle import synthesize_oracle
from tests.fixtures.fake_llm import FakeLLM


def _req() -> Requirement:
    return Requirement(
        id="REQ-001", raw_text="age must be 18-120",
        input_fields=[Field(name="age", type="int", min=18, max=120)],
        expected_actions=["accept registration"],
    )


def _tc(age: int) -> TestCase:
    return TestCase(id="TC-001", requirement_id="REQ-001", technique="EP", inputs={"age": age})


def test_out_of_range_uses_algorithmic_fallback_without_llm():
    req = _req()
    out = synthesize_oracle(req, _tc(17), llm=None)
    assert "reject" in out.expected_result.lower()


def test_in_range_calls_llm_when_available():
    req = _req()
    fake = FakeLLM()
    fake.queue("synthesize_oracle", {"expected_result": "System creates a new account."})
    out = synthesize_oracle(req, _tc(30), llm=fake)
    assert out.expected_result == "System creates a new account."


def test_llm_failure_falls_back_to_default():
    req = _req()
    class _Boom:
        def structured_call(self, *a, **kw):
            raise RuntimeError("x")
    out = synthesize_oracle(req, _tc(30), llm=_Boom())
    assert out.expected_result  # non-empty fallback
    assert "accept" in out.expected_result.lower() or "reject" in out.expected_result.lower()
```

- [ ] **Step 3: Run test, expect failure**

Run: `pytest tests/unit/test_oracle.py -v`
Expected: FAIL.

- [ ] **Step 4: Implement `autotestdesign/core/oracle.py`**

```python
from __future__ import annotations
from typing import Any, Protocol
from pydantic import BaseModel
from autotestdesign.core.models import Requirement, TestCase


class _OracleOut(BaseModel):
    expected_result: str


class _LLMLike(Protocol):
    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type) -> Any: ...


def _is_out_of_range(req: Requirement, tc: TestCase) -> tuple[bool, str]:
    for field in req.input_fields:
        if field.name not in tc.inputs:
            continue
        v = tc.inputs[field.name]
        if field.type in ("int", "float") and field.min is not None and v < field.min:
            return True, f"{field.name} below minimum ({field.min})"
        if field.type in ("int", "float") and field.max is not None and v > field.max:
            return True, f"{field.name} above maximum ({field.max})"
        if field.type == "enum" and field.allowed and v not in field.allowed:
            return True, f"{field.name} not in allowed set"
    return False, ""


def synthesize_oracle(req: Requirement, tc: TestCase, llm: _LLMLike | None) -> TestCase:
    out_of_range, reason = _is_out_of_range(req, tc)
    if out_of_range:
        return tc.model_copy(update={
            "expected_result": f"System rejects input: {reason}."
        })
    if llm is None:
        default = (
            f"System performs: {', '.join(req.expected_actions)}."
            if req.expected_actions else "System accepts input."
        )
        return tc.model_copy(update={"expected_result": default})
    try:
        res = llm.structured_call(
            "synthesize_oracle",
            {
                "raw_text": req.raw_text,
                "expected_actions": req.expected_actions,
                "inputs": tc.inputs,
            },
            _OracleOut,
        )
        return tc.model_copy(update={"expected_result": res.expected_result})
    except Exception:
        default = (
            f"System performs: {', '.join(req.expected_actions)}."
            if req.expected_actions else "System accepts input."
        )
        return tc.model_copy(update={"expected_result": default})
```

- [ ] **Step 5: Run tests, expect pass**

Run: `pytest tests/unit/test_oracle.py -v`
Expected: 3 passed.

- [ ] **Step 6: Commit**

```bash
git add autotestdesign/core/oracle.py autotestdesign/llm/prompts/synthesize_oracle.md tests/unit/test_oracle.py
git commit -m "feat(fr5): oracle synthesis with algorithmic fallback + LLM"
```

---

## Task 11: FR7 — Test suite optimization

**Files:**
- Create: `autotestdesign/core/optimizer.py`
- Create: `tests/unit/test_optimizer.py`

- [ ] **Step 1: Write failing test**

Create `tests/unit/test_optimizer.py`:

```python
from autotestdesign.core.models import TestCase, TestSuite
from autotestdesign.core.optimizer import dedup_and_prioritize, weighted_cover


def _tc(id_: str, req: str, tech: str, inputs: dict, priority: str = "Medium") -> TestCase:
    return TestCase(id=id_, requirement_id=req, technique=tech, inputs=inputs, priority=priority)


def test_dedup_removes_identical_inputs_same_technique():
    cases = [
        _tc("A", "R1", "EP", {"age": 10}),
        _tc("B", "R1", "EP", {"age": 10}),  # duplicate
        _tc("C", "R1", "EP", {"age": 11}),
    ]
    out = dedup_and_prioritize(cases)
    ids = [c.id for c in out]
    assert len(out) == 2
    assert ids[0] in ("A", "B")  # one kept, not both
    assert "C" in ids


def test_priority_sort_high_first():
    cases = [
        _tc("L", "R1", "EP", {"x": 1}, priority="Low"),
        _tc("H", "R1", "EP", {"x": 2}, priority="High"),
        _tc("M", "R1", "EP", {"x": 3}, priority="Medium"),
    ]
    out = dedup_and_prioritize(cases)
    assert [c.id for c in out] == ["H", "M", "L"]


def test_weighted_cover_drops_redundant_low_priority():
    cases = [
        _tc("H1", "R1", "BVA", {"a": 1}, priority="High"),
        _tc("L1", "R1", "BVA", {"a": 1}, priority="Low"),
        _tc("M1", "R2", "EP", {"a": 2}, priority="Medium"),
    ]
    suite: TestSuite = weighted_cover(cases, max_cases=2)
    assert len(suite.cases) == 2
    reqs = {c.requirement_id for c in suite.cases}
    assert reqs == {"R1", "R2"}
```

- [ ] **Step 2: Run test, expect failure**

Run: `pytest tests/unit/test_optimizer.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement `autotestdesign/core/optimizer.py`**

```python
from __future__ import annotations
import json
from autotestdesign.core.models import TestCase, TestSuite

PRIORITY_ORDER = {"High": 0, "Medium": 1, "Low": 2}
PRIORITY_WEIGHT = {"High": 5, "Medium": 3, "Low": 1}


def _signature(tc: TestCase) -> tuple:
    return (tc.requirement_id, tc.technique, json.dumps(tc.inputs, sort_keys=True, default=str))


def dedup_and_prioritize(cases: list[TestCase]) -> list[TestCase]:
    seen: dict[tuple, TestCase] = {}
    for tc in cases:
        sig = _signature(tc)
        existing = seen.get(sig)
        if existing is None or PRIORITY_ORDER[tc.priority] < PRIORITY_ORDER[existing.priority]:
            seen[sig] = tc
    return sorted(seen.values(), key=lambda c: (PRIORITY_ORDER[c.priority], c.id))


def weighted_cover(cases: list[TestCase], max_cases: int | None = None) -> TestSuite:
    deduped = dedup_and_prioritize(cases)
    selected: list[TestCase] = []
    covered_reqs: set[str] = set()
    for tc in deduped:
        if tc.requirement_id not in covered_reqs:
            selected.append(tc)
            covered_reqs.add(tc.requirement_id)
    remaining = [c for c in deduped if c not in selected]
    remaining.sort(key=lambda c: -PRIORITY_WEIGHT[c.priority])
    for tc in remaining:
        if max_cases is not None and len(selected) >= max_cases:
            break
        selected.append(tc)
    if max_cases is not None:
        selected = selected[:max_cases]
    total_reqs = len({c.requirement_id for c in cases})
    coverage = {
        "requirement_coverage": len({c.requirement_id for c in selected}) / total_reqs if total_reqs else 0.0,
    }
    return TestSuite(cases=selected, coverage=coverage)
```

- [ ] **Step 4: Run tests, expect pass**

Run: `pytest tests/unit/test_optimizer.py -v`
Expected: 3 passed.

- [ ] **Step 5: Commit**

```bash
git add autotestdesign/core/optimizer.py tests/unit/test_optimizer.py
git commit -m "feat(fr7): test suite optimizer (dedup + weighted cover)"
```

---

## Task 12: FR4 — State machine model

**Files:**
- Create: `autotestdesign/core/whitebox/__init__.py`
- Create: `autotestdesign/core/whitebox/state_machine.py`
- Create: `tests/unit/test_state_machine.py`

- [ ] **Step 1: Create empty `autotestdesign/core/whitebox/__init__.py`**

- [ ] **Step 2: Write failing test**

Create `tests/unit/test_state_machine.py`:

```python
import pytest
from autotestdesign.core.whitebox.state_machine import (
    StateMachine, Transition, parse_dsl, generate_all_states_cases, generate_all_transitions_cases,
)


def test_parse_dsl_simple():
    dsl = """
    S1 --login--> S2
    S2 --logout--> S1
    S2 --error--> S3
    """
    sm = parse_dsl(dsl, start_state="S1")
    assert sorted(sm.states) == ["S1", "S2", "S3"]
    assert len(sm.transitions) == 3


def test_state_machine_rejects_empty():
    with pytest.raises(ValueError):
        parse_dsl("", start_state="S1")


def test_all_states_coverage_reaches_every_state():
    sm = StateMachine(
        start_state="S1",
        states=["S1", "S2", "S3"],
        transitions=[
            Transition("S1", "login", "S2"),
            Transition("S2", "logout", "S1"),
            Transition("S2", "error", "S3"),
        ],
    )
    cases = generate_all_states_cases(sm, requirement_id="REQ-001")
    visited = {sm.start_state}
    for tc in cases:
        for step in tc.steps:
            for state in sm.states:
                if step.endswith(f"-> {state}"):
                    visited.add(state)
    assert visited == set(sm.states)


def test_all_transitions_coverage_includes_every_transition():
    sm = StateMachine(
        start_state="S1",
        states=["S1", "S2", "S3"],
        transitions=[
            Transition("S1", "login", "S2"),
            Transition("S2", "logout", "S1"),
            Transition("S2", "error", "S3"),
        ],
    )
    cases = generate_all_transitions_cases(sm, requirement_id="REQ-001")
    events = set()
    for tc in cases:
        for step in tc.steps:
            for t in sm.transitions:
                if f"--{t.event}-->" in step:
                    events.add(t.event)
    assert events == {"login", "logout", "error"}
    assert all(c.technique == "STT" for c in cases)
```

- [ ] **Step 3: Run test, expect failure**

Run: `pytest tests/unit/test_state_machine.py -v`
Expected: FAIL.

- [ ] **Step 4: Implement `autotestdesign/core/whitebox/state_machine.py`**

```python
from __future__ import annotations
import re
from dataclasses import dataclass
import networkx as nx
from autotestdesign.core.models import TestCase


@dataclass(frozen=True)
class Transition:
    source: str
    event: str
    target: str


@dataclass
class StateMachine:
    start_state: str
    states: list[str]
    transitions: list[Transition]

    def to_digraph(self) -> nx.MultiDiGraph:
        g = nx.MultiDiGraph()
        for s in self.states:
            g.add_node(s)
        for t in self.transitions:
            g.add_edge(t.source, t.target, event=t.event)
        return g


_DSL_LINE = re.compile(r"^\s*(\w+)\s*--\s*([^-\s][^-]*?)\s*-->\s*(\w+)\s*$")


def parse_dsl(text: str, start_state: str) -> StateMachine:
    transitions: list[Transition] = []
    states: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = _DSL_LINE.match(line)
        if not m:
            continue
        src, event, tgt = m.group(1), m.group(2).strip(), m.group(3)
        transitions.append(Transition(src, event, tgt))
        states.add(src)
        states.add(tgt)
    if not transitions:
        raise ValueError("DSL produced no transitions")
    if start_state not in states:
        states.add(start_state)
    return StateMachine(start_state=start_state, states=sorted(states), transitions=transitions)


def _path_steps(path: list[tuple[str, str, str]]) -> list[str]:
    steps = []
    for src, ev, tgt in path:
        steps.append(f"{src} --{ev}--> {tgt}")
    return steps


def generate_all_states_cases(sm: StateMachine, requirement_id: str) -> list[TestCase]:
    g = sm.to_digraph()
    reached = {sm.start_state}
    cases: list[TestCase] = []
    counter = 1
    for target in sm.states:
        if target in reached:
            continue
        try:
            node_path = nx.shortest_path(g, sm.start_state, target)
        except nx.NetworkXNoPath:
            continue
        edges: list[tuple[str, str, str]] = []
        for a, b in zip(node_path, node_path[1:]):
            data = g.get_edge_data(a, b)
            first_event = next(iter(data.values()))["event"]
            edges.append((a, first_event, b))
        steps = _path_steps(edges)
        steps.insert(0, f"Start in state {sm.start_state}")
        steps.append(f"-> {target}")
        reached.update(node_path)
        cases.append(TestCase(
            id=f"{requirement_id}-STT-AS-{counter:03d}",
            requirement_id=requirement_id,
            technique="STT",
            inputs={"target_state": target},
            steps=steps,
            expected_result=f"System reaches state {target}",
            priority="High",
            tags=["STT", "all_states"],
        ))
        counter += 1
    return cases


def generate_all_transitions_cases(sm: StateMachine, requirement_id: str) -> list[TestCase]:
    g = sm.to_digraph()
    cases: list[TestCase] = []
    counter = 1
    for t in sm.transitions:
        try:
            node_path = nx.shortest_path(g, sm.start_state, t.source)
        except nx.NetworkXNoPath:
            continue
        edges: list[tuple[str, str, str]] = []
        for a, b in zip(node_path, node_path[1:]):
            data = g.get_edge_data(a, b)
            first_event = next(iter(data.values()))["event"]
            edges.append((a, first_event, b))
        edges.append((t.source, t.event, t.target))
        steps = [f"Start in state {sm.start_state}"] + _path_steps(edges)
        cases.append(TestCase(
            id=f"{requirement_id}-STT-AT-{counter:03d}",
            requirement_id=requirement_id,
            technique="STT",
            inputs={"transition": f"{t.source} --{t.event}--> {t.target}"},
            steps=steps,
            expected_result=f"System moves from {t.source} to {t.target} on event '{t.event}'",
            priority="High",
            tags=["STT", "all_transitions", t.event],
        ))
        counter += 1
    return cases
```

- [ ] **Step 5: Run tests, expect pass**

Run: `pytest tests/unit/test_state_machine.py -v`
Expected: 4 passed.

- [ ] **Step 6: Commit**

```bash
git add autotestdesign/core/whitebox/ tests/unit/test_state_machine.py
git commit -m "feat(fr4): state machine model + all-states + all-transitions coverage"
```

---

## Task 13: Pipeline orchestrator

**Files:**
- Create: `autotestdesign/core/pipeline.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/integration/test_pipeline.py`

- [ ] **Step 1: Create empty `tests/integration/__init__.py`**

- [ ] **Step 2: Write failing integration test**

Create `tests/integration/test_pipeline.py`:

```python
from autotestdesign.core.models import Field, Requirement
from autotestdesign.core.pipeline import run_pipeline
from tests.fixtures.fake_llm import FakeLLM


def test_pipeline_end_to_end():
    req = Requirement(
        id="REQ-001",
        raw_text="process payment with amount 0.01-10000",
        input_fields=[Field(name="amount", type="float", min=0.01, max=10000.0)],
        conditions=["valid_card", "sufficient_funds"],
        expected_actions=["charge card", "record transaction"],
    )
    fake = FakeLLM()
    fake.queue("score_risk", {"rationale": "Payment flow is high-risk."})
    for _ in range(20):
        fake.queue("synthesize_oracle", {"expected_result": "Payment processed."})
    suite = run_pipeline([req], llm=fake, optimize_max_cases=None)
    assert suite.cases, "pipeline should produce cases"
    techniques = {c.technique for c in suite.cases}
    assert {"EP", "BVA", "DT"}.issubset(techniques)
    assert all(c.expected_result for c in suite.cases)
    assert suite.coverage.get("requirement_coverage") == 1.0
```

- [ ] **Step 3: Run test, expect failure**

Run: `pytest tests/integration/test_pipeline.py -v`
Expected: FAIL.

- [ ] **Step 4: Implement `autotestdesign/core/pipeline.py`**

```python
from __future__ import annotations
from typing import Any, Protocol
from autotestdesign.core.models import Requirement, TestCase, TestSuite
from autotestdesign.core.risk import attach_risk
from autotestdesign.core.blackbox.equivalence import generate_equivalence_cases
from autotestdesign.core.blackbox.boundary import generate_boundary_cases
from autotestdesign.core.blackbox.decision_table import generate_decision_table_cases
from autotestdesign.core.oracle import synthesize_oracle
from autotestdesign.core.optimizer import weighted_cover
from autotestdesign.core.whitebox.state_machine import (
    StateMachine, generate_all_states_cases, generate_all_transitions_cases,
)


class _LLMLike(Protocol):
    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type) -> Any: ...


def run_pipeline(
    requirements: list[Requirement],
    llm: _LLMLike | None,
    state_machine: StateMachine | None = None,
    state_machine_requirement_id: str | None = None,
    optimize_max_cases: int | None = None,
) -> TestSuite:
    risked: list[Requirement] = []
    for r in requirements:
        risked.append(attach_risk(r, llm) if llm else r.model_copy(update={"risk": None}))

    all_cases: list[TestCase] = []
    for r in risked:
        all_cases.extend(generate_equivalence_cases(r))
        all_cases.extend(generate_boundary_cases(r))
        all_cases.extend(generate_decision_table_cases(r))

    if state_machine is not None and state_machine_requirement_id is not None:
        all_cases.extend(generate_all_states_cases(state_machine, state_machine_requirement_id))
        all_cases.extend(generate_all_transitions_cases(state_machine, state_machine_requirement_id))

    req_map = {r.id: r for r in risked}
    all_cases = [
        synthesize_oracle(req_map[c.requirement_id], c, llm)
        if c.requirement_id in req_map else c
        for c in all_cases
    ]

    return weighted_cover(all_cases, max_cases=optimize_max_cases)
```

- [ ] **Step 5: Run tests, expect pass**

Run: `pytest tests/integration/test_pipeline.py -v`
Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add autotestdesign/core/pipeline.py tests/integration/
git commit -m "feat: pipeline orchestrator wiring all FRs end-to-end"
```

---

## Task 14: Built-in example requirement sets

**Files:**
- Create: `autotestdesign/examples/__init__.py`
- Create: `autotestdesign/examples/banking_registration.csv`
- Create: `autotestdesign/examples/shopping_cart.md`
- Create: `autotestdesign/examples/loader.py`
- Create: `tests/unit/test_examples.py`

- [ ] **Step 1: Create empty `autotestdesign/examples/__init__.py`**

- [ ] **Step 2: Create `autotestdesign/examples/banking_registration.csv`**

```csv
id,raw_text,category
REQ-001,"User age must be between 18 and 120 for registration.",functional
REQ-002,"Password must be 8-32 characters with at least one digit and one letter.",functional
REQ-003,"User must provide a valid email address.",functional
REQ-004,"System must lock the account after 5 consecutive failed login attempts.",functional
REQ-005,"All user data must be encrypted in transit and at rest.",non-functional
REQ-006,"Account creation must complete within 3 seconds.",non-functional
```

- [ ] **Step 3: Create `autotestdesign/examples/shopping_cart.md`**

```markdown
REQ-001: A user can add items to the cart. The cart supports up to 50 distinct items.

REQ-002: When a user applies a discount code, the system validates it against active promotions. Codes must be 6-12 uppercase characters.

REQ-003: At checkout, the user selects a payment method from: credit_card, paypal, bank_transfer, or gift_card. Order total must be between 0.01 and 50000.00.

REQ-004: The system must support concurrent checkouts without double-charging.
```

- [ ] **Step 4: Write failing test**

Create `tests/unit/test_examples.py`:

```python
from autotestdesign.examples.loader import list_examples, load_example


def test_list_examples_returns_expected_entries():
    names = list_examples()
    assert "banking_registration" in names
    assert "shopping_cart" in names


def test_load_example_banking_returns_requirements():
    reqs = load_example("banking_registration")
    assert len(reqs) == 6
    assert reqs[0].id == "REQ-001"


def test_load_example_shopping_returns_requirements():
    reqs = load_example("shopping_cart")
    assert len(reqs) == 4
    assert "cart" in reqs[0].raw_text.lower()
```

- [ ] **Step 5: Run test, expect failure**

Run: `pytest tests/unit/test_examples.py -v`
Expected: FAIL.

- [ ] **Step 6: Implement `autotestdesign/examples/loader.py`**

```python
from __future__ import annotations
from pathlib import Path
from autotestdesign.core.models import Requirement
from autotestdesign.core.parsing import parse_csv, parse_text_block

_EXAMPLES_DIR = Path(__file__).parent
_EXAMPLES: dict[str, tuple[str, str]] = {
    "banking_registration": ("banking_registration.csv", "csv"),
    "shopping_cart": ("shopping_cart.md", "text"),
}


def list_examples() -> list[str]:
    return sorted(_EXAMPLES.keys())


def load_example(name: str) -> list[Requirement]:
    if name not in _EXAMPLES:
        raise KeyError(f"Unknown example: {name}")
    filename, kind = _EXAMPLES[name]
    path = _EXAMPLES_DIR / filename
    if kind == "csv":
        return parse_csv(path)
    return parse_text_block(path.read_text())
```

- [ ] **Step 7: Run tests, expect pass**

Run: `pytest tests/unit/test_examples.py -v`
Expected: 3 passed.

- [ ] **Step 8: Commit**

```bash
git add autotestdesign/examples/ tests/unit/test_examples.py
git commit -m "feat: built-in banking and shopping cart example requirement sets"
```

---

## Task 15: Streamlit UI — layout + input tab

**Files:**
- Create: `autotestdesign/app.py`
- Create: `autotestdesign/ui/__init__.py`
- Create: `autotestdesign/ui/state.py`
- Create: `autotestdesign/ui/upload_panel.py`

Note: Streamlit UI code is not unit-tested (we verify it manually via `streamlit run`).

- [ ] **Step 1: Create empty `autotestdesign/ui/__init__.py`**

- [ ] **Step 2: Create `autotestdesign/ui/state.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, field
import streamlit as st
from autotestdesign.core.models import Requirement, TestSuite


@dataclass
class SessionData:
    requirements: list[Requirement] = field(default_factory=list)
    suite: TestSuite | None = None
    run_log: list[str] = field(default_factory=list)


def get_session() -> SessionData:
    if "atd" not in st.session_state:
        st.session_state.atd = SessionData()
    return st.session_state.atd
```

- [ ] **Step 3: Create `autotestdesign/ui/upload_panel.py`**

```python
from __future__ import annotations
import tempfile
from pathlib import Path
import streamlit as st
from autotestdesign.core.parsing import parse_csv, parse_text_block
from autotestdesign.examples.loader import list_examples, load_example
from autotestdesign.ui.state import get_session


def render_upload_tab() -> None:
    session = get_session()
    st.subheader("FR1 — Requirements Input")

    mode = st.radio(
        "Input mode",
        options=["Built-in example", "Upload file", "Manual text"],
        horizontal=True,
    )

    if mode == "Built-in example":
        choice = st.selectbox("Example", list_examples())
        if st.button("Load example", type="primary"):
            session.requirements = load_example(choice)
            st.success(f"Loaded {len(session.requirements)} requirements from '{choice}'.")

    elif mode == "Upload file":
        up = st.file_uploader("CSV or TXT", type=["csv", "txt", "md"])
        if up is not None and st.button("Parse upload"):
            suffix = Path(up.name).suffix
            with tempfile.NamedTemporaryFile(mode="wb", delete=False, suffix=suffix) as tmp:
                tmp.write(up.read())
                tmp_path = Path(tmp.name)
            if suffix == ".csv":
                session.requirements = parse_csv(tmp_path)
            else:
                session.requirements = parse_text_block(tmp_path.read_text())
            st.success(f"Parsed {len(session.requirements)} requirements.")

    else:
        text = st.text_area("Paste requirements (separate by blank lines)", height=220)
        if st.button("Parse text"):
            session.requirements = parse_text_block(text)
            st.success(f"Parsed {len(session.requirements)} requirements.")

    if session.requirements:
        import pandas as pd
        df = pd.DataFrame([
            {"id": r.id, "raw_text": r.raw_text, "category": r.category,
             "fields": len(r.input_fields), "conditions": len(r.conditions)}
            for r in session.requirements
        ])
        st.dataframe(df, use_container_width=True)
```

- [ ] **Step 4: Create `autotestdesign/app.py`**

```python
from __future__ import annotations
import streamlit as st
from autotestdesign.config import load_config
from autotestdesign.ui.upload_panel import render_upload_tab


st.set_page_config(page_title="AutoTestDesign", layout="wide", page_icon="🧪")
st.title("🧪 AutoTestDesign — AI-driven Test Case Generator")

with st.sidebar:
    st.header("Configuration")
    try:
        cfg = load_config()
        st.caption(f"Model: `{cfg.model}`")
        st.caption(f"Endpoint: `{cfg.base_url or '—'}`")
        st.caption(f"Temperature: {cfg.temperature}")
        st.session_state["_cfg_ok"] = bool(cfg.api_key)
        if not cfg.api_key:
            st.warning("API key not set. LLM features will fall back to rules.")
    except Exception as e:
        st.error(f"Config load error: {e}")
        st.session_state["_cfg_ok"] = False

tab_input, tab_risk, tab_design, tab_export = st.tabs(
    ["📥 Input", "📊 Risk", "🧪 Test Design", "📤 Export"]
)

with tab_input:
    render_upload_tab()

with tab_risk:
    st.info("Run FR2 to populate risk analysis. See Test Design tab for 'Run Pipeline'.")

with tab_design:
    st.info("Populated after running the pipeline on the Test Design tab.")

with tab_export:
    st.info("Export appears here once a TestSuite has been generated.")
```

- [ ] **Step 5: Smoke-test the UI launches**

Run: `streamlit run autotestdesign/app.py --server.headless true --server.port 8501 &`
Then: `sleep 3 && curl -s http://localhost:8501 | head -n 5`
Expected: HTML response (not error). Then kill the process.

- [ ] **Step 6: Commit**

```bash
git add autotestdesign/app.py autotestdesign/ui/
git commit -m "feat(ui): Streamlit shell with 4 tabs and requirements input panel"
```

---

## Task 16: Streamlit UI — risk, test design, export tabs + pipeline runner

**Files:**
- Create: `autotestdesign/ui/risk_panel.py`
- Create: `autotestdesign/ui/testcase_viewer.py`
- Create: `autotestdesign/ui/state_diagram.py`
- Create: `autotestdesign/ui/export_panel.py`
- Modify: `autotestdesign/app.py`

- [ ] **Step 1: Create `autotestdesign/ui/risk_panel.py`**

```python
from __future__ import annotations
import pandas as pd
import streamlit as st
from autotestdesign.ui.state import get_session


def render_risk_tab() -> None:
    session = get_session()
    st.subheader("FR2 — Risk Analysis & Prioritization")
    reqs_with_risk = [r for r in session.requirements if r.risk]
    if not reqs_with_risk:
        st.info("No risk data yet. Run the pipeline from the Test Design tab.")
        return

    df = pd.DataFrame([
        {
            "id": r.id,
            "raw_text": r.raw_text[:80],
            "likelihood": r.risk.likelihood,
            "impact": r.risk.impact,
            "score": r.risk.score,
            "priority": r.risk.priority,
            "rationale": r.risk.rationale,
        }
        for r in reqs_with_risk
    ])
    st.dataframe(df, use_container_width=True)

    counts = df["priority"].value_counts().reindex(["High", "Medium", "Low"]).fillna(0)
    st.bar_chart(counts)
```

- [ ] **Step 2: Create `autotestdesign/ui/state_diagram.py`**

```python
from __future__ import annotations
import streamlit as st
from graphviz import Digraph
from autotestdesign.core.whitebox.state_machine import StateMachine, parse_dsl


def render_state_diagram_section() -> StateMachine | None:
    st.markdown("**FR4 — State Machine (DSL)**")
    default_dsl = "\n".join([
        "# Format: SOURCE --event--> TARGET",
        "Guest --login--> LoggedIn",
        "LoggedIn --logout--> Guest",
        "LoggedIn --failedAttempt--> Locked",
        "Locked --reset--> Guest",
    ])
    dsl = st.text_area("State transitions", value=default_dsl, height=160)
    start = st.text_input("Start state", value="Guest")
    if not dsl.strip():
        return None
    try:
        sm = parse_dsl(dsl, start_state=start)
    except Exception as e:
        st.warning(f"DSL parse error: {e}")
        return None
    g = Digraph()
    for s in sm.states:
        g.node(s, shape="circle" if s != sm.start_state else "doublecircle")
    for t in sm.transitions:
        g.edge(t.source, t.target, label=t.event)
    st.graphviz_chart(g)
    return sm
```

- [ ] **Step 3: Create `autotestdesign/ui/testcase_viewer.py`**

```python
from __future__ import annotations
import pandas as pd
import streamlit as st
from autotestdesign.config import load_config
from autotestdesign.llm.client import LLMClient
from autotestdesign.core.pipeline import run_pipeline
from autotestdesign.ui.state import get_session
from autotestdesign.ui.state_diagram import render_state_diagram_section


def _build_llm_or_none():
    try:
        cfg = load_config()
        if not cfg.api_key:
            return None
        return LLMClient(cfg)
    except Exception:
        return None


def render_test_design_tab() -> None:
    session = get_session()
    st.subheader("FR3/FR4/FR5/FR7 — Test Case Design")

    if not session.requirements:
        st.info("Load requirements first (Input tab).")
        return

    col1, col2 = st.columns([1, 1])
    with col1:
        use_llm = st.toggle("Use LLM for risk rationale & oracles", value=True)
        max_cases = st.number_input("Optimize: max cases (0 = no cap)", min_value=0, value=0)
    with col2:
        include_stt = st.checkbox("Include state transition (FR4)", value=True)

    sm = None
    stt_req_id = None
    if include_stt:
        sm = render_state_diagram_section()
        stt_req_id = st.text_input("Attach state model to requirement ID", value=session.requirements[0].id)

    if st.button("▶ Run full pipeline", type="primary"):
        llm = _build_llm_or_none() if use_llm else None
        with st.spinner("Running pipeline..."):
            suite = run_pipeline(
                session.requirements,
                llm=llm,
                state_machine=sm,
                state_machine_requirement_id=stt_req_id,
                optimize_max_cases=max_cases or None,
            )
        session.suite = suite
        session.requirements = [r for r in session.requirements]  # trigger refresh
        st.success(f"Generated {len(suite.cases)} test cases.")

    if not session.suite:
        return

    st.markdown("---")
    techniques = sorted({c.technique for c in session.suite.cases})
    tech_tabs = st.tabs(techniques)
    for tab, tech in zip(tech_tabs, techniques):
        with tab:
            rows = [c for c in session.suite.cases if c.technique == tech]
            df = pd.DataFrame([{
                "id": c.id, "req": c.requirement_id,
                "priority": c.priority,
                "inputs": str(c.inputs),
                "expected_result": c.expected_result,
                "tags": ",".join(c.tags),
            } for c in rows])
            st.dataframe(df, use_container_width=True)

    st.markdown("**Coverage:** " + ", ".join(f"{k}={v:.2f}" for k, v in session.suite.coverage.items()))
```

- [ ] **Step 4: Create `autotestdesign/ui/export_panel.py`**

```python
from __future__ import annotations
import io
import tempfile
from pathlib import Path
import streamlit as st
from autotestdesign.core.export import to_json, to_csv, to_xlsx
from autotestdesign.ui.state import get_session


def render_export_tab() -> None:
    session = get_session()
    st.subheader("FR6 — Export")
    if not session.suite:
        st.info("Run the pipeline first (Test Design tab).")
        return

    st.download_button(
        "⬇ Download JSON",
        data=to_json(session.suite).encode("utf-8"),
        file_name="testsuite.json",
        mime="application/json",
    )

    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        to_csv(session.suite, Path(tmp.name))
        csv_bytes = Path(tmp.name).read_bytes()
    st.download_button("⬇ Download CSV", data=csv_bytes,
                       file_name="testsuite.csv", mime="text/csv")

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        to_xlsx(session.suite, Path(tmp.name))
        xlsx_bytes = Path(tmp.name).read_bytes()
    st.download_button("⬇ Download Excel", data=xlsx_bytes,
                       file_name="testsuite.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    st.markdown("**Preview (first 5 cases):**")
    for c in session.suite.cases[:5]:
        with st.expander(f"{c.id} — {c.technique} — {c.priority}"):
            st.json(c.model_dump())
```

- [ ] **Step 5: Update `autotestdesign/app.py`**

Replace the current file content with:

```python
from __future__ import annotations
import streamlit as st
from autotestdesign.config import load_config
from autotestdesign.ui.upload_panel import render_upload_tab
from autotestdesign.ui.risk_panel import render_risk_tab
from autotestdesign.ui.testcase_viewer import render_test_design_tab
from autotestdesign.ui.export_panel import render_export_tab


st.set_page_config(page_title="AutoTestDesign", layout="wide", page_icon="🧪")
st.title("🧪 AutoTestDesign — AI-driven Test Case Generator")

with st.sidebar:
    st.header("Configuration")
    try:
        cfg = load_config()
        st.caption(f"Model: `{cfg.model}`")
        st.caption(f"Endpoint: `{cfg.base_url or '—'}`")
        st.caption(f"Temperature: {cfg.temperature}")
        if not cfg.api_key:
            st.warning("API key not set. LLM features will fall back to rules.")
    except Exception as e:
        st.error(f"Config load error: {e}")

tab_input, tab_risk, tab_design, tab_export = st.tabs(
    ["📥 Input", "📊 Risk", "🧪 Test Design", "📤 Export"]
)

with tab_input:
    render_upload_tab()
with tab_risk:
    render_risk_tab()
with tab_design:
    render_test_design_tab()
with tab_export:
    render_export_tab()
```

- [ ] **Step 6: Smoke test UI launches**

Run: `streamlit run autotestdesign/app.py --server.headless true --server.port 8501 &`
Then: `sleep 3 && curl -s -o /dev/null -w "%{http_code}" http://localhost:8501`
Expected: `200`. Kill the process.

- [ ] **Step 7: Commit**

```bash
git add autotestdesign/ui/ autotestdesign/app.py
git commit -m "feat(ui): risk, test design (with state diagram), export panels + pipeline runner"
```

---

## Task 17: README with setup and demo instructions

**Files:**
- Create: `README.md`

- [ ] **Step 1: Create `README.md`**

```markdown
# AutoTestDesign

AI-driven test design tool that ingests software requirements, assesses risk, and generates systematic test cases using techniques from ISO/IEC/IEEE 29119-4.

## Features (FR coverage)

| FR | Feature | Location |
|----|---------|----------|
| FR1 | Requirement parsing (CSV/text/LLM) | `autotestdesign/core/parsing.py` |
| FR2 | Risk scoring (rule-based + LLM rationale) | `autotestdesign/core/risk.py` |
| FR3 | Black-box: Equivalence Partitioning, Boundary Value Analysis, Decision Tables | `autotestdesign/core/blackbox/` |
| FR4 | White-box: State transition modeling + coverage | `autotestdesign/core/whitebox/` |
| FR5 | Test oracle synthesis | `autotestdesign/core/oracle.py` |
| FR6 | Export to JSON/CSV/Excel | `autotestdesign/core/export.py` |
| FR7 | Test suite optimization | `autotestdesign/core/optimizer.py` |

## Setup

```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Install Graphviz system binary (needed for state diagram rendering):

- Ubuntu/Debian: `sudo apt-get install graphviz`
- macOS: `brew install graphviz`
- Windows: https://graphviz.org/download/

## Configuration

Edit `.env/config.json`:

```json
{
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "model": "gpt-4o-mini",
  "temperature": 0.2
}
```

The tool uses the OpenAI-compatible SDK — swap `base_url`/`model` to use DeepSeek, Anthropic-compatible proxies, etc. If `api_key` is empty, LLM features fall back to rule-based defaults.

## Run

```bash
streamlit run autotestdesign/app.py
```

Then open http://localhost:8501.

### Demo flow

1. **Input tab**: pick "Built-in example" → `banking_registration` → click *Load example*.
2. **Test Design tab**: keep defaults → click *Run full pipeline*.
3. **Risk tab**: review scored requirements.
4. **Test Design tab**: browse EP / BVA / DT / STT sub-tabs.
5. **Export tab**: download JSON / CSV / Excel.

## Tests

```bash
pytest
pytest --cov=autotestdesign/core --cov-report=term-missing
```

Target: `core/` coverage ≥ 80%.

## Project structure

```
autotestdesign/
├── app.py             # Streamlit entry
├── config.py          # Config loader
├── core/              # Pure algorithms + pydantic models
├── llm/               # OpenAI-compatible client + prompt templates (.md)
├── ui/                # Streamlit panels
└── examples/          # Built-in sample requirement sets
tests/
├── unit/              # Per-module unit tests
├── integration/       # End-to-end pipeline test
└── fixtures/          # FakeLLM for deterministic tests
```

## Prompts

All LLM prompts are externalized as Markdown templates in `autotestdesign/llm/prompts/`:

- `structure_requirement.md` — parse free-text into `Requirement` schema
- `score_risk.md` — generate risk rationale
- `synthesize_oracle.md` — derive expected result for an input

## License

Academic project — Assignment 2.
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add README with setup, configuration, demo, and test instructions"
```

---

## Task 18: Final coverage verification

**Files:**
- None (verification only)

- [ ] **Step 1: Run full test suite with coverage**

Run: `pytest --cov=autotestdesign/core --cov-report=term-missing -v`
Expected: all tests pass; `core/` coverage ≥ 80%.

- [ ] **Step 2: If coverage below 80%, add targeted unit tests**

Look at the missing-line report. Add tests for any untested branches in `core/` modules. Commit each fix separately as `test: cover <module> <branch>`.

- [ ] **Step 3: Smoke-test the full Streamlit demo flow manually**

Run: `streamlit run autotestdesign/app.py`
Then in browser:
1. Input → Built-in → `banking_registration` → Load.
2. Test Design → Run pipeline (LLM off if no API key).
3. Verify Risk, Test Design, Export tabs all populate.
4. Download JSON, open it — should contain `cases` array and `coverage` dict.

Expected: all steps work without errors.

- [ ] **Step 4: Final commit (if any test fixes were made)**

```bash
git log --oneline | head -20    # review sequence of commits
```

No action if nothing changed.
