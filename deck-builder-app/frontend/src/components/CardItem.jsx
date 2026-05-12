import { useEffect, useMemo, useState } from 'react'
import { createPortal } from 'react-dom'
import { buildTcgplayerUrl } from '../utils/cardLinks'

function renderDetailRow(label, value) {
  if (value === null || value === undefined || value === '') {
    return null
  }

  return (
    <p>
      <strong>{label}:</strong> {value}
    </p>
  )
}

export default function CardItem({ card, onAddCard }) {
  const setLabel = Array.isArray(card.set_name) ? card.set_name[0] : card.set_name
  const [imageFailed, setImageFailed] = useState(false)
  const [showDetails, setShowDetails] = useState(false)

  const rawRestrictionLimit = card.restriction_limit
  const restrictionLimit =
    rawRestrictionLimit === null || rawRestrictionLimit === undefined || rawRestrictionLimit === ''
      ? null
      : Number(rawRestrictionLimit)
  const showRestrictionBadge = Number.isInteger(restrictionLimit) && restrictionLimit < 4
  const colorLabel = [card.color, card.color2].filter(Boolean).join(' / ') || 'No color'
  const tcgplayerUrl = useMemo(() => buildTcgplayerUrl(card), [card])

  const imageSrc = useMemo(() => {
    if (!card.image_url) return null
    return card.image_url
  }, [card.image_url])

  useEffect(() => {
    if (!showDetails || typeof document === 'undefined') {
      return undefined
    }

    const originalOverflow = document.body.style.overflow
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') setShowDetails(false)
    }

    document.body.style.overflow = 'hidden'
    window.addEventListener('keydown', handleKeyDown)

    return () => {
      document.body.style.overflow = originalOverflow
      window.removeEventListener('keydown', handleKeyDown)
    }
  }, [showDetails])

  // Single click/tap → add to deck
  function handleClick() {
    onAddCard(card)
  }

  // Two-finger touch → view details
  function handleTouchStart(event) {
    if (event.touches.length === 2) {
      event.preventDefault()
      setShowDetails(true)
    }
  }

  // Right-click / two-finger trackpad tap → view details
  function handleContextMenu(event) {
    event.preventDefault()
    setShowDetails(true)
  }

  function renderCardArt(extraClassName = '') {
    return (
      <div className={`card-art ${extraClassName}`.trim()}>
        {showRestrictionBadge ? (
          <span
            className="restriction-badge"
            title={`Restricted to ${restrictionLimit} ${restrictionLimit === 1 ? 'copy' : 'copies'}`}
          >
            {restrictionLimit}
          </span>
        ) : null}
        {imageSrc && !imageFailed ? (
          <img src={imageSrc} alt={card.name} loading="lazy" onError={() => setImageFailed(true)} />
        ) : (
          <div>
            <div className="card-id">{card.id || 'Unknown ID'}</div>
            <div>{card.name}</div>
          </div>
        )}
      </div>
    )
  }

  const detailModal =
    showDetails && typeof document !== 'undefined'
      ? createPortal(
          <div className="card-modal-backdrop" role="dialog" aria-modal="true" onClick={() => setShowDetails(false)}>
            <div className="card-modal" onClick={(event) => event.stopPropagation()}>
              <div className="card-modal-header">
                <div>
                  <h3>{card.name || 'Unknown Card'}</h3>
                  <p className="card-id">{card.id || 'Unknown ID'}</p>
                </div>
                <button
                  type="button"
                  className="secondary-button card-modal-close"
                  onClick={() => setShowDetails(false)}
                >
                  Close
                </button>
              </div>

              <div className="card-modal-content">
                <div>{renderCardArt('card-art-large')}</div>

                <div className="card-modal-details">
                  {renderDetailRow('Type', card.type || 'Unknown type')}
                  {renderDetailRow('Color', colorLabel)}
                  {renderDetailRow('Level', card.level)}
                  {renderDetailRow('Play Cost', card.play_cost)}
                  {renderDetailRow('DP', card.dp)}
                  {renderDetailRow('Evolution Cost', card.evolution_cost)}
                  {renderDetailRow('Evolution Color', card.evolution_color)}
                  {renderDetailRow('Evolution Level', card.evolution_level)}
                  {renderDetailRow('Form', card.form)}
                  {renderDetailRow('Attribute', card.attribute)}
                  {renderDetailRow('Stage', card.stage)}
                  {renderDetailRow('Rarity', card.rarity)}
                  {renderDetailRow('Artist', card.artist)}
                  {renderDetailRow('Set', setLabel)}
                  {renderDetailRow('Link DP', card.link_dp)}
                  {renderDetailRow('Link Requirements', card.link_requirements)}
                  {renderDetailRow('Xros Requirement', card.xros_req)}
                  {renderDetailRow(
                    'Restriction',
                    showRestrictionBadge
                      ? `${restrictionLimit} ${restrictionLimit === 1 ? 'copy' : 'copies'} allowed`
                      : null,
                  )}

                  <div className="card-modal-links">
                    {tcgplayerUrl ? (
                      <a
                        className="secondary-button card-link-button"
                        href={tcgplayerUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        View on TCGplayer
                      </a>
                    ) : null}

                    {card.pretty_url ? (
                      <a className="card-detail-link" href={card.pretty_url} target="_blank" rel="noreferrer">
                        Open card page ↗
                      </a>
                    ) : null}
                  </div>

                  {card.main_effect ? (
                    <div className="card-detail-section">
                      <h4>Main Effect</h4>
                      <p>{card.main_effect}</p>
                    </div>
                  ) : null}

                  {card.source_effect ? (
                    <div className="card-detail-section">
                      <h4>Inherited Effect</h4>
                      <p>{card.source_effect}</p>
                    </div>
                  ) : null}
                </div>
              </div>
            </div>
          </div>,
          document.body,
        )
      : null

  return (
    <>
      <article className="panel card-item">
        <button
          type="button"
          className="card-art-button"
          onClick={handleClick}
          onContextMenu={handleContextMenu}
          onTouchStart={handleTouchStart}
          aria-label={`Add ${card.name || 'card'} to deck`}
        >
          {renderCardArt()}
        </button>

        <div className="card-meta">
          <strong>{card.name}</strong>
          <p className="card-id">{card.id}</p>
          <p>{card.type || 'Unknown type'} • {colorLabel}</p>
          <p>Level: {card.level ?? '—'} • Cost: {card.play_cost ?? '—'}</p>
          <p>{setLabel || 'Set not listed yet'}</p>
          <p className="card-preview-hint">Click to add · Right-click for details</p>
        </div>

        <div className="card-actions">
          <button type="button" onClick={() => onAddCard(card)}>
            Add to Deck
          </button>
          {tcgplayerUrl ? (
            <a
              className="secondary-button card-link-button"
              href={tcgplayerUrl}
              target="_blank"
              rel="noopener noreferrer"
            >
              View on TCGplayer
            </a>
          ) : null}
        </div>
      </article>

      {detailModal}
    </>
  )
}
