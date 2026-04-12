import client from './client'
import type { RefreshResult } from './types'

export async function refreshPrices(): Promise<RefreshResult> {
  const { data } = await client.post<RefreshResult>('/prices/refresh')
  return data
}
