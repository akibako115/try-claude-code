import type {
  PaperCreate,
  PaperListOut,
  PaperMemoUpdate,
  PaperOut,
  PaperTagsUpdate,
} from '../types/paper'
import client from './client'

export async function listPapers(tag = ''): Promise<PaperListOut> {
  const res = await client.get<PaperListOut>('/papers/', { params: tag ? { tag } : {} })
  return res.data
}

export async function createPaper(data: PaperCreate): Promise<PaperOut> {
  const res = await client.post<PaperOut>('/papers/', data)
  return res.data
}

export async function updateMemo(paperId: number, data: PaperMemoUpdate): Promise<PaperOut> {
  const res = await client.patch<PaperOut>(`/papers/${paperId}/memo`, data)
  return res.data
}

export async function updateTags(paperId: number, data: PaperTagsUpdate): Promise<PaperOut> {
  const res = await client.patch<PaperOut>(`/papers/${paperId}/tags`, data)
  return res.data
}

export async function deletePaper(paperId: number): Promise<void> {
  await client.delete(`/papers/${paperId}`)
}
