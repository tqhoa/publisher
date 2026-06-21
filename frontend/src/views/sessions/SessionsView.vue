<script setup lang="ts">
import { computed } from 'vue'
import { useSessions } from '@/features/sessions/composables/useSessions'

const { data, isPending, isError, dataUpdatedAt } = useSessions()

const sessions = computed(() => data.value?.data ?? [])
const total    = computed(() => sessions.value.length)
const idle     = computed(() => sessions.value.filter(s => s.status === 'idle').length)
const busy     = computed(() => sessions.value.filter(s => s.status === 'busy').length)
const crashed  = computed(() => sessions.value.filter(s => s.status === 'crashed').length)
const starting = computed(() => sessions.value.filter(s => s.status === 'starting').length)

const lastRefreshed = computed(() => {
  if (!dataUpdatedAt.value) return '—'
  return new Date(dataUpdatedAt.value).toLocaleTimeString()
})

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const s = Math.floor(diff / 1_000)
  if (s < 60) return `${s}s ago`
  const m = Math.floor(s / 60)
  if (m < 60) return `${m}m ago`
  return `${Math.floor(m / 60)}h ago`
}

const STATUS_STYLE: Record<string, { backgroundColor: string; color: string }> = {
  idle:     { backgroundColor: '#dcfce7', color: '#166534' },
  busy:     { backgroundColor: '#fef3c7', color: '#92400e' },
  crashed:  { backgroundColor: '#fee2e2', color: '#991b1b' },
  starting: { backgroundColor: '#dbeafe', color: '#1e40af' },
}

const kpis = [
  {
    label: 'Total',
    key: 'total' as const,
    accent: '#2563eb',
    iconBg: '#dbeafe',
    iconColor: '#1d4ed8',
    iconPath: 'M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25',
  },
  {
    label: 'Idle',
    key: 'idle' as const,
    accent: '#16a34a',
    iconBg: '#dcfce7',
    iconColor: '#15803d',
    iconPath: 'M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z',
  },
  {
    label: 'Busy',
    key: 'busy' as const,
    accent: '#d97706',
    iconBg: '#fef3c7',
    iconColor: '#b45309',
    iconPath: 'M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0l3.181 3.183a8.25 8.25 0 0013.803-3.7M4.031 9.865a8.25 8.25 0 0113.803-3.7l3.181 3.182m0-4.991v4.99',
  },
  {
    label: 'Crashed',
    key: 'crashed' as const,
    accent: '#dc2626',
    iconBg: '#fee2e2',
    iconColor: '#b91c1c',
    iconPath: 'M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z',
  },
]

const counts = computed(() => ({ total: total.value, idle: idle.value, busy: busy.value, crashed: crashed.value }))
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h2 class="page-title">Browser Sessions</h2>
        <p class="page-sub">Live browser farm status — auto-refreshes every 5s</p>
      </div>
      <div class="refresh-info">
        <span class="refresh-dot" :class="{ active: !isPending }"></span>
        <span class="refresh-label">Last updated {{ lastRefreshed }}</span>
      </div>
    </div>

    <!-- KPI cards -->
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
        <div class="kpi-value" :style="{ color: kpi.accent }">{{ counts[kpi.key] }}</div>
        <div class="kpi-sub">
          <template v-if="kpi.key === 'total'">{{ starting }} starting</template>
          <template v-else-if="kpi.key === 'idle'">ready for work</template>
          <template v-else-if="kpi.key === 'busy'">running jobs</template>
          <template v-else>needs attention</template>
        </div>
      </div>
    </div>

    <!-- Sessions table -->
    <div class="surface">
      <div class="section-header">
        <h3>Active Sessions</h3>
        <span class="session-count" v-if="!isPending">{{ total }} session{{ total !== 1 ? 's' : '' }}</span>
      </div>

      <div v-if="isPending" class="state-msg">Loading sessions…</div>
      <div v-else-if="isError" class="state-msg error">Failed to load sessions</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Account</th>
            <th>Node</th>
            <th>Status</th>
            <th>Last Activity</th>
            <th>Started</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="s in sessions" :key="s.id">
            <td class="mono-cell">{{ s.accountId }}</td>
            <td class="node-cell">{{ s.nodeId || '—' }}</td>
            <td>
              <span class="badge" :style="STATUS_STYLE[s.status] ?? { backgroundColor: '#f1f5f9', color: '#475569' }">
                {{ s.status }}
              </span>
            </td>
            <td class="muted-cell">{{ timeAgo(s.lastActivityAt) }}</td>
            <td class="muted-cell">{{ s.startedAt ? new Date(s.startedAt).toLocaleString() : '—' }}</td>
          </tr>
          <tr v-if="sessions.length === 0">
            <td colspan="5" class="empty-state">No active sessions</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
/* Page header */
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-title { font-size: 20px; font-weight: 700; }
.page-sub { font-size: 13px; color: #64748b; margin-top: 2px; }

.refresh-info {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 6px 12px;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 999px;
  font-size: 12px;
  color: #64748b;
}
.refresh-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #cbd5e1;
  transition: background 0.3s;
}
.refresh-dot.active { background: #22c55e; }
.refresh-label { white-space: nowrap; }

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

/* Surface */
.surface { background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.07); overflow: hidden; }

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f1f5f9;
}
.section-header h3 { font-size: 14px; font-weight: 600; }
.session-count { font-size: 12px; color: #94a3b8; }

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
.data-table td { padding: 12px 20px; border-bottom: 1px solid #f1f5f9; font-size: 13.5px; }
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

.mono-cell { font-family: var(--font-mono, ui-monospace, monospace); font-size: 12.5px; color: #334155; }
.node-cell { font-size: 13px; color: #475569; }
.muted-cell { color: #94a3b8; font-size: 13px; white-space: nowrap; }

.state-msg { padding: 40px; text-align: center; color: #64748b; }
.state-msg.error { color: #dc2626; }
.empty-state { padding: 40px; text-align: center; color: #94a3b8; font-size: 13.5px; }
</style>
