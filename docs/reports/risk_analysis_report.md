# Risk Analysis Report / 风险分析报告

**Application Under Test / 被测应用:** AutoTestDesign — AI-driven Test Case Generator
**Date / 日期:** 2026-05-01
**Version / 版本:** 0.1.0

---

## 1. Overview / 概述

This report identifies and assesses risks for the AutoTestDesign tool — a Python + Streamlit application that uses a Large Language Model (OpenAI-compatible interface) together with deterministic algorithms to generate test cases from software requirements. The tool integrates black-box techniques (Equivalence Partitioning, Boundary Value Analysis, Decision Tables) and a white-box state-transition technique per ISO/IEC/IEEE 29119-4, plus risk scoring, oracle synthesis, and test-suite optimization.

本报告针对 AutoTestDesign 工具自身的风险进行识别与评估。该工具基于 Python + Streamlit,结合大语言模型(OpenAI 兼容接口)与确定性算法,把软件需求转化为测试用例,覆盖 ISO/IEC/IEEE 29119-4 的等价类划分(EP)、边界值分析(BVA)、判定表(DT)三种黑盒技术以及状态转换(STT)白盒技术,辅以风险评分、Oracle 合成、测试套件优化等能力。

---

## 2. Risk Assessment Methodology / 风险评估方法

Each risk is scored along two dimensions:

- **Likelihood (1-5)** — probability the risk will materialize during normal use or demo.
- **Impact (1-5)** — consequence on correctness, usability, or graded deliverable if the risk materializes.

Priority:
- **High:** score ≥ 15
- **Medium:** 8 ≤ score < 15
- **Low:** score < 8

本工具内部的 FR2 风险打分算法使用完全一致的维度与阈值,与本报告方法对齐。

每项风险从两个维度打分:**可能性(1-5)** 与 **影响(1-5)**;总分 = 可能性 × 影响。阈值:≥15 高、8~14 中、<8 低。

---

## 3. Risk Register / 风险登记表

| ID | Risk / 风险 | Likelihood | Impact | Score | Priority |
|----|-------------|------------|--------|-------|----------|
| R-01 | LLM returns non-JSON or malformed schema / LLM 返回非 JSON 或结构不符 | 4 | 4 | 16 | High |
| R-02 | Network outage / rate-limit / LLM provider 不可用或被限流 | 3 | 4 | 12 | Medium |
| R-03 | Provider-specific parameter incompatibility (e.g. temperature unsupported) / 不同 provider 参数兼容性差异 | 4 | 3 | 12 | Medium |
| R-04 | API key leakage / API Key 泄漏 | 2 | 5 | 10 | Medium |
| R-05 | Incorrect test case generation (missing boundary / wrong partitions) / 测试用例生成错误(漏边界、分区错误) | 3 | 5 | 15 | High |
| R-06 | State machine DSL parse errors on user input / 用户提供的状态机 DSL 解析失败 | 4 | 3 | 12 | Medium |
| R-07 | LLM hallucinates inconsistent score (score ≠ likelihood × impact) / LLM 生成风险分自相矛盾 | 3 | 3 | 9 | Medium |
| R-08 | Excessive token cost from batched LLM calls / 批量 LLM 调用 token 成本过高 | 3 | 2 | 6 | Low |
| R-09 | Streamlit session state loss after long idle / Streamlit 会话长时间空闲丢失状态 | 2 | 2 | 4 | Low |
| R-10 | CSV/Excel injection via uploaded requirement files / 上传需求文件时的 CSV/Excel 注入 | 2 | 4 | 8 | Medium |
| R-11 | Unicode / encoding issues on Windows when reading uploaded files / Windows 上中文编码问题 | 3 | 2 | 6 | Low |
| R-12 | Incomplete coverage when requirement has no `input_fields` or `conditions` / 需求缺少结构化字段导致覆盖不完整 | 4 | 3 | 12 | Medium |
| R-13 | Exported JSON not importable by target TMS / 导出 JSON 字段映射与目标 TMS 不匹配 | 3 | 2 | 6 | Low |
| R-14 | Graphviz system binary missing at runtime / 系统未安装 graphviz 导致状态图渲染失败 | 3 | 2 | 6 | Low |

Total: 14 risks — **2 High, 6 Medium, 6 Low / 共 14 项:2 高、6 中、6 低**。

---

## 4. Detailed Analysis of High-Priority Risks / 高优先级风险详细分析

### R-01 — LLM returns non-JSON or malformed schema / LLM 返回非 JSON 或结构不符

**Description:** The LLM may occasionally emit free-text prose, markdown code fences (```json ... ```), or JSON that does not conform to the pydantic schema expected by the caller (e.g. wrong field names, missing required fields).

描述:LLM 可能返回自由文本、带 markdown 围栏的 JSON,或字段名错、缺必填字段的 JSON。

**Business impact:** Pipeline stage failures cause cases to fall back to algorithmic defaults, lowering the perceived "AI-ness" of the output and in extreme cases producing generic expected-results across many cases.

业务影响:流水线阶段失败会回退到算法默认值,在极端情况下大量用例 expected_result 变成泛化文本,影响"AI 驱动"的体感与最终演示说服力。

**Mitigation:**
1. `LLMClient.structured_call()` enforces `response_format={"type": "json_object"}` when the provider supports it.
2. Pydantic `model_validate_json()` validates the returned payload against the target schema — mismatch triggers retry (up to `max_retries=3`).
3. `_strip_json_fence()` removes ``` ```json``` wrappers before parsing.
4. On final failure, all callers (risk, oracle) fall back to rule-based defaults so the pipeline never crashes.

缓解:客户端层面启用 JSON 模式 + pydantic 校验 + 3 次重试 + 代码围栏剥离;所有调用方(风险、Oracle)都有算法兜底,不会让流水线崩溃。

**Residual risk:** Low — even if LLM is entirely unavailable, the tool produces complete test suites on rule-based defaults.

剩余风险:低。即便 LLM 完全不可用,工具仍能用规则生成完整测试套件。

### R-05 — Incorrect test case generation / 测试用例生成错误

**Description:** Algorithm bugs in EP/BVA/DT generators could produce wrong boundaries (e.g., off-by-one on `min`/`max`), miss equivalence classes, or duplicate decision-table rows.

描述:EP/BVA/DT 生成器的算法 bug 可能导致边界值偏移(±1 错位)、漏等价类、判定表行重复。

**Business impact:** Consumers of the generated test suite miss real defects, defeating the tool's core value proposition.

业务影响:生成的测试套件无法发现真实缺陷,工具核心价值被严重削弱。

**Mitigation:**
1. Every generator has dedicated pytest unit tests with hand-computed expected outputs:
   - `test_boundary.py`: asserts `[-1, 0, 1, 99, 100, 101]` for range `[0, 100]`.
   - `test_decision_table.py`: asserts 2^N rows for N conditions.
   - `test_equivalence.py`: asserts distinct partitions per field type.
2. `core/` coverage target ≥ 80% (current: 95%) ensures branches are exercised.
3. `core/` is decoupled from UI and LLM, so regressions are caught by pytest alone without needing integration.

缓解:每个生成器都有单元测试,人工推算的期望值做断言;`core/` 覆盖率 95%(目标 80%);`core/` 与 UI/LLM 解耦,纯 pytest 就能回归。

**Residual risk:** Low — algorithms are simple, mathematically well-defined, and unit-tested. Remaining risk is a rare pydantic/type-handling edge case.

剩余风险:低。算法简单且数学定义清晰,已被单元测试覆盖。

---

## 5. Medium-Priority Risks / 中优先级风险摘要

- **R-02 Network outage:** 3× retry with increasing tolerance; offline fallback to rule-based paths. Users see a warning in the Streamlit sidebar.
  网络中断:客户端 3 次重试 + 算法兜底;UI 侧边栏提示降级状态。

- **R-03 Provider parameter incompatibility:** Adaptive `_send_temperature` / `_send_response_format` flags in `LLMClient`. First 400 error mentioning the parameter disables it silently for subsequent calls.
  Provider 参数兼容性差异:客户端自适应关掉不支持的参数,首次遇到 400 后对后续调用生效。

- **R-04 API key leakage:** `.env/config.json` is listed in `.gitignore`. UI caption only shows first characters. Error messages never embed the key.
  API Key 泄漏:`.env/` 已在 gitignore 中;UI 不显示 key 原文;错误日志不会打印 key。

- **R-06 DSL parse errors:** Regex `^\s*(\w+)\s*--\s*([^-\s][^-]*?)\s*-->\s*(\w+)\s*$` validates each line; invalid lines are silently skipped; zero transitions raises `ValueError` with a user-friendly message surfaced as a Streamlit warning.
  DSL 解析失败:正则校验单行格式,无效行跳过,零转换时抛 ValueError 并在 UI 以警告提示。

- **R-07 Inconsistent LLM scoring:** Handled structurally — `RiskScore` pydantic model has `_score_matches_product` validator that rejects any payload where `score != likelihood × impact`. Combined with rule-based scoring (algorithm computes score, LLM only writes rationale), this class of bug cannot reach the user.
  LLM 自相矛盾打分:`RiskScore` 模型层校验 `score = likelihood × impact`,且打分本身由算法执行、LLM 只生成 rationale,该类 bug 不会到达用户。

- **R-10 CSV/Excel injection:** Uploads are parsed via `pandas.read_csv` (no `eval`); values never flow into shell or SQL. Excel export uses `openpyxl` which escapes formulas when the first cell char is `=`/`+`/`-`/`@` by default.
  上传文件注入:用 pandas.read_csv 解析,不走 eval;导出 Excel 走 openpyxl,默认会处理以 `=` 开头的单元格。

- **R-12 Incomplete coverage on unstructured requirements:** Pipeline now calls `parse_with_llm` via the `auto_structure` flag (default `True`) to fill empty `input_fields`/`conditions` before running black-box generators. Verified on `banking_registration.csv`: 6 requirements → 65 test cases after auto-structuring.
  结构不完整导致覆盖不足:流水线新增 `auto_structure` 开关(默认开),自动用 LLM 补齐空字段。内置示例实测 6 条需求 → 65 条用例。

---

## 6. Low-Priority Risks / 低优先级风险摘要

- **R-08 Token cost:** `temperature=0.2` keeps outputs short; prompts are concise; results cached in `session_state` so re-opening tabs doesn't re-charge.
  Token 成本:低温短响应 + session_state 缓存,切换 Tab 不重复扣费。

- **R-09 Session-state loss:** Acceptable — users can re-run the pipeline; no persistent data at risk.
  会话状态丢失:可接受,用户重新运行即可,无持久化数据损失。

- **R-11 Encoding issues:** `pd.read_csv` default is utf-8; `to_json` uses `ensure_ascii=False` so Chinese content roundtrips. Windows-specific edge case not observed in testing.
  编码问题:pandas 默认 utf-8;JSON 导出保留原字符,未观察到 Windows 具体问题。

- **R-13 TMS field mismatch:** Column names aligned with Jira Xray / TestRail conventions (`id`, `requirement_id`, `technique`, `priority`, `steps`, `expected_result`). Users can post-process CSV if a specific TMS needs re-mapping.
  TMS 字段不匹配:列名已对齐 Jira Xray / TestRail 常见惯例,用户可做 CSV 后处理。

- **R-14 Missing graphviz binary:** Error surfaces as a Streamlit warning on the state-diagram tab; test generation still works without the diagram render.
  缺 graphviz 二进制:状态图渲染失败,但测试用例生成不受影响。

---

## 7. Residual Risk Posture / 剩余风险态势

After mitigations, the residual risk profile is:

| Priority | Before mitigation | After mitigation |
|----------|-------------------|------------------|
| High     | 2                 | 0                |
| Medium   | 6                 | 2 (R-04, R-10)   |
| Low      | 6                 | 12               |

The two Medium residual risks (**API key leakage**, **injection via upload**) are fundamental properties of any tool that handles secrets and accepts user uploads. They are managed by operational practice (gitignore, user education) rather than eliminated in code.

实施缓解后,高风险全部降级;中风险仅 R-04 / R-10 仍属中位 — 这两项是此类工具固有特性,靠运维约定(gitignore、用户教育)而不是代码消除。

---

## 8. Recommendations / 建议

1. **Production hardening:** add a sandbox / firewall policy that prevents the Streamlit process from reading any file outside `.env/config.json` and `autotestdesign/`.
   生产加固:增加沙箱/防火墙策略,限制进程只能读 `.env/config.json` 与项目目录。

2. **LLM observability:** log token usage per call and surface on the sidebar; alert users when running expensive requirements.
   LLM 可观测性:记录每次调用的 token,在侧边栏显示,对大需求发预警。

3. **Template library:** pre-ship several example state-machine DSLs (shopping-cart checkout, authentication, order lifecycle) to reduce user friction on FR4.
   模板库:预置多个状态机 DSL 模板,降低 FR4 使用门槛。

4. **Test management integration:** provide a direct Jira Xray exporter (beyond generic CSV) for users who use that TMS.
   TMS 对接:为 Jira Xray 用户提供一键直推功能。

---

## 9. Conclusion / 结论

All High-priority risks have effective technical mitigations in place (retry + validation + fallback for LLM errors; unit-tested algorithms for generation correctness). Medium risks are either mitigated by design (adaptive provider handling, pipeline auto-structuring) or accepted as operational concerns (secret management, upload hygiene). The tool is suitable for the Assignment 2 demo and for extended pilot use within the scope documented in the Test Plan.

高优先级风险全部有技术侧有效缓解(LLM 错误的重试+校验+兜底;生成算法的单元测试);中风险或已通过设计缓解(provider 自适应、流水线自动结构化),或作为运维问题被接受(密钥管理、上传卫生)。工具适合 Assignment 2 演示与小范围试点。
