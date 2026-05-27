# Assignment 2 子任务拆解

> 状态图例: ✅ 已完成 / ⬜ 未完成 / 🔧 需修改

---

## 总览

| 阶段 | 名称 | 子任务数 | 完成数 | 状态 |
|------|------|---------|--------|------|
| 1 | 目标应用 AuthSystem | 3 | 0 | ⬜ |
| 2 | AutoTestDesign 工具增量 | 2 | 0 | ⬜ |
| 3 | 用工具测目标应用 | 2 | 0 | ⬜ |
| 4 | 三份报告重写 | 3 | 0 | ⬜ |
| 5 | 演示 PPT + 视频 | 2 | 0 | ⬜ |
| — | 基础设施（已完成） | 18 | 18 | ✅ |

---

## 阶段 1 — 目标应用 AuthSystem

### 1.1 实现 auth_system.py ⬜

**目标:** 创建 `target_app/auth_system.py`，实现完整的用户注册登录系统。

**业务规则:**
- BR-01: 年龄 18-120
- BR-02: 密码 8-32 字符，至少 1 数字 + 1 字母
- BR-03: 邮箱包含 `@` 和 `.`
- BR-04: 用户名 3-20 字符且唯一
- BR-05: 5 次连续失败 → 锁定
- BR-06: 密码重置可解锁

**状态机:** Guest → Registered → LoggedIn → Locked → Registered

**输出文件:**
- `target_app/__init__.py`
- `target_app/auth_system.py`

### 1.2 编写 pytest 测试脚本 ⬜

**目标:** 创建 `target_app/test_auth_system.py`，用 pytest 对 AuthSystem 执行测试。

**要求:**
- 覆盖所有 6 条业务规则
- 覆盖状态机的 4 条转换
- 使用 parametrize 进行数据驱动测试
- 可直接通过 `pytest target_app/` 运行

**输出文件:**
- `target_app/test_auth_system.py`

### 1.3 准备 AuthSystem 需求文档 ⬜

**目标:** 编写结构化的需求文本，作为 AutoTestDesign 工具的输入。

**要求:**
- CSV 格式，包含 6 条需求
- 中英文双语
- 覆盖所有输入字段（age、password、email、username）

**输出文件:**
- `target_app/requirements.csv`

---

## 阶段 2 — AutoTestDesign 工具增量

### 2.1 交互式测试用例编辑 ⬜

**目标:** 在 Test Design 面板增加编辑能力，满足 PDF "Mainly" 段落的交互式审查要求。

**具体功能:**
- 生成的测试用例改为可编辑表格（`st.data_editor`）
- 用户可修改输入值、预期结果、优先级、标签
- 用户可删除用例
- 用户可新增用例
- 修改后的套件可重新导出

**改动文件:**
- `autotestdesign/ui/testcase_viewer.py`

### 2.2 覆盖项与策略可视化编辑 ⬜

**目标:** 增加覆盖项识别与策略编辑面板。

**具体功能:**
- 显示当前覆盖项（每个需求的 EP/BVA/DT/STT 用例数）
- 用户可增删覆盖项
- 用户可调整策略（如禁用某个技术、修改优先级规则）
- 重新生成时应用用户编辑的策略

**改动文件:**
- `autotestdesign/ui/testcase_viewer.py`

---

## 阶段 3 — 用工具测目标应用

### 3.1 运行流水线生成测试套件 ⬜

**目标:** 将 AuthSystem 需求输入 AutoTestDesign，跑完整流水线。

**步骤:**
1. 加载 `target_app/requirements.csv`
2. 运行完整流水线（LLM 结构化 → 风险打分 → EP/BVA/DT/STT → Oracle → 优化）
3. 导出 JSON、CSV、Excel 三份产物到 `target_app/output/`

**输出文件:**
- `target_app/output/testsuite.json`
- `target_app/output/testsuite.csv`
- `target_app/output/testsuite.xlsx`

### 3.2 执行测试并收集结果 ⬜

**目标:** 运行 `target_app/test_auth_system.py` 并记录结果。

**要求:**
- 记录通过/失败数量
- 截图或日志留证（用于报告）
- 如有失败，分析原因并改进

---

## 阶段 4 — 三份报告重写

### 4.1 风险分析报告（10%）⬜

**目标:** 重写 `docs/reports/risk_analysis_report.md`，以 AuthSystem 为被测对象。

**要求覆盖:**
- AuthSystem 的风险识别（至少 10 项）
- 每项 Likelihood × Impact = Score
- 高中低优先级分类
- 缓解措施与剩余风险

**输出文件:**
- `docs/reports/risk_analysis_report.md`（覆盖重写）

### 4.2 测试计划（40%）⬜

**目标:** 重写 `docs/reports/test_plan.md`，以 AuthSystem 为被测对象。

**要求覆盖:**
- 项目范围：AuthSystem 测试活动的背景与目标
- 测试项：AuthSystem 功能/非功能特性 + 系统架构描述
- 高阶测试套件设计：为每个套件选择测试技术及理由
- 进度安排/检查清单
- 组织架构图：团队成员角色与职责
- 测试框架选择与理由：pytest 等
- 成本估算：使用 AutoTestDesign 工具 vs 手工测试的工时对比

**输出文件:**
- `docs/reports/test_plan.md`（覆盖重写）

### 4.3 详细测试设计与执行文档（30%）⬜

**目标:** 重写 `docs/reports/detailed_test_design.md`，以 AuthSystem 为被测对象。

**要求覆盖:**
- "Mainly" 流程：概念 → 覆盖项识别 → 覆盖策略与方法 → 测试用例及可追溯性 → Prompt 设计 → 结果分析 → 改进
- 测试用例设计：用 AutoTestDesign 工具为 AuthSystem 设计用例
- 测试工具实现：pytest 测试脚本
- 测试结果分析：基于执行结果的总结
- 体现交互式设计审查的使用过程

**输出文件:**
- `docs/reports/detailed_test_design.md`（覆盖重写）

---

## 阶段 5 — 演示 PPT + 视频

### 5.1 演示 PPT ⬜

**目标:** 制作 15 页演示 PPT。

**内容大纲:**
1. 封面（团队 ID、成员、学号）
2. 项目背景与目标
3. AutoTestDesign 工具架构总览
4. FR1-FR7 功能展示
5. 目标应用 AuthSystem 介绍
6. 用工具测试 AuthSystem 的完整流程
7. 交互式设计审查演示
8. 风险分析报告要点
9. 测试计划要点
10. 详细测试设计要点
11. 测试执行结果
12. 成本估算对比
13. 总结与收获
14. 改进建议
15. Q&A

**输出文件:**
- `demo/presentation.pptx`

### 5.2 演示视频 ⬜

**目标:** 录制 10 分钟演示视频。

**脚本要点:**
1. 工具启动与配置
2. 加载 AuthSystem 需求
3. 运行完整流水线
4. 交互式编辑覆盖项/用例
5. 导出测试套件
6. 在 AuthSystem 上执行测试
7. 结果分析

**输出文件:**
- `demo/demo_script.md`（录屏脚本）

---

## 附录：基础设施（全部已完成）

### A1 项目脚手架 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `requirements.txt` | ✅ | 11 个依赖，含版本约束 |
| `pyproject.toml` | ✅ | 项目元数据 + pytest/coverage/ruff 配置 |
| `.gitignore` | ✅ | 排除 .env、venv、缓存文件等 |
| `autotestdesign/__init__.py` | ✅ | 空文件 |
| `autotestdesign/config.py` | ✅ | 支持 .env/config.json + 多 provider 兼容 |

**代码位置:** `autotestdesign/config.py:1-35`

### A2 数据模型 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/core/models.py` | ✅ | Field, RiskScore, Requirement, TestCase, TestSuite |
| `autotestdesign/core/__init__.py` | ✅ | 空文件 |

**代码位置:** `autotestdesign/core/models.py:1-56`

### A3 LLM 客户端 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/llm/__init__.py` | ✅ | 空文件 |
| `autotestdesign/llm/client.py` | ✅ | OpenAI 兼容客户端，支持 retry + JSON 校验 + provider 自适应 |
| `autotestdesign/llm/prompts/__init__.py` | ✅ | 空文件 |
| `tests/fixtures/fake_llm.py` | ✅ | 确定性内存替身，供测试注入 |

**代码位置:** `autotestdesign/llm/client.py:1-103`

### A4 FR1 — 需求解析 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/core/parsing.py` | ✅ | CSV pandas 解析 / 纯文本按空行分割 / LLM 结构化 |
| `autotestdesign/llm/prompts/structure_requirement.md` | ✅ | 中文 prompt，提取 input_fields + conditions + expected_actions |

**代码位置:** `autotestdesign/core/parsing.py:1-44`

### A5 FR2 — 风险打分 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/core/risk.py` | ✅ | 中英双语关键词规则 + LLM rationale + 失败降级 |
| `autotestdesign/llm/prompts/score_risk.md` | ✅ | 中文 prompt |

**代码位置:** `autotestdesign/core/risk.py:1-94`

### A6 FR3 — 黑盒测试生成 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/core/blackbox/__init__.py` | ✅ | 空文件 |
| `autotestdesign/core/blackbox/equivalence.py` | ✅ | EP：按字段类型(int/float/enum/string/bool)生成等价类 |
| `autotestdesign/core/blackbox/boundary.py` | ✅ | BVA：每个区间字段 6 个边界值 |
| `autotestdesign/core/blackbox/decision_table.py` | ✅ | DT：N 个条件 → 2^N 行判定表 |

**代码位置:**
- `autotestdesign/core/blackbox/equivalence.py:1-64`
- `autotestdesign/core/blackbox/boundary.py:1-52`
- `autotestdesign/core/blackbox/decision_table.py:1-36`

### A7 FR4 — 白盒状态机 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/core/whitebox/__init__.py` | ✅ | 空文件 |
| `autotestdesign/core/whitebox/state_machine.py` | ✅ | DSL 解析 + all-states + all-transitions 覆盖 |

**代码位置:** `autotestdesign/core/whitebox/state_machine.py:1-130`

### A8 FR5 — 测试预言 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/core/oracle.py` | ✅ | 越界自动兜底 → LLM 合成 → 失败再降级 |
| `autotestdesign/llm/prompts/synthesize_oracle.md` | ✅ | 中文 prompt |

**代码位置:** `autotestdesign/core/oracle.py:1-65`

### A9 FR6 — 导出 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/core/export.py` | ✅ | JSON / CSV / Excel（openpyxl），列对齐常见 TMS |

**代码位置:** `autotestdesign/core/export.py:1-39`

### A10 FR7 — 测试套件优化 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/core/optimizer.py` | ✅ | 指纹去重 + 加权集合覆盖 + 优先级排序 |

**代码位置:** `autotestdesign/core/optimizer.py:1-51`

### A11 流水线编排 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/core/pipeline.py` | ✅ | FR1→FR7 全链路，含 auto_structure 开关 |

**代码位置:** `autotestdesign/core/pipeline.py:1-87`

### A12 LLM Prompt 模板 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/llm/prompts/structure_requirement.md` | ✅ | 中文，需求结构化 |
| `autotestdesign/llm/prompts/score_risk.md` | ✅ | 中文，风险理由生成 |
| `autotestdesign/llm/prompts/synthesize_oracle.md` | ✅ | 中文，Oracle 合成 |

### A13 Streamlit UI ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/app.py` | ✅ | 4 Tab 入口 + Hero + 顶栏 |
| `autotestdesign/ui/__init__.py` | ✅ | 空文件 |
| `autotestdesign/ui/state.py` | ✅ | SessionData + 跨 Tab 工作集状态条 |
| `autotestdesign/ui/theme.py` | ✅ | Apple 风格 CSS（SF Pro、圆角卡片、毛玻璃） |
| `autotestdesign/ui/upload_panel.py` | ✅ | 内置示例 / 上传文件 / 手动输入 |
| `autotestdesign/ui/risk_panel.py` | ✅ | 风险指标卡 + 表格 + 优先级柱状图 |
| `autotestdesign/ui/testcase_viewer.py` | ✅ | 流水线配置 + 运行 + 分技术 Tab 展示 |
| `autotestdesign/ui/state_diagram.py` | ✅ | DSL 编辑器 + graphviz 渲染 |
| `autotestdesign/ui/export_panel.py` | ✅ | JSON/CSV/Excel 下载卡片 + 预览 |

### A14 内置示例 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `autotestdesign/examples/__init__.py` | ✅ | 空文件 |
| `autotestdesign/examples/loader.py` | ✅ | 示例注册 + 加载 |
| `autotestdesign/examples/banking_registration.csv` | ✅ | 银行注册 6 条需求（中文） |
| `autotestdesign/examples/shopping_cart.md` | ✅ | 购物车 4 条需求（中文） |

### A15 测试套件 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `tests/unit/test_config.py` | ✅ | 配置加载 |
| `tests/unit/test_models.py` | ✅ | 数据模型 |
| `tests/unit/test_llm_client.py` | ✅ | LLM 客户端（stub） |
| `tests/unit/test_parsing.py` | ✅ | 需求解析 |
| `tests/unit/test_risk.py` | ✅ | 风险打分 |
| `tests/unit/test_equivalence.py` | ✅ | EP 生成器 |
| `tests/unit/test_boundary.py` | ✅ | BVA 生成器 |
| `tests/unit/test_decision_table.py` | ✅ | DT 生成器 |
| `tests/unit/test_state_machine.py` | ✅ | 状态机 |
| `tests/unit/test_oracle.py` | ✅ | Oracle 合成 |
| `tests/unit/test_optimizer.py` | ✅ | 套件优化 |
| `tests/unit/test_export.py` | ✅ | 导出 |
| `tests/unit/test_examples.py` | ✅ | 内置示例 |
| `tests/integration/test_pipeline.py` | ✅ | 端到端流水线 |
| `tests/fixtures/fake_llm.py` | ✅ | 测试替身 |

**测试统计:** 14 个测试文件，689 行测试代码，`core/` 覆盖率 ≥ 95%

### A16 README ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `README.md` | ✅ | 中英双语，含安装/配置/运行/测试/项目结构 |

### A17 现有报告 ⚠️

| 文件 | 状态 | 说明 |
|------|------|------|
| `docs/reports/risk_analysis_report.md` | ⚠️ | 以 AutoTestDesign 工具为对象，需要重写为以 AuthSystem 为对象 |
| `docs/reports/test_plan.md` | ⚠️ | 以 AutoTestDesign 工具为对象，需要重写为以 AuthSystem 为对象 |
| `docs/reports/detailed_test_design.md` | ⚠️ | 以 AutoTestDesign 工具为对象，需要重写为以 AuthSystem 为对象 |

### A18 设计文档 ✅

| 文件 | 状态 | 说明 |
|------|------|------|
| `docs/superpowers/specs/2026-05-01-autotestdesign-design.md` | ✅ | 原始设计 spec |
| `docs/superpowers/plans/2026-05-01-autotestdesign.md` | ✅ | 原始实现计划 |

---

## 执行顺序建议

```
阶段 1 (AuthSystem)
  → 阶段 2 (工具增量)
    → 阶段 3 (工具测目标应用)
      → 阶段 4 (三份报告)
        → 阶段 5 (PPT + 视频)
```

理由：必须先有目标应用，才能在工具中展示交互式编辑，才能生成测试用例并执行，报告和 PPT 才能有真实数据。
