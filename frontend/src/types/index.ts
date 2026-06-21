export interface User {
  id: string
  email: string
  role: string
}

export interface Account {
  id: string
  platform: string
  username: string
  status: string
  healthStatus: string | null
  cookieUpdatedAt: string | null
  lastHealthCheckAt: string | null
  createdAt: string
}

export interface Post {
  id: string
  accountId: string
  platform: string
  contentType: string
  caption: string | null
  hashtags: string[] | null
  mediaUrls: string[] | null
  status: string
  scheduledAt: string | null
  publishedAt: string | null
  errorMessage: string | null
  retryCount: number
  createdAt: string
}

export interface BrowserSession {
  id: string
  accountId: string
  nodeId: string
  status: string
  startedAt: string
  lastActivityAt: string
}

export interface AuditLog {
  id: string
  userId: string | null
  action: string
  resourceType: string | null
  resourceId: string | null
  ipAddress: string | null
  createdAt: string
}

export interface Pagination {
  page: number
  limit: number
  total: number
  totalPages: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
}

export interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  pagination: Pagination
}
