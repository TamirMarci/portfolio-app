import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import {
  fetchSnapshots, fetchSnapshotDetail, createSnapshot,
  compareSnapshots, renameSnapshot, deleteSnapshot,
} from '../api/snapshots'
import type { SnapshotCreate, SnapshotUpdate } from '../api/types'

export function useSnapshots() {
  return useQuery({ queryKey: ['snapshots'], queryFn: fetchSnapshots })
}

export function useSnapshotDetail(id: string | null) {
  return useQuery({
    queryKey: ['snapshots', id],
    queryFn: () => fetchSnapshotDetail(id!),
    enabled: !!id,
  })
}

export function useCompareSnapshots(fromId: string | null, toId: string | null) {
  return useQuery({
    queryKey: ['snapshots', 'compare', fromId, toId],
    queryFn: () => compareSnapshots(fromId!, toId!),
    enabled: !!fromId && !!toId,
  })
}

export function useCreateSnapshot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (body: SnapshotCreate) => createSnapshot(body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['snapshots'] }),
  })
}

export function useRenameSnapshot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: SnapshotUpdate }) => renameSnapshot(id, body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['snapshots'] }),
  })
}

export function useDeleteSnapshot() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => deleteSnapshot(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['snapshots'] }),
  })
}
