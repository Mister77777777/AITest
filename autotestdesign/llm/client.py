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
        # 兼容性开关:部分 provider(如 Bedrock 上的 Claude Opus 4.7)不支持某些参数。
        # 首次遭遇 BadRequest 后自动关闭对应开关,随后调用直接不发。
        self._send_temperature = True
        self._send_response_format = True

    def _render(self, prompt_name: str, variables: dict[str, Any]) -> str:
        path = self.prompt_dir / f"{prompt_name}.md"
        template = Template(path.read_text())
        return template.render(**variables)

    def _invoke(self, prompt: str) -> str:
        """实际调用 Chat Completions,按兼容性开关动态组装参数。"""
        kwargs: dict[str, Any] = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
        }
        if self._send_response_format:
            kwargs["response_format"] = {"type": "json_object"}
        if self._send_temperature:
            kwargs["temperature"] = self.config.temperature
        try:
            resp = self._client.chat.completions.create(**kwargs)
        except Exception as e:
            # 识别「参数不被支持」这类 400 错误,关闭对应开关后由外层重试
            msg = str(e).lower()
            if "temperature" in msg and self._send_temperature:
                self._send_temperature = False
                raise
            if "response_format" in msg and self._send_response_format:
                self._send_response_format = False
                raise
            raise
        return resp.choices[0].message.content

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
            try:
                content = self._invoke(prompt)
                # 某些 provider 会返回带 markdown fence 的 JSON,做一次清洗
                content = _strip_json_fence(content)
                return schema.model_validate_json(content)
            except (ValidationError, Exception) as e:
                # 对 schema 校验失败、参数兼容性错误、网络异常统一走重试
                last_err = e
                continue
        raise LLMOutputError(f"Failed to get valid response for '{prompt_name}': {last_err}")


def _strip_json_fence(content: str) -> str:
    """去掉 ```json ... ``` 之类的 markdown 围栏,保留内部 JSON。"""
    s = content.strip()
    if s.startswith("```"):
        # 去首行围栏(可能带 json / JSON / 其他语言标记)
        first_nl = s.find("\n")
        if first_nl != -1:
            s = s[first_nl + 1:]
        if s.endswith("```"):
            s = s[: -3]
    return s.strip()
