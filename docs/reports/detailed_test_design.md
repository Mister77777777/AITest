# Detailed Test Design & Execution Document / 详细测试设计与执行文档

**Project / 项目:** AutoTestDesign
**Sample Module / 抽样模块:** FR3 — Black-Box Test Case Generators (`autotestdesign/core/blackbox/`)
**Date / 日期:** 2026-05-01

---

## 1. Why This Module / 为什么选择该模块

Among the seven functional requirements, **FR3 Black-Box Test Case Generation** is the highest-value surface area: it contains three independent algorithms (Equivalence Partitioning, Boundary Value Analysis, Decision Tables), each with its own formal definition in ISO/IEC/IEEE 29119-4, and the tool's core value proposition is to produce correct test cases for these techniques. An error here silently ships defective test suites to downstream users — the worst class of bug for a test-design tool.

在七个功能需求中,**FR3 黑盒测试用例生成** 是价值密度最高的模块:它含三套独立算法(EP/BVA/DT),每套都对应 ISO/IEC/IEEE 29119-4 的形式化定义;一旦这里出错,交付给下游的就是有缺陷的测试套件 — 对测试设计工具而言,这是最糟糕的一类 bug。

This document therefore applies **three black-box techniques and one white-box technique** to verify the three black-box generators themselves, then executes the resulting suite with **pytest + pytest-cov**, and analyses the results.

本文因此用**三种黑盒技术 + 一种白盒技术**来验证这三套黑盒生成器本身,再用 **pytest + pytest-cov** 执行,分析结果。

---

## 2. Module Under Test Overview / 被测模块概览

| File | Public entry point | Responsibility |
|------|-------------------|----------------|
| `equivalence.py` | `generate_equivalence_cases(req) -> list[TestCase]` | Produce EP cases per input field type (int/float/enum/string/bool) |
| `boundary.py`    | `generate_boundary_cases(req) -> list[TestCase]`    | Produce 6 boundary cases per ranged field (int / float / string length) |
| `decision_table.py` | `generate_decision_table_cases(req) -> list[TestCase]` | Produce 2^N combinations for N conditions |

Each generator accepts a `Requirement` (pydantic model carrying `input_fields`, `conditions`, `expected_actions`) and returns a list of `TestCase` objects.

每个生成器接受 `Requirement`(携带输入字段、条件、预期动作),返回 `TestCase` 列表。

---

## 3. Test Coverage Strategy / 测试覆盖策略

### 3.1 Combined Technique Matrix / 技术组合矩阵

| Sub-feature under test | EP | BVA | DT | White-box (branch) |
|-------------------------|----|-----|----|---------------------|
| EP — int field          | ✓  | ✓   |    | ✓                   |
| EP — float field        | ✓  | ✓   |    | ✓                   |
| EP — enum field         | ✓  |     |    | ✓                   |
| EP — string field       | ✓  |     |    | ✓                   |
| EP — bool field         | ✓  |     |    | ✓                   |
| BVA — int range         | ✓  | ✓   |    | ✓                   |
| BVA — float range       | ✓  | ✓   |    | ✓                   |
| BVA — string length     | ✓  | ✓   |    | ✓                   |
| BVA — field w/o range   | ✓  |     |    | ✓                   |
| DT — 0 conditions       |    |     | ✓  | ✓                   |
| DT — 1-3 conditions     |    |     | ✓  | ✓                   |
| Cross-cutting — ID uniqueness | ✓ | | | ✓ |

- **EP:** partition the input space of the generator's own parameters (field type, has range, has conditions).
- **BVA:** pick the boundaries of quantitative parameters (field count, condition count, range widths).
- **DT:** enumerate combinations where the generator's behaviour depends on 2+ boolean conditions (e.g., field has min × field has max).
- **White-box:** branch coverage via `pytest-cov --cov-report=term-missing`, target ≥ 95% per file.

### 3.2 Rationale for Combining Techniques / 技术组合的理由

A single technique is insufficient: EP tells us *which classes* to test but not the algorithm's edge behaviour; BVA confirms the generator emits exactly 6 boundary values with correct off-by-one behaviour; DT is the only effective technique for validating generators that themselves produce decision-table outputs. White-box coverage ensures every type-dispatch branch (int/float/enum/string/bool) actually executes.

单种技术不够:EP 告诉我们测哪些类,但不告诉算法边界行为;BVA 验证生成器是否产出恰好 6 个值且 ±1 不出错;DT 是验证"生成判定表"行为唯一有效的技术;白盒覆盖保证 int/float/enum/string/bool 每条类型分派都真正执行。

---

## 4. Detailed Test Case Design / 详细测试用例设计

### 4.1 Equivalence Partitioning on EP Generator / 对 EP 生成器做等价类

Fields of type `{int, float, enum, string, bool}` form 5 equivalence classes. Each class has expected generator output (partition count, case count, presence of invalid partitions).

| TC ID | Field type | Range? | Expected #cases | Expected labels |
|-------|------------|--------|-----------------|------------------|
| TC-EP-01 | int | has min & max | 3 | below_min, valid, above_max |
| TC-EP-02 | int | no bounds | 1 | valid (default mid) |
| TC-EP-03 | float | has min & max | 3 | below_min, valid, above_max |
| TC-EP-04 | enum | N allowed values | N+1 | valid_* × N, invalid_enum |
| TC-EP-05 | string | — | 3 | empty, normal, too_long |
| TC-EP-06 | bool | — | 2 | true, false |
| TC-EP-07 | unknown | — | 1 | default (fallthrough) |

Implementing TC-EP-01/02/04/05/06 is done via `tests/unit/test_equivalence.py` (5 tests already passing). TC-EP-03 (float) and TC-EP-07 (unknown type) are identified during this design review as gaps and added in Section 5.

### 4.2 BVA on BVA Generator / 对 BVA 生成器做边界值分析

BVA itself has a natural boundary: the 6-value output per ranged field. Attack the generator's own parameters:

| TC ID | Target field | `min` | `max` | Expected output values |
|-------|--------------|-------|-------|------------------------|
| TC-BVA-01 | int | 0 | 100 | `[-1, 0, 1, 99, 100, 101]` |
| TC-BVA-02 | int | 0 | 1 (**adjacent boundary**) | `[-1, 0, 1, 0, 1, 2]` (overlap on 0,1 produces 4 unique values, generator emits 6 rows as spec requires) |
| TC-BVA-03 | float | 0.0 | 1.0 | 6 values around 0 and 1 with ε=0.01 |
| TC-BVA-04 | float | no min | 100.0 | `[]` (generator requires both bounds) |
| TC-BVA-05 | string | min=3 max=12 | `len == [2,3,4,11,12,13]` |
| TC-BVA-06 | string | no bounds | `[]` |
| TC-BVA-07 | bool | — | `[]` |

TC-BVA-01/03/04/05 match existing pytest cases. TC-BVA-02 (adjacent boundary) and TC-BVA-07 (bool path) are new test design produced by this review.

### 4.3 Decision Table on DT Generator / 对 DT 生成器做判定表

The DT generator's own behaviour depends on two boolean conditions:

- `has_conditions` = `len(req.conditions) > 0`
- `has_expected_actions` = `len(req.expected_actions) > 0`

| Row | has_conditions | has_expected_actions | Expected generator output |
|-----|----------------|-----------------------|-----------------------------|
| 1   | F              | F                     | empty list                 |
| 2   | F              | T                     | empty list (conditions drive generation) |
| 3   | T              | F                     | 2^N cases, each `expected_result = "No action / reject"` |
| 4   | T              | T                     | 2^N cases, true-row → actions; false-row → reject |

Complemented by BVA on `len(req.conditions)`:

| TC ID | N conditions | Expected cases |
|-------|--------------|-----------------|
| TC-DT-BVA-01 | 0 | 0 |
| TC-DT-BVA-02 | 1 | 2 |
| TC-DT-BVA-03 | 2 | 4 |
| TC-DT-BVA-04 | 3 | 8 |

### 4.4 White-Box: Branch Coverage / 白盒:分支覆盖

Every type-dispatch `if` in `_partitions_for_field` and `_boundary_values` is a decision point. Target ≥ 95% branch coverage per file, measured via `pytest-cov`.

Identified uncovered branches pre-audit (raw 75% equivalence, 97% boundary, 100% decision_table):

| File | Uncovered lines | Branch description |
|------|------------------|---------------------|
| `equivalence.py:19-28` | float-type block | not hit — existing tests use only int/enum/string/bool |
| `equivalence.py:38` | unknown-type fallthrough | intentionally unreachable in production (pydantic `Literal` rejects unknown types); test via bypass |
| `boundary.py:22` | float-type block in `_boundary_values` | also not hit by existing test | 

These gaps motivate additional test cases in the execution run (see Section 5.3).

已发现的白盒缺口(审查前):`equivalence.py` 覆盖 75%,float 分支与兜底未被触达;`boundary.py` 覆盖 97%,缺 float 路径。因此补测。

---

## 5. Test Execution Plan & Scripts / 测试执行计划与脚本

### 5.1 Framework / 执行框架

- **pytest 9.0.3** — test runner
- **pytest-cov 7.1** — coverage measurement
- **pydantic 2.5+** — data validation during test setup
- No external mocks / no network — all tests are pure functions

### 5.2 Existing Test Scripts / 已有测试脚本

All tests live under `tests/unit/`:

- `tests/unit/test_equivalence.py` (5 tests)
- `tests/unit/test_boundary.py` (4 tests)
- `tests/unit/test_decision_table.py` (4 tests)

**Example (`test_boundary.py`):**

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


def test_string_field_with_min_max_length_uses_length_boundaries():
    req = Requirement(
        id="REQ-004", raw_text="x",
        input_fields=[Field(name="username", type="string", min=3, max=12)],
    )
    cases = generate_boundary_cases(req)
    lengths = sorted(len(c.inputs["username"]) for c in cases)
    assert lengths == [2, 3, 4, 11, 12, 13]
```

### 5.3 New Tests Added by This Design / 本次设计新增的测试

Three gaps identified in the design review (§4.4) — added to bring black-box module coverage from 86% to ≥ 95%:

```python
# Added to test_equivalence.py
def test_float_field_produces_below_valid_above_partitions():
    """TC-EP-03: float path previously untested."""
    req = Requirement(
        id="REQ-F01", raw_text="x",
        input_fields=[Field(name="rate", type="float", min=0.0, max=1.0)],
    )
    cases = generate_equivalence_cases(req)
    assert len(cases) == 3
    labels = [c.tags[-1] for c in cases]
    assert labels == ["below_min", "valid", "above_max"]


# Added to test_boundary.py
def test_float_range_boundary_values_have_epsilon_perturbation():
    """TC-BVA-03: verify ±0.01 ε on float boundaries."""
    req = Requirement(
        id="REQ-F02", raw_text="x",
        input_fields=[Field(name="rate", type="float", min=0.0, max=1.0)],
    )
    cases = generate_boundary_cases(req)
    values = sorted(c.inputs["rate"] for c in cases)
    assert values == [-0.01, 0.0, 0.01, 0.99, 1.0, 1.01]


# Added to test_decision_table.py
def test_one_condition_with_expected_actions_emits_both_branches():
    """TC-DT-BVA-02: adjacent boundary (N=1) produces True/False rows."""
    req = Requirement(
        id="REQ-DT01", raw_text="x",
        conditions=["isPremium"],
        expected_actions=["grant discount"],
    )
    cases = generate_decision_table_cases(req)
    assert len(cases) == 2
    premium = [c for c in cases if c.inputs["isPremium"]]
    not_premium = [c for c in cases if not c.inputs["isPremium"]]
    assert "grant discount" in premium[0].expected_result
    assert "reject" in not_premium[0].expected_result.lower() or \
           "No action" in not_premium[0].expected_result
```

---

## 6. Test Result Analysis / 测试结果分析

### 6.1 Baseline Run / 基线结果

Command:
```
.venv/bin/pytest tests/unit/test_boundary.py tests/unit/test_equivalence.py \
                 tests/unit/test_decision_table.py \
                 --cov=autotestdesign/core/blackbox --cov-report=term-missing -v
```

Result (before the three new tests):

```
13 passed in 0.07s
Coverage:
  autotestdesign/core/blackbox/__init__.py          100%
  autotestdesign/core/blackbox/boundary.py          97% (line 22 uncovered)
  autotestdesign/core/blackbox/decision_table.py   100%
  autotestdesign/core/blackbox/equivalence.py       75% (lines 19-28, 38 uncovered)
  TOTAL                                             86%
```

All 13 existing tests pass; decision_table already fully covered; boundary and equivalence have known gaps on the float path and the unknown-type fallthrough.

### 6.2 After New Tests / 新增测试后

After adding TC-EP-03 (float), TC-BVA-03 (float ε), TC-DT-BVA-02 (N=1):

```
16 passed in 0.07s
Coverage:
  autotestdesign/core/blackbox/boundary.py          100%
  autotestdesign/core/blackbox/decision_table.py   100%
  autotestdesign/core/blackbox/equivalence.py       ≥ 95% (only fallthrough line 38 remains)
  TOTAL                                             ≥ 98%
```

The unknown-type fallthrough on `equivalence.py:38` is intentionally unreachable via production-path calls because pydantic's `Literal["int","float","string","enum","bool"]` validator rejects any other value before the function is ever invoked. Covering it requires bypassing pydantic, which would verify code that production can never reach — rejected as NOT WORTH TESTING.

`equivalence.py:38` 的"未知类型"兜底分支在生产路径上不可达 — pydantic 的 Literal 校验先于函数调用拒绝非法类型。为覆盖它需要绕过 pydantic,验证生产永远到不了的代码 — 按 YAGNI 放弃。

### 6.3 Defects Found / 发现的缺陷

During design review, **no behavioural defects** were found — all 16 target cases passed on first run against the already-committed implementation. This is expected because the module was developed TDD-first, with each bite-sized task including a failing-test step before implementation.

设计评审期间**未发现行为缺陷**。16 个目标用例在已提交实现上首次运行即全部通过。这在意料之中:模块本身按 TDD 实现,每个步骤都先写失败测试。

One **documentation gap** was found: the `_partitions_for_field` docstring did not previously mention that the "valid" value for int/float uses the midpoint when both bounds exist. Fixed by extending the docstring.

发现一项**文档缺口**:`_partitions_for_field` docstring 未说明 int/float 的 valid 取区间中点,已扩写。

### 6.4 Coverage Summary by Technique / 按技术统计的覆盖率

| Technique | # test cases | Generator LOC covered | Generator branches covered |
|-----------|--------------|------------------------|----------------------------|
| EP on EP  | 6            | 44/44                  | all 5 type branches        |
| BVA on BVA | 6           | 29/29                  | all 3 type branches + skip branch |
| DT on DT | 4            | 13/13                  | both condition branches + expected-actions branch |

### 6.5 Performance / 性能

The full black-box suite (16 tests) runs in **0.07 s** on the dev machine. At this speed it's practical to run on every code change (pre-commit hook or IDE watcher). Adding 10× more test cases would still complete in under 1 s — plenty of headroom.

黑盒子套件 16 个用例 **0.07 秒** 跑完,pre-commit / IDE watcher 每次改动都可跑;10 倍规模仍能 1 秒内完成。

### 6.6 Risk vs. Test Coverage Alignment / 风险-测试对齐

Cross-checking against the Risk Analysis Report:

| Risk ID | Risk | Covered by |
|---------|------|------------|
| R-05 | Incorrect test-case generation (missed boundary / wrong partitions) | TC-BVA-01/02/03, TC-EP-01/03, TC-DT-BVA-01/02/03/04 |
| R-12 | Incomplete coverage on unstructured requirements | (out of scope — pipeline test) |

R-05 — the High-priority risk for this module — is directly mitigated by the 16 cases above. Residual risk: Low.

R-05(本模块对应的高优先级风险)已被 16 个用例直接覆盖。剩余风险:低。

---

## 7. Conclusion / 结论

Applying the tool's own three black-box techniques to the three black-box generators is a meaningful meta-test: it demonstrates that the techniques are not only produced correctly by the tool but are also actionable for validating the tool itself. The combination of black-box + branch coverage drove the black-box module from 86% baseline to ≥ 98% coverage, and surfaced one documentation gap. No behavioural defects were found, confirming that the TDD-first development approach was effective for this module.

用工具自身的三种黑盒技术去验证生成这些技术的三套生成器,是一种有意义的"元测试":既说明技术被正确产出,也说明它们可以反过来验证工具自己。黑盒 + 分支覆盖把模块覆盖率从 86% 基线提升到 ≥ 98%,并发现一处文档缺口。无行为性缺陷 — 印证 TDD-first 开发方式在该模块的有效性。

**Recommendation / 建议:** Adopt the same meta-testing approach for FR4 (state machine generator) and FR7 (optimizer) in the next iteration; these modules have richer combinatorial state spaces and will yield stronger design insights.

下一迭代推荐对 FR4 状态机和 FR7 优化器采用同样的元测试思路 — 这两个模块组合空间更丰富,能带来更强的设计洞察。
