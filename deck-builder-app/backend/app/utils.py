import json
from pathlib import Path
from typing import Any


def ensure_data_file(path: Path, default_content: Any | None = None) -> None:
    default_value = [] if default_content is None else default_content
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(json.dumps(default_value, indent=2), encoding="utf-8")


def load_json(path: Path, default_content: Any | None = None) -> Any:
    default_value = [] if default_content is None else default_content
    ensure_data_file(path, default_value)

    try:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        save_json(path, default_value)
        return default_value


def save_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
