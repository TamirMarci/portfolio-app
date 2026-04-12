import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { fetchOptions, processExpiredOptions } from '../api/options'

export function useOptions() {
  return useQuery({
    queryKey: ['options'],
    queryFn: fetchOptions,
  })
}

export function useProcessExpiredOptions() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: processExpiredOptions,
    onSuccess: () => {
      // Refresh options list, holdings (shares may have changed), and snapshots
      qc.invalidateQueries({ queryKey: ['options'] })
      qc.invalidateQueries({ queryKey: ['holdings'] })
    },
  })
}
