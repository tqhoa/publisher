<script setup lang="ts">
import { ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import { auditApi } from '@/api/endpoints/audit.api'

const page = ref(1)
const actionFilter = ref('')

const { data, isPending, isError } = useQuery({
  queryKey: ['audit', page, actionFilter],
  queryFn: () => auditApi.list({ page: page.value, limit: 50, action: actionFilter.value || undefined }),
  staleTime: 10_000,
})
</script>

<template>
  <div>
    <div class="header">
      <h2>Audit Log</h2>
      <input v-model="actionFilter" placeholder="Filter by action..." class="filter-input" />
    </div>
    <div v-if="isPending">Loading...</div>
    <div v-else-if="isError" class="error">Failed to load audit log</div>
    <table v-else>
      <thead>
        <tr><th>Time</th><th>User</th><th>Action</th><th>Resource</th><th>IP</th></tr>
      </thead>
      <tbody>
        <tr v-for="log in data?.data" :key="log.id">
          <td class="mono">{{ new Date(log.createdAt).toLocaleString() }}</td>
          <td class="mono">{{ log.userId?.slice(0, 8) || '—' }}</td>
          <td><code>{{ log.action }}</code></td>
          <td>{{ log.resourceType ? `${log.resourceType}/${log.resourceId?.slice(0, 8)}` : '—' }}</td>
          <td>{{ log.ipAddress || '—' }}</td>
        </tr>
        <tr v-if="data?.data?.length === 0"><td colspan="5" class="empty">No audit logs</td></tr>
      </tbody>
    </table>
    <div v-if="data?.pagination" class="pagination">
      <button :disabled="page <= 1" @click="page--">← Prev</button>
      <span>Page {{ page }} of {{ data.pagination.totalPages }}</span>
      <button :disabled="page >= data.pagination.totalPages" @click="page++">Next →</button>
    </div>
  </div>
</template>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
h2 { margin: 0; }
.filter-input { padding: 0.4rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
th, td { padding: 0.65rem 1rem; text-align: left; border-bottom: 1px solid #f0f0f0; }
th { background: #f8f9fa; font-weight: 600; font-size: 0.875rem; }
.mono { font-family: monospace; font-size: 0.85rem; }
code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; font-size: 0.8rem; }
.empty { text-align: center; color: #888; }
.pagination { display: flex; gap: 1rem; align-items: center; margin-top: 1rem; justify-content: flex-end; }
button { padding: 0.35rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: white; }
button:disabled { opacity: 0.4; cursor: not-allowed; }
.error { color: #d32f2f; }
</style>
