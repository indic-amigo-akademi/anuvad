# tests/models/test_translation_model.py
"""Unit tests for TranslationModel."""

import time

import pytest

from models.translation_model import TranslationModel
from core.config import AppConfig


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def config(tmp_path):
    """Create a temporary AppConfig pointing to a writable directory."""
    import configparser

    c = configparser.ConfigParser()
    c["app"] = {"name": "TestApp", "version": "1.0", "author": "Tester"}
    c["paths"] = {
        "data_dir": str(tmp_path / "data"),
        "export_dir": str(tmp_path / "exports"),
    }
    c["user"] = {"author": "Test Author"}
    c["language"] = {
        "default_source": "en",
        "default_target": "bn",
        "auto_detect": "true",
    }
    c["ui"] = {
        "theme": "light",
        "language": "en",
        "font_family": "sans-serif",
        "font_size": "14",
    }
    cfg_path = str(tmp_path / "test.cfg")
    with open(cfg_path, "w", encoding="utf-8") as f:
        c.write(f)
    return AppConfig(cfg_path)


@pytest.fixture
def model(config):
    """Create a TranslationModel with a temporary config."""
    return TranslationModel(config)


@pytest.fixture
def populated_model(model):
    """Model loaded with 3 segments of source data."""
    data = [(1, "Hello"), (2, "World"), (3, "Goodbye")]
    model.load_source_text(data, "testbook", "en")
    return model


# ---------------------------------------------------------------------------
# Initialization / Reset
# ---------------------------------------------------------------------------

class TestTranslationModelInit:
    def test_default_reset_state(self, model):
        assert model.source_data == []
        assert model.translations == {}
        assert model.current_index == 0
        assert model.base_filename == ""
        assert model.has_unsaved_changes is False

    def test_reset_clears_everything(self, populated_model):
        populated_model.save_current_translation("translated", save_to_file=False)
        populated_model.reset()
        assert populated_model.source_data == []
        assert populated_model.translations == {}
        assert populated_model.current_index == 0
        assert populated_model.has_unsaved_changes is False


# ---------------------------------------------------------------------------
# Load Data
# ---------------------------------------------------------------------------

class TestLoadSourceData:
    def test_load_from_list(self, model):
        data = [(1, "First"), (2, "Second")]
        model.load_source_text(data, "mybook", "en")
        assert model.total_items() == 2
        assert model.base_filename == "mybook"
        assert model.src_lang == "en"
        assert model.current_index == 0

    def test_load_clears_previous_translations(self, populated_model):
        populated_model.save_current_translation("old", save_to_file=False)
        assert populated_model.total_items() == 3
        new_data = [(1, "New")]
        populated_model.load_source_text(new_data, "newbook", "fr")
        assert populated_model.total_items() == 1
        assert populated_model.translations == {}

    def test_src_lang_default(self, model):
        data = [(1, "Test")]
        model.load_source_text(data, "mybook")
        assert model.src_lang == "en"


# ---------------------------------------------------------------------------
# Getters
# ---------------------------------------------------------------------------

class TestGetters:
    def test_get_current_source_text(self, populated_model):
        assert populated_model.get_current_source_text() == "Hello"

    def test_get_current_source_text_empty(self, model):
        assert model.get_current_source_text() == ""

    def test_get_current_id(self, populated_model):
        assert populated_model.get_current_id() == 1

    def test_get_current_id_empty(self, model):
        assert model.get_current_id() is None

    def test_get_current_translation(self, populated_model):
        assert populated_model.get_current_translation() == ""

    def test_get_item_by_index(self, populated_model):
        assert populated_model.get_item_by_index(0) == (1, "Hello")
        assert populated_model.get_item_by_index(2) == (3, "Goodbye")

    def test_get_preview_list(self, populated_model):
        previews = populated_model.get_preview_list()
        assert len(previews) == 3
        assert previews[0] == "#1: Hello"


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

class TestNavigation:
    def test_next(self, populated_model):
        populated_model.next()
        assert populated_model.current_index == 1
        assert populated_model.get_current_source_text() == "World"

    def test_next_at_end_is_noop(self, populated_model):
        populated_model.set_index(2)
        populated_model.next()
        assert populated_model.current_index == 2

    def test_previous(self, populated_model):
        populated_model.set_index(2)
        populated_model.previous()
        assert populated_model.current_index == 1

    def test_previous_at_start_is_noop(self, populated_model):
        populated_model.previous()
        assert populated_model.current_index == 0

    def test_has_next(self, populated_model):
        assert populated_model.has_next() is True
        populated_model.set_index(2)
        assert populated_model.has_next() is False

    def test_has_previous(self, populated_model):
        assert populated_model.has_previous() is False
        populated_model.next()
        assert populated_model.has_previous() is True

    def test_set_index_in_range(self, populated_model):
        populated_model.set_index(1)
        assert populated_model.current_index == 1

    def test_set_index_out_of_range_is_noop(self, populated_model):
        populated_model.set_index(100)
        assert populated_model.current_index == 0
        populated_model.set_index(-1)
        assert populated_model.current_index == 0


# ---------------------------------------------------------------------------
# Save Translations
# ---------------------------------------------------------------------------

class TestSaveTranslation:
    def test_save_translation(self, populated_model):
        populated_model.save_current_translation("Hola", save_to_file=False)
        assert populated_model.translations[1] == "Hola"
        assert populated_model.has_unsaved_changes is True

    def test_save_strips_whitespace(self, populated_model):
        populated_model.save_current_translation("  Hola  ", save_to_file=False)
        assert populated_model.translations[1] == "Hola"

    def test_save_empty_string(self, populated_model):
        populated_model.save_current_translation("", save_to_file=False)
        assert populated_model.translations[1] == ""
        assert populated_model.has_unsaved_changes is True

    def test_save_none_id_is_noop(self, model):
        model.save_current_translation("text", save_to_file=False)
        assert model.translations == {}


# ---------------------------------------------------------------------------
# Progress Tracking
# ---------------------------------------------------------------------------

class TestProgressTracking:
    def test_translated_count_empty(self, model):
        assert model.translated_count() == 0

    def test_translated_count(self, populated_model):
        assert populated_model.translated_count() == 0
        populated_model.save_current_translation("Hola", save_to_file=False)
        assert populated_model.translated_count() == 1
        populated_model.next()
        populated_model.save_current_translation("Mundo", save_to_file=False)
        assert populated_model.translated_count() == 2

    def test_completion_percentage(self, populated_model):
        assert populated_model.completion_percentage() == 0.0
        populated_model.save_current_translation("Hola", save_to_file=False)
        assert populated_model.completion_percentage() == (1 / 3) * 100

    def test_untranslated_ids(self, populated_model):
        ids = populated_model.untranslated_ids()
        assert ids == [1, 2, 3]
        populated_model.save_current_translation("Hola", save_to_file=False)
        ids = populated_model.untranslated_ids()
        assert ids == [2, 3]


# ---------------------------------------------------------------------------
# Bulk Operations
# ---------------------------------------------------------------------------

class TestBulkTranslation:
    def test_apply_bulk(self, populated_model):
        bulk = {1: "Uno", 2: "Dos", 3: "Tres"}
        populated_model.apply_bulk_translation(bulk)
        assert populated_model.translated_count() == 3
        assert populated_model.has_unsaved_changes is True

    def test_apply_bulk_strips(self, populated_model):
        bulk = {1: "  Uno  ", 2: "  Dos  "}
        populated_model.apply_bulk_translation(bulk)
        assert populated_model.translations[1] == "Uno"
        assert populated_model.translations[2] == "Dos"


# ---------------------------------------------------------------------------
# Export Readiness
# ---------------------------------------------------------------------------

class TestExportReadiness:
    def test_not_ready_when_empty(self, model):
        assert model.is_ready_for_export() is False

    def test_not_ready_without_target_lang(self, populated_model):
        assert populated_model.is_ready_for_export() is False

    def test_ready_with_data_and_target(self, populated_model):
        populated_model.target_lang = "bn"
        assert populated_model.is_ready_for_export() is True


# ---------------------------------------------------------------------------
# Debug State
# ---------------------------------------------------------------------------

class TestDebugState:
    def test_debug_keys(self, populated_model):
        state = populated_model.debug_state()
        assert "total_items" in state
        assert "current_index" in state
        assert "translated_count" in state
        assert "completion_percentage" in state


# ---------------------------------------------------------------------------
# Metadata
# ---------------------------------------------------------------------------

class TestMetadata:
    def test_metadata_includes_defaults(self, populated_model):
        meta = populated_model.metadata
        assert "name" in meta
        assert "author" in meta
        assert "source_language" in meta

    def test_metadata_updates_on_access(self, populated_model):
        before = populated_model.metadata["last_modified"]
        time.sleep(0.01)
        after = populated_model.metadata["last_modified"]
        assert after >= before
