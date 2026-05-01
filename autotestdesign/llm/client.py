from __future__ import annotations
from pathlib import Path
from typing import Any, Protocol
from jinja2 import Template
from pydantic import BaseModel, ValidationError
from autotestdesign.config import Config


class LLMOutputError(RuntimeError):
    """LLM 多次重试后仍然无法返回合法 JSON 时抛出。"""


class _OpenAILike(Protocol):
    chat: Any


DEFAULT_PROMPT_DIR = Path(__file__).parent / "prompts"


class LLMClient:
    """OpenAI 兼容的 LLM 客户端,集中处理 prompt 渲染、JSON 校验与重试。"""

    def __init__(
        self,
        config: Config,
        prompt_dir: Path | None = None,
        openai_client: _OpenAILike | None = None,
    ) -> None:
        self.config = config
        self.prompt_dir = prompt_dir or DEFAULT_PROMPT_DIR
        if openai_client is None:
            # 延迟导入 openai,方便离线测试
            from openai import OpenAI
            openai_client = OpenAI(base_url=config.base_url, api_key=config.api_key)
        self._client = openai_client

    def _render(self, prompt_name: str, variables: dict[str, Any]) -> str:
        path = self.prompt_dir / f"{prompt_name}.md"
        template = Template(path.read_text())
        return template.render(**variables)

    def structured_call(
        self,
        prompt_name: str,
        variables: dict[str, Any],
        schema: type[BaseModel],
    ) -> BaseModel:
        """渲染 prompt 并调 LLM,返回经过 pydantic 校验的结构化对象。"""
        prompt = self._render(prompt_name, variables)
        last_err: Exception | None = None
        for _ in range(self.config.max_retries):
            resp = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=self.config.temperature,
            )
            content = resp.choices[0].message.content
            try:
                return schema.model_validate_json(content)
            except (ValidationError, Exception) as e:
                # 对 schema 校验失败与网络/解析异常一视同仁,重试
                last_err = e
                continue
        raise LLMOutputError(f"Failed to get valid response for '{prompt_name}': {last_err}")
