export default function SearchBar({ value, onChange, onClear }) {
  return (
    <div className="search-bar">
      <input
        type="search"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder="Search by card name, ID, or set..."
      />
      <button type="button" className="secondary-button" onClick={onClear}>
        Reset
      </button>
    </div>
  )
}
