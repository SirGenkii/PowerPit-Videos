"""Minimal YAML loader supporting the subset needed for Power Pit configs."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:  # pragma: no cover - executed when PyYAML is available
    import yaml  # type: ignore
except Exception:  # pragma: no cover - fallback when PyYAML missing
    yaml = None  # type: ignore


def safe_load(text: str) -> Any:
    """Load YAML text using PyYAML if available, otherwise a tiny parser."""

    if yaml is not None:  # pragma: no branch - simple delegation
        return yaml.safe_load(text)

    return _SimpleYAMLParser(text).parse()


@dataclass
class _Line:
    raw: str
    number: int

    @property
    def indent(self) -> int:
        return len(self.raw) - len(self.raw.lstrip(" "))

    @property
    def stripped(self) -> str:
        return self.raw.strip()


class _SimpleYAMLParser:
    """Extremely small YAML parser for mappings and lists."""

    def __init__(self, text: str) -> None:
        self.lines = [
            _Line(raw=line.rstrip("\n"), number=i + 1)
            for i, line in enumerate(text.splitlines())
            if line.strip() and not line.lstrip().startswith("#")
        ]
        self.index = 0

    def parse(self) -> Any:
        if not self.lines:
            return {}
        return self._parse_block(expected_indent=0)

    def _parse_block(self, expected_indent: int) -> Any:
        if self._current_line().stripped.startswith("- "):
            return self._parse_list(expected_indent)
        return self._parse_mapping(expected_indent)

    def _parse_list(self, expected_indent: int) -> list[Any]:
        result: list[Any] = []
        while self.index < len(self.lines):
            line = self._current_line()
            if line.indent != expected_indent or not line.stripped.startswith("- "):
                break
            value_str = line.stripped[2:].strip()
            self.index += 1
            if value_str:
                if ":" in value_str:
                    inline = " " * (expected_indent + 2) + value_str
                    self.lines.insert(self.index, _Line(raw=inline, number=line.number))
                    result.append(self._parse_block(expected_indent + 2))
                else:
                    result.append(_parse_scalar(value_str))
            else:
                result.append(self._parse_block(expected_indent + 2))
        return result

    def _parse_mapping(self, expected_indent: int) -> dict[str, Any]:
        result: dict[str, Any] = {}
        while self.index < len(self.lines):
            line = self._current_line()
            if line.indent < expected_indent:
                break
            if line.indent > expected_indent:
                raise ValueError(f"Indentation invalide ligne {line.number}: {line.raw}")
            key, sep, remainder = line.stripped.partition(":")
            if not sep:
                raise ValueError(f"Ligne {line.number}: clé YAML manquante")
            key = key.strip()
            value_str = remainder.strip()
            self.index += 1
            if value_str:
                result[key] = _parse_scalar(value_str)
            else:
                result[key] = self._parse_block(expected_indent + 2)
        return result

    def _current_line(self) -> _Line:
        return self.lines[self.index]


def _parse_scalar(value: str) -> Any:
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]

    lowered = value.lower()
    if lowered in {"true", "yes"}:
        return True
    if lowered in {"false", "no"}:
        return False
    if lowered in {"null", "none", "~"}:
        return None

    # Remove inline comments for scalars without quotes
    if " #" in value:
        value = value.split(" #", 1)[0].strip()

    # Try integer then float
    try:
        if value.startswith("0") and value != "0" and not value.startswith("0."):
            raise ValueError
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        return value
