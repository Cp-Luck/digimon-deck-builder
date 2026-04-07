import time
from typing import Any

import requests
from fastapi import APIRouter, HTTPException, Query

from app.deck import CurrentDeckStore, DeckManager
from app.models import Card, Deck
from app.storage import get_card_identifier, get_last_updated, load_cards
from config import BASE_URL, CARDS_DIR, IMAGES_DIR, REMOTE_IMAGE_BASE_URL, REQUEST_DELAY

router = APIRouter(prefix="/api", tags=["decks", "cards"])
deck_manager = DeckManager()
current_deck_store = CurrentDeckStore()


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


def _card_set_names(card: dict[str, Any]) -> list[str]:
    set_name = card.get("set_name")
    if isinstance(set_name, list):
        return [str(item) for item in set_name]
    if set_name:
        return [str(set_name)]
    return []


def build_remote_image_url(card_id: str | None) -> str | None:
    if card_id is None:
        return None
    normalized_card_id = card_id.strip().upper()
    if not normalized_card_id:
        return None
    return f"{REMOTE_IMAGE_BASE_URL}/{normalized_card_id}.webp"


def get_local_image_url(card_id: str | None) -> str | None:
    if card_id is None:
        return None
    normalized_card_id = card_id.strip().upper()
    if not normalized_card_id:
        return None

    image_path = IMAGES_DIR / f"{normalized_card_id}.webp"
    return f"/images/{image_path.name}" if image_path.exists() else None


def resolve_card_image_url(card: dict[str, Any]) -> str | None:
    card_id = get_card_identifier(card)
    return (
        get_local_image_url(card_id)
        or card.get("image_url")
        or card.get("img_url")
        or build_remote_image_url(card_id)
    )


def _normalize_card(card: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": get_card_identifier(card),
        "name": card.get("name"),
        "type": card.get("type"),
        "color": card.get("color"),
        "level": card.get("level"),
        "play_cost": card.get("play_cost"),
        "rarity": card.get("rarity"),
        "set_name": _card_set_names(card),
        "image_url": resolve_card_image_url(card),
        "pretty_url": card.get("pretty_url"),
        "main_effect": card.get("main_effect"),
        "source_effect": card.get("source_effect"),
    }


def _parse_pack_filters(pack: str) -> list[str]:
    return [value.strip().upper() for value in pack.split(",") if value.strip()]


def _card_set_code(card: dict[str, Any]) -> str:
    card_id = str(get_card_identifier(card) or "").strip().upper()
    return card_id.split("-", 1)[0] if card_id else ""


def _set_code_sort_key(set_code: str) -> tuple[str, int, str]:
    prefix = "".join(character for character in set_code if character.isalpha())
    number = "".join(character for character in set_code if character.isdigit())
    return (prefix, int(number) if number else 0, set_code)


def _matches_card_filters(
    card: dict[str, Any],
    q: str = "",
    color: str = "",
    card_type: str = "",
    pack: str = "",
) -> bool:
    normalized_name = str(card.get("name") or "").lower()
    normalized_id = str(get_card_identifier(card) or "").lower()
    normalized_type = str(card.get("type") or "").lower()
    normalized_color = str(card.get("color") or "").lower()
    normalized_sets = " ".join(_card_set_names(card)).lower()
    normalized_set_code = _card_set_code(card).lower()
    normalized_query = q.strip().lower()
    selected_packs = _parse_pack_filters(pack)

    if normalized_query and normalized_query not in " ".join(
        [normalized_name, normalized_id, normalized_type, normalized_sets, normalized_set_code]
    ):
        return False
    if color and normalized_color != color.strip().lower():
        return False
    if card_type and normalized_type != card_type.strip().lower():
        return False
    if selected_packs and normalized_set_code.upper() not in selected_packs:
        return False
    return True


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/cards")
def get_cards(
    q: str = Query(default=""),
    color: str = Query(default=""),
    card_type: str = Query(default=""),
    pack: str = Query(default=""),
    limit: int = Query(default=60, ge=1, le=500),
) -> dict[str, Any]:
    filtered_cards = [
        _normalize_card(card)
        for card in load_cards()
        if isinstance(card, dict) and _matches_card_filters(card, q=q, color=color, card_type=card_type, pack=pack)
    ]
    return {
        "count": len(filtered_cards),
        "cards": filtered_cards[:limit],
        "last_updated": get_last_updated(),
    }


@router.get("/cards/search")
def search_cards(
    q: str = Query(default=""),
    color: str = Query(default=""),
    card_type: str = Query(default=""),
    pack: str = Query(default=""),
    limit: int = Query(default=60, ge=1, le=500),
) -> dict[str, Any]:
    return get_cards(q=q, color=color, card_type=card_type, pack=pack, limit=limit)


@router.get("/cards/sets")
def get_card_sets() -> dict[str, list[str]]:
    by_set_dir = CARDS_DIR / "by_set"
    set_codes = []

    if by_set_dir.exists():
        set_codes = [entry.name for entry in by_set_dir.iterdir() if entry.is_dir()]

    if not set_codes:
        set_codes = list(
            {
                _card_set_code(card)
                for card in load_cards()
                if isinstance(card, dict) and _card_set_code(card)
            }
        )

    return {"sets": sorted(set_codes, key=_set_code_sort_key)}


@router.get("/cards/local")
def get_local_cards() -> dict[str, Any]:
    return {
        "cards": load_cards(),
        "last_updated": get_last_updated(),
    }


@router.get("/cards/{card_id}")
def get_card_detail(card_id: str) -> dict[str, Any]:
    normalized_card_id = card_id.strip().upper()
    for card in load_cards():
        if isinstance(card, dict) and get_card_identifier(card) == normalized_card_id:
            return card
    raise HTTPException(status_code=404, detail="Card not found")


@router.get("/deck")
def get_current_deck() -> dict[str, Any]:
    return current_deck_store.get_deck()


@router.post("/deck/add")
def add_card_to_deck(card: Card) -> dict[str, Any]:
    return current_deck_store.add_card(card)


@router.post("/deck/remove")
def remove_card_from_deck(card: Card) -> dict[str, Any]:
    return current_deck_store.remove_card(card)


@router.post("/deck/clear")
def clear_current_deck() -> dict[str, Any]:
    return current_deck_store.clear()


@router.post("/deck/load")
def load_current_deck(deck: Deck) -> dict[str, Any]:
    return current_deck_store.set_deck(deck)


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
