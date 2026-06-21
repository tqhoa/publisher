import { apiClient } from '@/api'
import type { ApiResponse, PaginatedResponse, Post } from '@/types'

interface PostCreateInput {
  accountId: string
  platform: string
  contentType: string
  caption?: string
  hashtags?: string[]
  mediaUrls?: string[]
  scheduledAt?: string
}

export const postsApi = {
  list: (params?: { page?: number; limit?: number; status?: string; platform?: string; accountId?: string }): Promise<PaginatedResponse<Post>> =>
    apiClient.get('/v1/posts', { params }),

  get: (id: string): Promise<ApiResponse<Post>> =>
    apiClient.get(`/v1/posts/${id}`),

  create: (data: PostCreateInput): Promise<ApiResponse<Post>> =>
    apiClient.post('/v1/posts', {
      account_id: data.accountId,
      platform: data.platform,
      content_type: data.contentType,
      caption: data.caption,
      hashtags: data.hashtags,
      media_urls: data.mediaUrls,
      scheduled_at: data.scheduledAt,
    }),

  delete: (id: string): Promise<void> =>
    apiClient.delete(`/v1/posts/${id}`),

  publishNow: (id: string): Promise<ApiResponse<Post>> =>
    apiClient.post(`/v1/posts/${id}/publish-now`),

  retry: (id: string): Promise<ApiResponse<Post>> =>
    apiClient.post(`/v1/posts/${id}/retry`),
}
