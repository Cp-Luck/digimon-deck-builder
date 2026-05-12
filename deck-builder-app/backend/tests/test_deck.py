"""Tests for deck persistence behavior.

Main coverage: saving a deck and loading it back from storage.
"""

import app.deck as deck_module
from app.deck import CurrentDeckStore, DeckManager
from app.models import Card, Deck


def test_save_and_get_deck(tmp_path):
    """Ensure a saved deck can be retrieved and listed correctly."""
    manager = DeckManager(tmp_path / "saved_decks.json")
    deck = Deck(name="Blue Flare", cards=[Card(name="Greymon", count=4)])

    saved = manager.save_deck(deck)

    assert saved["name"] == "Blue Flare"
    assert manager.get_deck("Blue Flare") is not None
    assert len(manager.list_decks()) == 1


def test_current_deck_exposes_estimated_total_cost(monkeypatch):
    """Ensure the current deck payload includes an estimated TCGplayer-based cost total."""
    store = CurrentDeckStore()
    store.cards = [{"id": "BT1-010", "name": "Agumon", "count": 2, "tcgplayer_id": 483247}]

    monkeypatch.setattr(
        deck_module,
        "summarize_deck_pricing",
        lambda cards: {"estimated_total_cost": 1.5, "priced_cards": 1, "missing_price_cards": 0},
        raising=False,
    )

    deck = store.get_deck()

    assert deck["estimated_total_cost"] == 1.5
    assert deck["priced_cards"] == 1
    assert deck["missing_price_cards"] == 0


