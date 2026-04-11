interface Props {
  allTags: string[]
  activeTag: string
  onSelect: (tag: string) => void
}

export default function TagFilter({ allTags, activeTag, onSelect }: Props) {
  if (allTags.length === 0) return null
  return (
    <div className="tag-bar">
      {activeTag && (
        <button className="btn-ghost btn-sm" onClick={() => onSelect('')}>✕ フィルター解除</button>
      )}
      {allTags.map((tag) => (
        <span
          key={tag}
          className={`tag${activeTag === tag ? ' active' : ''}`}
          onClick={() => onSelect(activeTag === tag ? '' : tag)}
        >
          {tag}
        </span>
      ))}
    </div>
  )
}
