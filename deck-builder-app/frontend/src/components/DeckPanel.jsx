export default function DeckPanel({
  deck,
  deckName,
  onDeckNameChange,
  onSaveDeck,
  onRemoveCard,
  onClearDeck,
  onLoadSavedDeck,
  savedDecks,
}) {
  return (
    <aside className="panel">
      <h2>Current Deck</h2>

      <div className="deck-summary">
        <span>{deck.total_cards || 0} cards</span>
        <span>{deck.cards?.length || 0} unique entries</span>
      </div>

      <div className="deck-actions">
        <input
          className="deck-name-input"
          value={deckName}
          onChange={(event) => onDeckNameChange(event.target.value)}
          placeholder="Deck name"
        />
        <button type="button" onClick={onSaveDeck}>Save Deck</button>
        <button type="button" className="secondary-button" onClick={onClearDeck}>Clear Deck</button>
      </div>

      <div className="deck-list">
        {deck.cards?.length ? (
          deck.cards.map((card) => (
            <div className="deck-entry" key={card.id || card.name}>
              <div>
                <strong>{card.name}</strong>
                <p>{card.card_type || 'Digimon'} • x{card.count}</p>
              </div>
              <button type="button" className="secondary-button" onClick={() => onRemoveCard(card)}>
                Remove
              </button>
            </div>
          ))
        ) : (
          <p className="card-empty">No cards added yet.</p>
        )}
      </div>

      <div className="saved-decks">
        <h3>Saved Decks</h3>
        {savedDecks.length ? (
          savedDecks.map((savedDeck) => (
            <div className="saved-deck" key={savedDeck.name}>
              <div>
                <strong>{savedDeck.name}</strong>
                <p>{savedDeck.cards?.length || 0} cards</p>
              </div>
              <button type="button" className="secondary-button" onClick={() => onLoadSavedDeck(savedDeck.name)}>
                Load
              </button>
            </div>
          ))
        ) : (
          <p className="card-empty">No saved decks yet.</p>
        )}
      </div>
    </aside>
  )
}
