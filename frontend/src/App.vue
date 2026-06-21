<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isLoginPage = computed(() => route.path === '/login')
const userInitial = computed(() => authStore.user?.email?.[0]?.toUpperCase() ?? '?')
const userEmail = computed(() => authStore.user?.email ?? '')
const userRole = computed(() => authStore.user?.role ?? '')

async function logout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <RouterView v-if="isLoginPage" />
  <div v-else class="shell">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <svg class="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
        </svg>
        <span>Publisher</span>
      </div>

      <nav class="sidebar-nav">
        <RouterLink to="/dashboard" class="nav-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="7" height="7" rx="1.5" /><rect x="14" y="3" width="7" height="7" rx="1.5" />
            <rect x="3" y="14" width="7" height="7" rx="1.5" /><rect x="14" y="14" width="7" height="7" rx="1.5" />
          </svg>
          <span>Dashboard</span>
        </RouterLink>

        <RouterLink to="/accounts" class="nav-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
          </svg>
          <span>Accounts</span>
        </RouterLink>

        <RouterLink to="/posts" class="nav-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
          </svg>
          <span>Posts</span>
        </RouterLink>

        <RouterLink to="/sessions" class="nav-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25" />
          </svg>
          <span>Sessions</span>
        </RouterLink>

        <RouterLink to="/audit" class="nav-item">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Audit Log</span>
        </RouterLink>
      </nav>

      <div class="sidebar-footer">
        <div class="user-row">
          <div class="user-avatar">{{ userInitial }}</div>
          <div class="user-meta">
            <span class="user-email">{{ userEmail }}</span>
            <span class="user-role">{{ userRole }}</span>
          </div>
        </div>
        <button class="logout-btn" title="Logout" @click="logout">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
            <path d="M15.75 9V5.25A2.25 2.25 0 0013.5 3h-6a2.25 2.25 0 00-2.25 2.25v13.5A2.25 2.25 0 007.5 21h6a2.25 2.25 0 002.25-2.25V15m3 0l3-3m0 0l-3-3m3 3H9" />
          </svg>
        </button>
      </div>
    </aside>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.shell { display: flex; min-height: 100svh; }

/* ── Sidebar ── */
.sidebar {
  width: 240px;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100svh;
  overflow-y: auto;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 18px 16px;
  color: #f8fafc;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: -0.3px;
  border-bottom: 1px solid #1e293b;
}
.logo-icon { width: 22px; height: 22px; color: #3b82f6; flex-shrink: 0; }

/* ── Nav ── */
.sidebar-nav {
  flex: 1;
  padding: 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 9px 10px;
  border-radius: 7px;
  color: #94a3b8;
  font-size: 13.5px;
  font-weight: 500;
  transition: background 0.12s, color 0.12s;
}
.nav-item svg { width: 17px; height: 17px; flex-shrink: 0; }
.nav-item:hover { background: #1e293b; color: #cbd5e1; }
.nav-item.router-link-active { background: #1e293b; color: #f1f5f9; }
.nav-item.router-link-active svg { color: #60a5fa; }

/* ── Footer ── */
.sidebar-footer {
  padding: 10px 10px 14px;
  border-top: 1px solid #1e293b;
  display: flex;
  align-items: center;
  gap: 8px;
}
.user-row { flex: 1; display: flex; align-items: center; gap: 9px; min-width: 0; }
.user-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: #2563eb;
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 12px; font-weight: 700;
  flex-shrink: 0;
}
.user-meta { display: flex; flex-direction: column; min-width: 0; }
.user-email { font-size: 11.5px; font-weight: 500; color: #cbd5e1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-role { font-size: 10.5px; color: #475569; text-transform: capitalize; }

.logout-btn {
  background: transparent;
  border: none;
  padding: 6px;
  border-radius: 6px;
  color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.12s, color 0.12s;
  flex-shrink: 0;
}
.logout-btn:hover { background: #1e293b; color: #f87171; }
.logout-btn svg { width: 16px; height: 16px; }

/* ── Main ── */
.main-content {
  flex: 1;
  padding: 28px 32px;
  overflow-y: auto;
  background: #f1f5f9;
  min-width: 0;
}
</style>
