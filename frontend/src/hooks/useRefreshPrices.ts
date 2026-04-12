import { useMutation, useQueryClient } from '@tanstack/react-query'
import { refreshPrices } from '../api/prices'

export function useRefreshPrices() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: refreshPrices,
    onSuccess: () => {
      // Invalidate holdings so the dashboard re-fetches with fresh prices
      queryClient.invalidateQueries({ queryKey: ['holdings'] })
    },
  })
}
