from fastapi.testclient import TestClient

import app.api as api_module
from app.deck import CurrentDeckStore, DeckManager
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_fetch_deck(tmp_path, monkeypatch):
    monkeypatch.setattr(api_module, "deck_manager", DeckManager(tmp_path / "saved_decks.json"))

    payload = {
        "name": "Starter Deck",
        "cards": [
            {"name": "Agumon", "card_type": "Digimon", "count": 4}
        ]
    }

    create_response = client.post("/api/decks", json=payload)
    fetch_response = client.get("/api/decks/Starter Deck")

    assert create_response.status_code == 200
    assert fetch_response.status_code == 200
    assert fetch_response.json()["name"] == "Starter Deck"


def test_search_cards_from_local_cache(monkeypatch):
    sample_cards = [
        {"id": "BT1-001", "name": "Agumon", "type": "Digimon", "color": "Red", "set_name": ["BT-01"]},
        {"id": "BT1-002", "name": "Gabumon", "type": "Digimon", "color": "Blue", "set_name": ["BT-01"]},
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search", params={"q": "agu", "color": "red"})

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["cards"][0]["id"] == "BT1-001"


def test_add_and_remove_current_deck_card(monkeypatch):
    monkeypatch.setattr(api_module, "current_deck_store", CurrentDeckStore())

    add_response = client.post(
        "/api/deck/add",
        json={"id": "BT1-001", "name": "Agumon", "card_type": "Digimon", "count": 2},
    )
    remove_response = client.post(
        "/api/deck/remove",
        json={"id": "BT1-001", "name": "Agumon", "card_type": "Digimon", "count": 1},
    )
    deck_response = client.get("/api/deck")

    assert add_response.status_code == 200
    assert remove_response.status_code == 200
    assert deck_response.status_code == 200
    assert deck_response.json()["cards"][0]["count"] == 1
