export default function CardItem({ card, onAddCard }) {
  const setLabel = Array.isArray(card.set_name) ? card.set_name[0] : card.set_name

  return (
    <article className="panel card-item">
      <div className="card-art">
        {card.image_url ? (
          <img src={card.image_url} alt={card.name} loading="lazy" />
        ) : (
          <div>
            <div className="card-id">{card.id || 'Unknown ID'}</div>
            <div>{card.name}</div>
          </div>
        )}
      </div>

      <div className="card-meta">
        <strong>{card.name}</strong>
        <p className="card-id">{card.id}</p>
        <p>{card.type || 'Unknown type'} • {card.color || 'No color'}</p>
        <p>Level: {card.level ?? '—'} • Cost: {card.play_cost ?? '—'}</p>
        <p>{setLabel || 'Set not listed yet'}</p>
      </div>

      <button type="button" onClick={() => onAddCard(card)}>
        Add to Deck
      </button>
    </article>
  )
}
