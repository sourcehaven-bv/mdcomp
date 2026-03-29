"""Tests for template rendering."""

import warnings
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

        from mdcomp.errors import UndefinedVariableError

        # Create a simple template with undefined variable
        template_path = templates_dir / "strict_test.md.j2"
        template_path.write_text("Hello {{ undefined_var }}!")

        with pytest.raises(UndefinedVariableError):
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
        template_path.write_text('---\ncontent_base: ../snippets\n---\n{{ content("header.md") }}')

        result = render_template(template_path, {})
        assert "Acme Corporation" in result

    def test_content_base_cli_overrides_frontmatter(self, templates_dir: Path, snippets_dir: Path):
        """CLI content_base should override frontmatter content_base."""
        # Create a template with wrong content_base in frontmatter
        template_path = templates_dir / "cli_override_test.md.j2"
        template_path.write_text('---\ncontent_base: /nonexistent\n---\n{{ content("header.md") }}')

        # CLI parameter should override frontmatter
        result = render_template(template_path, {}, content_base=snippets_dir)
        assert "Acme Corporation" in result

    def test_base_parameter_in_content_function(self, templates_dir: Path, snippets_dir: Path):
        """The base= parameter in content functions should override all defaults."""
        template_path = templates_dir / "base_param_test.md.j2"
        template_path.write_text(f'{{{{ content("header.md", base="{snippets_dir}") }}}}')

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
        template_path.write_text('{{ content("../snippets/header.md", base=template_dir) }}')

        result = render_template(template_path, {})
        assert "Acme Corporation" in result


class TestMarkdownAnchors:
    """Test that markdown anchor syntax {#id} works without escaping."""

    def test_markdown_anchor_in_heading(self):
        """Markdown anchors like {#my-id} should work without escaping."""
        result = render_string("### Heading {#my-anchor}", {})
        assert result == "### Heading {#my-anchor}"

    def test_markdown_anchor_with_variable(self):
        """Markdown anchors can be combined with variables."""
        result = render_string("### {{ title }} {#{{ id }}}", {"title": "Hello", "id": "hello"})
        assert result == "### Hello {#hello}"

    def test_new_comment_syntax(self):
        """Comments now use {## ##} syntax."""
        result = render_string("{## This is a comment ##}Hello", {})
        assert result == "Hello"

    def test_old_comment_syntax_treated_as_text(self):
        """Old {# #} syntax is now treated as regular text."""
        result = render_string("{# not a comment #}", {})
        assert result == "{# not a comment #}"


class TestSafeFilterWarning:
    """Test that using | safe filter emits a warning."""

    def test_safe_filter_emits_warning(self):
        """Using | safe should emit a warning since autoescape is False."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = render_string("{{ name | safe }}", {"name": "test"})

            assert result == "test"
            assert len(w) == 1
            assert "safe" in str(w[0].message).lower()
            assert "unnecessary" in str(w[0].message).lower()
            # Singular form for 1 usage
            assert "1 usage" in str(w[0].message)
            # Should include line number
            assert "line" in str(w[0].message).lower()

    def test_multiple_safe_filters_single_warning(self):
        """Multiple | safe usages should report count in single warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            render_string("{{ a | safe }} {{ b | safe }} {{ c | safe }}", {"a": 1, "b": 2, "c": 3})

            assert len(w) == 1
            # Plural form for multiple usages
            assert "3 usages" in str(w[0].message)

    def test_no_warning_without_safe_filter(self):
        """No warning should be emitted when | safe is not used."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            render_string("{{ name }}", {"name": "test"})

            assert len(w) == 0

    def test_safe_filter_warning_in_template_file(self, templates_dir: Path):
        """Warning should include template path when rendering a file."""
        template_path = templates_dir / "safe_filter_test.md.j2"
        template_path.write_text("{{ content | safe }}")

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            render_template(template_path, {"content": "hello"})

            assert len(w) == 1
            assert "safe_filter_test" in str(w[0].message)

    def test_safe_filter_warning_in_render_content(self, templates_dir: Path, snippets_dir: Path):
        """Warning should be emitted for | safe in render_content() included files."""
        # Create a snippet with | safe filter
        snippet_path = snippets_dir / "safe_snippet.md"
        snippet_path.write_text("---\ntype: snippet\n---\nHello {{ name | safe }}!")

        # Create a template that uses render_content
        template_path = templates_dir / "render_content_safe_test.md.j2"
        template_path.write_text(f'{{{{ render_content("{snippet_path}") }}}}')

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = render_template(template_path, {"name": "World"})

            assert "Hello World!" in result
            assert len(w) == 1
            assert "safe_snippet" in str(w[0].message)
