# Contributing to Anuvad

Thanks for helping improve Anuvad. This project is a desktop translation workbench built with PyQt5, so contributions should preserve a responsive UI, clear translation workflow, and reliable `.abd` project files.

## Getting Started

1. Fork or clone the repository.
2. Create a virtual environment:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

    On Windows PowerShell:

    ```powershell
    .venv\Scripts\Activate.ps1
    ```

3. Install dependencies:

    ```bash
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    ```

4. Run the app:

    ```bash
    python main.py
    ```

## Development Guidelines

- Keep changes focused and avoid unrelated refactors.
- Follow the existing project structure:
    - `core/` for parsing, file handling, language utilities, translation, and configuration.
    - `models/` for application state and translation data.
    - `ui/` for PyQt screens, widgets, and workers.
- Keep expensive work off the UI thread. Use workers and signals for translation or other long-running operations.
- Debounce frequent UI updates when they can be triggered on every keystroke.
- Prefer structured parsing and file helpers over ad hoc string handling.
- Preserve compatibility with the `.abd` file format unless the change intentionally updates the format.
- Use plain, readable UI text. Avoid decorative emoticons or emoji in documentation and interface copy.

## Translation and Language Behavior

- Use the known source or target language when available instead of repeatedly detecting language.
- Treat language detection as a fallback, especially for short or user-edited text.
- Keep transliteration optional and lightweight enough to avoid editor lag.
- When adding language support, update `core/language.py` and any relevant UI language lists together.

## Testing

Run tests with:

```bash
pytest
```

If imports fail from the repository root, run:

```powershell
$env:PYTHONPATH='.'; pytest
```

Before opening a pull request, also run:

```bash
git diff --check
```

For packaging changes, build locally and record the bundle size:

```powershell
.\scripts\build.ps1
.\scripts\size-report.ps1
```

If a test cannot run because of missing local data or an existing test setup issue, mention that clearly in the pull request.

## Documentation

Update `README.md` when a change affects:

- User-facing behavior
- Installation or dependencies
- Supported languages or translation providers
- File formats or metadata
- Known limitations

Use plain Markdown headings and concise descriptions. Keep documentation current with the code rather than describing planned behavior as already implemented.

## Pull Request Checklist

- The change is scoped to one clear purpose.
- User-facing behavior is documented.
- UI changes remain responsive for large projects or long text segments.
- Save, dirty-state, and navigation behavior still work as expected.
- Tests or manual verification steps are included in the pull request notes.
- New dependencies are justified and added to `requirements.txt`.

## Reporting Issues

When reporting a bug, include:

- What you were trying to do.
- What happened.
- What you expected to happen.
- Steps to reproduce the issue.
- Relevant language settings, input file type, and operating system.

For UI performance issues, include the approximate number of segments and the length of the text being edited or translated.
