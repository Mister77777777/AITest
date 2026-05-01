from __future__ import annotations
import json
from pathlib import Path
from pydantic import BaseModel, Field

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / ".env" / "config.json"


class Config(BaseModel):
    base_url: str
    api_key: str
    model: str = "gpt-4o-mini"
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_retries: int = 3


def load_config(path: Path | None = None) -> Config:
    path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    raw = json.loads(path.read_text())
    normalized = {
        "base_url": raw.get("base_url") or raw.get("ANTHROPIC_BASE_URL") or raw.get("OPENAI_BASE_URL", ""),
        "api_key": raw.get("api_key") or raw.get("ANTHROPIC_AUTH_TOKEN") or raw.get("OPENAI_API_KEY", ""),
        "model": raw.get("model", "gpt-4o-mini"),
        "temperature": raw.get("temperature", 0.2),
        "max_retries": raw.get("max_retries", 3),
    }
    return Config(**normalized)
