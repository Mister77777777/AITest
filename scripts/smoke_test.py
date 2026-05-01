"""手动端到端冒烟测试:用真实 LLM 跑一次完整流水线,确认 proxy 和 provider 可用。"""
from __future__ import annotations
import json
from pathlib import Path
from autotestdesign.config import load_config
from autotestdesign.llm.client import LLMClient
from autotestdesign.examples.loader import load_example
from autotestdesign.core.pipeline import run_pipeline
from autotestdesign.core.whitebox.state_machine import parse_dsl
from autotestdesign.core.export import to_json, to_csv, to_xlsx


def main() -> None:
    cfg = load_config()
    print(f"✓ 配置加载成功:model={cfg.model}, base_url={cfg.base_url}")

    llm = LLMClient(cfg)
    print("✓ LLM 客户端就绪(OpenAI 兼容)")

    # 用内置示例跑一次
    reqs = load_example("banking_registration")
    print(f"✓ 已载入 {len(reqs)} 条需求")

    # 挂一个状态机到 REQ-004(账户锁定)
    sm = parse_dsl(
        """
        # 登录状态机
        Idle --login--> LoggingIn
        LoggingIn --success--> LoggedIn
        LoggingIn --fail--> Idle
        Idle --fiveFails--> Locked
        Locked --reset--> Idle
        """,
        start_state="Idle",
    )

    suite = run_pipeline(
        reqs,
        llm=llm,
        state_machine=sm,
        state_machine_requirement_id="REQ-004",
        optimize_max_cases=None,
    )
    print(f"✓ 流水线输出 {len(suite.cases)} 条测试用例")
    print(f"  覆盖率:{suite.coverage}")

    # 按技术分桶计数
    by_tech: dict[str, int] = {}
    for c in suite.cases:
        by_tech[c.technique] = by_tech.get(c.technique, 0) + 1
    print(f"  按技术分布:{by_tech}")

    # 采样:展示第一条风险分析结果
    risked = [r for r in reqs if r.risk is not None]  # 原 reqs 不会被回写,忽略
    # 导出到 out/
    out_dir = Path("out")
    out_dir.mkdir(exist_ok=True)
    (out_dir / "testsuite.json").write_text(to_json(suite), encoding="utf-8")
    to_csv(suite, out_dir / "testsuite.csv")
    to_xlsx(suite, out_dir / "testsuite.xlsx")
    print(f"✓ 已导出到 {out_dir}/")

    # 抽样检查 5 条用例的 Expected Result
    print("\n前 5 条测试用例样例:")
    for c in suite.cases[:5]:
        print(f"  [{c.id}] {c.technique} / {c.priority}")
        print(f"    inputs: {c.inputs}")
        print(f"    expected: {c.expected_result}")

    # 检查 LLM 是否真的被调用(rationale 里不应出现 'LLM unavailable')
    first_req = next((r for r in reqs if r.id == "REQ-001"), None)
    # 注意 reqs 没有 risk 字段(pipeline 没有回写 reqs 列表),我们要看 suite 里的 expected_result 是否像 LLM 生成的
    llm_flavored = [c for c in suite.cases if not c.expected_result.lower().startswith("system ")]
    print(f"\n✓ Oracle 里看起来由 LLM 定制的用例数:{len(llm_flavored)} / {len(suite.cases)}")


if __name__ == "__main__":
    main()
