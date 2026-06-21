<script setup lang="ts">
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'

const authStore = useAuthStore()
const router = useRouter()
const route = useRoute()

const isLoginPage = computed(() => route.path === '/login')

async function logout() {
  authStore.logout()
  await router.push('/login')
}
</script>

<template>
  <div v-if="isLoginPage">
    <RouterView />
  </div>
  <div v-else class="layout">
    <nav class="sidebar">
      <div class="brand">Publisher</div>
      <RouterLink to="/dashboard">Dashboard</RouterLink>
      <RouterLink to="/accounts">Accounts</RouterLink>
      <RouterLink to="/posts">Posts</RouterLink>
      <RouterLink to="/sessions">Sessions</RouterLink>
      <RouterLink to="/audit">Audit Log</RouterLink>
      <button class="logout-btn" @click="logout">Logout</button>
    </nav>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.layout { display: flex; min-height: 100vh; }
.sidebar {
  width: 220px;
  background: #1a1a2e;
  color: white;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-shrink: 0;
}
.brand { font-size: 1.25rem; font-weight: bold; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #333; }
.sidebar a { color: #ccc; text-decoration: none; padding: 0.5rem; border-radius: 4px; }
.sidebar a:hover, .sidebar a.router-link-active { color: white; background: #333; }
.logout-btn { margin-top: auto; background: transparent; border: 1px solid #555; color: #ccc; padding: 0.4rem; border-radius: 4px; cursor: pointer; }
.content { flex: 1; padding: 2rem; background: #f8f9fa; overflow-y: auto; }
</style>
