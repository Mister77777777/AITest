# AutoTestDesign Tool — Design Specification

**Date:** 2026-05-01
**Status:** Approved (brainstorming phase)
**Scope:** AI-driven AutoTestDesign tool source code only (Assignment 2 artifact 1, 20%). Risk report, test plan, detailed test design document and PPT are deferred to later sessions.

---

## 1. Purpose

Build an AI-driven AutoTestDesign tool that ingests software requirements, assesses risk, and automatically generates black-box and white-box test cases aligned with ISTQB Foundation Level principles and ISO/IEC/IEEE 29119-4 techniques.

The tool must implement all seven functional requirements (FR1–FR7) and meet the non-functional requirements (performance, usability, security, maintainability) defined in Assignment 2.

## 2. Functional Requirements Coverage

| ID   | Feature                       | Implementation approach |
|------|-------------------------------|-------------------------|
| FR1  | Input / Parsing               | CSV via pandas; plain text via LLM-backed `structure_requirement.md` prompt; pydantic validation of the returned JSON. |
| FR1.1| Requirement Structuring       | Extract `input_fields`, `data_ranges`, `conditions`, `expected_actions` into a `Requirement` pydantic model. |
| FR2  | Risk Analysis & Prioritization| Rule-based likelihood/impact scoring (keyword weights for payment/auth/security) + LLM-generated rationale. Priority = High/Medium/Low from score band. |
| FR3  | Black-Box Test Design         | Three ISO 29119-4 techniques implemented deterministically: Equivalence Partitioning, Boundary Value Analysis, Decision Tables. |
| FR4  | White-Box Test Modeling       | State machine built via `networkx`; supports `all_states` coverage (minimum node-covering path) and `all_transitions` coverage (Chinese Postman approximation). State model input: DSL or LLM extraction. |
| FR5  | Test Oracle Generation        | Algorithmic fallback for out-of-range inputs ("reject with message X"); LLM synthesis via `synthesize_oracle.md` prompt for nuanced cases. |
| FR6  | Output & Export               | JSON, CSV, Excel (openpyxl). Field naming aligned with common TMS (Jira Xray / TestRail). |
| FR7  | Test Suite Optimization       | Greedy signature-based dedup + weighted set-cover (objective: requirement coverage × priority weight). |

## 3. Architecture

```
autotestdesign/
├── app.py                        # Streamlit entry (thin shell)
├── config.py                     # Loads .env/config.json → LLM/model config
│
├── core/                         # Pure algorithms + data models; no UI or LLM imports
│   ├── models.py                 # Requirement, Field, RiskScore, TestCase, TestSuite
│   ├── parsing.py                # FR1
│   ├── risk.py                   # FR2
│   ├── blackbox/
│   │   ├── equivalence.py        # FR3 EP
│   │   ├── boundary.py           # FR3 BVA
│   │   └── decision_table.py     # FR3 DT
│   ├── whitebox/
│   │   ├── state_machine.py      # FR4
│   │   └── coverage.py           # FR4 coverage calc
│   ├── oracle.py                 # FR5
│   ├── optimizer.py              # FR7
│   └── export.py                 # FR6
│
├── llm/                          # OpenAI-compatible abstraction
│   ├── client.py                 # OpenAI(base_url=..., api_key=...)
│   └── prompts/                  # Prompt templates (submitted as part of deliverable)
│       ├── structure_requirement.md
│       ├── score_risk.md
│       └── synthesize_oracle.md
│
├── ui/                           # Streamlit components
│   ├── upload_panel.py
│   ├── requirement_table.py
│   ├── testcase_viewer.py
│   └── state_diagram.py          # graphviz render
│
├── examples/                     # Built-in sample requirements for demo
│   ├── banking_registration.csv
│   └── shopping_cart.md
│
├── tests/                        # pytest
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── README.md
└── requirements.txt              # streamlit, openai, pandas, openpyxl, graphviz, networkx, pydantic, jinja2, pytest, pytest-cov
```

**Decoupling rules:**
- `core/` must not import `streamlit` or `openai`.
- LLM calls are confined to `llm/client.py` — mockable for tests.
- Prompts live as external `.md` files (Assignment requires prompts be submitted alongside code).

## 4. Data Model

```python
class Field(BaseModel):
    name: str
    type: Literal["int", "float", "string", "enum", "bool"]
    min: Any | None = None
    max: Any | None = None
    allowed: list[Any] | None = None

class Requirement(BaseModel):
    id: str                                 # "REQ-001"
    raw_text: str
    input_fields: list[Field]
    conditions: list[str]
    expected_actions: list[str]
    category: Literal["functional", "non-functional"]
    risk: "RiskScore | None" = None

class RiskScore(BaseModel):
    likelihood: int                         # 1-5
    impact: int                             # 1-5
    score: int                              # likelihood * impact
    priority: Literal["High", "Medium", "Low"]
    rationale: str

class TestCase(BaseModel):
    id: str
    requirement_id: str
    technique: Literal["EP", "BVA", "DT", "STT"]
    inputs: dict[str, Any]
    preconditions: list[str]
    steps: list[str]
    expected_result: str
    priority: Literal["High", "Medium", "Low"]
    tags: list[str]

class TestSuite(BaseModel):
    cases: list[TestCase]
    coverage: dict[str, float]              # {"all_states": 1.0, "all_transitions": 0.83}
```

## 5. Data Flow

```
Upload/Input
   → parsing.py             → Requirement[]
                             (CSV via pandas; free text via LLM-structured prompt)
   → risk.py (+ LLM)        → Requirement[] with RiskScore
                             (score/priority are rule-based; LLM only supplies rationale)
   → blackbox + whitebox    → TestCase[]
   → oracle.py (+ LLM)      → TestCase[] with expected_result
                             (LLM synthesis with algorithmic fallback for out-of-range inputs)
   → optimizer.py           → TestSuite (deduped, priority-sorted)
   → export.py              → JSON / CSV / Excel
```

Each UI tab subscribes to an intermediate artifact; steps never re-run unless the user explicitly re-triggers. LLM is only invoked where annotated above; all other stages are pure algorithmic.

## 6. LLM Integration

**Client (`llm/client.py`):**

- Uses the `openai` Python SDK with `base_url` and `api_key` sourced from `.env/config.json`. Default model: `gpt-4o-mini`; switchable to DeepSeek, Anthropic-compatible proxies, etc. by editing config only.
- `temperature=0.2` for reproducibility.
- `response_format={"type": "json_object"}`, validated against a pydantic schema; 3 retries on validation failure; then raises `LLMOutputError`.
- On `LLMOutputError`, upstream falls back to algorithmic defaults and surfaces a Streamlit warning.

**Prompts:** Jinja2-rendered `.md` files under `llm/prompts/`. Each prompt header specifies the expected JSON schema inline.

## 7. UI (Streamlit, single page with 4 tabs)

- **Tab 1 — Requirements Input:** selector for built-in example / CSV upload / manual textarea; editable parsed result table.
- **Tab 2 — Risk Analysis:** table (ID, text, L, I, score, priority, rationale) + priority distribution bar chart.
- **Tab 3 — Test Design:** sub-tabs for EP / BVA / DT / State Diagram. State diagram tab shows graphviz render on the left and generated test sequences on the right. A button applies FR7 optimization and reports before/after counts.
- **Tab 4 — Export:** download buttons for JSON / CSV / Excel; preview of oracle synthesis status.

**Sidebar:** model name, temperature, prompt version, LLM availability probe (ping on startup).

**State management:** `st.session_state` stores `requirements`, `test_cases`, `run_log`. Steps are idempotent against cached state to avoid repeat LLM spend.

**Demo golden path (for video):** select "banking registration" example → one-click full pipeline → walk through all 4 tabs → export JSON → switch to "shopping cart" to demonstrate generalizability.

## 8. Non-Functional Requirements

| NFR              | Approach |
|------------------|----------|
| Performance      | Batch LLM calls (one prompt covers multiple requirements); cache artifacts in `session_state`; streamed export. |
| Usability        | Linear 4-tab flow; loading indicators; errors via `st.toast`; algorithmic fallback visible as a warning banner. |
| Security         | API key only from `.env/config.json`, never logged; upload size ≤ 2MB; CSV parsed via pandas (injection-safe); `.env/` excluded via `.gitignore`. |
| Maintainability  | `core/` decoupled from UI and LLM; prompts externalized; `requirements.txt` pins deps; pytest + ruff/black enforced. |

## 9. Testing Strategy

```
tests/
├── unit/
│   ├── test_parsing.py
│   ├── test_risk.py
│   ├── test_equivalence.py
│   ├── test_boundary.py                  # range [0,100] asserts 6 BVA cases
│   ├── test_decision_table.py            # N conditions → 2^N rows
│   ├── test_state_machine.py             # asserts shortest all-states path on a small graph
│   ├── test_oracle.py                    # out-of-range inputs → fallback text
│   ├── test_optimizer.py                 # constructed redundant TCs → dedup assertion
│   └── test_export.py                    # JSON schema validation
├── integration/
│   └── test_end_to_end.py                # built-in example runs full pipeline with LLM mock
└── fixtures/
    └── fake_llm.py                       # injectable fake LLM client
```

Coverage target: `core/` ≥ 80% via `pytest-cov`. LLM layer is excluded (external dependency).

## 10. Risks & Mitigations

1. **LLM output instability** — JSON mode + pydantic validation + 3 retries + algorithmic fallback.
2. **State diagram extraction is the most complex FR** — support both LLM auto-extraction and a manual DSL (`S1 --event--> S2`); user can edit the model before generation.
3. **Token cost** — low temperature, short prompts, cache intermediates, batch where possible.
4. **Time pressure** — implement in order FR1 → FR2 → FR6 → FR3 → FR5 → FR7 → FR4, so every intermediate state is demo-ready.

## 11. Out of Scope (YAGNI)

- No authentication / multi-user.
- No database persistence (`session_state` is sufficient).
- No CI/CD or Docker.
- No Pairwise or MCDC (EP/BVA/DT already satisfy FR3's "at least three techniques").
- No LangChain / LangGraph (dependency overhead unjustified).
- No frontend/backend split (Streamlit covers it).

## 12. Deliverable Mapping

| Deliverable                     | Location / artifact |
|---------------------------------|---------------------|
| Source code                     | Everything under `autotestdesign/` |
| Prompts                         | `llm/prompts/*.md` |
| Setup instructions (README)     | `README.md` with install, config, run commands |
| Video demo                      | Recorded from the "demo golden path" above |

## 13. Technology Stack

Python 3.11+, Streamlit, OpenAI Python SDK (compatible endpoint), pandas, openpyxl, networkx, graphviz (Python binding), pydantic v2, Jinja2, pytest, pytest-cov, ruff, black.
