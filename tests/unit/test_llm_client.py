import pytest
from pydantic import BaseModel
from autotestdesign.config import Config
from autotestdesign.llm.client import LLMClient, LLMOutputError


class _Demo(BaseModel):
    name: str
    score: int


class _StubCompletion:
    def __init__(self, content: str) -> None:
        self.choices = [type("C", (), {"message": type("M", (), {"content": content})()})()]


class _StubOpenAI:
    def __init__(self, contents: list[str]) -> None:
        self._contents = contents
        self.chat = type("Chat", (), {"completions": self})()
        self.calls = 0

    def create(self, **kwargs):
        content = self._contents[self.calls]
        self.calls += 1
        return _StubCompletion(content)


def _make_client(stub: _StubOpenAI, tmp_path) -> LLMClient:
    prompt = tmp_path / "p.md"
    prompt.write_text("Hello {{ who }}. Return JSON.")
    cfg = Config(base_url="x", api_key="y", model="m", max_retries=3)
    c = LLMClient(cfg, prompt_dir=tmp_path, openai_client=stub)
    return c


def test_structured_call_parses_valid_json(tmp_path):
    stub = _StubOpenAI(['{"name": "a", "score": 1}'])
    client = _make_client(stub, tmp_path)
    out = client.structured_call("p", {"who": "world"}, _Demo)
    assert out.name == "a" and out.score == 1
    assert stub.calls == 1


def test_structured_call_retries_on_bad_json(tmp_path):
    stub = _StubOpenAI(["not json", '{"name": "b", "score": 2}'])
    client = _make_client(stub, tmp_path)
    out = client.structured_call("p", {"who": "x"}, _Demo)
    assert out.score == 2
    assert stub.calls == 2


def test_structured_call_raises_after_max_retries(tmp_path):
    stub = _StubOpenAI(["bad", "still bad", "nope"])
    client = _make_client(stub, tmp_path)
    with pytest.raises(LLMOutputError):
        client.structured_call("p", {"who": "x"}, _Demo)
