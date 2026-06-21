import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from './guards/auth.guard'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/login',
      component: () => import('@/views/auth/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/dashboard',
      component: () => import('@/views/dashboard/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/accounts',
      component: () => import('@/views/accounts/AccountListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/accounts/:id',
      component: () => import('@/views/accounts/AccountDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/posts',
      component: () => import('@/views/posts/PostListView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/posts/create',
      component: () => import('@/views/posts/PostCreateView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/posts/:id',
      component: () => import('@/views/posts/PostDetailView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/sessions',
      component: () => import('@/views/sessions/SessionsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/audit',
      component: () => import('@/views/audit/AuditLogView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(authGuard)
export default router
