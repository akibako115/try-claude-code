import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import * as papersApi from '../api/papers'
import type { PaperCreate, PaperMemoUpdate, PaperTagsUpdate } from '../types/paper'

export function useListPapers(tag = '') {
  return useQuery({
    queryKey: ['papers', tag],
    queryFn: () => papersApi.listPapers(tag),
  })
}

export function useCreatePaper() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: PaperCreate) => papersApi.createPaper(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['papers'] }),
  })
}

export function useUpdateMemo(paperId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: PaperMemoUpdate) => papersApi.updateMemo(paperId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['papers'] }),
  })
}

export function useUpdateTags(paperId: number) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: PaperTagsUpdate) => papersApi.updateTags(paperId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['papers'] }),
  })
}

export function useDeletePaper() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (paperId: number) => papersApi.deletePaper(paperId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['papers'] }),
  })
}
