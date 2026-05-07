# core/file_handler.py

from typing import List, Tuple, Dict
import os
import sys


def get_base_filename(filepath: str) -> str:
    """
    Extracts filename without extension
    """
    return os.path.splitext(os.path.basename(filepath))[0]

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_qss(path):
    """Load qss file"""
    with open(resource_path(path), "r", encoding="utf-8") as f:
        return f.read()

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
