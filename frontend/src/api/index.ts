import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 15_000,
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      // Lazy import to avoid circular dep — useAuthStore calls apiClient
      import('@/stores/useAuthStore').then(({ useAuthStore }) => {
        useAuthStore().logout()
        window.location.href = '/login'
      })
    }
    return Promise.reject(error)
  },
)
