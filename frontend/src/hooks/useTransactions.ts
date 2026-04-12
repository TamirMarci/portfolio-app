import { useQuery } from '@tanstack/react-query'
import { fetchTransactions } from '../api/transactions'

export function useTransactions() {
  return useQuery({
    queryKey: ['transactions'],
    queryFn: fetchTransactions,
  })
}
