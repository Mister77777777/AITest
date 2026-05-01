from __future__ import annotations
from typing import Any
from pydantic import BaseModel


class FakeLLM:
    """确定性的内存 LLM 替身,供单元测试使用。

    用法:先通过 queue() 预注册某个 prompt 的响应,再将此替身注入 LLMClient 的位置。
    """

    def __init__(self, responses: dict[str, list[dict[str, Any]]] | None = None) -> None:
        self.responses = responses or {}
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def queue(self, prompt_name: str, payload: dict[str, Any]) -> None:
        self.responses.setdefault(prompt_name, []).append(payload)

    def structured_call(self, prompt_name: str, variables: dict[str, Any], schema: type[BaseModel]) -> BaseModel:
        self.calls.append((prompt_name, variables))
        queue = self.responses.get(prompt_name)
        if not queue:
            raise AssertionError(f"FakeLLM has no response queued for prompt '{prompt_name}'")
        payload = queue.pop(0)
        return schema.model_validate(payload)
