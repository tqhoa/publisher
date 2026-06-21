import type { NavigationGuardNext, RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'

export function authGuard(
  to: RouteLocationNormalized,
  _from: RouteLocationNormalized,
  next: NavigationGuardNext,
): void {
  const { isAuthenticated } = useAuthStore()
  if (to.meta.requiresAuth && !isAuthenticated) return next('/login')
  if (to.meta.guestOnly && isAuthenticated) return next('/dashboard')
  next()
}
