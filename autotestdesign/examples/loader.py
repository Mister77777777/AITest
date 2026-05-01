from __future__ import annotations
from pathlib import Path
from autotestdesign.core.models import Requirement
from autotestdesign.core.parsing import parse_csv, parse_text_block

_EXAMPLES_DIR = Path(__file__).parent
# 内置示例注册表:名称 -> (文件, 类型)
_EXAMPLES: dict[str, tuple[str, str]] = {
    "banking_registration": ("banking_registration.csv", "csv"),
    "shopping_cart": ("shopping_cart.md", "text"),
}


def list_examples() -> list[str]:
    """返回所有可用的内置示例名(字母序)。"""
    return sorted(_EXAMPLES.keys())


def load_example(name: str) -> list[Requirement]:
    """根据名称加载内置示例,返回 Requirement 列表。"""
    if name not in _EXAMPLES:
        raise KeyError(f"Unknown example: {name}")
    filename, kind = _EXAMPLES[name]
    path = _EXAMPLES_DIR / filename
    if kind == "csv":
        return parse_csv(path)
    return parse_text_block(path.read_text())
