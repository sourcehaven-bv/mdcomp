"""Tests for context loading and variable layering."""

from pathlib import Path

import pytest

from mdcomp.context import load_context, load_yaml_or_json, parse_var


class TestParseVar:
    def test_simple_var(self):
        key, value = parse_var("name=John")
        assert key == "name"
        assert value == "John"

    def test_var_with_equals_in_value(self):
        key, value = parse_var("expr=a=b")
        assert key == "expr"
        assert value == "a=b"

    def test_invalid_var(self):
        with pytest.raises(ValueError):
            parse_var("invalid")


class TestLoadYamlOrJson:
    def test_load_yaml(self, tmp_path: Path):
        yaml_file = tmp_path / "test.yaml"
        yaml_file.write_text("name: test\nvalue: 42")
        result = load_yaml_or_json(yaml_file)
        assert result == {"name": "test", "value": 42}

    def test_load_json(self, tmp_path: Path):
        json_file = tmp_path / "test.json"
        json_file.write_text('{"name": "test", "value": 42}')
        result = load_yaml_or_json(json_file)
        assert result == {"name": "test", "value": 42}


class TestLoadContext:
    def test_from_file(self, context_file: Path):
        ctx = load_context(context_file=context_file)
        assert ctx["name"] == "Test User"
        assert ctx["project"] == "mdcomp"

    def test_var_overrides(self, context_file: Path):
        ctx = load_context(
            context_file=context_file,
            var_overrides=["name=Override"],
        )
        assert ctx["name"] == "Override"

    def test_env_vars(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("MDCOMP_VAR_test_var", "from_env")
        ctx = load_context()
        assert ctx["test_var"] == "from_env"

    def test_env_json_value(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("MDCOMP_VAR_items", "[1, 2, 3]")
        ctx = load_context()
        assert ctx["items"] == [1, 2, 3]

    def test_layering_priority(self, context_file: Path, monkeypatch: pytest.MonkeyPatch):
        # Env var has lowest priority
        monkeypatch.setenv("MDCOMP_VAR_name", "from_env")
        # File overrides env
        # CLI var overrides file
        ctx = load_context(
            context_file=context_file,
            var_overrides=["name=from_cli"],
        )
        assert ctx["name"] == "from_cli"
