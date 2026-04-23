# core/parser.py

from typing import List, Tuple


def parse_raw_text(filepath: str) -> List[Tuple[int, str]]:
    """
    Reads a raw text file and splits into numbered segments.
    Splitting strategy: double newline (paragraph-based)
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = [b.strip() for b in content.split("\n\n") if b.strip()]

    return [(i + 1, block) for i, block in enumerate(blocks)]


def parse_structured_file(filepath: str) -> List[Tuple[int, str]]:
    """
    Parses files like:
    #1
    text

    #2
    text
    """
    data = []
    current_id = None
    buffer = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()

            if line.startswith("#"):
                if current_id is not None:
                    data.append((current_id, "\n".join(buffer).strip()))
                    buffer = []

                current_id = int(line[1:])
            else:
                buffer.append(line)

        # last entry
        if current_id is not None:
            data.append((current_id, "\n".join(buffer).strip()))

    return data
