import { apiClient } from '@/api'
import type { AuditLog, PaginatedResponse } from '@/types'

export const auditApi = {
  list: (params?: { page?: number; limit?: number; action?: string }): Promise<PaginatedResponse<AuditLog>> =>
    apiClient.get('/v1/audit', { params }),
}
