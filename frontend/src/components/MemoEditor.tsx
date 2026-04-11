import { useEffect, useRef, useState } from 'react'
import { useUpdateMemo } from '../hooks/usePapers'

const COLLAPSE_HEIGHT = 80

interface Props {
  paperId: number
  initialMemo: string
}

export default function MemoEditor({ paperId, initialMemo }: Props) {
  const [memo, setMemo] = useState(initialMemo)
  const [isDirty, setIsDirty] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [needsCollapse, setNeedsCollapse] = useState(false)
  const [saved, setSaved] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const collapseInitialized = useRef(false)
  const { mutate, isPending } = useUpdateMemo(paperId)

  useEffect(() => {
    if (!isDirty) setMemo(initialMemo)
  }, [initialMemo, isDirty])

  // memo state（DOMに反映済みの値）を使って初回のみ折りたたみ判定を行う。
  // initialMemo に依存すると setMemo の再レンダリング前に scrollHeight を測定してしまうため、
  // 実際のテキストが反映された後に一度だけ実行する。
  useEffect(() => {
    if (collapseInitialized.current || !memo) return
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
    collapseInitialized.current = true
  }, [memo])

  const autoResize = () => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${el.scrollHeight}px`
  }

  const handleSave = () => {
    mutate({ memo }, {
      onSuccess: () => {
        setIsDirty(false)
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
        onChange={(e) => { setMemo(e.target.value); setIsDirty(true); autoResize() }}
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
