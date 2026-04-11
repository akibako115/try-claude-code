export interface PaperOut {
  id: number
  title: string
  authors: string
  url: string
  memo: string
  tags: string
  tags_list: string[]
  created_at: string
  updated_at: string
}

export interface PaperListOut {
  papers: PaperOut[]
  all_tags: string[]
  total: number
}

export interface PaperCreate {
  title: string
  authors?: string
  url?: string
  memo?: string
  tags?: string
  auto_memo?: boolean
}

export interface PaperMemoUpdate {
  memo: string
}

export interface PaperTagsUpdate {
  tags: string
}
