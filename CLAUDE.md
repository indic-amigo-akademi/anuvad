# CLAUDE Guidance for Anuvad

This repository is a PyQt5 desktop translation workbench. Use this file as a guide to understand the architecture, follow the existing structure, and keep new Python code clean, Zen-aligned, and PEP-compliant.

## Project Overview

- `main.py`: application entry point.
- `app.cfg`: default configuration values and app metadata.
- `core/`: shared backend utilities.
  - `config.py`: application configuration loader, UI theme helpers, translations, and icon caching.
  - `file_handler.py`: file I/O helpers, `.abd` project file reading/writing, QSS loading, and resource path resolution.
  - `parser.py`: parsing raw text and structured files into numbered segments.
  - `language.py`: language detection, Indic transliteration, and Latin-script preview helpers.
  - `translator.py`: translation provider wrapper using `deep_translator.GoogleTranslator`.
- `models/`: application state.
  - `translation_model.py`: central state manager for source content, translation content, navigation, metadata, and save/load operations.
- `ui/`: PyQt UI screens, custom widgets, and workers.
  - `main_window.py`: main window, screen navigation, menu creation, and app settings.
  - `upload_screen.py`: upload/new project workflow and project selection.
  - `list_screen.py`: project overview, jump-to-item, save behavior.
  - `editor_screen.py`: editor UI, translation text entry, auto-translate workflow, and save flow.
  - `translation_worker.py`: background worker for translation tasks.
  - `custom_widget.py`: reusable dialog and divider widgets.
- `assets/`: icons, images, and stylesheets.
- `tests/`: unit tests for core parsing and translation model behavior.

## High-Level Design Principles

- Keep UI thread work light.
  - Use `QThread` + `QObject` worker patterns for translation operations.
  - Avoid blocking UI widgets during long-running steps.
- Keep components small and purpose-driven.
  - `core/` is for logic and helpers.
  - `models/` is for state and domain data.
  - `ui/` is for widgets, screens, and presentation.
- Preserve `.abd` compatibility.
  - Changes to file structure should intentionally update the `.abd` format.
  - Prefer existing file helper functions in `core/file_handler.py`.
- Keep text handling explicit and safe.
  - Use `strip()` before saving translation text.
  - Do not assume language detection always succeeds.

## Style and Pythonic Best Practices

- Follow PEP 8 and Pythonic readability.
  - Use `snake_case` for functions and variables.
  - Use `CamelCase` for classes.
  - Keep lines reasonably short and avoid overly nested logic.
- Use type hints consistently for public APIs.
  - Many modules already use `typing.List`, `typing.Tuple`, `typing.Dict`, `typing.Optional` and return type annotations.
- Prefer explicit imports.
  - Avoid `from module import *`.
  - Use module-qualified names when clarity helps.
- Use expressive, descriptive names.
  - Examples: `save_structured_file`, `load_source_data`, `completion_percentage`, `set_translation_controls_enabled`.
- Prefer explicit truth tests and error handling.
  - Use `if not os.path.exists(path):` before file operations.
  - Avoid bare `except:`; use specific exception types.
- Keep state mutation controlled.
  - The `TranslationModel` centralizes state and metadata updates.
  - If adding state changes, update `has_unsaved_changes` and save behavior consistently.
- Keep logic in the correct layer.
  - UI classes should orchestrate widgets and user actions.
  - Business rules and file operations belong in `core/` or `models/`.
- Use helper methods for repeated tasks.
  - Example: `AppConfig.get_theme_stylesheet()` caches QSS content.

## Claude-Specific Traversal Tips

- When reviewing or proposing edits, start from `main.py` to understand app startup and global style application.
- Trace data flow from `UploadScreen` through `TranslationModel` to `EditorScreen`.
- Use `TranslationModel` methods instead of duplicating save/load logic in UI code.
- Read `core/config.py` for theme, translation, and icon-loading conventions.
- Respect translation key usage via `config.tr(...)` and `core/i18n.py`.

## Recommended Coding Zen

- Prefer clarity over cleverness.
- Keep the UI responsive.
- Keep business logic explicit and testable.
- Avoid speculative refactors unless they simplify the current design.
- When adding features, update tests, documentation, and localization helpers together.

## Useful Patterns in This Repository

- `@property` for computed configuration values.
- `QThread` + worker object for background translation.
- `os.path.join` and `resource_path()` for file paths.
- `datetime.now(tz=timezone.utc)` for timezone-aware metadata.
- `list_projects()` / `read_abd_metadata()` for project enumerations.
- `QProgressDialog` for cancellable progress feedback.

## Local Conventions to Preserve

- Use `self.config.tr('key')` for UI strings instead of hard-coded text.
- Cache loaded icons and stylesheets in `AppConfig`.
- Keep `save_current_translation()` and `save_target_file()` separate and explicit.
- Keep translation preview and romanization logic in `core/language.py`.
- Keep `.abd` file metadata in a dedicated metadata section.

## When to Update This File

Update `CLAUDE.md` if you add new major modules, change the `.abd` file schema, or change the UI/workflow architecture.

---

This file exists to help Claude navigate the repository and preserve the project's Pythonic, maintainable style.
