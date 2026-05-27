"""
运行 AutoTestDesign 流水线处理 AuthSystem 需求。

将 requirements.csv 输入完整 FR1→FR7 流水线,
导出 JSON / CSV / Excel 到 target_app/output/ 目录。
LLM 关闭,使用规则兜底;手动补充 input_fields 确保 EP/BVA/DT 可生成。
"""

from __future__ import annotations
from pathlib import Path
from autotestdesign.core.models import Requirement, Field
from autotestdesign.core.parsing import parse_csv
from autotestdesign.core.pipeline import run_pipeline
from autotestdesign.core.whitebox.state_machine import parse_dsl
from autotestdesign.core.export import to_json, to_csv, to_xlsx

OUTPUT_DIR = Path(__file__).parent / "output"


def _enrich_requirements(requirements: list[Requirement]) -> list[Requirement]:
    """为每条需求补充 input_fields,在无 LLM 时使 EP/BVA/DT 能生成用例。

    各需求对应字段:
      REQ-001 (年龄):     age (int, 18-120)
      REQ-002 (密码):     password (string, 8-32) — 用 min/max 表示长度约束
      REQ-003 (邮箱):     email (string) — 只做格式校验
      REQ-004 (用户名):   username (string, 3-20)
      REQ-005 (失败次数): failed_attempts (int, 0-4 safe, 5 lock)
      REQ-006 (重置):     password (string, 8-32) — 重置密码格式
    """
    field_map = {
        "REQ-001": [Field(name="age", type="int", min=18, max=120)],
        "REQ-002": [Field(name="password", type="string", min=8, max=32)],
        "REQ-003": [Field(name="email", type="string")],
        "REQ-004": [Field(name="username", type="string", min=3, max=20)],
        "REQ-005": [Field(name="failed_attempts", type="int", min=0, max=5)],
        "REQ-006": [Field(name="new_password", type="string", min=8, max=32)],
    }
    # 补充 conditions (供判定表 DT 使用)
    condition_map = {
        "REQ-001": ["年龄在 18-120 之间"],
        "REQ-002": ["密码长度 8-32", "密码包含数字", "密码包含字母"],
        "REQ-003": ["邮箱包含 @", "邮箱包含 ."],
        "REQ-004": ["用户名长度 3-20", "用户名唯一"],
        "REQ-005": ["连续失败次数 >= 5"],
        "REQ-006": ["账户状态为 Locked", "新密码符合规范"],
    }
    # 补充 expected_actions (供判定表 DT 和 Oracle 使用)
    action_map = {
        "REQ-001": ["通过注册校验", "拒绝注册"],
        "REQ-002": ["通过密码校验", "拒绝密码"],
        "REQ-003": ["通过邮箱校验", "拒绝邮箱"],
        "REQ-004": ["通过用户名校验", "拒绝用户名"],
        "REQ-005": ["允许登录", "锁定账户"],
        "REQ-006": ["重置密码成功", "解锁账户"],
    }
    for r in requirements:
        if r.id in field_map and not r.input_fields:
            r.input_fields = field_map[r.id]
        if r.id in condition_map and not r.conditions:
            r.conditions = condition_map[r.id]
        if r.id in action_map and not r.expected_actions:
            r.expected_actions = action_map[r.id]
    return requirements


def main() -> None:
    print("=" * 60)
    print("AutoTestDesign 流水线 — AuthSystem 目标应用测试")
    print("=" * 60)

    # 1. 加载需求
    csv_path = Path(__file__).parent / "requirements.csv"
    print(f"\n① 加载需求: {csv_path}")
    requirements = parse_csv(csv_path)
    print(f"   解析到 {len(requirements)} 条需求:")
    for r in requirements:
        print(f"     {r.id}: {r.raw_text[:60]}...")

    # 1.5 补充 input_fields
    requirements = _enrich_requirements(requirements)
    print(f"\n   补充 input_fields 完成")

    # 2. 构建状态机 DSL
    dsl = """
    Guest --register--> Registered
    Registered --login--> LoggedIn
    LoggedIn --logout--> Registered
    Registered --failedAttempt--> Registered
    LoggedIn --failedAttempt--> LoggedIn
    LoggedIn --fifthFailedAttempt--> Locked
    Registered --fifthFailedAttempt--> Locked
    Locked --resetPassword--> Registered
    """
    print("\n② 构建状态机 DSL:")
    print(dsl)

    sm = parse_dsl(dsl, start_state="Guest")
    g = sm.to_digraph()
    print(f"   状态数: {len(g.nodes())}")
    print(f"   转换数: {len(g.edges())}")

    # 3. 运行流水线 (LLM 关闭,走规则兜底)
    print("\n③ 运行流水线 (LLM 关闭,走规则兜底)...")
    suite = run_pipeline(
        requirements,
        llm=None,
        state_machine=sm,
        state_machine_requirement_id="REQ-006",
        optimize_max_cases=None,
    )
    print(f"   生成 {len(suite.cases)} 条测试用例")

    # 统计各技术用例数
    by_tech: dict[str, int] = {}
    for c in suite.cases:
        by_tech[c.technique] = by_tech.get(c.technique, 0) + 1
    print("   技术分布:")
    for tech, count in sorted(by_tech.items()):
        print(f"     {tech}: {count} 条")

    # 4. 导出
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\n④ 导出到 {OUTPUT_DIR}/")

    json_path = OUTPUT_DIR / "testsuite.json"
    json_path.write_text(to_json(suite), encoding="utf-8")
    print(f"   ✓ {json_path.name}")

    csv_out = OUTPUT_DIR / "testsuite.csv"
    to_csv(suite, csv_out)
    print(f"   ✓ {csv_out.name}")

    xlsx_out = OUTPUT_DIR / "testsuite.xlsx"
    to_xlsx(suite, xlsx_out)
    print(f"   ✓ {xlsx_out.name}")

    print("\n" + "=" * 60)
    print("流水线执行完成。")
    print("=" * 60)


if __name__ == "__main__":
    main()
