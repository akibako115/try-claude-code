import type { PaperOut } from '../types/paper'
import { useDeletePaper } from '../hooks/usePapers'
import MemoEditor from './MemoEditor'
import TagEditor from './TagEditor'

interface Props {
  paper: PaperOut
  onTagClick: (tag: string) => void
}

const formatDate = (iso: string) =>
  new Date(iso).toLocaleDateString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit' })

const isSafeUrl = (url: string) =>
  url.startsWith('http://') || url.startsWith('https://')

export default function PaperCard({ paper, onTagClick }: Props) {
  const { mutate: deletePaper } = useDeletePaper()

  const handleDelete = () => {
    if (window.confirm(`「${paper.title}」を削除しますか？`)) {
      deletePaper(paper.id, {
        onError: () => alert('削除に失敗しました。'),
      })
    }
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="paper-title">{paper.title}</div>
          <div className="paper-meta">
            {paper.authors && <span>{paper.authors} · </span>}
            {paper.url && isSafeUrl(paper.url) && <a href={paper.url} target="_blank" rel="noreferrer">{paper.url}</a>}
            {paper.url && !isSafeUrl(paper.url) && <span>{paper.url}</span>}
            {(paper.authors || paper.url) && <span> · </span>}
            <span>登録: {formatDate(paper.created_at)}</span>
          </div>
        </div>
        <button className="btn-danger btn-sm" onClick={handleDelete}>削除</button>
      </div>

      {paper.tags_list.length > 0 && (
        <div className="tag-bar" style={{ marginTop: 8 }}>
          {paper.tags_list.map((t) => (
            <span key={t} className="tag inline" onClick={() => onTagClick(t)}>{t}</span>
          ))}
        </div>
      )}

      <div className="paper-section">
        <div className="paper-section-label">メモ</div>
        <MemoEditor paperId={paper.id} initialMemo={paper.memo} />
      </div>

      <div className="paper-section">
        <div className="paper-section-label">タグ</div>
        <TagEditor paperId={paper.id} initialTags={paper.tags} />
      </div>
    </div>
  )
}
