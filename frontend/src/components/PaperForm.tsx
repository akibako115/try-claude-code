import { useState } from 'react'
import type { FormEvent } from 'react'
import { useCreatePaper } from '../hooks/usePapers'

export default function PaperForm() {
  const [title, setTitle] = useState('')
  const [authors, setAuthors] = useState('')
  const [url, setUrl] = useState('')
  const [memo, setMemo] = useState('')
  const [tags, setTags] = useState('')
  const [autoMemo, setAutoMemo] = useState(false)
  const [error, setError] = useState('')

  const { mutate, isPending } = useCreatePaper()

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!title.trim()) { setError('タイトルは必須です。'); return }
    setError('')
    mutate(
      { title: title.trim(), authors, url, memo, tags, auto_memo: autoMemo },
      {
        onSuccess: () => {
          setTitle(''); setAuthors(''); setUrl(''); setMemo(''); setTags(''); setAutoMemo(false)
        },
        onError: () => setError('作成に失敗しました。'),
      },
    )
  }

  return (
    <div className="card">
      <h2 style={{ fontSize: '1rem', fontWeight: 700, color: '#5c3d1e', marginBottom: 14 }}>論文を追加</h2>
      {error && <div className="error-msg" style={{ marginBottom: 10 }}>{error}</div>}
      <form onSubmit={handleSubmit} className="form-grid">
        <label>
          タイトル <span style={{ color: '#c0392b' }}>*</span>
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="論文タイトル" />
        </label>
        <div className="form-row">
          <label>
            著者
            <input type="text" value={authors} onChange={(e) => setAuthors(e.target.value)} placeholder="著者名" />
          </label>
          <label>
            タグ
            <input type="text" value={tags} onChange={(e) => setTags(e.target.value)} placeholder="カンマ区切り" />
          </label>
        </div>
        <label>
          URL
          <input type="text" value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://arxiv.org/..." />
        </label>
        <label>
          メモ
          <textarea value={memo} onChange={(e) => setMemo(e.target.value)} rows={3} placeholder="読んで気づいたこと..." />
        </label>
        <div className="checkbox-row">
          <input
            id="auto-memo"
            type="checkbox"
            checked={autoMemo}
            onChange={(e) => setAutoMemo(e.target.checked)}
          />
          <label htmlFor="auto-memo" style={{ flexDirection: 'row', alignItems: 'center', gap: 0 }}>
            AIでメモを自動生成（OpenAI API キーが必要）
          </label>
        </div>
        <button type="submit" className="btn-primary" disabled={isPending}>
          {isPending ? '追加中...' : '追加'}
        </button>
      </form>
    </div>
  )
}
