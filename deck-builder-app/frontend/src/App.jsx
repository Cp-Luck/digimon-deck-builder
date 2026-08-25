import { useEffect, useMemo, useState } from 'react'
import SearchBar from './components/SearchBar'
import FilterPanel from './components/FilterPanel'
import CardGrid from './components/CardGrid'
import DeckPanel from './components/DeckPanel'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const defaultFilters = {
  q: '',
  color: [],
  card_type: [],
  pack: [],
  level: '',
  play_cost: '',
  evolution_cost: '',
  evolution_color: '',
  evolution_level: '',
  xros_req: '',
  digi_type: [],
  form: '',
  dp: '',
  attribute: '',
  rarity: '',
  stage: '',
  artist: '',
  link_requirements: '',
  link_dp: '',
}

function parseCardId(cardId) {
  const normalized = String(cardId || '').trim().toUpperCase()
  const match = normalized.match(/^(?<prefix>[A-Z]+)(?<setNumber>\d*)-(?<cardNumber>\d+)(?<suffix>[A-Z]*)$/)

  if (match?.groups) {
    return {
      prefix: match.groups.prefix || '',
      setNumber: Number(match.groups.setNumber || 0),
      cardNumber: Number(match.groups.cardNumber || 0),
      suffix: match.groups.suffix || '',
      raw: normalized,
    }
  }

  const [prefix = '', remainder = ''] = normalized.split('-', 2)
  const cardNumber = Number((remainder.match(/\d+/) || ['0'])[0])
  const suffix = (remainder.match(/[A-Z]+$/) || [''])[0]

  return {
    prefix,
    setNumber: Number((prefix.match(/\d+/) || ['0'])[0]),
    cardNumber,
    suffix,
    raw: normalized,
  }
}

function compareCardsById(leftCard, rightCard) {
  const left = parseCardId(leftCard?.id)
  const right = parseCardId(rightCard?.id)

  return (
    left.prefix.localeCompare(right.prefix) ||
    left.setNumber - right.setNumber ||
    left.cardNumber - right.cardNumber ||
    left.suffix.localeCompare(right.suffix) ||
    String(leftCard?.name || '').localeCompare(String(rightCard?.name || ''))
  )
}

function sortCardsById(cards = []) {
  return [...cards].sort(compareCardsById)
}

function normalizeDeckOrder(deckData) {
  return {
    ...deckData,
    cards: sortCardsById(deckData?.cards || []),
  }
}

// FastAPI validation failures (banned card, over the copy limit, etc.) come
// back as `{"detail": "..."}` with a non-2xx status. Every deck-mutating
// call below routes its response through this instead of parsing the body
// unconditionally — otherwise an error body gets treated as a deck payload,
// and normalizeDeckOrder's `cards: sortCardsById(deckData?.cards || [])`
// silently turns "banned card" into "your deck is now empty" with no
// indication anything went wrong.
async function parseDeckResponse(response) {
  const data = await response.json().catch(() => ({}))
  if (!response.ok) {
    throw new Error(data.detail || `Request failed (${response.status})`)
  }
  return data
}

function App() {
  const [filters, setFilters] = useState(defaultFilters)
  const [cards, setCards] = useState([])
  const [setOptions, setSetOptions] = useState([])
  const [filterOptions, setFilterOptions] = useState({})
  const [deck, setDeck] = useState({ name: 'Current Deck', cards: [], total_cards: 0 })
  const [savedDecks, setSavedDecks] = useState([])
  const [deckName, setDeckName] = useState('My Digimon Deck')
  const [status, setStatus] = useState('Loading cards...')
  const [loadingCards, setLoadingCards] = useState(false)
  const [lastUpdated, setLastUpdated] = useState('')
  const [cardZoom, setCardZoom] = useState(100)

  const searchParams = useMemo(() => {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (Array.isArray(value)) {
        if (value.length) {
          params.set(key, value.join(','))
        }
        return
      }

      if (value) {
        params.set(key, value)
      }
    })
    params.set('limit', '120')
    return params.toString()
  }, [filters])

  useEffect(() => {
    fetchCards()
    // fetchCards is redefined every render but always closes over the
    // current searchParams, and this effect is already correctly gated on
    // searchParams itself -- adding the function to the dep array would
    // just re-run this on every render instead of only when the query
    // actually changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams])

  useEffect(() => {
    fetchCurrentDeck()
    fetchSavedDecks()
    fetchSetOptions()
    fetchFilterOptions()
  }, [])

  async function fetchCards() {
    setLoadingCards(true)
    try {
      const response = await fetch(`${API_BASE}/cards/search?${searchParams}`)
      const data = await response.json()
      setCards(sortCardsById(data.cards || []))
      setStatus(`Showing ${data.count ?? 0} cards from the local database.`)

      if (data.last_updated && data.last_updated !== lastUpdated) {
        setLastUpdated(data.last_updated)
        fetchSetOptions()
        fetchFilterOptions()
      }
    } catch (error) {
      setStatus(`Could not load cards: ${error.message}`)
    } finally {
      setLoadingCards(false)
    }
  }

  async function fetchCurrentDeck() {
    try {
      const response = await fetch(`${API_BASE}/deck`)
      const data = await response.json()
      setDeck(normalizeDeckOrder(data))
    } catch (error) {
      setStatus(`Could not load current deck: ${error.message}`)
    }
  }

  async function fetchSetOptions() {
    try {
      const response = await fetch(`${API_BASE}/cards/sets`)
      const data = await response.json()
      setSetOptions(data.sets || [])
    } catch {
      setSetOptions([])
    }
  }

  async function fetchFilterOptions() {
    try {
      const response = await fetch(`${API_BASE}/cards/filter-options`)
      const data = await response.json()
      setFilterOptions(data.filters || {})
    } catch {
      setFilterOptions({})
    }
  }

  async function fetchSavedDecks() {
    try {
      const response = await fetch(`${API_BASE}/decks`)
      const data = await response.json()
      setSavedDecks(data.decks || [])
    } catch {
      setSavedDecks([])
    }
  }

  async function addCard(card) {
    const payload = {
      id: card.id,
      name: card.name,
      card_type: card.type || 'Digimon',
      color: card.color || null,
      image_url: card.image_url || null,
      level: card.level ?? null,
      play_cost: card.play_cost ?? null,
      tcgplayer_id: card.tcgplayer_id ?? null,
      tcgplayer_name: card.tcgplayer_name || card.name || null,
      count: 1,
    }

    try {
      const response = await fetch(`${API_BASE}/deck/add`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await parseDeckResponse(response)
      setDeck(normalizeDeckOrder(data))
    } catch (error) {
      setStatus(`Could not add card: ${error.message}`)
    }
  }

  async function removeCard(card) {
    const payload = {
      id: card.id,
      name: card.name,
      card_type: card.card_type || card.type || 'Digimon',
      count: 1,
    }

    try {
      const response = await fetch(`${API_BASE}/deck/remove`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      const data = await parseDeckResponse(response)
      setDeck(normalizeDeckOrder(data))
    } catch (error) {
      setStatus(`Could not remove card: ${error.message}`)
    }
  }

  async function clearDeck() {
    try {
      const response = await fetch(`${API_BASE}/deck/clear`, { method: 'POST' })
      const data = await parseDeckResponse(response)
      setDeck(normalizeDeckOrder(data))
    } catch (error) {
      setStatus(`Could not clear deck: ${error.message}`)
    }
  }

  async function saveDeck() {
    if (!deck.cards.length) {
      setStatus('Add at least one card before saving a deck.')
      return
    }

    try {
      const response = await fetch(`${API_BASE}/decks`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: deckName.trim() || 'My Digimon Deck',
          cards: deck.cards,
        }),
      })
      const data = await parseDeckResponse(response)
      setStatus(data.message || 'Deck saved successfully.')
      setDeckName(data.deck?.name || deckName)
      fetchSavedDecks()
    } catch (error) {
      setStatus(`Could not save deck: ${error.message}`)
    }
  }

  async function loadSavedDeck(name) {
    try {
      const response = await fetch(`${API_BASE}/decks/${encodeURIComponent(name)}`)
      const data = await parseDeckResponse(response)

      const loadResponse = await fetch(`${API_BASE}/deck/load`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      })
      const loadedDeck = await parseDeckResponse(loadResponse)

      setDeck(normalizeDeckOrder(loadedDeck))
      setDeckName(data.name || name)
      setStatus(`Loaded saved deck: ${name}`)
    } catch (error) {
      setStatus(`Could not load saved deck: ${error.message}`)
    }
  }

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">React + FastAPI</p>
          <h1>Digimon Deck Builder</h1>
          <p className="hero-text">
            Search your local Digimon card database, build a deck, and save it for later.
          </p>
        </div>
        <SearchBar
          value={filters.q}
          onChange={(value) => setFilters((current) => ({ ...current, q: value }))}
          onClear={() => setFilters(defaultFilters)}
        />
      </header>

      <p className="status-banner">{status}</p>

      <main className="layout-grid">
        <FilterPanel
          filters={filters}
          onChange={setFilters}
          setOptions={setOptions}
          fieldOptions={filterOptions}
        />
        <CardGrid
          cards={cards}
          loading={loadingCards}
          onAddCard={addCard}
          zoom={cardZoom}
          onZoomChange={setCardZoom}
        />
        <DeckPanel
          deck={deck}
          deckName={deckName}
          onDeckNameChange={setDeckName}
          onSaveDeck={saveDeck}
          onRemoveCard={removeCard}
          onClearDeck={clearDeck}
          onLoadSavedDeck={loadSavedDeck}
          savedDecks={savedDecks}
        />
      </main>
    </div>
  )
}

export default App
