const COLOR_OPTIONS = ['', 'Red', 'Blue', 'Yellow', 'Green', 'Black', 'Purple', 'White']
const TYPE_OPTIONS = ['', 'Digimon', 'Option', 'Tamer', 'Digi-Egg']

const NUMERIC_FILTERS = [
  { key: 'level', label: 'Level', step: 1 },
  { key: 'play_cost', label: 'Play Cost', step: 1 },
  { key: 'evolution_cost', label: 'Evolution Cost', step: 1 },
  { key: 'evolution_level', label: 'Evolution Level', step: 1 },
  { key: 'dp', label: 'DP', step: 1000 },
  { key: 'link_dp', label: 'Link DP', step: 1000 },
]

const TEXT_FILTERS = [
  { key: 'xros_req', label: 'Xros Req' },
  { key: 'digi_type', label: 'Digi Type' },
  { key: 'digi_type2', label: 'Digi Type 2' },
  { key: 'digi_type3', label: 'Digi Type 3' },
  { key: 'digi_type4', label: 'Digi Type 4' },
  { key: 'form', label: 'Form' },
  { key: 'attribute', label: 'Attribute' },
  { key: 'rarity', label: 'Rarity' },
  { key: 'stage', label: 'Stage' },
  { key: 'artist', label: 'Artist' },
  { key: 'link_requirements', label: 'Link Requirements' },
]

export default function FilterPanel({ filters, onChange, setOptions = [] }) {
  function updateField(key, value) {
    onChange((current) => ({ ...current, [key]: value }))
  }

  function togglePackOption(setName) {
    onChange((current) => {
      const currentPacks = Array.isArray(current.pack) ? current.pack : []
      const nextPacks = currentPacks.includes(setName)
        ? currentPacks.filter((value) => value !== setName)
        : [...currentPacks, setName]

      return { ...current, pack: nextPacks }
    })
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
          Evolution Color
          <select
            value={filters.evolution_color}
            onChange={(event) => updateField('evolution_color', event.target.value)}
          >
            {COLOR_OPTIONS.map((option) => (
              <option key={option || 'all-evolution-colors'} value={option}>
                {option || 'Any evolution color'}
              </option>
            ))}
          </select>
        </label>

        <label>
          Color 2
          <select value={filters.color2} onChange={(event) => updateField('color2', event.target.value)}>
            {COLOR_OPTIONS.map((option) => (
              <option key={option || 'all-second-colors'} value={option}>
                {option || 'Any second color'}
              </option>
            ))}
          </select>
        </label>

        <div>
          <div className="filter-section-header">
            <span>Set</span>
            {filters.pack?.length ? (
              <button type="button" className="filter-clear-button" onClick={() => updateField('pack', [])}>
                Clear
              </button>
            ) : null}
          </div>

          <div className="checkbox-list">
            {setOptions.length ? (
              setOptions.map((setName) => (
                <label key={setName} className="checkbox-option">
                  <input
                    type="checkbox"
                    checked={filters.pack?.includes(setName) || false}
                    onChange={() => togglePackOption(setName)}
                  />
                  <span>{setName}</span>
                </label>
              ))
            ) : (
              <p className="card-empty">No set options loaded yet.</p>
            )}
          </div>
        </div>

        <details className="advanced-filters" open>
          <summary>Advanced Filters</summary>
          <div className="advanced-filter-grid">
            {NUMERIC_FILTERS.map((field) => (
              <label key={field.key}>
                {field.label}
                <input
                  type="number"
                  step={field.step}
                  value={filters[field.key] || ''}
                  onChange={(event) => updateField(field.key, event.target.value)}
                  placeholder={`Any ${field.label.toLowerCase()}`}
                />
              </label>
            ))}

            {TEXT_FILTERS.map((field) => (
              <label key={field.key}>
                {field.label}
                <input
                  value={filters[field.key] || ''}
                  onChange={(event) => updateField(field.key, event.target.value)}
                  placeholder={`Any ${field.label.toLowerCase()}`}
                />
              </label>
            ))}
          </div>
        </details>
      </div>
    </aside>
  )
}
