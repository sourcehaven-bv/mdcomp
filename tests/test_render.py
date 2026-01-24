"""Tests for template rendering."""

from pathlib import Path

from mdcomp.render import render_string, render_template


class TestRenderString:
    def test_simple_template(self):
        result = render_string("Hello {{ name }}!", {"name": "World"})
        assert result == "Hello World!"

    def test_loop(self):
        result = render_string(
            "{% for i in items %}{{ i }} {% endfor %}",
            {"items": [1, 2, 3]},
        )
        assert result == "1 2 3 "

    def test_conditional(self):
        result = render_string(
            "{% if show %}visible{% endif %}",
            {"show": True},
        )
        assert result == "visible"


class TestRenderTemplate:
    def test_simple_template(self, templates_dir: Path):
        result = render_template(
            templates_dir / "simple.md.j2",
            {"name": "Tester", "project": "mdcomp"},
        )
        assert "Hello Tester" in result
        assert "Welcome to mdcomp" in result

    def test_template_with_defaults(self, templates_dir: Path):
        # Without override - uses default
        result = render_template(templates_dir / "with_defaults.md.j2", {})
        assert "Hello, Default Name!" in result

        # With override
        result = render_template(
            templates_dir / "with_defaults.md.j2",
            {"name": "Override"},
        )
        assert "Hello, Override!" in result

    def test_template_with_include(self, templates_dir: Path):
        result = render_template(
            templates_dir / "with_include.md.j2",
            {"body": "Main content here"},
        )
        assert "Acme Corporation" in result  # From header.md
        assert "Main content here" in result
        assert "info@example.com" in result  # From footer.md


class TestCustomFunctions:
    def test_read_function(self, snippets_dir: Path):
        result = render_string(
            '{{ read("' + str(snippets_dir / "header.md") + '") }}',
            {},
        )
        assert "Acme Corporation" in result

    def test_frontmatter_function(self, snippets_dir: Path):
        result = render_string(
            '{{ frontmatter("' + str(snippets_dir / "item1.md") + '").title }}',
            {},
        )
        assert result == "First Item"

    def test_glob_function(self, snippets_dir: Path):
        result = render_string(
            '{% for f in glob("*.md", "' + str(snippets_dir) + '") %}{{ f.name }} {% endfor %}',
            {},
        )
        assert "item1.md" in result
        assert "item2.md" in result

    def test_shell_function(self):
        result = render_string('{{ shell("echo hello") }}', {})
        assert "hello" in result


class TestCustomFilters:
    def test_from_json_filter(self):
        result = render_string(
            "{% set data = '{\"a\": 1}' | from_json %}{{ data.a }}",
            {},
        )
        assert result == "1"

    def test_slugify_filter(self):
        result = render_string('{{ "Hello World" | slugify }}', {})
        assert result == "hello-world"

    def test_to_json_filter(self):
        result = render_string("{{ items | to_json }}", {"items": [1, 2, 3]})
        assert result == "[1, 2, 3]"


class TestStrictMode:
    def test_strict_mode_raises_on_undefined(self, templates_dir: Path):
        import pytest
        from jinja2 import UndefinedError

        # Create a simple template with undefined variable
        template_path = templates_dir / "strict_test.md.j2"
        template_path.write_text("Hello {{ undefined_var }}!")

        with pytest.raises(UndefinedError):
            render_template(template_path, {}, strict=True)

    def test_non_strict_mode_allows_undefined(self, templates_dir: Path):
        template_path = templates_dir / "strict_test.md.j2"
        template_path.write_text("Hello {{ undefined_var }}!")

        result = render_template(template_path, {}, strict=False)
        assert result == "Hello !"


class TestRenderContent:
    def test_render_content_renders_template(self, templates_dir: Path, snippets_dir: Path):
        # Create a snippet with template variables
        snippet_path = snippets_dir / "template_snippet.md"
        snippet_path.write_text(
            "---\ntype: snippet\n---\nHello {{ name }}! You have {{ count }} messages."
        )

        # Create a template that uses render_content
        template_path = templates_dir / "render_content_test.md.j2"
        template_path.write_text(f'# Main\n{{{{ render_content("{snippet_path}") }}}}')

        result = render_template(template_path, {"name": "Alice", "count": 5})

        assert "Hello Alice!" in result
        assert "You have 5 messages." in result

    def test_content_does_not_render_template(self, templates_dir: Path, snippets_dir: Path):
        # Create a snippet with template variables
        snippet_path = snippets_dir / "raw_snippet.md"
        snippet_path.write_text("---\ntype: snippet\n---\nHello {{ name }}!")

        # Create a template that uses content (not render_content)
        template_path = templates_dir / "content_test.md.j2"
        template_path.write_text(f'# Main\n{{{{ content("{snippet_path}") }}}}')

        result = render_template(template_path, {"name": "Alice"})

        # The {{ name }} should NOT be rendered
        assert "Hello {{ name }}!" in result


class TestPathResolution:
    def test_content_defaults_to_cwd(self, templates_dir: Path, snippets_dir: Path):
        """Content functions should default to resolving paths from cwd."""
        import os

        # Create a template that uses a path relative to cwd
        template_path = templates_dir / "cwd_test.md.j2"
        rel_path = snippets_dir.relative_to(Path.cwd())
        template_path.write_text(f'{{{{ content("{rel_path}/header.md") }}}}')

        result = render_template(template_path, {})
        assert "Acme Corporation" in result

    def test_content_base_parameter(self, templates_dir: Path, snippets_dir: Path):
        """content_base parameter should override the default base."""
        # Create a template that uses paths relative to snippets_dir
        template_path = templates_dir / "content_base_test.md.j2"
        template_path.write_text('{{ content("header.md") }}')

        # Without content_base, this would look in cwd
        result = render_template(template_path, {}, content_base=snippets_dir)
        assert "Acme Corporation" in result

    def test_content_base_frontmatter(self, templates_dir: Path, snippets_dir: Path):
        """content_base in frontmatter should set the base directory."""
        # Create a template with content_base in frontmatter
        template_path = templates_dir / "fm_content_base_test.md.j2"
        template_path.write_text(
            "---\ncontent_base: ../snippets\n---\n{{ content(\"header.md\") }}"
        )

        result = render_template(template_path, {})
        assert "Acme Corporation" in result

    def test_content_base_cli_overrides_frontmatter(
        self, templates_dir: Path, snippets_dir: Path
    ):
        """CLI content_base should override frontmatter content_base."""
        # Create a template with wrong content_base in frontmatter
        template_path = templates_dir / "cli_override_test.md.j2"
        template_path.write_text(
            "---\ncontent_base: /nonexistent\n---\n{{ content(\"header.md\") }}"
        )

        # CLI parameter should override frontmatter
        result = render_template(template_path, {}, content_base=snippets_dir)
        assert "Acme Corporation" in result

    def test_base_parameter_in_content_function(
        self, templates_dir: Path, snippets_dir: Path
    ):
        """The base= parameter in content functions should override all defaults."""
        template_path = templates_dir / "base_param_test.md.j2"
        template_path.write_text(
            f'{{{{ content("header.md", base="{snippets_dir}") }}}}'
        )

        result = render_template(template_path, {})
        assert "Acme Corporation" in result

    def test_template_dir_variable(self, templates_dir: Path):
        """template_dir variable should be available in templates."""
        template_path = templates_dir / "template_dir_test.md.j2"
        template_path.write_text("{{ template_dir }}")

        result = render_template(template_path, {})
        assert str(templates_dir.resolve()) in result

    def test_cwd_variable(self, templates_dir: Path):
        """cwd variable should be available in templates."""
        template_path = templates_dir / "cwd_test2.md.j2"
        template_path.write_text("{{ cwd }}")

        result = render_template(template_path, {})
        assert str(Path.cwd().resolve()) in result

    def test_base_parameter_with_template_dir_variable(
        self, templates_dir: Path, snippets_dir: Path
    ):
        """base=template_dir should resolve paths relative to template directory."""
        # Create a template that uses template_dir as base
        template_path = templates_dir / "template_dir_base_test.md.j2"
        template_path.write_text(
            '{{ content("../snippets/header.md", base=template_dir) }}'
        )

        result = render_template(template_path, {})
        assert "Acme Corporation" in result
