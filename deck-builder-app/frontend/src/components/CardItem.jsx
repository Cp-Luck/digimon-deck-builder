import { useMemo, useState } from 'react'

export default function CardItem({ card, onAddCard }) {
  const setLabel = Array.isArray(card.set_name) ? card.set_name[0] : card.set_name
  const [imageFailed, setImageFailed] = useState(false)

  const imageSrc = useMemo(() => {
    if (!card.image_url) {
      return null
    }
    if (card.image_url.startsWith('/')) {
      return card.image_url
    }
    return card.image_url
  }, [card.image_url])

  return (
    <article className="panel card-item">
      <div className="card-art">
        {imageSrc && !imageFailed ? (
          <img src={imageSrc} alt={card.name} loading="lazy" onError={() => setImageFailed(true)} />
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
