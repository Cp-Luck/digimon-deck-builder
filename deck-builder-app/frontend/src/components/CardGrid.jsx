import CardItem from './CardItem'

export default function CardGrid({ cards = [], loading, onAddCard, zoom = 50, onZoomChange }) {
  const normalizedZoom = Math.min(Math.max(Number(zoom) || 50, 50), 100)

  // The parent page already provides the left Filters and right Current Deck panels.
  // This component only controls the center results area and uses CSS variables so
  // the slider can make the card tiles denser or larger without changing colors.
  const zoomRatio = normalizedZoom / 50
  const gridStyle = {
    '--result-card-min': `${Math.round(142 * zoomRatio)}px`,
    '--result-card-max': `${Math.round(172 * zoomRatio)}px`,
    '--result-card-gap': `${Math.round(10 + 8 * zoomRatio)}px`,
    '--result-art-width': `${Math.round(96 * zoomRatio)}px`,
  }

  return (
    <section className="panel card-grid-panel">
      <div className="card-grid-header">
        <h2>Card Results</h2>

        <label className="card-zoom-control">
          <span className="card-zoom-label">Zoom</span>
          <input
            className="card-zoom-range"
            type="range"
            min="50"
            max="100"
            step="5"
            value={normalizedZoom}
            onChange={(event) => onZoomChange?.(Number(event.target.value))}
            aria-label="Adjust card result zoom"
          />
          <strong className="card-zoom-value">{normalizedZoom}%</strong>
        </label>
      </div>

      {loading ? (
        <p className="card-empty">Loading cards...</p>
      ) : cards.length === 0 ? (
        <p className="card-empty">No cards matched the current search.</p>
      ) : (
        <div className="card-grid" style={gridStyle}>
          {cards.map((card) => (
            <CardItem
              key={card.id || `${card.set_code || card.set_name}-${card.card_number || card.name}`}
              card={card}
              onAddCard={onAddCard}
            />
          ))}
        </div>
      )}
    </section>
  )
}
