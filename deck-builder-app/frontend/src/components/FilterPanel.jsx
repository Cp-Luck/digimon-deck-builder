const COLOR_OPTIONS = ['', 'Red', 'Blue', 'Yellow', 'Green', 'Black', 'Purple', 'White']
const TYPE_OPTIONS = ['', 'Digimon', 'Option', 'Tamer', 'Digi-Egg']

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
      </div>
    </aside>
  )
}
