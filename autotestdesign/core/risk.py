from __future__ import annotations
from typing import Any, Protocol
from pydantic import BaseModel
from autotestdesign.core.models import Requirement, RiskScore

# 高影响关键词:触发 impact +2(中英双语,适配中文需求文本)
HIGH_IMPACT_KEYWORDS = {
    # 英文关键词
    "payment", "credit card", "billing", "auth", "login", "password",
    "security", "encrypt", "token", "admin", "permission", "privacy",
    "personal data", "pii", "compliance",
    # 中文关键词
    "支付", "信用卡", "付款", "计费", "账单",
    "认证", "鉴权", "登录", "登陆", "密码", "口令",
    "安全", "加密", "解密", "令牌",
    "管理员", "权限", "授权",
    "隐私", "个人数据", "敏感信息", "合规",
}
# 高可能性关键词:触发 likelihood +2;金融/认证类功能天生被频繁攻击,可能性同样高
HIGH_LIKELIHOOD_KEYWORDS = {
    # 英文关键词
    "concurrent", "real-time", "external api", "network", "integration",
    "migration", "async", "parallel",
    "payment", "credit card", "billing", "auth", "login", "password",
    "security", "encrypt", "token",
    # 中文关键词
    "并发", "并行", "实时", "外部接口", "第三方接口", "网络",
    "集成", "迁移", "异步", "分布式",
    "支付", "信用卡", "付款", "认证", "鉴权", "登录", "密码", "加密", "令牌",
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
    # 英文走 lower(),中文不受大小写影响;用原文兼顾两种匹配
    text_lower = req.raw_text.lower()
    text_raw = req.raw_text
    impact = 2
    likelihood = 2
    for kw in HIGH_IMPACT_KEYWORDS:
        if kw in text_lower or kw in text_raw:
            impact = min(5, impact + 2)
            break
    for kw in HIGH_LIKELIHOOD_KEYWORDS:
        if kw in text_lower or kw in text_raw:
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
        rationale="规则基线评分。",
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
        rs = rs.model_copy(update={"rationale": f"{rs.rationale}(LLM 不可用,已降级为规则基线。)"})
    return req.model_copy(update={"risk": rs})
