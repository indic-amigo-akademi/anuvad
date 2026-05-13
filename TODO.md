# TODO

## High Priority

- [ ] Add support for editing text metadata.
    - Allow updating project metadata such as title and author.
    - Save metadata changes back into `.abd` files.
    - Keep metadata editing consistent for source and target files.

## Completed

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
