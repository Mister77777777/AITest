# AutoTestDesign

**AI-powered automated test design toolkit — from requirements to structured test suites in minutes.**

**AI 驱动的自动化测试设计工具包 — 从需求到结构化测试套件,全程分钟级完成。**

---

## Table of Contents / 目录

1. [Features / 功能矩阵](#features--功能矩阵)
2. [Setup / 环境准备](#setup--环境准备)
3. [System Dependencies / 系统依赖](#system-dependencies--系统依赖)
4. [Configuration / 配置](#configuration--配置)
5. [Run / 运行](#run--运行)
6. [Tests / 测试](#tests--测试)
7. [Project Structure / 项目结构](#project-structure--项目结构)
8. [Prompts / 提示模板](#prompts--提示模板)
9. [License / 许可](#license--许可)

---

## Features / 功能矩阵

The following seven functional requirements are implemented end-to-end.

以下七项功能需求已完整实现。

| FR | Feature / 功能 | Implementation / 实现位置 |
|----|---------------|--------------------------|
| FR1 | **Requirement Parsing** — Parse free-text requirements into structured JSON models with typed fields, conditions, and expected actions.<br>**需求解析** — 将自由文本需求解析为带类型字段、前置条件和预期动作的结构化 JSON 模型。 | `autotestdesign/core/parsing.py` |
| FR2 | **Risk Scoring** — Compute likelihood, impact and priority scores for each requirement; LLM generates a human-readable rationale.<br>**风险打分** — 为每条需求计算可能性、影响度和优先级分数；LLM 自动生成可读说明。 | `autotestdesign/core/risk.py` |
| FR3 | **Black-box Test Design** — Generate test cases using Equivalence Partitioning (EP), Boundary Value Analysis (BVA) and Decision Table (DT) techniques.<br>**黑盒测试设计** — 基于等价类划分（EP）、边界值分析（BVA）和判定表（DT）技术生成测试用例。 | `autotestdesign/core/blackbox/` |
| FR4 | **White-box State Machine** — Build a finite state machine from requirements and derive transition-coverage test paths.<br>**白盒状态机** — 从需求构建有限状态机，推导转换覆盖测试路径。 | `autotestdesign/core/whitebox/` |
| FR5 | **Test Oracle** — For each concrete test input, produce an LLM-synthesized expected result and acceptance criterion.<br>**测试预言** — 针对每个具体测试输入，由 LLM 合成预期结果与验收标准。 | `autotestdesign/core/oracle.py` |
| FR6 | **Export** — Export the full test suite to JSON, CSV and Excel (`.xlsx`) with one click.<br>**导出** — 一键将完整测试套件导出为 JSON、CSV 和 Excel（`.xlsx`）格式。 | `autotestdesign/core/export.py` |
| FR7 | **Test Suite Optimization** — Remove redundant test cases and rank the remaining set by risk priority to minimize regression cost.<br>**测试套件优化** — 去除冗余测试用例，并按风险优先级排序，降低回归成本。 | `autotestdesign/core/optimizer.py` |

---

## Setup / 环境准备

Create a virtual environment and install all Python dependencies.

创建虚拟环境并安装全部 Python 依赖。

```bash
# Create virtual environment / 创建虚拟环境
python3 -m venv .venv

# Activate (Linux / macOS) / 激活（Linux / macOS）
source .venv/bin/activate

# Activate (Windows PowerShell) / 激活（Windows PowerShell）
# .venv\Scripts\Activate.ps1

# Install dependencies / 安装依赖
pip install -r requirements.txt
```

Key runtime dependencies (see `requirements.txt` for pinned versions):

主要运行时依赖（完整版本约束见 `requirements.txt`）：

| Package | Purpose / 用途 |
|---------|---------------|
| `streamlit` | Web UI / 网页界面 |
| `openai` | LLM API client / LLM API 客户端 |
| `pydantic` | Data validation / 数据校验 |
| `pandas` + `openpyxl` | Tabular data & Excel export / 表格数据与 Excel 导出 |
| `networkx` + `graphviz` | State machine graph / 状态机图形化 |
| `Jinja2` | Prompt template rendering / 提示词模板渲染 |
| `pytest` + `pytest-cov` | Testing & coverage / 测试与覆盖率 |

---

## System Dependencies / 系统依赖

The `graphviz` Python package wraps the Graphviz CLI binaries, which must be installed separately at the OS level.

`graphviz` Python 包封装了 Graphviz 命令行工具，后者需在操作系统层面单独安装。

**Ubuntu / Debian**

```bash
sudo apt-get update && sudo apt-get install -y graphviz
```

**macOS (Homebrew)**

```bash
brew install graphviz
```

**Windows (Chocolatey)**

```powershell
choco install graphviz
```

After installation, verify the binary is on your `PATH`:

安装后，验证二进制文件已在 `PATH` 中：

```bash
dot -V
```

If Graphviz is not installed, state machine diagrams will be skipped but all other features remain functional.

若未安装 Graphviz，状态机图表将被跳过，其他所有功能保持正常。

---

## Configuration / 配置

AutoTestDesign reads its LLM settings from a `.env` file or `config.json` in the repo root. If neither is present, or if `api_key` is left empty, LLM-dependent features (FR2 rationale, FR5 oracle) gracefully degrade to rule-based / algorithmic fallbacks — the tool remains fully usable offline.

AutoTestDesign 从仓库根目录的 `.env` 文件或 `config.json` 读取 LLM 配置。若两者均不存在，或 `api_key` 为空，依赖 LLM 的功能（FR2 风险说明、FR5 测试预言）将自动降级为基于规则/算法的兜底实现 — 工具在离线状态下仍可完整使用。

### `config.json` example / 示例

```json
{
  "base_url": "https://api.openai.com/v1",
  "api_key": "sk-...",
  "model": "gpt-4o-mini",
  "temperature": 0.2
}
```

### `.env` example / 示例

```dotenv
BASE_URL=https://api.openai.com/v1
API_KEY=sk-...
MODEL=gpt-4o-mini
TEMPERATURE=0.2
```

### Field reference / 字段说明

| Field / 字段 | Type / 类型 | Default / 默认值 | Description / 说明 |
|-------------|------------|-----------------|-------------------|
| `base_url` | string | `https://api.openai.com/v1` | OpenAI-compatible endpoint root URL. Change to use alternative providers.<br>OpenAI 兼容端点根 URL，切换即可使用其他 provider。 |
| `api_key` | string | _(empty)_ | Secret key for the chosen provider. Leave empty to disable LLM calls.<br>所选 provider 的密钥，留空则禁用 LLM 调用。 |
| `model` | string | `gpt-4o-mini` | Model identifier passed to the `/chat/completions` endpoint.<br>传递给 `/chat/completions` 端点的模型标识符。 |
| `temperature` | float | `0.2` | Sampling temperature (0 = deterministic, 1 = creative).<br>采样温度（0 为确定性输出，1 为最大随机性）。 |

### Supported providers / 支持的 Provider

AutoTestDesign uses the OpenAI-compatible chat completions API, so any provider that implements this interface works without code changes.

AutoTestDesign 使用 OpenAI 兼容的 chat completions API，任何实现该接口的 provider 均可无缝接入，无需修改代码。

| Provider | `base_url` | `model` example |
|----------|-----------|----------------|
| **OpenAI** | `https://api.openai.com/v1` | `gpt-4o-mini` |
| **DeepSeek** | `https://api.deepseek.com/v1` | `deepseek-chat` |
| **Anthropic proxy** | _(your proxy URL)_ | `claude-3-5-haiku-20241022` |
| **Local (Ollama)** | `http://localhost:11434/v1` | `llama3` |

---

## Run / 运行

Start the Streamlit application with:

使用以下命令启动 Streamlit 应用：

```bash
streamlit run autotestdesign/app.py
```

The app opens automatically in your browser at `http://localhost:8501`.

应用会自动在浏览器中打开，地址为 `http://localhost:8501`。

### Demo walkthrough / 演示流程

Follow the steps below to see a complete end-to-end run using the built-in banking registration example.

按以下步骤完整体验内置银行开户注册示例的全流程。

**Step 1 — Load a requirement / 步骤 1 — 载入需求**

Navigate to the **Requirement Input** page. Under *Built-in Examples*, select `banking_registration` from the dropdown and click **Load**. The requirement text and its structured fields will appear in the editor.

进入 **需求录入** 页面，在「内置示例」下拉列表中选择 `banking_registration`，点击 **载入**。需求文本及结构化字段随即显示在编辑器中。

**Step 2 — Run the pipeline / 步骤 2 — 运行完整流水线**

Switch to the **Test Design** page and click **Run Full Pipeline**. The application parses the requirement, scores risks, generates black-box and white-box test cases, synthesizes test oracles, and optimizes the suite in sequence.

切换到 **测试设计** 页面，点击 **运行完整流水线**。应用依次完成需求解析、风险打分、黑盒与白盒用例生成、测试预言合成和套件优化。

**Step 3 — Review results / 步骤 3 — 查看结果**

Three result tabs are available:

结果区提供三个选项卡：

- **Risk Analysis / 风险分析** — Priority-sorted risk table with LLM rationale. / 按优先级排序的风险表，含 LLM 生成的说明。
- **Test Design / 测试设计** — Complete test case matrix (ID, technique, inputs, oracle, priority). / 完整测试用例矩阵（ID、技术手段、输入、预言、优先级）。
- **Export / 导出** — Download buttons for all three formats. / 三种格式的下载按钮。

**Step 4 — Export / 步骤 4 — 导出**

On the **Export** tab, click any of the three download buttons to save results:

在 **导出** 选项卡，点击下载按钮保存结果：

- **Download JSON** — Machine-readable full suite. / 完整套件的机器可读格式。
- **Download CSV** — Flat table for spreadsheet tools. / 适用于表格工具的平铺格式。
- **Download Excel** — Formatted `.xlsx` workbook with multiple sheets. / 含多工作表的格式化 `.xlsx` 文件。

---

## Tests / 测试

Run the test suite with coverage reporting:

运行测试套件并生成覆盖率报告：

```bash
# Run all tests with coverage / 运行全部测试并统计覆盖率
.venv/bin/pytest --cov=autotestdesign/core --cov-report=term-missing

# Generate HTML coverage report / 生成 HTML 覆盖率报告
.venv/bin/pytest --cov=autotestdesign/core --cov-report=html
# Open htmlcov/index.html in a browser / 在浏览器中打开 htmlcov/index.html

# Run only unit tests / 仅运行单元测试
.venv/bin/pytest tests/unit/

# Run only integration tests / 仅运行集成测试
.venv/bin/pytest tests/integration/
```

**Coverage target / 覆盖率目标:** `autotestdesign/core/` ≥ 80 %

Tests are organized in three directories:

测试按以下三个目录组织：

| Directory / 目录 | Contents / 内容 |
|-----------------|----------------|
| `tests/unit/` | Fast, isolated unit tests for core algorithms. / 对核心算法的快速隔离单元测试。 |
| `tests/integration/` | End-to-end pipeline tests with fixture inputs. / 使用固定输入的端到端流水线测试。 |
| `tests/fixtures/` | Shared test data (sample requirements, expected outputs). / 共享测试数据（示例需求、预期输出）。 |

---

## Project Structure / 项目结构

The repository is organized as follows. Each package has a single, well-scoped responsibility.

仓库结构如下，每个包职责单一、边界清晰。

```
AutoTestDesign/
├── README.md                  # This file / 本文件
├── requirements.txt           # Python dependencies / Python 依赖
├── pyproject.toml             # Build & lint config / 构建与 lint 配置
│
├── autotestdesign/            # Main application package / 主应用包
│   ├── app.py                 # Streamlit entry point / Streamlit 入口
│   ├── config.py              # Config loader (.env / config.json) / 配置加载器
│   │
│   ├── core/                  # Pure algorithms & data models / 纯算法与数据模型
│   │   ├── parsing.py         # FR1: Requirement parsing / 需求解析
│   │   ├── risk.py            # FR2: Risk scoring / 风险打分
│   │   ├── blackbox/          # FR3: EP / BVA / DT test generation / 黑盒测试生成
│   │   ├── whitebox/          # FR4: State machine & path coverage / 状态机与路径覆盖
│   │   ├── oracle.py          # FR5: Test oracle synthesis / 测试预言合成
│   │   ├── export.py          # FR6: JSON / CSV / Excel export / 导出
│   │   └── optimizer.py       # FR7: Test suite optimization / 测试套件优化
│   │
│   ├── llm/                   # OpenAI-compatible client + prompt templates
│   │   │                      # OpenAI 兼容客户端 + 提示词模板
│   │   └── prompts/           # Jinja2 prompt templates / Jinja2 提示词模板
│   │       ├── structure_requirement.md
│   │       ├── score_risk.md
│   │       └── synthesize_oracle.md
│   │
│   ├── ui/                    # Streamlit page panels / Streamlit 页面面板
│   └── examples/              # Built-in sample requirement sets / 内置示例需求集
│       ├── banking_registration.csv
│       └── shopping_cart.md
│
└── tests/                     # Test suite / 测试套件
    ├── unit/                  # Unit tests / 单元测试
    ├── integration/           # Integration tests / 集成测试
    └── fixtures/              # Shared test data / 共享测试数据
```

---

## Prompts / 提示模板

Three Jinja2 prompt templates in `autotestdesign/llm/prompts/` drive LLM interactions. Each template returns a strict JSON object — no prose, no markdown fences.

`autotestdesign/llm/prompts/` 中的三个 Jinja2 提示词模板驱动 LLM 交互。每个模板均要求返回严格的 JSON 对象，不含多余文本或 Markdown 格式符号。

| Template / 模板 | Used by / 使用方 | Purpose / 用途 |
|----------------|-----------------|----------------|
| `structure_requirement.md` | FR1 `parsing.py` | Instructs the LLM to extract typed input fields, preconditions, expected actions, and a functional/non-functional category from raw requirement text.<br>指示 LLM 从原始需求文本中提取类型化输入字段、前置条件、预期动作及功能/非功能分类。 |
| `score_risk.md` | FR2 `risk.py` | Given a requirement plus pre-computed rule-based likelihood/impact/score values, asks the LLM to generate a 1–2 sentence rationale explaining why the score is appropriate.<br>给定需求及预计算的规则评分（可能性/影响度/分数），要求 LLM 生成 1–2 句说明该分数合理性的文字。 |
| `synthesize_oracle.md` | FR5 `oracle.py` | Given a requirement, its declared expected actions, and a concrete test input, produces one sentence describing the expected system behavior (the test oracle).<br>给定需求、其声明的预期动作及具体测试输入，生成一句话描述预期系统行为（即测试预言）。 |

---

## License / 许可

This project is an academic submission for **Assignment 2** of the Software Testing course.

本项目为软件测试课程**作业 2** 的学术提交成果。

It is intended solely for educational and evaluation purposes. All rights are reserved by the author unless otherwise stated.

本项目仅用于教育和评估目的，作者保留所有权利，另有声明者除外。
