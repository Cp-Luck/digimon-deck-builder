"""API regression tests for card search, deck operations, and restriction handling.

Main coverage: search filters, deck CRUD routes, image URL behavior, and deck validation rules.
"""

import json

from fastapi.testclient import TestClient

import app.api as api_module
import app.deck as deck_module
from app.deck import CurrentDeckStore, DeckManager
from main import app

client = TestClient(app)


def test_health_check():
    """Verify that the health endpoint responds successfully."""
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_fetch_deck(tmp_path, monkeypatch):
    """Ensure decks can be created and retrieved through the API."""
    monkeypatch.setattr(
        api_module, "deck_manager", DeckManager(tmp_path / "saved_decks.json")
    )

    payload = {
        "name": "Starter Deck",
        "cards": [{"name": "Agumon", "card_type": "Digimon", "count": 4}],
    }

    create_response = client.post("/api/decks", json=payload)
    fetch_response = client.get("/api/decks/Starter Deck")

    assert create_response.status_code == 200
    assert fetch_response.status_code == 200
    assert fetch_response.json()["name"] == "Starter Deck"


def test_search_cards_from_local_cache(monkeypatch):
    """Verify local search filters return the expected cached card results."""
    sample_cards = [
        {
            "id": "BT1-001",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-002",
            "name": "Gabumon",
            "type": "Digimon",
            "color": "Blue",
            "set_name": ["BT-01"],
        },
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search", params={"q": "agu", "color": "red"})

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["cards"][0]["id"] == "BT1-001"


def test_search_cards_accepts_multiple_set_filters(monkeypatch):
    """Ensure the set filter accepts multiple folder-based set codes at once."""
    sample_cards = [
        {
            "id": "BT1-001",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "set_name": ["BT-01"],
        },
        {
            "id": "EX1-001",
            "name": "Mugendramon",
            "type": "Digimon",
            "color": "Black",
            "set_name": ["EX-01"],
        },
        {
            "id": "ST1-01",
            "name": "Greymon",
            "type": "Digimon",
            "color": "Red",
            "set_name": ["ST-01"],
        },
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search", params={"pack": "BT1,EX1"})

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert {card["id"] for card in response.json()["cards"]} == {"BT1-001", "EX1-001"}


def test_search_cards_accepts_multiple_type_values(monkeypatch):
    """Ensure the type filter can match any selected value from a checkbox dropdown."""
    sample_cards = [
        {
            "id": "BT1-001",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-090",
            "name": "Gaia Force",
            "type": "Option",
            "color": "Red",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-087",
            "name": "Tai Kamiya",
            "type": "Tamer",
            "color": "Red",
            "set_name": ["BT-01"],
        },
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search", params={"card_type": "Digimon,Option"})

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert {card["id"] for card in response.json()["cards"]} == {"BT1-001", "BT1-090"}


def test_search_cards_requires_all_selected_colors_across_color_and_color2(monkeypatch):
    """Ensure multi-color filtering uses AND matching across primary and secondary colors."""
    sample_cards = [
        {
            "id": "BT1-001",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "color2": None,
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-002",
            "name": "Omnimon Alter-S",
            "type": "Digimon",
            "color": "Red",
            "color2": "Blue",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-003",
            "name": "Imperialdramon",
            "type": "Digimon",
            "color": "Green",
            "color2": "Blue",
            "set_name": ["BT-01"],
        },
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search", params={"color": "Red,Blue"})

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert {card["id"] for card in response.json()["cards"]} == {"BT1-002"}


def test_search_cards_accepts_multiple_digi_type_values(monkeypatch):
    """Ensure one digi type filter can match any selected value across all digi type fields."""
    sample_cards = [
        {
            "id": "BT1-001",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "digi_type": "Reptile",
            "digi_type2": "Dragonkin",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-002",
            "name": "Wizardmon",
            "type": "Digimon",
            "color": "Purple",
            "digi_type": "Wizard",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-003",
            "name": "Patamon",
            "type": "Digimon",
            "color": "Yellow",
            "digi_type": "Mammal",
            "set_name": ["BT-01"],
        },
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search", params={"digi_type": "Dragonkin,Wizard"})

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert {card["id"] for card in response.json()["cards"]} == {"BT1-001", "BT1-002"}


def test_search_cards_accepts_advanced_field_filters(monkeypatch):
    """Ensure advanced numeric and text-based field filters are applied by the card search route."""
    sample_cards = [
        {
            "id": "AD1-002",
            "name": "Aldamon",
            "type": "Digimon",
            "level": 5,
            "play_cost": 8,
            "evolution_cost": 3,
            "evolution_color": "Red",
            "evolution_level": 4,
            "xros_req": "Takuya Kanbara",
            "color": "Red",
            "color2": "Blue",
            "digi_type": "Wizard",
            "digi_type2": "Hybrid",
            "digi_type3": None,
            "digi_type4": None,
            "form": "Hybrid",
            "dp": 8000,
            "attribute": "Variable",
            "rarity": "SR",
            "stage": "Hybrid",
            "artist": "Artist A",
            "link_requirements": "Red trait",
            "link_dp": 2000,
            "set_name": ["AD-01"],
        },
        {
            "id": "BT1-010",
            "name": "Greymon",
            "type": "Digimon",
            "level": 4,
            "play_cost": 5,
            "evolution_cost": 2,
            "evolution_color": "Yellow",
            "evolution_level": 3,
            "xros_req": "Other card",
            "color": "Red",
            "color2": None,
            "digi_type": "Dragon",
            "form": "Champion",
            "dp": 4000,
            "attribute": "Vaccine",
            "rarity": "C",
            "stage": "Champion",
            "artist": "Artist B",
            "link_requirements": "Yellow trait",
            "link_dp": None,
            "set_name": ["BT-01"],
        },
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get(
        "/api/cards/search",
        params={
            "card_type": "Digimon",
            "level": "5",
            "play_cost": "8",
            "evolution_cost": "3",
            "evolution_color": "Red",
            "evolution_level": "4",
            "xros_req": "takuya",
            "color2": "Blue",
            "digi_type": "Wizard",
            "digi_type2": "Hybrid",
            "form": "hybrid",
            "dp": "8000",
            "attribute": "variable",
            "rarity": "sr",
            "stage": "hybrid",
            "artist": "artist a",
            "link_requirements": "red",
            "link_dp": "2000",
        },
    )

    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["cards"][0]["id"] == "AD1-002"


def test_get_card_sets_returns_unique_sorted_options(tmp_path, monkeypatch):
    """Ensure the set-options route returns sorted folder names from the export directory."""
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


def test_search_cards_rarity_filter_matches_exact_canonical_rarity(monkeypatch):
    """Ensure selecting rarity R only returns R cards, including lowercase source values."""
    sample_cards = [
        {
            "id": "BT1-001",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "rarity": "R",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-002",
            "name": "Greymon",
            "type": "Digimon",
            "color": "Red",
            "rarity": "SR",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-003",
            "name": "Birdramon",
            "type": "Digimon",
            "color": "Red",
            "rarity": "r",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-004",
            "name": "Omnimon",
            "type": "Digimon",
            "color": "White",
            "rarity": "UR",
            "set_name": ["BT-01"],
        },
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search", params={"rarity": "R"})

    assert response.status_code == 200
    assert response.json()["count"] == 2
    assert {card["id"] for card in response.json()["cards"]} == {"BT1-001", "BT1-003"}


def test_get_card_filter_options_returns_summary_data(tmp_path, monkeypatch):
    """Ensure the frontend can fetch summarized field options for advanced filters."""
    summary_file = tmp_path / "field_value_summary.json"
    summary_file.write_text(
        json.dumps({"rarity": {"C": 10, "R": 8}, "digi_type": {"Dragon": 4}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(api_module, "CARDS_DIR", tmp_path)

    response = client.get("/api/cards/filter-options")

    assert response.status_code == 200
    assert response.json()["filters"] == {
        "rarity": {"C": 10, "R": 8},
        "digi_type": {"Dragon": 4},
    }


def test_search_cards_exposes_restriction_limits(tmp_path, monkeypatch):
    """Ensure restricted cards include their allowed copy count for frontend badges."""
    restriction_file = tmp_path / "restricted_list.json"
    restriction_file.write_text(
        json.dumps({"card_limits": {"BT1-001": 1}, "banned_cards": ["BT1-002"]}),
        encoding="utf-8",
    )
    sample_cards = [
        {
            "id": "BT1-001",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-002",
            "name": "Gabumon",
            "type": "Digimon",
            "color": "Blue",
            "set_name": ["BT-01"],
        },
        {
            "id": "BT1-003",
            "name": "Patamon",
            "type": "Digimon",
            "color": "Yellow",
            "set_name": ["BT-01"],
        },
    ]
    monkeypatch.setattr(deck_module, "RESTRICTED_LIST_FILE", restriction_file)
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search")

    assert response.status_code == 200
    cards_by_id = {card["id"]: card for card in response.json()["cards"]}
    assert cards_by_id["BT1-001"]["restriction_limit"] == 1
    assert cards_by_id["BT1-002"]["restriction_limit"] == 0
    assert cards_by_id["BT1-003"]["restriction_limit"] is None


def test_search_cards_exposes_tcgplayer_fields(monkeypatch):
    """Ensure existing TCGplayer fields are passed through for safe frontend links."""
    sample_cards = [
        {
            "id": "BT1-001",
            "name": "Agumon",
            "type": "Digimon",
            "color": "Red",
            "tcgplayer_name": "Agumon",
            "tcgplayer_id": 483247,
            "set_name": ["BT-01"],
        }
    ]
    monkeypatch.setattr(api_module, "load_cards", lambda: sample_cards)

    response = client.get("/api/cards/search")

    assert response.status_code == 200
    assert response.json()["cards"][0]["tcgplayer_name"] == "Agumon"
    assert response.json()["cards"][0]["tcgplayer_id"] == 483247


def test_add_and_remove_current_deck_card(monkeypatch):
    """Verify that cards can be added to and removed from the active deck."""
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


def test_add_card_to_current_deck_caps_count_at_four(monkeypatch):
    """Ensure the active deck never allows more than four copies of one card."""
    monkeypatch.setattr(api_module, "current_deck_store", CurrentDeckStore())

    client.post(
        "/api/deck/add",
        json={"id": "BT1-001", "name": "Agumon", "card_type": "Digimon", "count": 4},
    )
    add_response = client.post(
        "/api/deck/add",
        json={"id": "BT1-001", "name": "Agumon", "card_type": "Digimon", "count": 1},
    )

    assert add_response.status_code == 200
    assert add_response.json()["cards"][0]["count"] == 4


def test_create_deck_rejects_more_than_four_copies():
    """Ensure deck creation rejects requests that exceed the per-card copy limit."""
    response = client.post(
        "/api/decks",
        json={
            "name": "Too Many Agumon",
            "cards": [
                {"id": "BT1-001", "name": "Agumon", "card_type": "Digimon", "count": 5}
            ],
        },
    )

    assert response.status_code == 422


def test_add_card_to_current_deck_rejects_restricted_limit(tmp_path, monkeypatch):
    """Ensure restriction-file copy limits are enforced during active deck updates."""
    restriction_file = tmp_path / "restricted_list.json"
    restriction_file.write_text(
        json.dumps({"card_limits": {"BT1-001": 1}}), encoding="utf-8"
    )
    monkeypatch.setattr(deck_module, "RESTRICTED_LIST_FILE", restriction_file)
    monkeypatch.setattr(api_module, "current_deck_store", CurrentDeckStore())

    client.post(
        "/api/deck/add",
        json={"id": "BT1-001", "name": "Agumon", "card_type": "Digimon", "count": 1},
    )
    add_response = client.post(
        "/api/deck/add",
        json={"id": "BT1-001", "name": "Agumon", "card_type": "Digimon", "count": 1},
    )

    assert add_response.status_code == 400
    assert "limited to 1 copy" in add_response.json()["detail"]


def test_create_deck_rejects_banned_card_from_restricted_list(tmp_path, monkeypatch):
    """Ensure saved decks cannot include cards listed as banned."""
    restriction_file = tmp_path / "restricted_list.json"
    restriction_file.write_text(
        json.dumps({"banned_cards": ["BT1-001"]}), encoding="utf-8"
    )
    monkeypatch.setattr(deck_module, "RESTRICTED_LIST_FILE", restriction_file)
    monkeypatch.setattr(
        api_module, "deck_manager", DeckManager(tmp_path / "saved_decks.json")
    )

    response = client.post(
        "/api/decks",
        json={
            "name": "Banned Card Deck",
            "cards": [
                {"id": "BT1-001", "name": "Agumon", "card_type": "Digimon", "count": 1}
            ],
        },
    )

    assert response.status_code == 400
    assert "banned" in response.json()["detail"].lower()


def test_create_deck_rejects_banned_pair_from_restricted_list(tmp_path, monkeypatch):
    """Ensure decks are rejected when they contain both sides of a banned pair."""
    restriction_file = tmp_path / "restricted_list.json"
    restriction_file.write_text(
        json.dumps({"banned_pairs": [{"a": "BT1-001", "b": "BT1-002"}]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(deck_module, "RESTRICTED_LIST_FILE", restriction_file)
    monkeypatch.setattr(
        api_module, "deck_manager", DeckManager(tmp_path / "saved_decks.json")
    )

    response = client.post(
        "/api/decks",
        json={
            "name": "Banned Pair Deck",
            "cards": [
                {"id": "BT1-001", "name": "Agumon", "card_type": "Digimon", "count": 1},
                {
                    "id": "BT1-002",
                    "name": "Gabumon",
                    "card_type": "Digimon",
                    "count": 1,
                },
            ],
        },
    )

    assert response.status_code == 400
    assert "banned pair" in response.json()["detail"].lower()


def test_search_cards_uses_remote_image_fallback(monkeypatch):
    """Verify that card search falls back to the remote CDN image URL when needed."""
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
    assert (
        response.json()["cards"][0]["image_url"]
        == "https://images.digimoncard.io/images/cards/BT1-010.webp"
    )


def test_normalize_card_prefers_local_image_when_available(monkeypatch):
    """Verify that locally downloaded images take priority over remote URLs."""
    monkeypatch.setattr(
        api_module, "get_local_image_url", lambda card_id: f"/images/{card_id}.webp"
    )

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
