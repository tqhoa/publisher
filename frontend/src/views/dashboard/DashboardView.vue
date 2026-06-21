<script setup lang="ts">
import { computed } from 'vue'
import { useAccounts } from '@/features/accounts/composables/useAccounts'
import { usePosts } from '@/features/posts/composables/usePosts'
import { useSessions } from '@/features/sessions/composables/useSessions'

const { data: accountsData } = useAccounts({ limit: 100 })
const { data: postsData } = usePosts({ limit: 50 })
const { data: sessionsData } = useSessions()

const today = new Date().toISOString().slice(0, 10)

const totalAccounts = computed(() => accountsData.value?.pagination?.total ?? 0)
const healthyAccounts = computed(() =>
  accountsData.value?.data?.filter(a => a.healthStatus === 'healthy').length ?? 0,
)
const postsToday = computed(() =>
  postsData.value?.data?.filter(p => p.createdAt?.startsWith(today)).length ?? 0,
)
const publishedToday = computed(() =>
  postsData.value?.data?.filter(p => p.status === 'published' && p.publishedAt?.startsWith(today)).length ?? 0,
)
const successRate = computed(() => {
  if (!postsToday.value) return '—'
  return `${Math.round((publishedToday.value / postsToday.value) * 100)}%`
})
const activeSessions = computed(() =>
  sessionsData.value?.data?.filter(s => s.status !== 'crashed').length ?? 0,
)
const recentPosts = computed(() => postsData.value?.data?.slice(0, 10) ?? [])

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60_000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

const kpis = computed(() => [
  {
    label: 'Total Accounts',
    value: totalAccounts.value,
    sub: `${healthyAccounts.value} healthy`,
    accent: '#2563eb',
    iconBg: '#dbeafe',
    iconColor: '#1d4ed8',
    iconPath: 'M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z',
  },
  {
    label: 'Healthy Accounts',
    value: healthyAccounts.value,
    sub: `of ${totalAccounts.value} total`,
    accent: '#16a34a',
    iconBg: '#dcfce7',
    iconColor: '#15803d',
    iconPath: 'M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    label: 'Posts Today',
    value: postsToday.value,
    sub: `${publishedToday.value} published`,
    accent: '#7c3aed',
    iconBg: '#ede9fe',
    iconColor: '#6d28d9',
    iconPath: 'M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z',
  },
  {
    label: 'Success Rate',
    value: successRate.value,
    sub: 'published / created',
    accent: '#0891b2',
    iconBg: '#cffafe',
    iconColor: '#0e7490',
    iconPath: 'M3 13.125C3 12.504 3.504 12 4.125 12h2.25c.621 0 1.125.504 1.125 1.125v6.75C7.5 20.496 6.996 21 6.375 21h-2.25A1.125 1.125 0 013 19.875v-6.75zM9.75 8.625c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125v11.25c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V8.625zM16.5 4.125c0-.621.504-1.125 1.125-1.125h2.25C20.496 3 21 3.504 21 4.125v15.75c0 .621-.504 1.125-1.125 1.125h-2.25a1.125 1.125 0 01-1.125-1.125V4.125z',
  },
  {
    label: 'Active Sessions',
    value: activeSessions.value,
    sub: 'browser farm',
    accent: '#ea580c',
    iconBg: '#ffedd5',
    iconColor: '#c2410c',
    iconPath: 'M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25',
  },
])

const PLATFORM_STYLE: Record<string, { backgroundColor: string; color: string }> = {
  facebook: { backgroundColor: '#1877f2', color: '#fff' },
  tiktok:   { backgroundColor: '#010101', color: '#fff' },
}

const STATUS_STYLE: Record<string, { backgroundColor: string; color: string }> = {
  pending:    { backgroundColor: '#f1f5f9', color: '#475569' },
  queued:     { backgroundColor: '#dbeafe', color: '#1e40af' },
  publishing: { backgroundColor: '#fef3c7', color: '#92400e' },
  published:  { backgroundColor: '#dcfce7', color: '#166534' },
  failed:     { backgroundColor: '#fee2e2', color: '#991b1b' },
  cancelled:  { backgroundColor: '#f3f4f6', color: '#6b7280' },
}
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h2 class="page-title">Dashboard</h2>
        <p class="page-sub">Overview of your publishing platform</p>
      </div>
    </div>

    <div class="kpi-grid">
      <div
        v-for="kpi in kpis"
        :key="kpi.label"
        class="kpi-card"
        :style="{ borderTopColor: kpi.accent }"
      >
        <div class="kpi-top">
          <span class="kpi-label">{{ kpi.label }}</span>
          <div class="kpi-icon" :style="{ background: kpi.iconBg, color: kpi.iconColor }">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
              <path :d="kpi.iconPath" />
            </svg>
          </div>
        </div>
        <div class="kpi-value" :style="{ color: kpi.accent }">{{ kpi.value }}</div>
        <div class="kpi-sub">{{ kpi.sub }}</div>
      </div>
    </div>

    <div class="surface">
      <div class="section-header">
        <h3>Recent Posts</h3>
        <RouterLink to="/posts" class="view-all">View all →</RouterLink>
      </div>

      <table v-if="recentPosts.length" class="data-table">
        <thead>
          <tr>
            <th>Platform</th>
            <th>Caption</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in recentPosts" :key="p.id">
            <td>
              <span class="badge" :style="PLATFORM_STYLE[p.platform] ?? { backgroundColor: '#64748b', color: '#fff' }">
                {{ p.platform }}
              </span>
            </td>
            <td class="caption-cell">{{ p.caption?.slice(0, 64) || '—' }}</td>
            <td>
              <span class="badge" :style="STATUS_STYLE[p.status] ?? STATUS_STYLE.pending">
                {{ p.status }}
              </span>
            </td>
            <td class="time-cell">{{ timeAgo(p.createdAt) }}</td>
          </tr>
        </tbody>
      </table>

      <div v-else class="empty-state">No posts yet</div>
    </div>
  </div>
</template>

<style scoped>
/* Page header */
.page-header { margin-bottom: 24px; }
.page-title { font-size: 20px; font-weight: 700; }
.page-sub { font-size: 13px; color: #64748b; margin-top: 2px; }

/* KPI grid */
.kpi-grid {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  margin-bottom: 24px;
}
.kpi-card {
  flex: 1;
  min-width: 160px;
  background: #fff;
  border-radius: 12px;
  padding: 18px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,.07);
  border-top: 3px solid transparent;
}
.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}
.kpi-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: #64748b;
}
.kpi-icon {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kpi-icon svg { width: 17px; height: 17px; }
.kpi-value { font-size: 2rem; font-weight: 700; line-height: 1; margin-bottom: 4px; }
.kpi-sub { font-size: 12px; color: #94a3b8; }

/* Surface card */
.surface {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,.07);
  overflow: hidden;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}
.section-header h3 { font-size: 14px; font-weight: 600; }
.view-all { font-size: 12.5px; color: #2563eb; font-weight: 500; }
.view-all:hover { text-decoration: underline; }

/* Table */
.data-table { width: 100%; border-collapse: collapse; }
.data-table th {
  text-align: left;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #64748b;
  padding: 10px 20px;
  border-bottom: 1px solid #e2e8f0;
  background: #f8fafc;
}
.data-table td {
  padding: 11px 20px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 13.5px;
}
.data-table tbody tr:last-child td { border-bottom: none; }
.data-table tbody tr:hover { background: #f8fafc; }

.badge {
  display: inline-block;
  padding: 2px 9px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 500;
  text-transform: capitalize;
}

.caption-cell {
  max-width: 280px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #334155;
}

.time-cell { color: #94a3b8; font-size: 13px; white-space: nowrap; }

.empty-state { padding: 40px; text-align: center; color: #94a3b8; font-size: 13.5px; }
</style>
