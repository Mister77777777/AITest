import pytest
from autotestdesign.core.models import Requirement
from autotestdesign.core.risk import compute_risk_rule_based, attach_risk
from tests.fixtures.fake_llm import FakeLLM


def _req(text: str) -> Requirement:
    return Requirement(id="REQ-001", raw_text=text)


def test_payment_keyword_raises_likelihood():
    rs = compute_risk_rule_based(_req("handle credit card payment securely"))
    assert rs.likelihood >= 4
    assert rs.priority in ("High",)


def test_generic_requirement_is_medium_or_low():
    rs = compute_risk_rule_based(_req("display the user profile picture on the homepage"))
    assert rs.priority in ("Medium", "Low")


def test_score_is_product_of_factors():
    rs = compute_risk_rule_based(_req("auth system"))
    assert rs.score == rs.likelihood * rs.impact


def test_attach_risk_populates_rationale_from_llm():
    fake = FakeLLM()
    fake.queue("score_risk", {"rationale": "Payment flow carries financial and reputational risk."})
    req = _req("process customer payment via Stripe")
    out = attach_risk(req, fake)
    assert out.risk is not None
    assert out.risk.rationale.startswith("Payment flow")
    assert out.risk.score == out.risk.likelihood * out.risk.impact


def test_attach_risk_falls_back_on_llm_failure():
    class _BoomLLM:
        def structured_call(self, *a, **kw):
            raise RuntimeError("network down")
    req = _req("login with password")
    out = attach_risk(req, _BoomLLM())
    assert out.risk is not None
    # 降级兜底信息应为中文
    assert "规则基线" in out.risk.rationale or "LLM 不可用" in out.risk.rationale
