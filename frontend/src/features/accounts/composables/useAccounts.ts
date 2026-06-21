import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { accountsApi } from '@/api/endpoints/accounts.api'

export function useAccounts(params?: { page?: number; limit?: number; platform?: string }) {
  return useQuery({
    queryKey: ['accounts', params],
    queryFn: () => accountsApi.list(params),
    staleTime: 30_000,
  })
}

export function useAccount(id: string) {
  return useQuery({
    queryKey: ['account', id],
    queryFn: () => accountsApi.get(id),
    staleTime: 30_000,
  })
}

export function useCreateAccount() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: accountsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ['accounts'] }),
  })
}

export function useDeleteAccount() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => accountsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['accounts'] }),
  })
}

export function useImportCookie() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({ id, cookieJson }: { id: string; cookieJson: string }) =>
      accountsApi.importCookie(id, cookieJson),
    onSuccess: (_data, vars) => qc.invalidateQueries({ queryKey: ['account', vars.id] }),
  })
}

export function useCheckHealth() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => accountsApi.checkHealth(id),
    onSuccess: (_data, id) => qc.invalidateQueries({ queryKey: ['account', id] }),
  })
}
