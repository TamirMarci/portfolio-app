import client from './client'
import type { PortfolioSummary } from './types'

export async function fetchHoldings(): Promise<PortfolioSummary> {
  const { data } = await client.get<PortfolioSummary>('/holdings')
  return data
}
