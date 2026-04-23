# models/translation_model.py

from typing import List, Tuple, Dict, Optional
from datetime import datetime, timezone
from core.file_handler import read_abd_file, save_structured_file, save_translated_file
from core.config import AppConfig


class TranslationModel:
    """
    Central state manager for Anuvad.
    Keeps track of source text, translations, navigation, and metadata.
    """

    def __init__(self, config: AppConfig):
        self.config = config
        self.reset()

    @property
    def metadata(self):
        if not self.created_at:
            self.created_at = datetime.now(tz=timezone.utc)

        self.last_modified = datetime.now(tz=timezone.utc)

        return {
            "name": self.base_filename,
            "author": self.author,
            "role": "source",
            "language": self.target_lang,
            "source_language": self.src_lang,
            "created_at": self.created_at,
            "last_modified": self.last_modified,
        }

    # ---------------------------
    # 🔹 INITIALIZATION / RESET
    # ---------------------------
    def reset(self):
        self.source_data: List[Tuple[int, str]] = []
        self.translations: Dict[int, str] = {}

        self.current_index: int = 0

        self.base_filename: str = ""
        self.src_lang: str = ""
        self.target_lang: str = ""
        self.author = self.config.author
        self.created_at = None
        self.last_modified = None

    # ---------------------------
    # 🔹 LOAD DATA
    # ---------------------------
    def load_source_text(
        self, data: List[Tuple[int, str]], base_filename: str, src_lang: str = "en"
    ):
        self.source_data = data
        self.base_filename = base_filename
        self.src_lang = src_lang
        self.target_lang = ""
        self.current_index = 0

        # Reset translations when new file is loaded
        self.translations = {}

    def load_source_data(self, filepath: str, src_lang: str = "en"):
        """
        Load from structured source file
        """
        metadata, data = read_abd_file(filepath)

        self.source_data = data
        self.base_filename = metadata.get("name", "unnamed")
        self.src_lang = metadata.get("source_language", src_lang)
        self.target_lang = metadata.get("language", "")
        self.author = metadata.get("author", self.config.author)
        self.current_index = 0

        # Reset translations when new file is loaded
        self.translations = {}

    def load_target_data(self, filepath: str, target_lang: str = "en"):
        """
        Load from structured translated file
        """
        # self.translations = {idx: text for idx, text in translations}
        # self.target_lang = target_lang

        metadata, data = read_abd_file(filepath)

        self.translations = {idx: text for idx, text in data}
        self.target_lang = metadata.get("language", target_lang)
        self.current_index = 0

    # ---------------------------
    # 🔹 GETTERS
    # ---------------------------
    def total_items(self) -> int:
        return len(self.source_data)

    def get_current_id(self) -> Optional[int]:
        if not self.source_data:
            return None
        return self.source_data[self.current_index][0]

    def get_current_source_text(self) -> str:
        if not self.source_data:
            return ""
        return self.source_data[self.current_index][1]

    def get_current_translation(self) -> str:
        idx = self.get_current_id()
        if idx is None:
            return ""
        return self.translations.get(idx, "")

    def get_item_by_index(self, index: int) -> Tuple[int, str]:
        return self.source_data[index]

    def get_preview_list(self) -> List[str]:
        """
        For QListWidget display
        """
        previews = []
        for idx, text in self.source_data:
            short = text.replace("\n", " ")[:50]
            previews.append(f"#{idx}: {short}")
        return previews

    # ---------------------------
    # 🔹 NAVIGATION
    # ---------------------------
    def set_index(self, index: int):
        if 0 <= index < self.total_items():
            self.current_index = index

    def next(self):
        if self.current_index < self.total_items() - 1:
            self.current_index += 1

    def previous(self):
        if self.current_index > 0:
            self.current_index -= 1

    def has_next(self) -> bool:
        return self.current_index < self.total_items() - 1

    def has_previous(self) -> bool:
        return self.current_index > 0

    # ---------------------------
    # 🔹 UPDATE TRANSLATIONS
    # ---------------------------
    def save_current_translation(self, text: str, save_to_file: bool = True):
        idx = self.get_current_id()
        if idx is not None:
            self.translations[idx] = text.strip()

        output_dir = self.config.data_dir
        if output_dir is None:
            raise ValueError("Data directory is not configured")

        if save_to_file:
            self.save_target_file(output_dir=output_dir)

    def get_translation(self, idx: int) -> str:
        return self.translations.get(idx, "")

    # ---------------------------
    # 🔹 PROGRESS TRACKING
    # ---------------------------
    def translated_count(self) -> int:
        return sum(
            1
            for x in self.translations.values()
            if x is None or x.strip() != ""
        )

    def completion_percentage(self) -> float:
        total = self.total_items()
        if total == 0:
            return 0.0
        return (self.translated_count() / total) * 100

    def untranslated_ids(self) -> List[int]:
        return [
            idx
            for idx, _ in self.source_data
            if idx not in self.translations or not self.translations[idx].strip()
        ]

    # ---------------------------
    # 🔹 SAVING
    # ---------------------------
    def save_source_file(self, output_dir: str = "data"):
        save_structured_file(
            self.base_filename,
            self.src_lang,
            self.source_data,
            metadata=self.metadata,
            output_dir=output_dir,
        )

    def save_target_file(self, output_dir: str = "data"):
        save_translated_file(
            self.base_filename,
            self.target_lang,
            self.translations,
            metadata=self.metadata,
            output_dir=output_dir,
        )

    # ---------------------------
    # 🔹 BULK OPERATIONS
    # ---------------------------
    def apply_bulk_translation(self, translations: Dict[int, str]):
        """
        Useful when using API later
        """
        for idx, text in translations.items():
            self.translations[idx] = text.strip()

    # ---------------------------
    # 🔹 VALIDATION
    # ---------------------------
    def is_ready_for_export(self) -> bool:
        return self.total_items() > 0 and self.target_lang != ""

    # ---------------------------
    # 🔹 DEBUG / STATE INFO
    # ---------------------------
    def debug_state(self) -> dict:
        return {
            "total_items": self.total_items(),
            "current_index": self.current_index,
            "current_id": self.get_current_id(),
            "translated_count": self.translated_count(),
            "completion_percentage": self.completion_percentage(),
            "src_lang": self.src_lang,
            "target_lang": self.target_lang,
            "base_filename": self.base_filename,
        }
