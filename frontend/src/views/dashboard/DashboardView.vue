<script setup lang="ts">
import { computed } from 'vue'
import { useAccounts } from '@/features/accounts/composables/useAccounts'
import { usePosts } from '@/features/posts/composables/usePosts'
import { useSessions } from '@/features/sessions/composables/useSessions'

const { data: accountsData } = useAccounts({ limit: 100 })
const { data: postsData } = usePosts({ limit: 10 })
const { data: sessionsData } = useSessions()

const today = new Date().toISOString().slice(0, 10)

const totalAccounts = computed(() => accountsData.value?.pagination?.total ?? 0)
const healthyAccounts = computed(() =>
  accountsData.value?.data?.filter(a => a.healthStatus === 'healthy').length ?? 0
)
const postsToday = computed(() =>
  postsData.value?.data?.filter(p => p.createdAt?.startsWith(today)).length ?? 0
)
const publishedToday = computed(() =>
  postsData.value?.data?.filter(p => p.status === 'published' && p.publishedAt?.startsWith(today)).length ?? 0
)
const successRate = computed(() => {
  if (!postsToday.value) return 'N/A'
  return `${Math.round((publishedToday.value / postsToday.value) * 100)}%`
})
const activeSessions = computed(() =>
  sessionsData.value?.data?.filter(s => s.status !== 'crashed').length ?? 0
)
const recentPosts = computed(() => postsData.value?.data?.slice(0, 10) ?? [])

const STATUS_COLORS: Record<string, string> = {
  pending: '#94a3b8', queued: '#60a5fa', publishing: '#f59e0b',
  published: '#22c55e', failed: '#ef4444', cancelled: '#6b7280',
}
</script>

<template>
  <div>
    <h2>Dashboard</h2>
    <div class="kpi-row">
      <div class="kpi"><div class="kpi-val">{{ totalAccounts }}</div><div class="kpi-lbl">Total Accounts</div></div>
      <div class="kpi"><div class="kpi-val ok">{{ healthyAccounts }}</div><div class="kpi-lbl">Healthy Accounts</div></div>
      <div class="kpi"><div class="kpi-val">{{ postsToday }}</div><div class="kpi-lbl">Posts Today</div></div>
      <div class="kpi"><div class="kpi-val ok">{{ successRate }}</div><div class="kpi-lbl">Success Rate</div></div>
      <div class="kpi"><div class="kpi-val">{{ activeSessions }}</div><div class="kpi-lbl">Active Sessions</div></div>
    </div>

    <div class="section">
      <h3>Recent Posts</h3>
      <table v-if="recentPosts.length">
        <thead><tr><th>Platform</th><th>Caption</th><th>Status</th><th>Created</th></tr></thead>
        <tbody>
          <tr v-for="p in recentPosts" :key="p.id">
            <td>{{ p.platform }}</td>
            <td class="caption">{{ p.caption?.slice(0, 50) || '—' }}</td>
            <td><span class="badge" :style="{ background: STATUS_COLORS[p.status] || '#888' }">{{ p.status }}</span></td>
            <td>{{ new Date(p.createdAt).toLocaleDateString() }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="empty">No posts yet</p>
    </div>
  </div>
</template>

<style scoped>
h2, h3 { margin: 0 0 1rem; }
.kpi-row { display: flex; gap: 1rem; margin-bottom: 2rem; flex-wrap: wrap; }
.kpi { background: white; padding: 1.25rem 1.5rem; border-radius: 8px; min-width: 130px; text-align: center; }
.kpi-val { font-size: 2rem; font-weight: bold; }
.kpi-val.ok { color: #22c55e; }
.kpi-lbl { font-size: 0.8rem; color: #888; margin-top: 4px; }
.section { background: white; padding: 1.25rem; border-radius: 8px; }
table { width: 100%; border-collapse: collapse; }
th, td { padding: 0.6rem 0.75rem; text-align: left; border-bottom: 1px solid #f0f0f0; }
th { font-weight: 600; font-size: 0.875rem; color: #555; }
.caption { max-width: 280px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.badge { color: white; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; }
.empty { color: #888; text-align: center; padding: 1rem; }
</style>
