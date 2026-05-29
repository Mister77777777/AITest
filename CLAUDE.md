# CLAUDE.md — AutoTestDesign 项目约定

## 项目概述

AutoTestDesign 是一个 AI 驱动的测试用例自动生成工具，基于 ISTQB Foundation Level 原则和 ISO/IEC/IEEE 29119-4 技术标准。目标应用为 AuthSystem（纯 Python 用户注册登录系统）。

## 语言规范

- **代码标识符**（变量名、函数名、类名、模块名）：英文
- **文档、注释、UI 文案、Prompt 模板**：中文
- **Git 提交信息**：中文

## 环境

- Python 虚拟环境: `.venv/`
- 所有 Python 命令通过 `.venv/bin/python` 执行
- 安装依赖: `.venv/bin/pip install <package>`
- 运行测试: `.venv/bin/python -m pytest <path>`

## 项目结构

```
AITest/
├── autotestdesign/          # AutoTestDesign 工具源码
│   ├── app.py               # Streamlit 入口
│   ├── config.py            # 配置加载 (.env / config.json)
│   ├── core/                # 纯算法层 (不依赖 UI 或 LLM)
│   │   ├── models.py        # Pydantic 数据模型
│   │   ├── parsing.py       # FR1 需求解析
│   │   ├── risk.py          # FR2 风险打分
│   │   ├── blackbox/        # FR3 EP / BVA / DT
│   │   ├── whitebox/        # FR4 状态机覆盖
│   │   ├── oracle.py        # FR5 测试预言
│   │   ├── optimizer.py     # FR7 套件优化
│   │   ├── export.py        # FR6 导出
│   │   └── pipeline.py      # 流水线编排
│   ├── llm/                 # LLM 客户端 + Prompt 模板
│   ├── ui/                  # Streamlit UI 组件
│   └── examples/            # 内置示例需求
├── target_app/              # 目标被测应用 AuthSystem
│   ├── auth_system.py       # AuthSystem 类
│   ├── test_auth_system.py  # pytest 测试
│   └── requirements.csv     # 结构化需求
├── docs/reports/            # 三份报告 (需重写)
├── tests/                   # AutoTestDesign 测试套件
└── task/                    # 任务管理文档
```

## 架构原则

- `core/` 不依赖 `streamlit` 或 `openai`
- LLM 调用限定在 `llm/client.py`，可 mock 注入
- Prompt 模板作为外部 `.md` 文件存放在 `llm/prompts/`
- UI 层通过 `st.session_state` 持有 `SessionData`（参见 `autotestdesign/ui/state.py`）

## 工作流程

1. 每个阶段完成后运行测试验证
2. 测试通过后立即 git commit
3. commit 后执行 `git push`，超时时间 15 秒
4. 遵循 `task/tasks.md` 中的任务顺序
4. 不修改 `core/` 算法层（FR1-FR7 已全部完成）

## 关键约定

- 使用 pydantic v2 `model_validator` 做数据校验
- 测试使用 `tests/fixtures/fake_llm.py` 作为 LLM 替身
- 导出格式：JSON / CSV / Excel（openpyxl）
- Streamlit 页面使用 Apple 风格主题（`ui/theme.py`）
