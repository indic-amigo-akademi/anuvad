# tests/core/test_parser.py
"""Unit tests for core.parser."""

import pytest

from core.parser import parse_raw_text, parse_structured_file


class TestParseRawText:
    def test_basic_parsing(self, tmp_path):
        p = tmp_path / "sample.txt"
        p.write_text("First paragraph\n\nSecond paragraph\n\nThird paragraph", encoding="utf-8")
        result = parse_raw_text(str(p))
        assert len(result) == 3
        assert result[0] == (1, "First paragraph")
        assert result[1] == (2, "Second paragraph")
        assert result[2] == (3, "Third paragraph")

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.txt"
        p.write_text("", encoding="utf-8")
        result = parse_raw_text(str(p))
        assert result == []

    def test_single_block(self, tmp_path):
        p = tmp_path / "single.txt"
        p.write_text("Only one block", encoding="utf-8")
        result = parse_raw_text(str(p))
        assert len(result) == 1
        assert result[0] == (1, "Only one block")

    def test_multiple_newlines_collapsed(self, tmp_path):
        p = tmp_path / "multi_nl.txt"
        p.write_text("A\n\n\n\nB", encoding="utf-8")
        result = parse_raw_text(str(p))
        assert len(result) == 2
        assert result[0] == (1, "A")
        assert result[1] == (2, "B")

    def test_leading_trailing_whitespace(self, tmp_path):
        p = tmp_path / "ws.txt"
        p.write_text("  hello  \n\n  world  ", encoding="utf-8")
        result = parse_raw_text(str(p))
        assert result[0] == (1, "hello")
        assert result[1] == (2, "world")


class TestParseStructuredFile:
    def test_basic_parsing(self, tmp_path):
        p = tmp_path / "structured.txt"
        p.write_text("#1\nFirst\n\n#2\nSecond\n\n#3\nThird\n\n", encoding="utf-8")
        result = parse_structured_file(str(p))
        assert len(result) == 3
        assert result[0] == (1, "First")
        assert result[1] == (2, "Second")
        assert result[2] == (3, "Third")

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty_struct.txt"
        p.write_text("", encoding="utf-8")
        result = parse_structured_file(str(p))
        assert result == []

    def test_multiline_segments(self, tmp_path):
        p = tmp_path / "multi_line.txt"
        p.write_text("#1\nLine one\nLine two\n\n#2\nLine three\n\n", encoding="utf-8")
        result = parse_structured_file(str(p))
        assert len(result) == 2
        assert "\n" in result[0][1]
        assert result[1] == (2, "Line three")