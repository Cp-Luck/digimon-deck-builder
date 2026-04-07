from typing import List

from pydantic import BaseModel, Field


class Card(BaseModel):
    id: str | None = None
    name: str
    card_type: str = Field(default="Digimon")
    color: str | None = None
    image_url: str | None = None
    level: int | None = None
    play_cost: int | None = None
    count: int = Field(default=1, ge=1, le=4)


class Deck(BaseModel):
    name: str = "My Deck"
    cards: List[Card] = Field(default_factory=list)
