from autotestdesign.core.models import Field, Requirement, TestCase
from autotestdesign.core.oracle import synthesize_oracle
from tests.fixtures.fake_llm import FakeLLM


def _req() -> Requirement:
    return Requirement(
        id="REQ-001", raw_text="age must be 18-120",
        input_fields=[Field(name="age", type="int", min=18, max=120)],
        expected_actions=["accept registration"],
    )


def _tc(age: int) -> TestCase:
    return TestCase(id="TC-001", requirement_id="REQ-001", technique="EP", inputs={"age": age})


def test_out_of_range_uses_algorithmic_fallback_without_llm():
    req = _req()
    out = synthesize_oracle(req, _tc(17), llm=None)
    assert "拒绝" in out.expected_result


def test_in_range_calls_llm_when_available():
    req = _req()
    fake = FakeLLM()
    fake.queue("synthesize_oracle", {"expected_result": "System creates a new account."})
    out = synthesize_oracle(req, _tc(30), llm=fake)
    assert out.expected_result == "System creates a new account."


def test_llm_failure_falls_back_to_default():
    req = _req()
    class _Boom:
        def structured_call(self, *a, **kw):
            raise RuntimeError("x")
    out = synthesize_oracle(req, _tc(30), llm=_Boom())
    assert out.expected_result  # 非空
    # 算法兜底时应当用中文陈述"接受"或"拒绝"
    assert "接受" in out.expected_result or "拒绝" in out.expected_result or "执行" in out.expected_result
