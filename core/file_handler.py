# core/file_handler.py

from typing import List, Tuple, Dict
import os
import re
import sys
from pathlib import Path

QSS_URL_RE = re.compile(r"url\((['\"]?)([^)'\"\n]+)\1\)")


def app_root_path() -> str:
    """Return the bundled or source-tree root used for application assets."""
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return str(Path(__file__).resolve().parents[1])


def get_base_filename(filepath: str) -> str:
    """
    Extracts filename without extension
    """
    return os.path.splitext(os.path.basename(filepath))[0]


def user_data_path(relative_path) -> str:
    """Return an absolute path for a file in the user's data directory."""
    if os.path.isabs(relative_path):
        return os.path.normpath(relative_path)

    relative_path = os.path.normpath(relative_path)
    return os.path.join(os.path.expanduser("~"), ".anuvad", relative_path)


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if os.path.isabs(relative_path):
        return os.path.normpath(relative_path)

    relative_path = os.path.normpath(relative_path)
    return os.path.join(app_root_path(), relative_path)


def _resolve_qss_url(match):
    quote, url = match.groups()
    if (
        "://" in url
        or url.startswith(":")
        or url.startswith("data:")
        or os.path.isabs(url)
    ):
        return match.group(0)

    resolved = Path(resource_path(url)).as_posix()
    return f"url({quote}{resolved}{quote})"


def resolve_qss_asset_urls(stylesheet):
    """Make relative QSS asset URLs independent of the process cwd."""
    return QSS_URL_RE.sub(_resolve_qss_url, stylesheet)


def load_qss(path):
    """Load qss file"""
    with open(resource_path(path), "r", encoding="utf-8") as f:
        return resolve_qss_asset_urls(f.read())


def save_structured_file(
    base_filename: str,
    src_lang: str,
    data: List[Tuple[int, str]],
    metadata: Dict[str, str],
    output_dir: str = "data",
) -> str:
    """
    Saves structured file like: dracula.en.txt
    """
    filename = f"{base_filename}.{src_lang}.abd"
    output_path = os.path.join(output_dir, filename)

    # with open(output_path, "w", encoding="utf-8") as f:
    #     for idx, text in data:
    #         f.write(f"#{idx}\n{text}\n\n")
    write_abd_file(output_path, metadata, data)

    return output_path


def save_translated_file(
    base_filename: str,
    target_lang: str,
    translations: Dict[int, str],
    metadata: Dict[str, str],
    output_dir: str = "data",
) -> str:
    """
    Saves translated file like: dracula.bn.txt
    """
    filename = f"{base_filename}.{target_lang}.abd"
    output_path = os.path.join(output_dir, filename)

    write_abd_file(output_path, metadata, translations.items())

    return output_path


def list_projects(data_dir="data"):
    """
    Returns grouped project files:
    {
        "dracula": ["dracula.en.abd", "dracula.bn.abd"]
    }
    """

    files = os.listdir(data_dir)
    projects = {}

    for f in files:
        if f.endswith(".abd") and "." in f:
            parts = f.split(".")
            if len(parts) >= 3:
                base = parts[0]
                projects.setdefault(base, []).append(f)

    return projects


def write_abd_file(filepath, metadata: dict, data):
    """
    Writes structured file like:
    #1
    text

    #2
    text
    """
    with open(filepath, "w", encoding="utf-8") as f:
        # Metadata block
        f.write("# --- ANUVAD METADATA ---\n")
        for k, v in metadata.items():
            f.write(f"{k}: {v}\n")
        f.write("# --- END METADATA ---\n\n")

        # Content
        for idx, text in data:
            f.write(f"#{idx}\n{text}\n\n")


def read_abd_file(filepath):
    """
    Reads structured file like:
    #1
    text

    #2
    text
    """
    metadata = {}
    data = []

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Parse metadata
    i = 0
    if lines[i].startswith("# --- ANUVAD METADATA ---"):
        i += 1
        while not lines[i].startswith("# --- END METADATA ---"):
            key, value = lines[i].split(":", 1)
            metadata[key.strip()] = value.strip()
            i += 1
        i += 1  # skip END line

    # Parse content
    current_id = None
    buffer = []

    for line in lines[i:]:
        line = line.rstrip()

        if line.startswith("#"):
            if current_id is not None:
                data.append((current_id, "\n".join(buffer).strip()))
                buffer = []

            current_id = int(line[1:])
        else:
            buffer.append(line)

    if current_id is not None:
        data.append((current_id, "\n".join(buffer).strip()))

    return metadata, data


def read_abd_metadata(filepath):
    """
    Reads only the metadata block from an ABD file.
    Stops before segment content so project listing/opening stays lightweight.
    """
    metadata = {}

    with open(filepath, "r", encoding="utf-8") as f:
        first_line = f.readline()
        if not first_line.startswith("# --- ANUVAD METADATA ---"):
            return metadata

        for line in f:
            if line.startswith("# --- END METADATA ---"):
                break

            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()

    return metadata
