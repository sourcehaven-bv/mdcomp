"""Tests for custom exception hierarchy and error handling."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from mdcomp.cli import app
from mdcomp.context import load_context, load_yaml_or_json, parse_var
from mdcomp.errors import (
    ContentNotFoundError,
    ContextError,
    ContextParseError,
    MdcompError,
    ShellError,
    TemplateError,
    TemplateSyntaxError,
    UndefinedVariableError,
)
from mdcomp.filters import pipe
from mdcomp.render import render_string, render_template

runner = CliRunner()


class TestExceptionHierarchy:
    """Verify the exception class hierarchy."""

    def test_all_exceptions_are_mdcomp_errors(self):
        for cls in [
            TemplateError,
            TemplateSyntaxError,
            UndefinedVariableError,
            ContextError,
            ContextParseError,
            ContentNotFoundError,
            ShellError,
        ]:
            assert issubclass(cls, MdcompError)

    def test_template_subclasses(self):
        assert issubclass(TemplateSyntaxError, TemplateError)
        assert issubclass(UndefinedVariableError, TemplateError)

    def test_context_subclasses(self):
        assert issubclass(ContextParseError, ContextError)


class TestTemplateSyntaxErrors:
    def test_bad_jinja2_syntax(self):
        with pytest.raises(TemplateSyntaxError, match="line 1"):
            render_string("{% if %}oops{% endif %}", {})

    def test_unclosed_block(self):
        with pytest.raises(TemplateSyntaxError, match="line 1"):
            render_string("{% for x in items %}", {})

    def test_bad_syntax_on_later_line(self):
        with pytest.raises(TemplateSyntaxError, match="line 3"):
            render_string("line one\nline two\n{% if %}oops{% endif %}", {})

    def test_bad_syntax_in_file(self, tmp_path: Path):
        template = tmp_path / "bad.md.j2"
        template.write_text("{% if %}oops{% endif %}")
        with pytest.raises(TemplateSyntaxError, match="line 1"):
            render_template(template, {})


class TestUndefinedVariableErrors:
    def test_undefined_var_strict(self, tmp_path: Path):
        template = tmp_path / "undef.md.j2"
        template.write_text("Hello {{ missing_var }}!")
        with pytest.raises(UndefinedVariableError, match=r"line 1.*missing_var"):
            render_template(template, {}, strict=True)

    def test_undefined_var_on_later_line(self, tmp_path: Path):
        template = tmp_path / "undef2.md.j2"
        template.write_text("line one\nline two\nHello {{ missing }}!")
        with pytest.raises(UndefinedVariableError, match=r"line 3"):
            render_template(template, {}, strict=True)

    def test_non_strict_allows_undefined(self, tmp_path: Path):
        template = tmp_path / "ok.md.j2"
        template.write_text("Hello {{ missing }}!")
        result = render_template(template, {}, strict=False)
        assert result == "Hello !"


class TestContentNotFoundErrors:
    def test_read_nonexistent_file(self):
        with pytest.raises(ContentNotFoundError, match="not found"):
            render_string("{{ read('does_not_exist.txt') }}", {})

    def test_content_nonexistent_file(self):
        with pytest.raises(ContentNotFoundError, match="not found"):
            render_string("{{ content('does_not_exist.md') }}", {})

    def test_frontmatter_nonexistent_file(self):
        with pytest.raises(ContentNotFoundError, match="not found"):
            render_string("{{ frontmatter('does_not_exist.md') }}", {})

    def test_error_message_includes_path(self):
        with pytest.raises(ContentNotFoundError, match=r"does_not_exist\.txt"):
            render_string("{{ read('does_not_exist.txt') }}", {})

    def test_error_includes_line_number(self):
        with pytest.raises(ContentNotFoundError, match=r"line 3"):
            render_string(
                "line one\nline two\n{{ read('does_not_exist.txt') }}", {}
            )


class TestShellErrors:
    def test_shell_command_failure(self):
        with pytest.raises(ShellError, match="Shell command failed"):
            render_string("{{ shell('exit 1') }}", {})

    def test_pipe_command_failure(self):
        with pytest.raises(ShellError, match="Pipe command failed"):
            pipe("input", "exit 1")

    def test_shell_error_includes_command(self):
        with pytest.raises(ShellError, match="exit 42"):
            render_string("{{ shell('exit 42') }}", {})

    def test_shell_error_includes_line_number(self):
        with pytest.raises(ShellError, match=r"line 2"):
            render_string("line one\n{{ shell('exit 1') }}", {})


class TestContextErrors:
    def test_invalid_var_format(self):
        with pytest.raises(ContextError, match="Expected key=value"):
            parse_var("no_equals_sign")

    def test_invalid_json_file(self, tmp_path: Path):
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{not valid json")
        with pytest.raises(ContextParseError, match="Invalid JSON"):
            load_yaml_or_json(bad_json)

    def test_invalid_yaml_file(self, tmp_path: Path):
        bad_yaml = tmp_path / "bad.yaml"
        bad_yaml.write_text(":\n  - :\n    unbalanced: [brackets")
        with pytest.raises(ContextParseError, match="Invalid YAML"):
            load_yaml_or_json(bad_yaml)

    def test_nonexistent_context_file(self, tmp_path: Path):
        with pytest.raises(ContextParseError, match="not found"):
            load_yaml_or_json(tmp_path / "missing.yaml")

    def test_invalid_var_in_load_context(self):
        with pytest.raises(ContextError):
            load_context(var_overrides=["bad_format"])


class TestCLIErrorOutput:
    def test_render_error_shows_friendly_message(self, tmp_path: Path):
        template = tmp_path / "bad.md.j2"
        template.write_text("{{ read('nonexistent.txt') }}")
        result = runner.invoke(app, ["render", str(template)])
        assert result.exit_code == 1
        output = result.stderr or result.stdout
        assert "Error" in output
        assert "nonexistent.txt" in output
        # Should NOT contain Python traceback markers
        assert "Traceback (most recent call last)" not in output

    def test_render_error_verbose_shows_traceback(self, tmp_path: Path):
        template = tmp_path / "bad.md.j2"
        template.write_text("{{ read('nonexistent.txt') }}")
        result = runner.invoke(app, ["--verbose", "render", str(template)])
        assert result.exit_code == 1
        output = result.stderr or result.stdout
        assert "Error" in output
        assert "Traceback" in output

    def test_syntax_error_message(self, tmp_path: Path):
        template = tmp_path / "bad.md.j2"
        template.write_text("{% if %}oops{% endif %}")
        result = runner.invoke(app, ["render", str(template)])
        assert result.exit_code == 1
        output = result.stderr or result.stdout
        assert "Error" in output
        assert "line 1" in output
        assert "Traceback (most recent call last)" not in output

    def test_meta_error_friendly(self, tmp_path: Path):
        result = runner.invoke(app, ["meta", str(tmp_path / "missing.md")])
        assert result.exit_code == 1
        output = result.stderr or result.stdout
        assert "not found" in output.lower()
