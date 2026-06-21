import { useQuery } from '@tanstack/vue-query'
import { sessionsApi } from '@/api/endpoints/sessions.api'

export function useSessions() {
  return useQuery({
    queryKey: ['sessions'],
    queryFn: () => sessionsApi.list(),
    refetchInterval: 5_000,
    staleTime: 0,
  })
}
