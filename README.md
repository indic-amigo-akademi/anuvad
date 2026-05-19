# Anuvad - Desktop Translation Workbench

<div align="center">
<img width="200" src="assets/images/logo.png" alt="Anuvad" />
</div>

**Anuvad** is a PyQt5 desktop application for structured text translation workflows. It breaks large text files into numbered segments, supports manual and automatic translation, tracks progress, and stores work in a reusable project format.

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE.md)
[![Coverage Status](https://github.com/indic-amigo-akademi/anuvad/actions/workflows/python-test.yml/badge.svg)](https://github.com/indic-amigo-akademi/anuvad/actions)

---

## Features

### Project Management

- Start a new project by uploading a `.txt` file.
- Resume existing work from `.abd` files.
- Store source and target files in the configured data directory.
- Read project metadata without parsing full segment content when listing saved projects.

### Structured Translation Workflow

- Automatically parse text into numbered segments:

    ```text
    #1
    D R A C U L A

    #2
    CHAPTER I
    ```

- Navigate segment by segment or jump from the list view.
- Track unsaved edits and save the active screen intentionally with `Ctrl+S`.

### Editor

- Split editor with resizable source and translation panels.
- Romanized preview text for non-Latin scripts.
- Translated-text romanization uses the selected target language directly instead of repeatedly detecting language.
- Translation romanization is debounced while typing to reduce UI lag on longer segments.

### List View

- Two-column project overview backed by `QTableView` and `QAbstractTableModel`.
- Search and filtering through `QSortFilterProxyModel`.
- Debounced search input to avoid rebuilding or filtering on every keystroke.
- Completion counts ignore empty or whitespace-only translations.

### Multi-Language Support

- Optional source language auto-detection on upload.
- Dynamic target-language selection.
- Application language can be changed from the Settings menu.
- Indic transliteration support through `indic-transliteration`.
- Extensible language definitions in `core/language.py`.

### Auto Translation

- Automatic translation uses `deep-translator` with `GoogleTranslator`.
- Single-segment and bulk translation run on worker threads.
- Translation progress, cancellation, completion, and errors are reported back to the UI.
- Translator instances are cached per source/target language pair during worker execution.

### Custom File Format (`.abd`)

- Stores content and metadata together:

    ```text
    # --- ANUVAD METADATA ---
    name: dracula
    author: Purbayan
    role: source
    language: en
    source_language: en
    created_at: 2026-05-09T00:00:00+00:00
    last_modified: 2026-05-09T00:00:00+00:00
    # --- END METADATA ---
    ```

- Designed to avoid fragile filename parsing.
- Supports separate source and target files for the same project.

### Configuration

- Configure behavior through `app.cfg`, including:
    - Data directory
    - Default source and target languages
    - Author metadata
    - UI font and theme
    - Application language
    - Translation settings

- Stylesheets and icons are cached to avoid repeated file reads and icon construction.

---

## Project Structure

```text
anuvad/
|
- main.py
- app.cfg
- requirements.txt
- requirements-dev.txt
|
- core/
|   - parser.py
|   - file_handler.py
|   - language.py
|   - translator.py
|   - config.py
|
- models/
|   - translation_model.py
|
- ui/
|   - main_window.py
|   - upload_screen.py
|   - list_screen.py
|   - editor_screen.py
|   - translation_worker.py
|
- assets/
|   - icons/
|   - images/
|   - qss/
|
- data/
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd anuvad
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

For development, tests, linting, and packaging tools, install:

```bash
pip install -r requirements-dev.txt
```

---

## Running the App

```bash
python main.py
```

## Running Tests

To run the test suite:

```bash
pytest
```

If you encounter import errors when running tests from the repository root, use:

```bash
# On Linux/Mac
PYTHONPATH=. pytest

# On Windows PowerShell
$env:PYTHONPATH='.'; pytest
```

### Generating Coverage Reports

To generate a coverage report, first install `pytest-cov`:

```bash
pip install -r requirements-dev.txt
```

Then run the tests with coverage:

```bash
pytest --cov=./ --cov-report=html --cov-report=term
```

This will:

- Generate an HTML report in the `htmlcov/` directory (open `htmlcov/index.html` in a browser)
- Show a terminal report with coverage percentages

For CI systems, you can also generate an XML report:

```bash
pytest --cov=./ --cov-report=xml
```

This produces `coverage.xml` for tools like Codecov or GitHub Actions.

---

## Packaging

Windows builds use PyInstaller and bundle only runtime assets: icons, `icon.ico`,
translations, QSS, and `app.cfg`. Development tools and tests live in
`requirements-dev.txt` so they do not become runtime dependencies.

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
.\scripts\build.ps1
.\scripts\size-report.ps1
```

Use `scripts/size-report.ps1` after a build to list total bundle size and the
largest files in `dist/Anuvad`.

Current Windows measurements from the project venv:

- `onedir`: `85.55 MB` in `dist/Anuvad`, preferred for easier debugging and faster startup.
- `onefile`: `37.88 MB` compressed as a single EXE, with slower first launch due to extraction.

---

## How It Works

1. Upload a text file.
2. The app parses it into structured segments.
3. Segments appear in the list view with source and translation columns.
4. Choose a target language.
5. Translate manually, translate a single segment, or bulk translate untranslated segments.
6. Save progress in `.abd` format.
7. Resume the project later from the saved source or target file.

---

## Known Limitations

- Public translation services may be rate-limited or unavailable.
- Language detection may fail on very short text.
- Automatic translation quality depends on the upstream translation provider.

---

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup steps, development guidelines, testing notes, and pull request expectations.

---

## Author

**Purbayan Chowdhury**

---

## License

MIT License. See [LICENSE.md](LICENSE.md).

---

## Philosophy

Anuvad is built as a translator's tool, not just a translator. It focuses on control, structure, and workflow rather than blind automation.
