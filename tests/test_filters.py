"""Tests for custom Jinja2 filters."""

import pytest

from mdcomp.filters import (
    date_format,
    from_json,
    from_yaml,
    headers,
    pipe,
    shift_headers,
    slugify,
    to_json,
    to_yaml,
)


class TestFromJson:
    def test_parse_object(self):
        result = from_json('{"name": "test", "value": 42}')
        assert result == {"name": "test", "value": 42}

    def test_parse_array(self):
        result = from_json("[1, 2, 3]")
        assert result == [1, 2, 3]

    def test_empty_string_returns_none(self):
        assert from_json("") is None

    def test_whitespace_only_returns_none(self):
        assert from_json("   ") is None
        assert from_json("\n\t") is None


class TestFromYaml:
    def test_parse_object(self):
        result = from_yaml("name: test\nvalue: 42")
        assert result == {"name": "test", "value": 42}

    def test_parse_list(self):
        result = from_yaml("- one\n- two\n- three")
        assert result == ["one", "two", "three"]

    def test_empty_string_returns_none(self):
        assert from_yaml("") is None

    def test_whitespace_only_returns_none(self):
        assert from_yaml("   ") is None


class TestToJson:
    def test_serialize_dict(self):
        result = to_json({"name": "test"})
        assert result == '{"name": "test"}'

    def test_serialize_with_indent(self):
        result = to_json({"name": "test"}, indent=2)
        assert '"name": "test"' in result


class TestToYaml:
    def test_serialize_dict(self):
        result = to_yaml({"name": "test"})
        assert "name: test" in result


class TestSlugify:
    def test_simple(self):
        assert slugify("Hello World") == "hello-world"

    def test_special_chars(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_multiple_spaces(self):
        assert slugify("Hello   World") == "hello-world"

    def test_integer_input(self):
        assert slugify(12345) == "12345"

    def test_float_input(self):
        assert slugify(3.14) == "314"

    def test_none_input(self):
        assert slugify(None) == "none"

    def test_list_input(self):
        # List gets converted to string representation
        result = slugify([1, 2, 3])
        assert "1" in result and "2" in result and "3" in result


class TestDateFormat:
    def test_format_iso_date(self):
        result = date_format("2024-01-15", "%d/%m/%Y")
        assert result == "15/01/2024"

    def test_default_format(self):
        result = date_format("2024-01-15")
        assert result == "2024-01-15"


class TestShiftHeaders:
    def test_shift_up(self):
        md = "# Title\n\n## Section\n"
        result = shift_headers(md, 2)
        assert "### Title" in result
        assert "#### Section" in result

    def test_shift_down(self):
        md = "### Title\n\n#### Section\n"
        result = shift_headers(md, -1)
        assert "## Title" in result
        assert "### Section" in result

    def test_no_shift(self):
        md = "# Title\n\nSome text.\n"
        result = shift_headers(md, 0)
        assert "# Title" in result

    def test_clamp_max(self):
        md = "##### Deep Header\n"
        result = shift_headers(md, 3)
        # Should clamp at h6
        assert "######" in result
        assert "#######" not in result

    def test_clamp_min(self):
        md = "## Header\n"
        result = shift_headers(md, -5)
        # Should clamp at h1
        assert result.strip().startswith("# ")

    def test_preserves_content(self):
        md = "# Title\n\nParagraph text.\n\n- List item\n- Another item\n"
        result = shift_headers(md, 1)
        assert "## Title" in result
        assert "Paragraph text." in result
        assert "- List item" in result


class TestHeaders:
    def test_extract_headers(self):
        md = "# Title\n\n## Section 1\n\n### Subsection\n\n## Section 2\n"
        result = headers(md)
        assert result == [
            {"level": 1, "title": "Title"},
            {"level": 2, "title": "Section 1"},
            {"level": 3, "title": "Subsection"},
            {"level": 2, "title": "Section 2"},
        ]

    def test_min_level(self):
        md = "# Title\n\n## Section\n\n### Subsection\n"
        result = headers(md, min_level=2)
        assert result == [
            {"level": 2, "title": "Section"},
            {"level": 3, "title": "Subsection"},
        ]

    def test_max_level(self):
        md = "# Title\n\n## Section\n\n### Subsection\n"
        result = headers(md, max_level=2)
        assert result == [
            {"level": 1, "title": "Title"},
            {"level": 2, "title": "Section"},
        ]

    def test_level_range(self):
        md = "# Title\n\n## Section\n\n### Subsection\n\n#### Deep\n"
        result = headers(md, min_level=2, max_level=3)
        assert result == [
            {"level": 2, "title": "Section"},
            {"level": 3, "title": "Subsection"},
        ]

    def test_empty_content(self):
        result = headers("")
        assert result == []

    def test_no_headers(self):
        md = "Just some text.\n\nMore text.\n"
        result = headers(md)
        assert result == []

    def test_header_with_formatting(self):
        md = "## Section with **bold** and *italic*\n"
        result = headers(md)
        assert result == [{"level": 2, "title": "Section with bold and italic"}]


class TestPipe:
    def test_simple_command(self):
        result = pipe("hello world", "tr a-z A-Z")
        assert result.strip() == "HELLO WORLD"

    def test_multiline_input(self):
        result = pipe("banana\napple\ncherry", "sort")
        assert result.strip() == "apple\nbanana\ncherry"

    def test_pipeline(self):
        result = pipe("hello\nhello\nworld", "sort | uniq")
        assert result.strip() == "hello\nworld"

    def test_command_failure_raises(self):
        from mdcomp.errors import ShellError

        with pytest.raises(ShellError, match="Pipe command failed"):
            pipe("test", "exit 1")
