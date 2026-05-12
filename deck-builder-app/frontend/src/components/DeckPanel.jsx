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
  const estimatedDeckCost =
    typeof deck.estimated_total_cost === 'number' ? `$${deck.estimated_total_cost.toFixed(2)}` : '—'

  return (
    <aside className="panel deck-panel">
      <h2>Current Deck</h2>

      <div className="deck-summary">
        <span>{deck.total_cards || 0} cards</span>
        <span>{deck.cards?.length || 0} unique entries</span>
      </div>

      <div className="deck-cost-summary">
        <span>Est. TCGplayer Cost</span>
        <strong>{estimatedDeckCost}</strong>
      </div>

      <p className="deck-price-note">
        {deck.missing_price_cards
          ? `Price unavailable for ${deck.missing_price_cards} ${deck.missing_price_cards === 1 ? 'entry' : 'entries'}.`
          : 'Based on current TCGplayer market prices.'}
      </p>

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
                {typeof card.estimated_line_cost === 'number' ? (
                  <p className="deck-entry-price">
                    ${card.estimated_line_cost.toFixed(2)} total
                    {typeof card.estimated_unit_price === 'number'
                      ? ` • $${card.estimated_unit_price.toFixed(2)} each`
                      : ''}
                  </p>
                ) : null}
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
