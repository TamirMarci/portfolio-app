import { useMutation, useQueryClient } from '@tanstack/react-query'
import { deleteOptionTrade } from '../api/options'

export function useDeleteOptionTrade() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: deleteOptionTrade,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['options'] })
    },
  })
}
