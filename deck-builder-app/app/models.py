from typing import List

from pydantic import BaseModel, Field


class Card(BaseModel):
    name: str
    card_type: str = Field(default="Digimon")
    count: int = Field(default=1, ge=1)


class Deck(BaseModel):
    name: str
    cards: List[Card] = Field(default_factory=list)
