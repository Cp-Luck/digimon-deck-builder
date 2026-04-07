from pathlib import Path
from typing import Any

from config import SAVED_DECKS_FILE
from app.models import Card, Deck
from app.utils import load_json, save_json


class DeckManager:
    def __init__(self, storage_path: Path = SAVED_DECKS_FILE):
        self.storage_path = storage_path

    def list_decks(self) -> list[dict[str, Any]]:
        return load_json(self.storage_path, default_content=[])

    def save_deck(self, deck: Deck) -> dict[str, Any]:
        decks = self.list_decks()
        deck_data = deck.model_dump()

        for index, existing_deck in enumerate(decks):
            if existing_deck["name"].lower() == deck.name.lower():
                decks[index] = deck_data
                save_json(self.storage_path, decks)
                return deck_data

        decks.append(deck_data)
        save_json(self.storage_path, decks)
        return deck_data

    def get_deck(self, name: str) -> dict[str, Any] | None:
        for deck in self.list_decks():
            if deck["name"].lower() == name.lower():
                return deck
        return None


class CurrentDeckStore:
    def __init__(self, deck_name: str = "Current Deck"):
        self.deck_name = deck_name
        self.cards: list[dict[str, Any]] = []

    def get_deck(self) -> dict[str, Any]:
        return {
            "name": self.deck_name,
            "cards": self.cards,
            "total_cards": sum(int(card.get("count", 0)) for card in self.cards),
        }

    def set_deck(self, deck: Deck) -> dict[str, Any]:
        self.deck_name = deck.name or "Current Deck"
        self.cards = [card.model_dump() for card in deck.cards]
        return self.get_deck()

    def add_card(self, card: Card) -> dict[str, Any]:
        card_data = card.model_dump()
        card_key = str(card_data.get("id") or card_data["name"]).lower()

        for existing_card in self.cards:
            existing_key = str(existing_card.get("id") or existing_card.get("name", "")).lower()
            if existing_key == card_key:
                existing_card["count"] = int(existing_card.get("count", 1)) + int(card_data.get("count", 1))
                for key, value in card_data.items():
                    if existing_card.get(key) in (None, "") and value not in (None, ""):
                        existing_card[key] = value
                return self.get_deck()

        self.cards.append(card_data)
        return self.get_deck()

    def remove_card(self, card: Card) -> dict[str, Any]:
        card_data = card.model_dump()
        card_key = str(card_data.get("id") or card_data["name"]).lower()
        remove_count = int(card_data.get("count", 1))

        for index, existing_card in enumerate(self.cards):
            existing_key = str(existing_card.get("id") or existing_card.get("name", "")).lower()
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
        self.deck_name = "Current Deck"
        self.cards = []
        return self.get_deck()
