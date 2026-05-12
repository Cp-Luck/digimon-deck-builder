import CardItem from './CardItem'

export default function CardGrid({ cards, loading, onAddCard, zoom = 100, onZoomChange }) {
  const normalizedZoom = Math.min(Math.max(Number(zoom) || 100, 50), 180)
  const zoomScale = 0.55 + (normalizedZoom / 100) * 0.9
  const gridStyle = {
    '--card-min-width': `${Math.round(210 * zoomScale)}px`,
    '--card-art-min-height': `${Math.round(160 * zoomScale)}px`,
    '--card-gap': `${Math.max(8, Math.round(12 * zoomScale))}px`,
    '--card-item-gap': `${Math.max(6, Math.round(9 * zoomScale))}px`,
  }

  return (
    <section className="panel card-grid-panel">
      <div className="card-grid-header">
        <h2>Card Results</h2>

        <label className="card-zoom-control">
          <span className="card-zoom-label">
            <span>Zoom</span>
            <strong>{normalizedZoom}%</strong>
          </span>
          <input
            className="card-zoom-range"
            type="range"
            min="50"
            max="180"
            step="5"
            value={normalizedZoom}
            onChange={(event) => onZoomChange?.(Number(event.target.value))}
            aria-label="Adjust card result zoom"
          />
        </label>
      </div>

      {loading ? (
        <p className="card-empty">Loading cards...</p>
      ) : cards.length === 0 ? (
        <p className="card-empty">No cards matched the current search.</p>
      ) : (
        <div className="card-grid" style={gridStyle}>
          {cards.map((card) => (
            <CardItem key={card.id || `${card.name}-${card.type}`} card={card} onAddCard={onAddCard} />
          ))}
        </div>
      )}
    </section>
  )
}
