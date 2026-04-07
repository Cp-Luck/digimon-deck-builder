"""Deck persistence and rule validation for the deck builder.

Main responsibilities: save decks, manage the current deck, and enforce copy limits and restriction rules.
"""

from pathlib import Path
from typing import Any

from config import RESTRICTED_LIST_FILE, SAVED_DECKS_FILE
from app.models import Card, Deck
from app.utils import load_json, save_json

MAX_COPIES_PER_CARD = 4
RESTRICTED_LIST_DEFAULT = {
    "card_limits": {},
    "banned_cards": [],
    "banned_pairs": [],
}


def _card_key(card: dict[str, Any]) -> str:
    """Build a stable key for comparing cards inside a deck."""
    return str(card.get("id") or card.get("name") or "").strip().lower()


def _card_label(card: dict[str, Any]) -> str:
    """Return a human-friendly card label for validation messages."""
    return str(card.get("id") or card.get("name") or "This card")


def _normalize_restriction_key(value: Any) -> str:
    """Normalize a restriction entry key so IDs compare consistently."""
    return str(value or "").strip().lower()


def _normalize_count(value: Any) -> int:
    """Clamp a requested card count to the allowed per-card range."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = 1
    return max(1, min(parsed, MAX_COPIES_PER_CARD))


def load_restricted_list() -> dict[str, Any]:
    """Load the editable local restricted-list configuration from disk."""
    data = load_json(RESTRICTED_LIST_FILE, default_content=RESTRICTED_LIST_DEFAULT)
    if not isinstance(data, dict):
        return dict(RESTRICTED_LIST_DEFAULT)

    return {
        "card_limits": data.get("card_limits", {}) if isinstance(data.get("card_limits"), dict) else {},
        "banned_cards": data.get("banned_cards", []) if isinstance(data.get("banned_cards"), list) else [],
        "banned_pairs": data.get("banned_pairs", []) if isinstance(data.get("banned_pairs"), list) else [],
    }


def _load_card_limits() -> dict[str, int]:
    """Build the effective per-card limit map from the restriction file."""
    restricted_list = load_restricted_list()
    limits: dict[str, int] = {}

    for raw_key, raw_value in restricted_list.get("card_limits", {}).items():
        normalized_key = _normalize_restriction_key(raw_key)
        if not normalized_key:
            continue
        try:
            parsed_limit = int(raw_value)
        except (TypeError, ValueError):
            continue
        limits[normalized_key] = max(0, min(parsed_limit, MAX_COPIES_PER_CARD))

    for raw_key in restricted_list.get("banned_cards", []):
        normalized_key = _normalize_restriction_key(raw_key)
        if normalized_key:
            limits[normalized_key] = 0

    return limits


def get_card_limits() -> dict[str, int]:
    """Return the effective restricted-card limit map for API and UI consumers."""
    return _load_card_limits()


def get_card_limit(card_or_value: dict[str, Any] | Any, card_limits: dict[str, int] | None = None) -> int | None:
    """Return the allowed copy count for a specific restricted card, if one exists."""
    if isinstance(card_or_value, dict):
        lookup_value = card_or_value.get("id") or card_or_value.get("name")
    else:
        lookup_value = card_or_value

    normalized_key = _normalize_restriction_key(lookup_value)
    if not normalized_key:
        return None

    limits = card_limits if card_limits is not None else _load_card_limits()
    return limits.get(normalized_key)


def _load_banned_pairs() -> list[tuple[str, str]]:
    """Normalize the configured banned-pair rules into comparable card ID pairs."""
    restricted_list = load_restricted_list()
    normalized_pairs: list[tuple[str, str]] = []

    for pair in restricted_list.get("banned_pairs", []):
        first = second = None
        if isinstance(pair, dict):
            first = pair.get("a") or pair.get("first") or pair.get("card_a")
            second = pair.get("b") or pair.get("second") or pair.get("card_b")
        elif isinstance(pair, (list, tuple)) and len(pair) >= 2:
            first, second = pair[0], pair[1]

        first_key = _normalize_restriction_key(first)
        second_key = _normalize_restriction_key(second)
        if first_key and second_key and first_key != second_key:
            normalized_pairs.append((first_key, second_key))

    return normalized_pairs


def validate_deck_cards(cards: list[dict[str, Any]]) -> None:
    """Validate a deck against copy limits, banned cards, and banned pairs."""
    card_limits = _load_card_limits()
    present_cards = {key: card for card in cards if (key := _card_key(card))}

    for key, card in present_cards.items():
        allowed_copies = card_limits.get(key, MAX_COPIES_PER_CARD)
        if allowed_copies <= 0:
            raise ValueError(f"{_card_label(card)} is banned and cannot be included in decks.")

        current_count = int(card.get("count", 1))
        if current_count > allowed_copies:
            copy_word = "copy" if allowed_copies == 1 else "copies"
            raise ValueError(f"{_card_label(card)} is limited to {allowed_copies} {copy_word} per deck.")

    for first_key, second_key in _load_banned_pairs():
        if first_key in present_cards and second_key in present_cards:
            first_label = _card_label(present_cards[first_key])
            second_label = _card_label(present_cards[second_key])
            raise ValueError(
                f"Banned pair: {first_label} and {second_label} cannot be included in the same deck."
            )


def _normalize_deck_cards(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Merge duplicate entries, clamp counts, and validate the finished deck list."""
    normalized_cards: list[dict[str, Any]] = []

    for raw_card in cards:
        card_data = dict(raw_card)
        card_data["count"] = _normalize_count(card_data.get("count", 1))
        current_key = _card_key(card_data)
        if not current_key:
            continue

        for existing_card in normalized_cards:
            if _card_key(existing_card) == current_key:
                existing_card["count"] = min(
                    MAX_COPIES_PER_CARD,
                    int(existing_card.get("count", 1)) + int(card_data.get("count", 1)),
                )
                for key, value in card_data.items():
                    if existing_card.get(key) in (None, "") and value not in (None, ""):
                        existing_card[key] = value
                break
        else:
            normalized_cards.append(card_data)

    validate_deck_cards(normalized_cards)
    return normalized_cards


class DeckManager:
    """Persist named decks to the JSON deck storage file."""

    def __init__(self, storage_path: Path = SAVED_DECKS_FILE):
        self.storage_path = storage_path

    def list_decks(self) -> list[dict[str, Any]]:
        """Return all saved decks from storage."""
        return load_json(self.storage_path, default_content=[])

    def save_deck(self, deck: Deck) -> dict[str, Any]:
        """Create or update a saved deck after normalizing and validating it."""
        decks = self.list_decks()
        deck_data = deck.model_dump()
        deck_data["cards"] = _normalize_deck_cards(deck_data.get("cards", []))

        for index, existing_deck in enumerate(decks):
            if existing_deck["name"].lower() == deck.name.lower():
                decks[index] = deck_data
                save_json(self.storage_path, decks)
                return deck_data

        decks.append(deck_data)
        save_json(self.storage_path, decks)
        return deck_data

    def get_deck(self, name: str) -> dict[str, Any] | None:
        """Fetch a saved deck by name, ignoring case."""
        for deck in self.list_decks():
            if deck["name"].lower() == name.lower():
                return deck
        return None


class CurrentDeckStore:
    """Manage the currently active in-memory deck shown in the UI."""

    def __init__(self, deck_name: str = "Current Deck"):
        self.deck_name = deck_name
        self.cards: list[dict[str, Any]] = []

    def get_deck(self) -> dict[str, Any]:
        """Return the current deck payload and total card count."""
        return {
            "name": self.deck_name,
            "cards": self.cards,
            "total_cards": sum(int(card.get("count", 0)) for card in self.cards),
        }

    def set_deck(self, deck: Deck) -> dict[str, Any]:
        """Replace the current deck with a validated deck payload."""
        self.deck_name = deck.name or "Current Deck"
        self.cards = _normalize_deck_cards([card.model_dump() for card in deck.cards])
        return self.get_deck()

    def add_card(self, card: Card) -> dict[str, Any]:
        """Add a card to the current deck while enforcing all deck rules."""
        card_data = card.model_dump()
        card_data["count"] = _normalize_count(card_data.get("count", 1))
        card_key = _card_key(card_data)
        next_cards = [dict(existing_card) for existing_card in self.cards]

        for existing_card in next_cards:
            existing_key = _card_key(existing_card)
            if existing_key == card_key:
                existing_card["count"] = min(
                    MAX_COPIES_PER_CARD,
                    int(existing_card.get("count", 1)) + int(card_data.get("count", 1)),
                )
                for key, value in card_data.items():
                    if existing_card.get(key) in (None, "") and value not in (None, ""):
                        existing_card[key] = value
                validate_deck_cards(next_cards)
                self.cards = next_cards
                return self.get_deck()

        next_cards.append(card_data)
        validate_deck_cards(next_cards)
        self.cards = next_cards
        return self.get_deck()

    def remove_card(self, card: Card) -> dict[str, Any]:
        """Remove one or more copies of a card from the current deck."""
        card_data = card.model_dump()
        card_key = _card_key(card_data)
        remove_count = int(card_data.get("count", 1))

        for index, existing_card in enumerate(self.cards):
            existing_key = _card_key(existing_card)
            if existing_key != card_key:
                continue

            new_count = int(existing_card.get("count", 1)) - remove_count
            if new_count > 0:
                existing_card["count"] = new_count
            else:
                self.cards.pop(index)
            break

        return self.get_deck()

    def clear(self) -> dict[str, Any]:
        """Reset the current deck back to an empty default state."""
        self.deck_name = "Current Deck"
        self.cards = []
        return self.get_deck()
