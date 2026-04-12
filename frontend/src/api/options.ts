import client from './client'
import type { OptionTrade, OptionTradeCreate, OptionTradeUpdate, OptionsSummary, ProcessExpiredResult } from './types'

export async function fetchOptions(): Promise<OptionsSummary> {
  const { data } = await client.get<OptionsSummary>('/options')
  return data
}

export async function createOptionTrade(body: OptionTradeCreate): Promise<OptionTrade> {
  const { data } = await client.post<OptionTrade>('/options', body)
  return data
}

export async function updateOptionTrade(id: string, body: OptionTradeUpdate): Promise<OptionTrade> {
  const { data } = await client.patch<OptionTrade>(`/options/${id}`, body)
  return data
}

export async function deleteOptionTrade(id: string): Promise<void> {
  await client.delete(`/options/${id}`)
}

export async function processExpiredOptions(): Promise<ProcessExpiredResult> {
  const { data } = await client.post<ProcessExpiredResult>('/options/process-expired')
  return data
}
