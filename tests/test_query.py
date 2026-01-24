"""Tests for file querying by frontmatter."""

from pathlib import Path

from mdcomp.query import Document, glob_files, match_value, query_files


class TestDocument:
    def test_load(self, snippets_dir: Path):
        doc = Document.load(snippets_dir / "item1.md")
        assert doc.meta["title"] == "First Item"
        assert doc.meta["status"] == "published"
        assert "first item content" in doc.content.lower()


class TestMatchValue:
    def test_eq(self):
        assert match_value("test", "test", "eq")
        assert not match_value("test", "other", "eq")

    def test_contains_list(self):
        assert match_value(["a", "b", "c"], "b", "contains")
        assert not match_value(["a", "b", "c"], "d", "contains")

    def test_contains_string(self):
        assert match_value("hello world", "world", "contains")
        assert not match_value("hello world", "foo", "contains")

    def test_startswith(self):
        assert match_value("hello world", "hello", "startswith")
        assert not match_value("hello world", "world", "startswith")

    def test_endswith(self):
        assert match_value("hello world", "world", "endswith")
        assert not match_value("hello world", "hello", "endswith")

    def test_gt_lt(self):
        assert match_value(10, 5, "gt")
        assert not match_value(5, 10, "gt")
        assert match_value(5, 10, "lt")

    def test_none_value(self):
        assert not match_value(None, "test", "eq")


class TestQueryFiles:
    def test_query_by_status(self, snippets_dir: Path):
        docs = query_files(snippets_dir, status="published")
        assert len(docs) == 1
        assert docs[0].meta["title"] == "First Item"

    def test_query_by_tags_contains(self, snippets_dir: Path):
        docs = query_files(snippets_dir, tags__contains="important")
        assert len(docs) == 1
        assert docs[0].meta["title"] == "First Item"

    def test_query_multiple_filters(self, snippets_dir: Path):
        docs = query_files(snippets_dir, status="draft", tags__contains="review")
        assert len(docs) == 1
        assert docs[0].meta["title"] == "Second Item"

    def test_query_no_match(self, snippets_dir: Path):
        docs = query_files(snippets_dir, status="nonexistent")
        assert len(docs) == 0


class TestGlobFiles:
    def test_glob_md_files(self, snippets_dir: Path):
        files = glob_files("*.md", snippets_dir)
        assert len(files) >= 2
        assert all(f.suffix == ".md" for f in files)
