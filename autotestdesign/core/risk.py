from __future__ import annotations
from typing import Any, Protocol
from pydantic import BaseModel
from autotestdesign.core.models import Requirement, RiskScore

# 高影响关键词:触发 impact +2
HIGH_IMPACT_KEYWORDS = {
    "payment", "credit card", "billing", "auth", "login", "password",
    "security", "encrypt", "token", "admin", "permission", "privacy",
    "personal data", "pii", "compliance",
}
# 高可能性关键词:触发 likelihood +2;金融/认证类功能天生被频繁攻击,可能性同样高
HIGH_LIKELIHOOD_KEYWORDS = {
    "concurrent", "real-time", "external api", "network", "integration",
    "migration", "async", "parallel",
    "payment", "credit card", "billing", "auth", "login", "password",
    "security", "encrypt", "token",
}


class _Rationale(BaseModel):
    rationale: str


class _LLMLike(Protocol):
    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type) -> Any: ...


def _priority_from_score(score: int) -> str:
    if score >= 15:
        return "High"
    if score >= 8:
        return "Medium"
    return "Low"


def compute_risk_rule_based(req: Requirement) -> RiskScore:
    """基于关键词规则计算风险分。输出 score = likelihood * impact。"""
    text = req.raw_text.lower()
    impact = 2
    likelihood = 2
    for kw in HIGH_IMPACT_KEYWORDS:
        if kw in text:
            impact = min(5, impact + 2)
            break
    for kw in HIGH_LIKELIHOOD_KEYWORDS:
        if kw in text:
            likelihood = min(5, likelihood + 2)
            break
    if req.category == "non-functional":
        impact = max(impact, 3)
    score = likelihood * impact
    return RiskScore(
        likelihood=likelihood,
        impact=impact,
        score=score,
        priority=_priority_from_score(score),  # type: ignore[arg-type]
        rationale="Rule-based baseline.",
    )


def attach_risk(req: Requirement, llm: _LLMLike) -> Requirement:
    """先用规则打分,再把 LLM 生成的 rationale 合并进去;LLM 失败则算法兜底。"""
    rs = compute_risk_rule_based(req)
    try:
        rationale = llm.structured_call(
            "score_risk",
            {
                "raw_text": req.raw_text,
                "likelihood": rs.likelihood,
                "impact": rs.impact,
                "score": rs.score,
                "priority": rs.priority,
            },
            _Rationale,
        )
        rs = rs.model_copy(update={"rationale": rationale.rationale})
    except Exception:
        rs = rs.model_copy(update={"rationale": f"{rs.rationale} (LLM unavailable; used rule-based only.)"})
    return req.model_copy(update={"risk": rs})
