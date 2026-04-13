import { useQuery } from '@tanstack/react-query'
import { fetchTransactions, type TransactionDateFilter } from '../api/transactions'

export function useTransactions(filter?: TransactionDateFilter) {
  return useQuery({
    queryKey: ['transactions', filter?.start_date ?? null, filter?.end_date ?? null],
    queryFn: () => fetchTransactions(filter),
  })
}
