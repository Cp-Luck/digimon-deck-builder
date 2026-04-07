from app.deck import DeckManager
from app.models import Card, Deck


def test_save_and_get_deck(tmp_path):
    manager = DeckManager(tmp_path / "saved_decks.json")
    deck = Deck(name="Blue Flare", cards=[Card(name="Greymon", count=4)])

    saved = manager.save_deck(deck)

    assert saved["name"] == "Blue Flare"
    assert manager.get_deck("Blue Flare") is not None
    assert len(manager.list_decks()) == 1
