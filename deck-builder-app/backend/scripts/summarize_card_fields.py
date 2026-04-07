"""Summarize repeated card field values across the local Digimon card dataset.

Main function: `main()`, which scans all saved cards, groups recurring values by field,
merges `digi_type` variants, removes one-off values, and writes human-readable output files.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.storage import load_cards
from config import CARDS_DIR

SUMMARY_JSON_FILE = CARDS_DIR / "field_value_summary.json"
SUMMARY_MARKDOWN_FILE = CARDS_DIR / "field_value_summary.md"
RARITY_ORDER = ["C", "U", "R", "SR", "SEC", "P", "UR"]
RARITY_SORT_INDEX = {value: index for index, value in enumerate(RARITY_ORDER)}
EXCLUDED_FIELDS = {
    "alt_effect",
    "date_added",
    "link_requirements",
    "main_effect",
    "name",
    "set_name",
    "source_effect",
    "tcgplayer_name",
    "xros_req",
}


def normalize_field_name(field_name: str) -> str:
    """Normalize related field names so they are grouped under one shared heading."""
    if field_name.startswith("digi_type"):
        return "digi_type"
    if field_name == "color2":
        return "color"
    return field_name


def extract_field_values(value: Any) -> list[str]:
    """Return normalized non-empty values from a card field while ignoring null-like entries."""
    if value is None:
        return []

    if isinstance(value, (list, tuple, set)):
        results: list[str] = []
        for item in value:
            results.extend(extract_field_values(item))
        return results

    normalized = str(value).strip()
    return [normalized] if normalized else []


def normalize_field_value(field_name: str, value: str) -> str:
    """Normalize individual field values so the summary groups equivalent entries together."""
    normalized = value.strip()
    if field_name == "rarity":
        return normalized.upper()
    return normalized


def field_value_sort_key(field_name: str, item: tuple[str, int]) -> tuple[Any, ...]:
    """Return the display order for summarized values within one field group."""
    value, count = item

    if field_name == "rarity":
        return (RARITY_SORT_INDEX.get(value.upper(), len(RARITY_ORDER)), value.upper())

    return (-count, value.lower())


def build_field_summary(cards: list[dict[str, Any]], minimum_count: int = 2) -> dict[str, dict[str, int]]:
    """Count repeated values for each card field and drop entries that appear only once."""
    counts_by_field: dict[str, Counter[str]] = defaultdict(Counter)

    for card in cards:
        if not isinstance(card, dict):
            continue

        for field_name, raw_value in card.items():
            normalized_field = normalize_field_name(field_name)
            if normalized_field in EXCLUDED_FIELDS:
                continue
            for normalized_value in extract_field_values(raw_value):
                canonical_value = normalize_field_value(normalized_field, normalized_value)
                if canonical_value:
                    counts_by_field[normalized_field][canonical_value] += 1

    summary: dict[str, dict[str, int]] = {}
    for field_name in sorted(counts_by_field):
        filtered_values = {
            value: count
            for value, count in sorted(
                counts_by_field[field_name].items(),
                key=lambda item: field_value_sort_key(field_name, item),
            )
            if count >= minimum_count
        }
        if filtered_values:
            summary[field_name] = filtered_values

    return summary


def write_summary_json(summary: dict[str, dict[str, int]], output_path: Path = SUMMARY_JSON_FILE) -> None:
    """Write the grouped field summary to a JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")


def write_summary_markdown(summary: dict[str, dict[str, int]], output_path: Path = SUMMARY_MARKDOWN_FILE) -> None:
    """Write the grouped field summary to a readable markdown report with bullet lists."""
    lines = [
        "# Card Field Value Summary",
        "",
        "This report only includes values that appear more than once in the local card dataset.",
        "",
    ]

    for field_name, values in summary.items():
        lines.append(f"## `{field_name}`")
        lines.append("")
        for value, count in values.items():
            lines.append(f"- `{value}`: {count}")
        lines.append("")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> None:
    """Scan the saved card dataset and write grouped value summaries to JSON and markdown files."""
    cards = load_cards()
    summary = build_field_summary(cards)
    write_summary_json(summary)
    write_summary_markdown(summary)

    print(f"Processed {len(cards)} cards.")
    print(f"Saved JSON summary to: {SUMMARY_JSON_FILE}")
    print(f"Saved Markdown summary to: {SUMMARY_MARKDOWN_FILE}")
    print(f"Included {len(summary)} grouped fields with repeated values.")


if __name__ == "__main__":
    main()
