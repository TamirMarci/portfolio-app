import { useMutation, useQueryClient } from '@tanstack/react-query'
import { createOptionTrade } from '../api/options'

export function useCreateOptionTrade() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: createOptionTrade,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['options'] })
    },
  })
}
