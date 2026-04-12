import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateTransaction } from '../api/transactions'
import type { TransactionUpdate } from '../api/types'

export function useUpdateTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: TransactionUpdate }) =>
      updateTransaction(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['holdings'] })
    },
  })
}
