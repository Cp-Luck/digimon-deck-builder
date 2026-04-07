# 🃏 Deck Builder App

A Digimon deck builder with a **React frontend** and **FastAPI backend**, backed by a locally cached card database.

---

## 📁 Project Structure

```text
deck-builder-app/
├─ backend/
│  ├─ app/                 # FastAPI routes, models, deck logic, storage helpers
│  ├─ data/
│  │  ├─ cards/            # all_cards.json, by_set/, last_updated.txt
│  │  ├─ decks/            # saved_decks.json
│  │  └─ images/           # downloaded local card images
│  ├─ scripts/             # update/sort/download helper scripts
│  ├─ tests/               # backend tests
│  ├─ config.py            # backend paths and API settings
│  ├─ main.py              # FastAPI app entry point
│  └─ requirements.txt
├─ frontend/               # React + Vite UI
└─ README.md
```

---

## 🚀 Run the app

### 1) Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend URLs:
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/api/health`

### 2) Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL:
- `http://127.0.0.1:5173/`

> If port `5173` is already in use, Vite may choose `5174` instead.

---

## ✅ Current features
- Search local Digimon cards
- Filter by name, color, type, and set
- Add/remove cards in the current deck
- Save and reload decks
- Refresh card data from the API
- Sort cards into set folders under `backend/data/cards/by_set/`
- Serve local card images from `backend/data/images/`

---

## ⚙️ Notable backend scripts

### `backend/scripts/update_cards.py`
Updates the local card database from the Digimon API.

What it does:
- fetches card data from the API
- skips already-saved complete cards
- refreshes cards with missing/null important fields
- dedupes entries by card ID
- updates `backend/data/cards/all_cards.json`
- writes the timestamp to `backend/data/cards/last_updated.txt`

Run it:

```bash
cd backend
/Users/calebpham/Documents/programing/DigimonCard_Recognizer/.venv/bin/python scripts/update_cards.py
```

---

### `backend/scripts/sortall_cards.py`
Sorts the local card database into folders by set code.

Example:
- `ST19-03` → `backend/data/cards/by_set/ST19/ST19-03.json`

It also creates:
- `cards.json` inside each set folder
- `index.json` for a summary of generated sets

Run it:

```bash
cd backend
/Users/calebpham/Documents/programing/DigimonCard_Recognizer/.venv/bin/python scripts/sortall_cards.py
```

---

### `backend/scripts/download_card_images.py`
Downloads card photos for local use and serves them through FastAPI.

Run a small test batch:

```bash
cd backend
/Users/calebpham/Documents/programing/DigimonCard_Recognizer/.venv/bin/python scripts/download_card_images.py --limit 50
```

Download the full set:

```bash
cd backend
/Users/calebpham/Documents/programing/DigimonCard_Recognizer/.venv/bin/python scripts/download_card_images.py
```

Downloaded images are stored in:

```text
backend/data/images/
```

and served like:

```text
http://127.0.0.1:8000/images/BT1-010.webp
```

---

## 🔌 Main API routes

### Health
- `GET /api/health` → backend status check

### Cards
- `GET /api/cards` → list cards with optional filters
- `GET /api/cards/search` → search cards by query/filter
- `GET /api/cards/local` → raw local cached card data
- `GET /api/cards/{card_id}` → full details for a single card

#### Supported card query params
- `q` → search text
- `color` → card color
- `card_type` → `Digimon`, `Option`, `Tamer`, etc.
- `pack` → set/pack text
- `limit` → max results returned

Example:

```bash
curl "http://127.0.0.1:8000/api/cards/search?q=agumon&color=red&limit=5"
```

### Current deck
- `GET /api/deck` → current in-memory deck
- `POST /api/deck/add` → add a card to current deck
- `POST /api/deck/remove` → remove/decrement a card
- `POST /api/deck/clear` → clear current deck
- `POST /api/deck/load` → load a saved deck into current deck state

### Saved decks
- `GET /api/decks` → list saved decks
- `GET /api/decks/{deck_name}` → get a saved deck by name
- `POST /api/decks` → save or update a deck

---

## 🧠 Notable backend files

### `backend/main.py`
- creates the FastAPI app
- enables CORS for the React frontend
- mounts `/images` as static files
- includes the API router

### `backend/app/api.py`
Contains the main API routes and card normalization logic.

### `backend/app/deck.py`
Contains:
- `DeckManager` for saved deck persistence
- `CurrentDeckStore` for the active in-memory deck

### `backend/app/storage.py`
Contains helpers for:
- loading/saving JSON
- deduping cards
- deciding whether a card should be refreshed
- getting card identifiers

### `backend/config.py`
Stores important paths and constants, including:
- `CARD_FILE`
- `LAST_UPDATED_FILE`
- `IMAGES_DIR`
- `BASE_URL`
- `REQUEST_DELAY`

---

## 🎨 Frontend notes

The React frontend in `frontend/` uses Vite and talks to the backend through `/api` and `/images`.

Notable frontend files:
- `frontend/src/App.jsx` → main UI state and API calls
- `frontend/src/components/SearchBar.jsx`
- `frontend/src/components/FilterPanel.jsx`
- `frontend/src/components/CardGrid.jsx`
- `frontend/src/components/CardItem.jsx`
- `frontend/src/components/DeckPanel.jsx`

---

## 🧪 Testing

Run backend tests:

```bash
cd backend
/Users/calebpham/Documents/programing/DigimonCard_Recognizer/.venv/bin/python -m pytest -q
```

---

## 🔗 API Source
- `https://digimoncard.io/api-public/`
- card pages/images are available through `https://digimoncard.io/` and `https://images.digimoncard.io/`
