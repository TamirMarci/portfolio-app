import client from './client'
import type { SnapshotCreate, SnapshotUpdate, SnapshotListItem, SnapshotDetail, SnapshotCompareResult } from './types'

export async function fetchSnapshots(): Promise<SnapshotListItem[]> {
  const { data } = await client.get<SnapshotListItem[]>('/snapshots')
  return data
}

export async function fetchSnapshotDetail(id: string): Promise<SnapshotDetail> {
  const { data } = await client.get<SnapshotDetail>(`/snapshots/${id}`)
  return data
}

export async function createSnapshot(body: SnapshotCreate): Promise<SnapshotListItem> {
  const { data } = await client.post<SnapshotListItem>('/snapshots', body)
  return data
}

export async function compareSnapshots(fromId: string, toId: string): Promise<SnapshotCompareResult> {
  const { data } = await client.get<SnapshotCompareResult>('/snapshots/compare', {
    params: { from_id: fromId, to_id: toId },
  })
  return data
}

export async function renameSnapshot(id: string, body: SnapshotUpdate): Promise<SnapshotListItem> {
  const { data } = await client.patch<SnapshotListItem>(`/snapshots/${id}`, body)
  return data
}

export async function deleteSnapshot(id: string): Promise<void> {
  await client.delete(`/snapshots/${id}`)
}
