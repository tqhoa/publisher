import { type Ref, computed } from 'vue'
import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { postsApi } from '@/api/endpoints/posts.api'

export function usePosts(params?: { status?: string; platform?: string; page?: number; limit?: number }) {
  return useQuery({
    queryKey: computed(() => ['posts', params]),
    queryFn: () => postsApi.list(params),
    staleTime: 15_000,
  })
}

export function usePost(id: Ref<string>) {
  return useQuery({
    queryKey: computed(() => ['post', id.value]),
    queryFn: () => postsApi.get(id.value),
    staleTime: 10_000,
    enabled: computed(() => !!id.value),
  })
}

export function useCreatePost() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: postsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['posts'] }),
  })
}

export function usePublishNow() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => postsApi.publishNow(id),
    onSuccess: (_data, id) => {
      qc.invalidateQueries({ queryKey: ['posts'] })
      qc.invalidateQueries({ queryKey: ['post', id] })
    },
  })
}

export function useRetryPost() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => postsApi.retry(id),
    onSuccess: (_data, id) => {
      qc.invalidateQueries({ queryKey: ['posts'] })
      qc.invalidateQueries({ queryKey: ['post', id] })
    },
  })
}
