from pathlib import Path
from typing import Any

from config import SAVED_DECKS_FILE
from app.models import Deck
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
