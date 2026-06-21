import { apiClient } from '@/api'
import type { ApiResponse, BrowserSession } from '@/types'

export const sessionsApi = {
  list: (): Promise<ApiResponse<BrowserSession[]>> =>
    apiClient.get('/v1/sessions'),

  get: (accountId: string): Promise<ApiResponse<BrowserSession>> =>
    apiClient.get(`/v1/sessions/${accountId}`),
}
