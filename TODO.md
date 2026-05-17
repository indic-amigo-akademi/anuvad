# TODO

## High Priority

## Medium Priority

- [ ] Add export to PDF functionality.

## Low Priority

## Completed

- [x] Fix QSS asset and icon loading so stylesheets and icons resolve outside the project working directory.
- [x] Add UI integration tests for upload, list, editor, and main-window navigation.
- [x] Add shared pytest fixtures, including headless Qt app/config/model helpers and a QTest-backed `qtbot`.
- [x] Add text metadata editing with title/author updates saved back to source and target `.abd` files.
- [x] Support internationalization with a Settings menu language option.
- [x] Move auto-translation off the UI thread for list and editor translation.
- [x] Debounce list search input.
- [x] Fix translated-count logic so empty values do not count as translated.
- [x] Cache translator instances per source/target language pair.
- [x] Replace `QTableWidget` with `QTableView`, `QAbstractTableModel`, and `QSortFilterProxyModel`.
- [x] Add metadata-only ABD reading for project listings.
- [x] Fix available target language tracking in `ui/upload_screen.py`.
- [x] Improve save and dirty-state behavior, including active-screen `Ctrl+S`.
- [x] Cache loaded QSS stylesheets and icons.
- [x] Clean up unused imports and unused fields.
- [x] Harden file and path handling.
- [x] Set up comprehensive pytest suite — 90 tests covering core modules, UI screens, and TranslationModel.
