"""Pydantic models shared by the deck builder API.

Main models: `Card` for individual cards and `Deck` for saved or active deck payloads.
"""

from typing import List

from pydantic import BaseModel, Field


class Card(BaseModel):
    """Represents a single card entry used by the API and deck builder."""

    id: str | None = None
    name: str
    card_type: str = Field(default="Digimon")
    color: str | None = None
    image_url: str | None = None
    level: int | None = None
    play_cost: int | None = None
    tcgplayer_id: int | None = None
    tcgplayer_name: str | None = None
    count: int = Field(default=1, ge=1, le=4)


class Deck(BaseModel):
    """Represents a named deck containing a list of card entries."""

    name: str = "My Deck"
    cards: List[Card] = Field(default_factory=list)
