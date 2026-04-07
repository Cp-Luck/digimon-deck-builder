import { useEffect, useMemo, useState } from 'react'
import SearchBar from './components/SearchBar'
import FilterPanel from './components/FilterPanel'
import CardGrid from './components/CardGrid'
import DeckPanel from './components/DeckPanel'

const API_BASE = import.meta.env.VITE_API_BASE || '/api'

const defaultFilters = {
  q: '',
  color: '',
  card_type: '',
  pack: '',
}

function App() {
  const [filters, setFilters] = useState(defaultFilters)
  const [cards, setCards] = useState([])
  const [deck, setDeck] = useState({ name: 'Current Deck', cards: [], total_cards: 0 })
  const [savedDecks, setSavedDecks] = useState([])
  const [deckName, setDeckName] = useState('My Digimon Deck')
  const [status, setStatus] = useState('Loading cards...')
  const [loadingCards, setLoadingCards] = useState(false)

  const searchParams = useMemo(() => {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        params.set(key, value)
      }
    })
    params.set('limit', '120')
    return params.toString()
  }, [filters])

  useEffect(() => {
    fetchCards()
  }, [searchParams])

  useEffect(() => {
    fetchCurrentDeck()
    fetchSavedDecks()
  }, [])

  async function fetchCards() {
    setLoadingCards(true)
    try {
      const response = await fetch(`${API_BASE}/cards/search?${searchParams}`)
      const data = await response.json()
      setCards(data.cards || [])
      setStatus(`Showing ${data.count ?? 0} cards from the local database.`)
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
      setDeck(data)
    } catch (error) {
      setStatus(`Could not load current deck: ${error.message}`)
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
      count: 1,
    }

    const response = await fetch(`${API_BASE}/deck/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await response.json()
    setDeck(data)
  }

  async function removeCard(card) {
    const payload = {
      id: card.id,
      name: card.name,
      card_type: card.card_type || card.type || 'Digimon',
      count: 1,
    }

    const response = await fetch(`${API_BASE}/deck/remove`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    const data = await response.json()
    setDeck(data)
  }

  async function clearDeck() {
    const response = await fetch(`${API_BASE}/deck/clear`, { method: 'POST' })
    const data = await response.json()
    setDeck(data)
  }

  async function saveDeck() {
    if (!deck.cards.length) {
      setStatus('Add at least one card before saving a deck.')
      return
    }

    const response = await fetch(`${API_BASE}/decks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: deckName.trim() || 'My Digimon Deck',
        cards: deck.cards,
      }),
    })
    const data = await response.json()
    setStatus(data.message || 'Deck saved successfully.')
    setDeckName(data.deck?.name || deckName)
    fetchSavedDecks()
  }

  async function loadSavedDeck(name) {
    const response = await fetch(`${API_BASE}/decks/${encodeURIComponent(name)}`)
    const data = await response.json()

    const loadResponse = await fetch(`${API_BASE}/deck/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    const loadedDeck = await loadResponse.json()

    setDeck(loadedDeck)
    setDeckName(data.name || name)
    setStatus(`Loaded saved deck: ${name}`)
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
        <FilterPanel filters={filters} onChange={setFilters} />
        <CardGrid cards={cards} loading={loadingCards} onAddCard={addCard} />
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
