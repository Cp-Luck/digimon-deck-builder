"""Card cache storage helpers for loading, deduping, and timestamping saved card data.

Main functions: `load_cards()`, `save_cards()`, `dedupe_cards()`, and `card_needs_refresh()`.
"""

from datetime import datetime, timezone
from typing import Any

from app.utils import load_json, save_json
from config import CARD_FILE, LAST_UPDATED_FILE


def get_card_identifier(card: dict[str, Any]) -> str | None:
    """Return the best available card identifier from a card payload."""
    for key in ("id", "cardnumber", "card"):
        value = card.get(key)
        if value is not None and str(value).strip():
            return str(value).strip().upper()
    return None


def get_card_dedupe_key(card: dict[str, Any]) -> str | None:
    """Build a deduplication key that keeps card variants distinct when needed."""
    identifier = get_card_identifier(card)
    if identifier is None:
        return None

    variant = card.get("image_url") or card.get("pretty_url")
    if variant is None or not str(variant).strip():
        return identifier

    return f"{identifier}::{str(variant).strip()}"


def has_card_value(card: dict[str, Any], key: str) -> bool:
    """Check whether a card field contains a meaningful non-empty value."""
    value = card.get(key)
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict, tuple, set)):
        return len(value) > 0
    return True


def card_needs_refresh(card: dict[str, Any]) -> bool:
    """Identify cached cards that are incomplete and should be refreshed from the API."""
    if not isinstance(card, dict):
        return True

    if get_card_identifier(card) is None:
        return True

    important_fields = ("name", "type", "color", "rarity", "set_name")
    if any(key in card and not has_card_value(card, key) for key in important_fields):
        return True

    card_type = str(card.get("type") or "").strip().lower()
    if card_type == "digimon":
        digimon_required_fields = ("play_cost", "level")
        if any(
            key in card and card.get(key) is None for key in digimon_required_fields
        ):
            return True
        if "dp" in card and card.get("dp") is None and card.get("link_dp") is None:
            return True

    return False


def dedupe_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Remove duplicate card entries while keeping the latest version of each card."""
    deduped_cards: list[dict[str, Any]] = []
    index_by_key: dict[str, int] = {}

    for card in cards:
        if not isinstance(card, dict):
            continue

        key = get_card_dedupe_key(card)
        if key is None:
            deduped_cards.append(card)
            continue

        if key in index_by_key:
            deduped_cards[index_by_key[key]] = card
        else:
            index_by_key[key] = len(deduped_cards)
            deduped_cards.append(card)

    return deduped_cards


def save_cards(cards: list[dict[str, Any]]) -> None:
    """Persist the deduplicated card cache to disk."""
    save_json(CARD_FILE, dedupe_cards(cards))


def load_cards() -> list[dict[str, Any]]:
    """Load the saved local card cache from disk."""
    cards = load_json(CARD_FILE, default_content=[])
    if not isinstance(cards, list):
        return []
    return dedupe_cards(cards)


def save_last_updated() -> None:
    """Record the current UTC timestamp as the last successful sync time."""
    LAST_UPDATED_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_UPDATED_FILE.write_text(
        datetime.now(timezone.utc).isoformat(),
        encoding="utf-8",
    )


def get_last_updated() -> str | None:
    """Return the last card sync timestamp if one has been recorded."""
    LAST_UPDATED_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not LAST_UPDATED_FILE.exists():
        return None

    value = LAST_UPDATED_FILE.read_text(encoding="utf-8").strip()
    return value or None
