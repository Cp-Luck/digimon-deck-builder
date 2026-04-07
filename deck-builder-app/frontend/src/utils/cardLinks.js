function slugifyTcgplayerPart(value) {
  return String(value || '')
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/&/g, ' and ')
    .replace(/["'.,()\[\]:/]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function buildTcgplayerSlug(card = {}) {
  const rawSetName = Array.isArray(card?.set_name) ? card.set_name[0] : card?.set_name
  const cleanedSetName = String(rawSetName || '')
    .replace(/^[A-Z0-9-]+\s*:\s*/i, '')
    .trim()

  return [card?.series || 'Digimon Card Game', cleanedSetName, card?.name || card?.tcgplayer_name]
    .map(slugifyTcgplayerPart)
    .filter(Boolean)
    .join('-')
}

export function buildTcgplayerUrl(card = {}) {
  const rawProductId = card?.tcgplayer_id
  const productId = rawProductId === null || rawProductId === undefined ? '' : String(rawProductId).trim()

  if (/^\d+$/.test(productId)) {
    const slug = buildTcgplayerSlug(card)
    return slug
      ? `https://www.tcgplayer.com/product/${productId}/${slug}?Language=English`
      : `https://www.tcgplayer.com/product/${productId}?Language=English`
  }

  const searchName = String(card?.tcgplayer_name || card?.name || '').trim()
  if (searchName) {
    return `https://www.tcgplayer.com/search/all/product?q=${encodeURIComponent(searchName)}`
  }

  return null
}
