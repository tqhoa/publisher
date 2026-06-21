import { apiClient } from '@/api'
import type { Account, ApiResponse, PaginatedResponse } from '@/types'

export const accountsApi = {
  list: (params?: { page?: number; limit?: number; platform?: string }): Promise<PaginatedResponse<Account>> =>
    apiClient.get('/v1/accounts', { params }),

  get: (id: string): Promise<ApiResponse<Account>> =>
    apiClient.get(`/v1/accounts/${id}`),

  create: (data: { platform: string; username: string }): Promise<ApiResponse<Account>> =>
    apiClient.post('/v1/accounts', data),

  update: (id: string, data: Partial<Account>): Promise<ApiResponse<Account>> =>
    apiClient.patch(`/v1/accounts/${id}`, data),

  delete: (id: string): Promise<void> =>
    apiClient.delete(`/v1/accounts/${id}`),

  importCookie: (id: string, cookieJson: string): Promise<ApiResponse<Account>> =>
    apiClient.post(`/v1/accounts/${id}/cookie`, { cookie_json: cookieJson }),

  checkHealth: (id: string): Promise<ApiResponse<{ accountId: string; healthy: boolean; checkedAt: string; message?: string }>> =>
    apiClient.get(`/v1/accounts/${id}/health`),
}
