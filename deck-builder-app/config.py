from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CARDS_DIR = DATA_DIR / "cards"

SAVED_DECKS_FILE = DATA_DIR / "saved_decks.json"
CARD_FILE = CARDS_DIR / "all_cards.json"
LAST_UPDATED_FILE = CARDS_DIR / "last_updated.txt"

BASE_URL = "https://digimoncard.io/api-public"
REQUEST_DELAY = 1.0
