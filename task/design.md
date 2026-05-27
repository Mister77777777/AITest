# Assignment 2 完整交付设计文档

**日期:** 2026-05-27
**状态:** 已批准

---

## 1. 交付物总览

| # | 交付物 | 权重 | 描述 |
|---|--------|------|------|
| 1 | AutoTestDesign 工具 | 20% | 源码 + prompt + README + 视频演示 |
| 2 | 风险分析报告 | 10% | 针对 AuthSystem 目标应用 |
| 3 | 测试计划 | 40% | 针对 AuthSystem 目标应用 |
| 4 | 详细测试设计与执行文档 | 30% | 针对 AuthSystem 目标应用 |
| 5 | 演示 PPT | — | 15 页，中英双语 |

---

## 2. 目标应用：AuthSystem

### 2.1 功能描述

一个纯 Python 内存实现的用户注册与登录系统。

**核心功能：**
- 用户注册（用户名、密码、年龄、邮箱）
- 用户登录 / 登出
- 密码重置
- 5 次连续失败 → 账户锁定

### 2.2 业务规则

| 规则 | 描述 |
|------|------|
| BR-01 | 年龄必须在 18 至 120 之间 |
| BR-02 | 密码长度 8-32 字符，且至少包含 1 位数字 + 1 位字母 |
| BR-03 | 邮箱必须包含 `@` 和 `.` |
| BR-04 | 用户名必须唯一，长度 3-20 字符 |
| BR-05 | 连续登录失败 5 次后账户锁定 |
| BR-06 | 锁定账户需要通过密码重置解锁 |

### 2.3 状态机

```
Guest --register--> Registered
Registered --login--> LoggedIn
LoggedIn --logout--> Registered
LoggedIn --failedAttempt--> LoggedIn (attempts < 5)
LoggedIn --failedAttempt(5th)--> Locked
Locked --resetPassword--> Registered
```

### 2.4 技术实现

- `target_app/auth_system.py`：纯 Python 类，dict 存储，零外部依赖
- `target_app/test_auth_system.py`：pytest 测试脚本

---

## 3. AutoTestDesign 工具增量改进

### 3.1 交互式设计审查（核心增量）

在 Test Design 面板增加编辑能力：

- 用户可查看生成的覆盖项（coverage items）
- 用户可增删改覆盖项和策略
- 用户可编辑测试用例（修改输入、预期结果、优先级）
- 变更可追溯（记录修改时间与修改人）

### 3.2 已有模块确认无改动

FR1-FR7 的 `core/` 模块全部完成，本次不修改算法层。

---

## 4. 语言规范

- 所有文档：中文
- 所有注释：中文
- 所有 UI 文案：中文
- 代码标识符（变量名、函数名、类名）：英文
- Prompt 模板：中文

---

## 5. 产出物结构

```
AITest/
├── autotestdesign/          # 工具（已有，增量：交互式编辑）
├── target_app/              # 【新建】目标应用
│   ├── __init__.py
│   ├── auth_system.py       #   AuthSystem 类
│   └── test_auth_system.py  #   pytest 测试脚本
├── docs/reports/            # 【重写】三份报告
│   ├── risk_analysis_report.md     # 以 AuthSystem 为对象
│   ├── test_plan.md                # 以 AuthSystem 为对象
│   └── detailed_test_design.md     # 以 AuthSystem 为对象
├── task/                    # 【新建】任务管理
│   ├── design.md            #   本文档
│   └── tasks.md             #   详细子任务拆解
└── demo/                    # 【新建】演示材料
    ├── presentation.pptx    #   PPT
    └── demo_script.md       #   录屏脚本
```
