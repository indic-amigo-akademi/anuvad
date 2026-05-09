# TODO

## High Priority

- [x] Move auto-translation off the UI thread with `QThread` or `QRunnable`.
    - Applies to bulk translation in `ui/list_screen.py`.
    - Applies to single-item translation in `ui/editor_screen.py`.
    - Emit progress, completion, cancellation, and error signals back to the UI.

- [x] Debounce list search input.
    - Use a short `QTimer` delay, around 150-250ms.
    - Avoid rebuilding the table on every keystroke.

- [x] Fix translated-count logic in `models/translation_model.py`.
    - `None` should not count as translated.
    - Expected check: value exists and `value.strip() != ""`.

- [x] Cache translator instances in `core/translator.py`.
    - Reuse `GoogleTranslator` per `(source, target)` pair.
    - Avoid recreating the translator for every segment during bulk translation.

## Medium Priority

- [x] Replace `QTableWidget` with `QTableView` plus `QAbstractTableModel`.
    - Add `QSortFilterProxyModel` for efficient search/filtering.
    - This will scale better for large projects.

- [x] Add metadata-only ABD reading.
    - Create `read_abd_metadata(filepath)` in `core/file_handler.py`.
    - Use it in `ui/upload_screen.py` when listing/opening projects.
    - Avoid parsing full segment content when only metadata is needed.

- [x] Fix available target language tracking in `ui/upload_screen.py`.
    - Use `extend(...)` instead of appending a list into `model.avl_tgt_langs`.
    - Keep `avl_tgt_langs` as a flat list of language codes.

- [x] Improve save and dirty-state behavior.
    - Track whether editor/list translations have unsaved changes.
    - Make `Ctrl+S` save the active screen's current data intentionally.
    - Avoid surprising saves from the wrong screen.

## Low Priority

- [ ] Cache loaded QSS stylesheets and icons in `core/config.py`.
    - Avoid rereading theme files and recreating icons repeatedly.

- [ ] Clean up unused imports and unused fields.
    - Remove unused imports from `core/translator.py`.
    - Either apply `timeout`/`throttle` or remove them until needed.

- [ ] Harden file/path handling.
    - Prefer `os.path.join(...)` or `pathlib.Path` over manual `f"{dir}/{file}"`.
    - Keep behavior consistent across platforms.
