import { apiClient } from '@/api'
import type { ApiResponse, User } from '@/types'

interface LoginResponse {
  accessToken: string
  refreshToken: string
  user: User
}

export const authApi = {
  login: (email: string, password: string): Promise<ApiResponse<LoginResponse>> =>
    apiClient.post('/v1/auth/login', { email, password }),

  refresh: (refreshToken: string): Promise<ApiResponse<{ accessToken: string }>> =>
    apiClient.post('/v1/auth/refresh', { refresh_token: refreshToken }),

  logout: (): Promise<void> => apiClient.post('/v1/auth/logout'),
}
