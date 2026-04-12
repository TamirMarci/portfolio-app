import { useMutation, useQueryClient } from '@tanstack/react-query'
import { updateOptionTrade } from '../api/options'
import type { OptionTradeUpdate } from '../api/types'

export function useUpdateOptionTrade() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, body }: { id: string; body: OptionTradeUpdate }) =>
      updateOptionTrade(id, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['options'] })
    },
  })
}
