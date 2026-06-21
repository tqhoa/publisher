import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/useAuthStore'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (k: string) => store[k] ?? null,
    setItem: (k: string, v: string) => { store[k] = v },
    removeItem: (k: string) => { delete store[k] },
    clear: () => { store = {} },
  }
})()
Object.defineProperty(global, 'localStorage', { value: localStorageMock })

describe('useAuthStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('isAuthenticated is false when no token', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
  })

  it('isAuthenticated is true after setToken', () => {
    const store = useAuthStore()
    store.setToken('abc123')
    expect(store.isAuthenticated).toBe(true)
  })

  it('token persisted in localStorage after setToken', () => {
    const store = useAuthStore()
    store.setToken('mytoken')
    expect(localStorage.getItem('token')).toBe('mytoken')
  })

  it('logout clears token and user', () => {
    const store = useAuthStore()
    store.setToken('abc')
    store.setUser({ id: '1', email: 'a@b.com', role: 'admin' })
    store.logout()
    expect(store.token).toBeNull()
    expect(store.user).toBeNull()
    expect(store.isAuthenticated).toBe(false)
    expect(localStorage.getItem('token')).toBeNull()
  })

  it('setUser stores user object', () => {
    const store = useAuthStore()
    const user = { id: '1', email: 'test@test.com', role: 'admin' }
    store.setUser(user)
    expect(store.user).toEqual(user)
  })
})
