import { useState, useEffect } from 'react'
import { useUpdateTags } from '../hooks/usePapers'

interface Props {
  paperId: number
  initialTags: string
}

export default function TagEditor({ paperId, initialTags }: Props) {
  const [tags, setTags] = useState(initialTags)
  const [saved, setSaved] = useState(false)
  const { mutate, isPending } = useUpdateTags(paperId)

  useEffect(() => {
    setTags(initialTags)
  }, [initialTags])

  const handleSave = () => {
    mutate({ tags }, {
      onSuccess: () => {
        setSaved(true)
        setTimeout(() => setSaved(false), 2000)
      },
    })
  }

  return (
    <div className="memo-actions">
      <input
        type="text"
        value={tags}
        onChange={(e) => setTags(e.target.value)}
        placeholder="タグ（カンマ区切り）"
        style={{ flex: 1 }}
      />
      <button className="btn-primary btn-sm" onClick={handleSave} disabled={isPending}>
        {isPending ? '保存中...' : '保存'}
      </button>
      {saved && <span className="saved-msg">保存しました</span>}
    </div>
  )
}
