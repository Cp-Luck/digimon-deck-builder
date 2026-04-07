from pathlib import Path

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


def test_search_cards_accepts_multiple_set_filters(monkeypatch):
    sample_cards = [
        {"id": "BT1-001", "name": "Agumon", "type": "Digimon", "color": "Red", "set_name": ["BT-01"]},
        {"id": "EX1-001", "name": "Mugendramon", "type": "Digimon", "color": "Black", "set_name": ["EX-01"]},
        {"id": "ST1-01", "name": "Greymon", "type": "Digimon", "color": "Red", "set_name": ["ST-01"]},
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search", params={"pack": "BT1,EX1"})

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert {card["id"] for card in response.json()["cards"]} == {"BT1-001", "EX1-001"}


def test_get_card_sets_returns_unique_sorted_options(tmp_path, monkeypatch):
    by_set_dir = tmp_path / "by_set"
    (by_set_dir / "EX1").mkdir(parents=True)
    (by_set_dir / "BT10").mkdir(parents=True)
    (by_set_dir / "BT2").mkdir(parents=True)
    (by_set_dir / "BT1").mkdir(parents=True)
    (by_set_dir / "index.json").write_text("[]", encoding="utf-8")
    monkeypatch.setattr(api_module, "CARDS_DIR", tmp_path)

    response = client.get("/api/cards/sets")

    assert response.status_code == 200
    assert response.json()["sets"] == ["BT1", "BT2", "BT10", "EX1"]


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


def test_search_cards_uses_remote_image_fallback(monkeypatch):
    sample_cards = [
        {
            "id": "BT1-010",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "set_name": ["BT-01"],
            "image_url": None,
        }
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search", params={"q": "agumon"})

    assert response.status_code == 200
    assert response.json()["cards"][0]["image_url"] == "https://images.digimoncard.io/images/cards/BT1-010.webp"


def test_normalize_card_prefers_local_image_when_available(monkeypatch):
    monkeypatch.setattr(api_module, "get_local_image_url", lambda card_id: f"/images/{card_id}.webp")

    normalized = api_module._normalize_card(
        {
            "id": "BT1-010",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "set_name": ["BT-01"],
        }
    )

    assert normalized["image_url"] == "/images/BT1-010.webp"
