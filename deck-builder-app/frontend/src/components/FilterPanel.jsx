const COLOR_OPTIONS = ['Red', 'Blue', 'Yellow', 'Green', 'Black', 'Purple', 'White']
const TYPE_OPTIONS = ['Digimon', 'Option', 'Tamer', 'Digi-Egg']
const SPECIAL_OPTION_ORDER = {
  rarity: ['C', 'U', 'R', 'SR', 'SEC', 'P', 'UR'],
}

const SUMMARY_FILTERS = [
  { key: 'level', label: 'Level', summaryKey: 'level', inputType: 'number', step: 1 },
  { key: 'play_cost', label: 'Play Cost', summaryKey: 'play_cost', inputType: 'number', step: 1 },
  { key: 'evolution_cost', label: 'Evolution Cost', summaryKey: 'evolution_cost', inputType: 'number', step: 1 },
  { key: 'evolution_level', label: 'Evolution Level', summaryKey: 'evolution_level', inputType: 'number', step: 1 },
  { key: 'dp', label: 'DP', summaryKey: 'dp', inputType: 'number', step: 1000 },
  { key: 'link_dp', label: 'Link DP', summaryKey: 'link_dp', inputType: 'number', step: 1000 },
  { key: 'form', label: 'Form', summaryKey: 'form' },
  { key: 'attribute', label: 'Attribute', summaryKey: 'attribute' },
  { key: 'rarity', label: 'Rarity', summaryKey: 'rarity' },
  { key: 'stage', label: 'Stage', summaryKey: 'stage' },
]

const TEXT_FILTERS = [
  { key: 'xros_req', label: 'Xros Req' },
  { key: 'artist', label: 'Artist' },
  { key: 'link_requirements', label: 'Link Requirements' },
]

function getSelectOptions(fieldOptions, summaryKey, fallback = []) {
  const rawOptions = fieldOptions?.[summaryKey]

  if (rawOptions && typeof rawOptions === 'object') {
    const entries = Object.entries(rawOptions).filter(([value]) => value !== '')
    const numericValues = entries.length > 0 && entries.every(([value]) => !Number.isNaN(Number(value)))
    const explicitOrder = SPECIAL_OPTION_ORDER[summaryKey] || []

    return entries
      .sort((left, right) => {
        if (explicitOrder.length) {
          const leftIndex = explicitOrder.indexOf(String(left[0]).toUpperCase())
          const rightIndex = explicitOrder.indexOf(String(right[0]).toUpperCase())
          const normalizedLeftIndex = leftIndex === -1 ? explicitOrder.length : leftIndex
          const normalizedRightIndex = rightIndex === -1 ? explicitOrder.length : rightIndex

          return normalizedLeftIndex - normalizedRightIndex || String(left[0]).localeCompare(String(right[0]))
        }

        if (numericValues) {
          return Number(left[0]) - Number(right[0])
        }

        return String(left[0]).localeCompare(String(right[0]))
      })
      .map(([value]) => ({
        value,
        label: String(value),
      }))
  }

  return fallback.filter(Boolean).map((value) => ({ value, label: value }))
}

function renderSelect(label, value, onChange, options, emptyLabel) {
  return (
    <label>
      {label}
      <select value={value} onChange={onChange}>
        <option value="">{emptyLabel}</option>
        {options.map((option) => (
          <option key={`${label}-${option.value}`} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  )
}

export default function FilterPanel({ filters, onChange, setOptions = [], fieldOptions = {} }) {
  function updateField(key, value) {
    onChange((current) => ({ ...current, [key]: value }))
  }

  function toggleMultiValue(key, optionValue) {
    onChange((current) => {
      const currentValues = Array.isArray(current[key]) ? current[key] : []
      const nextValues = currentValues.includes(optionValue)
        ? currentValues.filter((value) => value !== optionValue)
        : [...currentValues, optionValue]

      return { ...current, [key]: nextValues }
    })
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

  const colorOptions = getSelectOptions(fieldOptions, 'color', COLOR_OPTIONS)
  const typeOptions = getSelectOptions(fieldOptions, 'type', TYPE_OPTIONS)
  const evolutionColorOptions = getSelectOptions(fieldOptions, 'evolution_color', COLOR_OPTIONS)
  const digiTypeOptions = getSelectOptions(fieldOptions, 'digi_type')

  return (
    <aside className="panel">
      <h2>Filters</h2>
      <div className="filter-panel">
        {renderSelect(
          'Color',
          filters.color,
          (event) => updateField('color', event.target.value),
          colorOptions,
          'All colors',
        )}

        {renderSelect(
          'Type',
          filters.card_type,
          (event) => updateField('card_type', event.target.value),
          typeOptions,
          'All types',
        )}

        {renderSelect(
          'Evolution Color',
          filters.evolution_color,
          (event) => updateField('evolution_color', event.target.value),
          evolutionColorOptions,
          'Any evolution color',
        )}

        {renderSelect(
          'Color 2',
          filters.color2,
          (event) => updateField('color2', event.target.value),
          colorOptions,
          'Any second color',
        )}

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
            <div className="advanced-filter-section">
              <div className="filter-section-header">
                <span>Digi Type</span>
                {filters.digi_type?.length ? (
                  <button type="button" className="filter-clear-button" onClick={() => updateField('digi_type', [])}>
                    Clear
                  </button>
                ) : null}
              </div>

              <div className="checkbox-list checkbox-list-compact">
                {digiTypeOptions.length ? (
                  digiTypeOptions.map((option) => (
                    <label key={`digi-type-${option.value}`} className="checkbox-option">
                      <input
                        type="checkbox"
                        checked={filters.digi_type?.includes(option.value) || false}
                        onChange={() => toggleMultiValue('digi_type', option.value)}
                      />
                      <span>{option.label}</span>
                    </label>
                  ))
                ) : (
                  <p className="card-empty">No digi type options loaded yet.</p>
                )}
              </div>
            </div>

            {SUMMARY_FILTERS.map((field) => {
              const options = getSelectOptions(fieldOptions, field.summaryKey)

              if (options.length) {
                return (
                  <label key={field.key}>
                    {field.label}
                    <select
                      value={filters[field.key] || ''}
                      onChange={(event) => updateField(field.key, event.target.value)}
                    >
                      <option value="">{`Any ${field.label.toLowerCase()}`}</option>
                      {options.map((option) => (
                        <option key={`${field.key}-${option.value}`} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </label>
                )
              }

              return (
                <label key={field.key}>
                  {field.label}
                  <input
                    type={field.inputType || 'text'}
                    step={field.step}
                    value={filters[field.key] || ''}
                    onChange={(event) => updateField(field.key, event.target.value)}
                    placeholder={`Any ${field.label.toLowerCase()}`}
                  />
                </label>
              )
            })}

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
