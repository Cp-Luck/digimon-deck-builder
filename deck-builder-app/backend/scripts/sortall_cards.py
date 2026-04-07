"""Sort cached cards into per-set folders and JSON exports.

Main function: `main()`, which groups cards by set code and writes the `by_set` output structure.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.storage import get_card_identifier, load_cards
from config import CARDS_DIR

SORTED_ROOT = CARDS_DIR / "by_set"
CARD_ID_PATTERN = re.compile(r"^(?P<set>[A-Z]+\d*)-(?P<number>\d+)(?P<suffix>[A-Z]*)$")


def parse_card_id(card_id: str) -> tuple[str, int, str]:
    """Split a card ID into set code, numeric order, and optional suffix."""
    normalized = card_id.strip().upper()
    match = CARD_ID_PATTERN.match(normalized)
    if match:
        return (
            match.group("set"),
            int(match.group("number")),
            match.group("suffix"),
        )

    if "-" in normalized:
        prefix, _, remainder = normalized.partition("-")
    else:
        prefix, remainder = "UNKNOWN", normalized

    digits = "".join(character for character in remainder if character.isdigit())
    suffix = "".join(character for character in remainder if character.isalpha())
    return prefix or "UNKNOWN", int(digits) if digits else 0, suffix


def card_sort_key(card: dict[str, Any]) -> tuple[str, int, str, str]:
    """Return a sort key that orders cards by set, number, suffix, and name."""
    card_id = get_card_identifier(card) or ""
    set_code, number, suffix = parse_card_id(card_id)
    return set_code, number, suffix, str(card.get("name") or "").lower()


def group_cards_by_set(cards: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group cards into ordered lists keyed by their set folder code."""
    grouped_cards: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for card in cards:
        if not isinstance(card, dict):
            continue

        card_id = get_card_identifier(card)
        if not card_id:
            continue

        set_code, _, _ = parse_card_id(card_id)
        grouped_cards[set_code].append(card)

    return {
        set_code: sorted(set_cards, key=card_sort_key)
        for set_code, set_cards in sorted(grouped_cards.items())
    }


def write_grouped_cards(
    grouped_cards: dict[str, list[dict[str, Any]]],
    output_root: Path = SORTED_ROOT,
) -> list[dict[str, Any]]:
    """Write grouped card exports to each set folder and return a summary index."""
    output_root.mkdir(parents=True, exist_ok=True)
    summary: list[dict[str, Any]] = []

    for set_code, cards in grouped_cards.items():
        set_dir = output_root / set_code
        set_dir.mkdir(parents=True, exist_ok=True)

        (set_dir / "cards.json").write_text(
            json.dumps(cards, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        for card in cards:
            card_id = get_card_identifier(card) or "UNKNOWN"
            (set_dir / f"{card_id}.json").write_text(
                json.dumps(card, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        summary.append({"set": set_code, "count": len(cards)})

    (output_root / "index.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return summary


def main() -> None:
    """Run the full card-sorting export process and print a short summary."""
    cards = load_cards()
    grouped_cards = group_cards_by_set(cards)
    summary = write_grouped_cards(grouped_cards)

    print(f"Sorted {len(cards)} cards into {len(summary)} set folders.")
    print(f"Output directory: {SORTED_ROOT}")

    for item in summary[:10]:
        print(f"- {item['set']}: {item['count']} cards")


if __name__ == "__main__":
    main()
