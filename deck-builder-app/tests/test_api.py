from fastapi.testclient import TestClient

import app.api as api_module
from app.deck import DeckManager
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
