import time
from typing import Any

import requests
from fastapi import APIRouter, HTTPException

from app.deck import DeckManager
from app.models import Deck
from app.storage import get_last_updated, load_cards
from config import BASE_URL, REQUEST_DELAY

router = APIRouter(prefix="/api", tags=["decks", "cards"])
deck_manager = DeckManager()


def get_all_cards_basic() -> list[dict[str, Any]]:
    url = f"{BASE_URL}/getAllCards"
    params = {
        "sort": "name",
        "series": "Digimon Card Game",
        "sortdirection": "asc",
    }
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if isinstance(payload, list):
        return payload

    if isinstance(payload, dict):
        for key in ("cards", "results", "data"):
            value = payload.get(key)
            if isinstance(value, list):
                return value
        return [payload]

    return []


def search_card_by_number(card_number: str) -> Any:
    url = f"{BASE_URL}/search"
    params = {"card": card_number}
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    time.sleep(REQUEST_DELAY)
    return response.json()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/decks")
def get_decks() -> dict[str, list[dict[str, Any]]]:
    return {"decks": deck_manager.list_decks()}


@router.get("/decks/{deck_name}")
def get_deck(deck_name: str) -> dict[str, Any]:
    deck = deck_manager.get_deck(deck_name)
    if deck is None:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck


@router.post("/decks")
def create_or_update_deck(deck: Deck) -> dict[str, Any]:
    saved_deck = deck_manager.save_deck(deck)
    return {"message": "Deck saved successfully", "deck": saved_deck}


@router.get("/cards/local")
def get_local_cards() -> dict[str, Any]:
    return {
        "cards": load_cards(),
        "last_updated": get_last_updated(),
    }
