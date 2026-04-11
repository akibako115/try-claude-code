import { useEffect, useRef, useState } from 'react'
import { useUpdateMemo } from '../hooks/usePapers'

const COLLAPSE_HEIGHT = 80

interface Props {
  paperId: number
  initialMemo: string
}

export default function MemoEditor({ paperId, initialMemo }: Props) {
  const [memo, setMemo] = useState(initialMemo)
  const [collapsed, setCollapsed] = useState(false)
  const [needsCollapse, setNeedsCollapse] = useState(false)
  const [saved, setSaved] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const { mutate, isPending } = useUpdateMemo(paperId)

  useEffect(() => {
    setMemo(initialMemo)
  }, [initialMemo])

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    const full = el.scrollHeight
    if (full > COLLAPSE_HEIGHT) {
      setNeedsCollapse(true)
      setCollapsed(true)
    } else {
      el.style.height = `${full}px`
    }
  }, [])

  const autoResize = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
  }

  const handleSave = () => {
    mutate({ memo }, {
      onSuccess: () => {
        setSaved(true)
        setTimeout(() => setSaved(false), 2000)
      },
    })
  }

  return (
    <div className="memo-editor">
      <textarea
        ref={textareaRef}
        value={memo}
        onChange={(e) => { setMemo(e.target.value); autoResize() }}
        className={collapsed ? 'memo-collapsed' : ''}
        rows={3}
        placeholder="メモを入力..."
      />
      <div className="memo-actions">
        <button className="btn-primary btn-sm" onClick={handleSave} disabled={isPending}>
          {isPending ? '保存中...' : '保存'}
        </button>
        {needsCollapse && (
          <button className="btn-ghost btn-sm" onClick={() => setCollapsed((c) => !c)}>
            {collapsed ? '全文表示' : '折りたたむ'}
          </button>
        )}
        {saved && <span className="saved-msg">保存しました</span>}
      </div>
    </div>
  )
}
