"""Tests for the CLI interface."""

import subprocess
import sys
from pathlib import Path

from typer.testing import CliRunner

from mdcomp import __version__
from mdcomp.cli import app

runner = CliRunner()


class TestMainModule:
    def test_python_m_mdcomp(self):
        """Test running as python -m mdcomp."""
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "mdcomp", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        assert f"mdcomp {__version__}" in result.stdout


class TestVersionFlag:
    def test_version_long(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert f"mdcomp {__version__}" in result.stdout

    def test_version_short(self):
        result = runner.invoke(app, ["-V"])
        assert result.exit_code == 0
        assert f"mdcomp {__version__}" in result.stdout


class TestRenderCommand:
    def test_render_simple(self, templates_dir: Path):
        result = runner.invoke(
            app,
            [
                "render",
                str(templates_dir / "simple.md.j2"),
                "--var",
                "name=Test",
                "--var",
                "project=CLI",
            ],
        )
        assert result.exit_code == 0
        assert "Hello Test" in result.stdout
        assert "Welcome to CLI" in result.stdout

    def test_render_with_context_file(self, templates_dir: Path, context_file: Path):
        result = runner.invoke(
            app,
            ["render", str(templates_dir / "simple.md.j2"), "-c", str(context_file)],
        )
        assert result.exit_code == 0
        assert "Hello Test User" in result.stdout

    def test_render_with_output_file(self, templates_dir: Path, tmp_path: Path):
        output_file = tmp_path / "output.md"
        result = runner.invoke(
            app,
            [
                "render",
                str(templates_dir / "simple.md.j2"),
                "--var",
                "name=Test",
                "--var",
                "project=CLI",
                "-o",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        assert "Hello Test" in output_file.read_text()

    def test_render_nonexistent_template(self):
        result = runner.invoke(app, ["render", "nonexistent.md.j2"])
        assert result.exit_code == 1
        output = (result.stderr or result.stdout).lower()
        assert "not found" in output

    def test_render_error_strict_mode(self, tmp_path: Path):
        """Test that render errors in strict mode exit with code 1."""
        # Create a template that will fail
        bad_template = tmp_path / "bad.md.j2"
        bad_template.write_text("{{ read('nonexistent_file.txt') }}")
        result = runner.invoke(
            app,
            ["render", str(bad_template), "--strict"],
        )
        assert result.exit_code == 1
        assert "Error" in (result.stderr or result.stdout)

    def test_render_error_no_strict_mode(self, tmp_path: Path):
        """Test that render errors without strict mode exit cleanly."""
        # Create a template that will fail
        bad_template = tmp_path / "bad.md.j2"
        bad_template.write_text("{{ read('nonexistent_file.txt') }}")
        result = runner.invoke(
            app,
            ["render", str(bad_template)],
        )
        assert result.exit_code == 1
        assert "Error" in (result.stderr or result.stdout)


class TestListCommand:
    def test_list_table(self, snippets_dir: Path):
        result = runner.invoke(app, ["list", str(snippets_dir)])
        assert result.exit_code == 0
        # Should show file names in table
        assert "item1.md" in result.stdout or "First Item" in result.stdout

    def test_list_json(self, snippets_dir: Path):
        result = runner.invoke(app, ["list", str(snippets_dir), "--format", "json"])
        assert result.exit_code == 0
        assert '"path"' in result.stdout
        assert '"meta"' in result.stdout

    def test_list_yaml(self, snippets_dir: Path):
        result = runner.invoke(app, ["list", str(snippets_dir), "--format", "yaml"])
        assert result.exit_code == 0
        assert "path:" in result.stdout
        assert "meta:" in result.stdout

    def test_list_with_filter(self, snippets_dir: Path):
        result = runner.invoke(
            app,
            ["list", str(snippets_dir), "--filter", "status=published", "--format", "json"],
        )
        assert result.exit_code == 0
        assert "First Item" in result.stdout
        assert "Second Item" not in result.stdout

    def test_list_with_sort(self, snippets_dir: Path):
        result = runner.invoke(
            app,
            ["list", str(snippets_dir), "--sort", "title", "--format", "json"],
        )
        assert result.exit_code == 0

    def test_list_with_sort_reverse(self, snippets_dir: Path):
        result = runner.invoke(
            app,
            ["list", str(snippets_dir), "--sort", "title", "--reverse", "--format", "json"],
        )
        assert result.exit_code == 0

    def test_list_reverse_without_sort(self, snippets_dir: Path):
        result = runner.invoke(
            app,
            ["list", str(snippets_dir), "--reverse", "--format", "json"],
        )
        assert result.exit_code == 0

    def test_list_empty_directory(self, tmp_path: Path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        result = runner.invoke(app, ["list", str(empty_dir)])
        assert result.exit_code == 0
        assert "No matching files" in result.stdout

    def test_list_nonexistent_directory(self):
        result = runner.invoke(app, ["list", "nonexistent_dir"])
        assert result.exit_code == 1
        output = (result.stderr or result.stdout).lower()
        assert "not found" in output


class TestMetaCommand:
    def test_meta_yaml(self, snippets_dir: Path):
        result = runner.invoke(app, ["meta", str(snippets_dir / "item1.md")])
        assert result.exit_code == 0
        assert "title: First Item" in result.stdout

    def test_meta_json(self, snippets_dir: Path):
        result = runner.invoke(
            app,
            ["meta", str(snippets_dir / "item1.md"), "--format", "json"],
        )
        assert result.exit_code == 0
        assert '"title"' in result.stdout
        assert "First Item" in result.stdout

    def test_meta_nonexistent_file(self):
        result = runner.invoke(app, ["meta", "nonexistent.md"])
        assert result.exit_code == 1


class TestWatchCommand:
    def test_watch_requires_output(self, templates_dir: Path):
        """Watch mode requires --output flag."""
        result = runner.invoke(
            app,
            ["watch", str(templates_dir / "simple.md.j2"), "--var", "name=Test"],
        )
        assert result.exit_code == 1
        output = result.stderr or result.stdout
        assert "--output" in output and "required" in output

    def test_watch_nonexistent_template(self, tmp_path: Path):
        result = runner.invoke(
            app,
            ["watch", "nonexistent.md.j2", "-o", str(tmp_path / "out.md")],
        )
        assert result.exit_code == 1
        output = (result.stderr or result.stdout).lower()
        assert "not found" in output

    def test_watch_initial_render(self, tmp_path: Path):
        """Watch performs initial render before starting to watch."""
        from unittest.mock import patch

        template = tmp_path / "test.md.j2"
        template.write_text("# {{ title }}")
        output = tmp_path / "output.md"
        context = tmp_path / "ctx.yaml"
        context.write_text("title: Test Title")

        # Mock watchfiles.watch to immediately raise KeyboardInterrupt
        with patch("watchfiles.watch") as mock_watch:
            mock_watch.side_effect = KeyboardInterrupt()
            result = runner.invoke(
                app,
                [
                    "watch",
                    str(template),
                    "-c",
                    str(context),
                    "-o",
                    str(output),
                ],
            )

        # Exit code 0 for KeyboardInterrupt (normal exit)
        assert result.exit_code == 0
        # Output file should exist from initial render
        assert output.exists()
        assert "# Test Title" in output.read_text()

    def test_watch_with_var_overrides(self, tmp_path: Path):
        """Watch respects --var overrides."""
        from unittest.mock import patch

        template = tmp_path / "test.md.j2"
        template.write_text("# {{ title }}")
        output = tmp_path / "output.md"

        with patch("watchfiles.watch") as mock_watch:
            mock_watch.side_effect = KeyboardInterrupt()
            result = runner.invoke(
                app,
                [
                    "watch",
                    str(template),
                    "--var",
                    "title=Override Title",
                    "-o",
                    str(output),
                ],
            )

        assert result.exit_code == 0
        assert output.exists()
        assert "# Override Title" in output.read_text()

    def test_watch_missing_watchfiles(self, tmp_path: Path, monkeypatch):
        """Watch gives helpful error when watchfiles not installed."""
        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "watchfiles":
                raise ImportError("No module named 'watchfiles'")
            return original_import(name, *args, **kwargs)

        template = tmp_path / "test.md.j2"
        template.write_text("# Test")
        output = tmp_path / "output.md"

        monkeypatch.setattr(builtins, "__import__", mock_import)

        result = runner.invoke(
            app,
            ["watch", str(template), "-o", str(output)],
        )

        assert result.exit_code == 1
        output_text = result.stderr or result.stdout
        assert "watchfiles" in output_text
        assert "pip install" in output_text
