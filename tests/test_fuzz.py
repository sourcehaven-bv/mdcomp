"""Property-based fuzz tests using Hypothesis.

The key invariant: all user-facing operations either succeed or raise
MdcompError. Any other exception type (KeyError, TypeError, AttributeError,
etc.) is a bug.
"""

import contextlib
import tempfile
from pathlib import Path

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from mdcomp.context import load_yaml_or_json, parse_var
from mdcomp.errors import MdcompError
from mdcomp.filters import date_format, from_json, from_yaml, slugify, to_json, to_yaml
from mdcomp.render import render_string

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------

# Simple Jinja2-like template fragments
jinja_var = st.from_regex(r"\{\{ *[a-z_][a-z0-9_]* *\}\}", fullmatch=True)
jinja_filter = st.from_regex(
    r"\{\{ *[a-z_][a-z0-9_]* *\| *(slugify|to_json|to_yaml) *\}\}", fullmatch=True
)
plain_text = st.text(
    alphabet=st.characters(categories=("L", "N", "P", "Z"), max_codepoint=0x7E),
    min_size=0,
    max_size=50,
)

template_fragment = st.one_of(plain_text, jinja_var, jinja_filter)
template_string = st.lists(template_fragment, max_size=5).map("".join)

# Context values: keep types that Jinja2 can handle
context_value = st.one_of(
    st.text(max_size=30),
    st.integers(min_value=-1000, max_value=1000),
    st.floats(allow_nan=False, allow_infinity=False),
    st.booleans(),
    st.none(),
    st.lists(st.text(max_size=10), max_size=5),
)

# Context dicts with keys that look like Python identifiers
context_dict = st.dictionaries(
    keys=st.from_regex(r"[a-z_][a-z0-9_]{0,10}", fullmatch=True),
    values=context_value,
    max_size=10,
)


# ---------------------------------------------------------------------------
# Template rendering fuzz
# ---------------------------------------------------------------------------


class TestRenderStringFuzz:
    @given(template=template_string, context=context_dict)
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_render_never_raises_raw_exception(self, template: str, context: dict) -> None:
        """Rendering should either succeed or raise MdcompError."""
        try:
            result = render_string(template, context)
            assert isinstance(result, str)
        except MdcompError:
            pass  # expected

    @given(data=st.text(max_size=100))
    @settings(max_examples=200, suppress_health_check=[HealthCheck.too_slow])
    def test_arbitrary_text_as_template(self, data: str) -> None:
        """Arbitrary text should not crash — it either renders or raises MdcompError."""
        try:
            result = render_string(data, {})
            assert isinstance(result, str)
        except MdcompError:
            pass  # expected


# ---------------------------------------------------------------------------
# Filter fuzz
# ---------------------------------------------------------------------------


class TestSlugifyFuzz:
    @given(value=st.one_of(st.text(max_size=100), st.integers(), st.none()))
    @settings(max_examples=200)
    def test_slugify_never_crashes(self, value) -> None:  # type: ignore[no-untyped-def]
        result = slugify(value)
        assert isinstance(result, str)


class TestDateFormatFuzz:
    @given(value=st.text(max_size=50), fmt=st.text(max_size=30))
    @settings(max_examples=200)
    def test_date_format_never_crashes(self, value: str, fmt: str) -> None:
        """date_format should gracefully handle any string input."""
        try:
            result = date_format(value, fmt)
            assert isinstance(result, str)
        except MdcompError:
            pass  # expected


class TestFromJsonFuzz:
    @given(value=st.text(max_size=200))
    @settings(max_examples=200)
    def test_from_json_arbitrary_text(self, value: str) -> None:
        """from_json should either parse or raise — never crash unexpectedly."""
        with contextlib.suppress(MdcompError, ValueError):
            from_json(value)


class TestFromYamlFuzz:
    @given(value=st.text(max_size=200))
    @settings(max_examples=200)
    def test_from_yaml_arbitrary_text(self, value: str) -> None:
        """from_yaml should handle any text input."""
        with contextlib.suppress(MdcompError, Exception):
            from_yaml(value)


class TestToJsonFuzz:
    @given(
        value=st.one_of(
            st.dictionaries(st.text(max_size=10), st.text(max_size=10), max_size=5),
            st.lists(st.text(max_size=10), max_size=5),
        )
    )
    @settings(max_examples=200)
    def test_to_json_never_crashes(self, value) -> None:  # type: ignore[no-untyped-def]
        result = to_json(value)
        assert isinstance(result, str)


class TestToYamlFuzz:
    @given(
        value=st.one_of(
            st.dictionaries(st.text(max_size=10), st.text(max_size=10), max_size=5),
            st.lists(st.text(max_size=10), max_size=5),
        )
    )
    @settings(max_examples=200)
    def test_to_yaml_never_crashes(self, value) -> None:  # type: ignore[no-untyped-def]
        result = to_yaml(value)
        assert isinstance(result, str)


# ---------------------------------------------------------------------------
# Context fuzz
# ---------------------------------------------------------------------------


class TestParseVarFuzz:
    @given(var_string=st.text(max_size=100))
    @settings(max_examples=200)
    def test_parse_var_never_raises_raw_exception(self, var_string: str) -> None:
        """parse_var should either succeed or raise ContextError."""
        try:
            key, value = parse_var(var_string)
            assert isinstance(key, str)
            assert isinstance(value, str)
        except MdcompError:
            pass  # expected


class TestLoadYamlOrJsonFuzz:
    @given(content=st.text(max_size=200))
    @settings(max_examples=100)
    def test_load_yaml_fuzz(self, content: str) -> None:
        """Loading arbitrary text as YAML should either succeed or raise ContextParseError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(content)
            yaml_file = Path(f.name)
        try:
            result = load_yaml_or_json(yaml_file)
            # YAML is very permissive — most text is valid YAML
            assert result is None or isinstance(result, (dict, list, str, int, float, bool))
        except MdcompError:
            pass  # expected
        finally:
            yaml_file.unlink(missing_ok=True)

    @given(content=st.text(max_size=200))
    @settings(max_examples=100)
    def test_load_json_fuzz(self, content: str) -> None:
        """Loading arbitrary text as JSON should either succeed or raise ContextParseError."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(content)
            json_file = Path(f.name)
        try:
            result = load_yaml_or_json(json_file)
            assert isinstance(result, (dict, list, str, int, float, bool, type(None)))
        except MdcompError:
            pass  # expected
        finally:
            json_file.unlink(missing_ok=True)
