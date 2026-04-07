import scripts.update_cards as updater


def test_dedupe_cards_keeps_unique_cardnumbers():
    from app.storage import dedupe_cards

    cards = [
        {"cardnumber": "BT1-001", "name": "Agumon"},
        {"cardnumber": "BT1-001", "name": "Agumon Updated"},
        {"cardnumber": "BT1-002", "name": "Greymon"},
    ]

    deduped = dedupe_cards(cards)

    assert len(deduped) == 2
    assert {card["cardnumber"] for card in deduped} == {"BT1-001", "BT1-002"}
    assert next(card for card in deduped if card["cardnumber"] == "BT1-001")["name"] == "Agumon Updated"


def test_update_cards_only_fetches_missing_numbers(monkeypatch):
    existing_cards = [{"cardnumber": "BT1-001", "name": "Agumon"}]
    basic_cards = [
        {"cardnumber": "BT1-001"},
        {"cardnumber": "BT1-002"},
    ]
    searched_numbers: list[str] = []
    saved_payload: dict[str, list[dict]] = {}

    monkeypatch.setattr(updater, "get_all_cards_basic", lambda: basic_cards)
    monkeypatch.setattr(updater, "load_cards", lambda: existing_cards)

    def fake_search(card_number: str):
        searched_numbers.append(card_number)
        return {"cardnumber": card_number, "name": "Greymon"}

    monkeypatch.setattr(updater, "search_card_by_number", fake_search)
    monkeypatch.setattr(updater, "save_last_updated", lambda: None)
    monkeypatch.setattr(updater, "save_cards", lambda cards: saved_payload.setdefault("cards", cards))

    updater.update_cards()

    assert searched_numbers == ["BT1-002"]
    assert len(saved_payload["cards"]) == 2
    assert {card["cardnumber"] for card in saved_payload["cards"]} == {"BT1-001", "BT1-002"}


def test_update_cards_refreshes_incomplete_saved_cards(monkeypatch):
    existing_cards = [{
        "id": "ST21-04",
        "name": "New Card",
        "type": "Digimon",
        "color": "Red",
        "rarity": None,
        "set_name": [],
        "play_cost": None,
        "level": None,
        "dp": None,
    }]
    basic_cards = [{"id": "ST21-04"}]
    searched_numbers: list[str] = []
    saved_payload: dict[str, list[dict]] = {}

    monkeypatch.setattr(updater, "get_all_cards_basic", lambda: basic_cards)
    monkeypatch.setattr(updater, "load_cards", lambda: existing_cards)

    def fake_search(card_number: str):
        searched_numbers.append(card_number)
        return {
            "id": "ST21-04",
            "name": "New Card",
            "type": "Digimon",
            "color": "Red",
            "rarity": "R",
            "set_name": ["Starter Deck"],
            "play_cost": 3,
            "level": 3,
            "dp": 1000,
        }

    monkeypatch.setattr(updater, "search_card_by_number", fake_search)
    monkeypatch.setattr(updater, "save_last_updated", lambda: None)
    monkeypatch.setattr(updater, "save_cards", lambda cards: saved_payload.__setitem__("cards", cards))

    updater.update_cards()

    assert searched_numbers == ["ST21-04"]
    assert len(saved_payload["cards"]) == 1
    assert saved_payload["cards"][0]["rarity"] == "R"
    assert saved_payload["cards"][0]["play_cost"] == 3
