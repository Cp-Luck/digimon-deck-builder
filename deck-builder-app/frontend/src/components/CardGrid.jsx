import CardItem from './CardItem'

export default function CardGrid({ cards, loading, onAddCard }) {
  return (
    <section className="panel">
      <h2>Card Results</h2>
      {loading ? (
        <p className="card-empty">Loading cards...</p>
      ) : cards.length === 0 ? (
        <p className="card-empty">No cards matched the current search.</p>
      ) : (
        <div className="card-grid">
          {cards.map((card) => (
            <CardItem key={card.id || `${card.name}-${card.type}`} card={card} onAddCard={onAddCard} />
          ))}
        </div>
      )}
    </section>
  )
}
