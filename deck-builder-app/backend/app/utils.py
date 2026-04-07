"""Shared JSON file helpers for backend persistence.

Main functions: `ensure_data_file()`, `load_json()`, and `save_json()`.
"""

import json
from pathlib import Path
from typing import Any


def ensure_data_file(path: Path, default_content: Any | None = None) -> None:
    """Create a JSON file with default content when it does not already exist."""
    default_value = [] if default_content is None else default_content
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(json.dumps(default_value, indent=2), encoding="utf-8")


def load_json(path: Path, default_content: Any | None = None) -> Any:
    """Load JSON from disk and fall back to default content if the file is missing or invalid."""
    default_value = [] if default_content is None else default_content
    ensure_data_file(path, default_value)

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        save_json(path, default_value)
        return default_value


def save_json(path: Path, data: Any) -> None:
    """Write JSON data to disk using a pretty indented format."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
