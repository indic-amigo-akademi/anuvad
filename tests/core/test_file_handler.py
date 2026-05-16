# tests/core/test_file_handler.py
"""Unit tests for core.file_handler."""

import os

import pytest

from core.file_handler import (
    get_base_filename,
    save_structured_file,
    read_abd_file,
    write_abd_file,
    read_abd_metadata,
    list_projects,
)


class TestGetBaseFilename:
    def test_simple(self):
        assert get_base_filename("/path/to/file.txt") == "file"

    def test_no_extension(self):
        assert get_base_filename("/path/to/file") == "file"

    def test_multiple_dots(self):
        assert get_base_filename("my.file.txt") == "my.file"


class TestWriteAndReadABD:
    def test_roundtrip_with_metadata(self, tmp_path):
        filepath = str(tmp_path / "test.abd")
        metadata = {"name": "book1", "author": "Writer"}
        data = [(1, "First segment"), (2, "Second segment")]

        write_abd_file(filepath, metadata, data)
        read_meta, read_data = read_abd_file(filepath)

        assert read_meta["name"] == "book1"
        assert read_meta["author"] == "Writer"
        assert read_data == data

    def test_roundtrip_no_metadata(self, tmp_path):
        filepath = str(tmp_path / "minimal.abd")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("#1\nHello world\n\n#2\nGoodbye world\n\n")
        metadata, data = read_abd_file(filepath)
        assert metadata == {}
        assert len(data) == 2


class TestSaveStructuredFile:
    def test_save_creates_file(self, tmp_path):
        data = [(1, "Hello"), (2, "World")]
        out = save_structured_file("testbook", "en", data, {}, output_dir=str(tmp_path))
        assert os.path.exists(out)
        read_meta, read_data = read_abd_file(out)
        assert read_data == data


class TestReadABDMetadata:
    def test_metadata_reading(self, tmp_path):
        p = tmp_path / "meta.abd"
        p.write_text(
            "# --- ANUVAD METADATA ---\n"
            "name: mybook\n"
            "author: John Doe\n"
            "source_language: en\n"
            "language: bn\n"
            "# --- END METADATA ---\n\n"
            "#1\nSome text\n\n",
            encoding="utf-8",
        )
        meta = read_abd_metadata(str(p))
        assert meta["name"] == "mybook"
        assert meta["author"] == "John Doe"
        assert meta["source_language"] == "en"

    def test_no_metadata_returns_empty(self, tmp_path):
        p = tmp_path / "minimal.abd"
        p.write_text("#1\nHello world\n\n#2\nGoodbye world\n\n", encoding="utf-8")
        meta = read_abd_metadata(str(p))
        assert meta == {}


class TestListProjects:
    def test_grouping(self, tmp_path):
        (tmp_path / "book1.en.abd").touch()
        (tmp_path / "book1.bn.abd").touch()
        (tmp_path / "book2.en.abd").touch()
        (tmp_path / "readme.txt").touch()

        result = list_projects(str(tmp_path))
        assert "book1" in result
        assert "book2" in result
        assert len(result["book1"]) == 2
        assert len(result["book2"]) == 1
        assert "readme" not in result