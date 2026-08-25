"""Tests for deck persistence behavior and TCGplayer price fetching.

Main coverage: saving a deck and loading it back from storage, and
get_card_market_price/summarize_deck_pricing's caching, fallback, and
price-selection logic. requests.get is faked throughout rather than hit
for real, so these are deterministic and don't depend on TCGplayer's
actual API or rate limits.
"""

import requests

import app.deck as deck_module
from app.deck import (
    CurrentDeckStore,
    DeckManager,
    get_card_market_price,
    summarize_deck_pricing,
)
from app.models import Card, Deck


class _FakeRequestsResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error")

    def json(self):
        return self._payload


def test_save_and_get_deck(tmp_path):
    """Ensure a saved deck can be retrieved and listed correctly."""
    manager = DeckManager(tmp_path / "saved_decks.json")
    deck = Deck(name="Blue Flare", cards=[Card(name="Greymon", count=4)])

    saved = manager.save_deck(deck)

    assert saved["name"] == "Blue Flare"
    assert manager.get_deck("Blue Flare") is not None
    assert len(manager.list_decks()) == 1


def test_get_card_market_price_returns_none_without_tcgplayer_id():
    """No product ID means no lookup is even attempted."""
    assert get_card_market_price({"id": "BT1-010", "name": "Agumon"}) is None


def test_get_card_market_price_fetches_and_caches(monkeypatch):
    """A successful primary-endpoint fetch is cached, so a second call for
    the same product within the TTL shouldn't hit the network again."""
    call_count = {"n": 0}

    def fake_get(url, headers=None, timeout=None):
        call_count["n"] += 1
        assert "pricepoints" in url
        return _FakeRequestsResponse([{"printingType": "Normal", "marketPrice": 4.5}])

    monkeypatch.setattr(deck_module.requests, "get", fake_get)
    monkeypatch.setattr(deck_module, "TCGPLAYER_PRICE_CACHE", {})

    first = get_card_market_price({"tcgplayer_id": 111111})
    second = get_card_market_price({"tcgplayer_id": 111111})

    assert first == 4.5
    assert second == 4.5
    assert call_count["n"] == 1  # second call served from cache


def test_get_card_market_price_prefers_normal_printing_type(monkeypatch):
    """When multiple printings are returned, a "Normal" one should be
    preferred over foil/other variants, regardless of list order."""

    def fake_get(url, headers=None, timeout=None):
        return _FakeRequestsResponse(
            [
                {"printingType": "Foil", "marketPrice": 99.0},
                {"printingType": "Normal", "marketPrice": 2.25},
            ]
        )

    monkeypatch.setattr(deck_module.requests, "get", fake_get)
    monkeypatch.setattr(deck_module, "TCGPLAYER_PRICE_CACHE", {})

    price = get_card_market_price({"tcgplayer_id": 222222})

    assert price == 2.25


def test_get_card_market_price_falls_back_to_secondary_endpoint(monkeypatch):
    """If the primary pricepoints endpoint has nothing usable, the
    secondary details endpoint should be tried before giving up."""

    def fake_get(url, headers=None, timeout=None):
        if "pricepoints" in url:
            return _FakeRequestsResponse([])  # no price points at all
        return _FakeRequestsResponse({"marketPrice": 7.75})

    monkeypatch.setattr(deck_module.requests, "get", fake_get)
    monkeypatch.setattr(deck_module, "TCGPLAYER_PRICE_CACHE", {})

    price = get_card_market_price({"tcgplayer_id": 333333})

    assert price == 7.75


def test_get_card_market_price_returns_none_on_request_failure(monkeypatch):
    """A network error shouldn't raise -- pricing is best-effort."""

    def fake_get(url, headers=None, timeout=None):
        raise requests.ConnectionError("network is down")

    monkeypatch.setattr(deck_module.requests, "get", fake_get)
    monkeypatch.setattr(deck_module, "TCGPLAYER_PRICE_CACHE", {})

    assert get_card_market_price({"tcgplayer_id": 444444}) is None


def test_summarize_deck_pricing_aggregates_priced_and_unpriced_cards(monkeypatch):
    """A mix of priced and unpriced cards should total correctly and count
    each category, using count to scale each card's line cost."""

    def fake_get(url, headers=None, timeout=None):
        return _FakeRequestsResponse([{"printingType": "Normal", "marketPrice": 3.0}])

    monkeypatch.setattr(deck_module.requests, "get", fake_get)
    monkeypatch.setattr(deck_module, "TCGPLAYER_PRICE_CACHE", {})

    cards = [
        {"id": "BT1-010", "tcgplayer_id": 555555, "count": 2},  # priced: 3.00 * 2
        {"id": "BT1-011", "count": 1},  # no tcgplayer_id -> unpriced
    ]

    summary = summarize_deck_pricing(cards)

    assert summary["estimated_total_cost"] == 6.0
    assert summary["priced_cards"] == 1
    assert summary["missing_price_cards"] == 1
    assert cards[0]["estimated_line_cost"] == 6.0
    assert cards[1]["estimated_unit_price"] is None


def test_current_deck_exposes_estimated_total_cost(monkeypatch):
    """Ensure the current deck payload includes an estimated TCGplayer-based cost total."""
    store = CurrentDeckStore()
    store.cards = [
        {"id": "BT1-010", "name": "Agumon", "count": 2, "tcgplayer_id": 483247}
    ]

    monkeypatch.setattr(
        deck_module,
        "summarize_deck_pricing",
        lambda cards: {
            "estimated_total_cost": 1.5,
            "priced_cards": 1,
            "missing_price_cards": 0,
        },
        raising=False,
    )

    deck = store.get_deck()

    assert deck["estimated_total_cost"] == 1.5
    assert deck["priced_cards"] == 1
    assert deck["missing_price_cards"] == 0
