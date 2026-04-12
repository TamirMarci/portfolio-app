import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteTransaction } from '../api/transactions'

export function useDeleteTransaction() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteTransaction,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      queryClient.invalidateQueries({ queryKey: ['holdings'] })
    },
  })
}
