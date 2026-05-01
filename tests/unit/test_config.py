import json
from pathlib import Path
import pytest
from autotestdesign.config import load_config, Config


def test_load_config_reads_json(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "base_url": "https://api.example.com/v1",
        "api_key": "sk-test",
        "model": "gpt-4o-mini",
    }))
    cfg = load_config(cfg_file)
    assert isinstance(cfg, Config)
    assert cfg.base_url == "https://api.example.com/v1"
    assert cfg.api_key == "sk-test"
    assert cfg.model == "gpt-4o-mini"
    assert cfg.temperature == 0.2


def test_load_config_supports_legacy_anthropic_keys(tmp_path: Path):
    cfg_file = tmp_path / "config.json"
    cfg_file.write_text(json.dumps({
        "ANTHROPIC_BASE_URL": "https://hub.fishriceai.com",
        "ANTHROPIC_AUTH_TOKEN": "token-abc",
    }))
    cfg = load_config(cfg_file)
    assert cfg.base_url == "https://hub.fishriceai.com"
    assert cfg.api_key == "token-abc"


def test_load_config_missing_file_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        load_config(tmp_path / "missing.json")
