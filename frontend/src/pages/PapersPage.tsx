import { useSearchParams } from 'react-router-dom'
import Layout from '../components/Layout'
import PaperCard from '../components/PaperCard'
import PaperForm from '../components/PaperForm'
import TagFilter from '../components/TagFilter'
import { useListPapers } from '../hooks/usePapers'

export default function PapersPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const activeTag = searchParams.get('tag') ?? ''

  const { data, isLoading, isError } = useListPapers(activeTag)

  const handleTagSelect = (tag: string) => {
    if (tag) setSearchParams({ tag })
    else setSearchParams({})
  }

  return (
    <Layout>
      <div className="hero">
        <h1>Paper Notes</h1>
        <p>読んだ論文を記録・整理するツール</p>
      </div>

      <PaperForm />

      {data && (
        <TagFilter allTags={data.all_tags} activeTag={activeTag} onSelect={handleTagSelect} />
      )}

      {activeTag && (
        <p style={{ fontSize: '0.85rem', color: '#7a6652', marginBottom: 8 }}>
          タグ「{activeTag}」でフィルター中 ({data?.total ?? 0}件)
        </p>
      )}

      {isLoading && <p style={{ color: '#7a6652', padding: '20px 0' }}>読み込み中...</p>}
      {isError && <p className="error-msg">論文の取得に失敗しました。</p>}

      {data && data.papers.length === 0 && (
        <div className="empty-state">
          {activeTag ? `タグ「${activeTag}」の論文はありません。` : 'まだ論文が登録されていません。'}
        </div>
      )}

      {data?.papers.map((paper) => (
        <PaperCard key={paper.id} paper={paper} onTagClick={handleTagSelect} />
      ))}
    </Layout>
  )
}
