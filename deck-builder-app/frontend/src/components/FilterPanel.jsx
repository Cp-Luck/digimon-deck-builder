const COLOR_OPTIONS = ['', 'Red', 'Blue', 'Yellow', 'Green', 'Black', 'Purple', 'White']
const TYPE_OPTIONS = ['', 'Digimon', 'Option', 'Tamer', 'Digi-Egg']

export default function FilterPanel({ filters, onChange }) {
  function updateField(key, value) {
    onChange((current) => ({ ...current, [key]: value }))
  }

  return (
    <aside className="panel">
      <h2>Filters</h2>
      <div className="filter-panel">
        <label>
          Color
          <select value={filters.color} onChange={(event) => updateField('color', event.target.value)}>
            {COLOR_OPTIONS.map((option) => (
              <option key={option || 'all-colors'} value={option}>
                {option || 'All colors'}
              </option>
            ))}
          </select>
        </label>

        <label>
          Type
          <select value={filters.card_type} onChange={(event) => updateField('card_type', event.target.value)}>
            {TYPE_OPTIONS.map((option) => (
              <option key={option || 'all-types'} value={option}>
                {option || 'All types'}
              </option>
            ))}
          </select>
        </label>

        <label>
          Pack / Set
          <input
            value={filters.pack}
            onChange={(event) => updateField('pack', event.target.value)}
            placeholder="EX10, BT1, ST19..."
          />
        </label>
      </div>
    </aside>
  )
}
