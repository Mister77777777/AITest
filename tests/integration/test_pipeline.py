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
