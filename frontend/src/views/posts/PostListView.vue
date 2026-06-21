<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePosts } from '@/features/posts/composables/usePosts'

const router = useRouter()

const STATUSES = ['pending', 'queued', 'publishing', 'published', 'failed', 'cancelled']
const PLATFORMS = ['facebook', 'tiktok']

const statusFilter = ref('')
const platformFilter = ref('')

const filters = computed(() => ({
  status: statusFilter.value || undefined,
  platform: platformFilter.value || undefined,
}))

const { data, isPending, isError } = usePosts(filters)

function toggleStatus(s: string) {
  statusFilter.value = statusFilter.value === s ? '' : s
}
function togglePlatform(p: string) {
  platformFilter.value = platformFilter.value === p ? '' : p
}

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  const m = Math.floor(diff / 60_000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}

const STATUS_STYLE: Record<string, { backgroundColor: string; color: string }> = {
  pending:    { backgroundColor: '#f1f5f9', color: '#475569' },
  queued:     { backgroundColor: '#dbeafe', color: '#1e40af' },
  publishing: { backgroundColor: '#fef3c7', color: '#92400e' },
  published:  { backgroundColor: '#dcfce7', color: '#166534' },
  failed:     { backgroundColor: '#fee2e2', color: '#991b1b' },
  cancelled:  { backgroundColor: '#f3f4f6', color: '#6b7280' },
}

const PLATFORM_STYLE: Record<string, { backgroundColor: string; color: string }> = {
  facebook: { backgroundColor: '#1877f2', color: '#fff' },
  tiktok:   { backgroundColor: '#010101', color: '#fff' },
}
</script>

<template>
  <div>
    <div class="page-header">
      <div>
        <h2 class="page-title">Posts</h2>
        <p class="page-sub">Manage and monitor your scheduled content</p>
      </div>
      <button class="btn-primary" @click="router.push('/posts/create')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        New Post
      </button>
    </div>

    <!-- Filters -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="filter-label">Status</span>
        <button
          v-for="s in STATUSES"
          :key="s"
          class="filter-pill"
          :class="{ active: statusFilter === s }"
          :style="statusFilter === s ? STATUS_STYLE[s] : undefined"
          @click="toggleStatus(s)"
        >{{ s }}</button>
      </div>
      <div class="filter-group">
        <span class="filter-label">Platform</span>
        <button
          v-for="p in PLATFORMS"
          :key="p"
          class="filter-pill"
          :class="{ active: platformFilter === p }"
          :style="platformFilter === p ? PLATFORM_STYLE[p] : undefined"
          @click="togglePlatform(p)"
        >{{ p }}</button>
      </div>
      <button v-if="statusFilter || platformFilter" class="clear-btn" @click="statusFilter = ''; platformFilter = ''">
        Clear filters
      </button>
    </div>

    <div class="surface">
      <div v-if="isPending" class="state-msg">Loading posts…</div>
      <div v-else-if="isError" class="state-msg error">Failed to load posts</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Platform</th>
            <th>Caption</th>
            <th>Status</th>
            <th>Scheduled</th>
            <th>Created</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="post in data?.data" :key="post.id">
            <td>
              <span class="badge" :style="PLATFORM_STYLE[post.platform] ?? { backgroundColor: '#64748b', color: '#fff' }">
                {{ post.platform }}
              </span>
            </td>
            <td class="caption-cell">{{ post.caption?.slice(0, 60) || '—' }}</td>
            <td>
              <span class="badge" :style="STATUS_STYLE[post.status] ?? STATUS_STYLE.pending">
                {{ post.status }}
              </span>
            </td>
            <td class="muted-cell">{{ post.scheduledAt ? new Date(post.scheduledAt).toLocaleString() : '—' }}</td>
            <td class="muted-cell">{{ timeAgo(post.createdAt) }}</td>
            <td>
              <button class="btn-ghost" @click="router.push(`/posts/${post.id}`)">Detail</button>
            </td>
          </tr>
          <tr v-if="!data?.data?.length">
            <td colspan="6" class="empty-state">No posts found</td>
          </tr>
        </tbody>
      </table>

      <div v-if="data?.pagination && data.pagination.totalPages > 1" class="pagination">
        <span class="pagination-info">{{ data.pagination.total }} posts</span>
        <span>Page {{ data.pagination.page }} of {{ data.pagination.totalPages }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Page header */
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.page-title { font-size: 20px; font-weight: 700; }
.page-sub { font-size: 13px; color: #64748b; margin-top: 2px; }

/* Filter bar */
.filter-bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  padding: 14px 16px;
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,.06);
}
.filter-group { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.filter-label { font-size: 11.5px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.4px; margin-right: 2px; }

.filter-pill {
  padding: 4px 11px;
  border-radius: 999px;
  border: 1px solid #e2e8f0;
  background: #fff;
  font-size: 12px;
  font-weight: 500;
  color: #475569;
  text-transform: capitalize;
  transition: all 0.12s;
}
.filter-pill:hover { border-color: #cbd5e1; background: #f8fafc; }
.filter-pill.active { border-color: transparent; }

.clear-btn {
  margin-left: auto;
  padding: 4px 10px;
  background: transparent;
  border: none;
  font-size: 12px;
  color: #64748b;
  border-radius: 6px;
  text-decoration: underline;
}
.clear-btn:hover { color: #0f172a; }

/* Surface */
.surface { background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.07); overflow: hidden; }

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
.caption-cell { max-width: 280px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #334155; }
.muted-cell { color: #94a3b8; font-size: 13px; white-space: nowrap; }

.state-msg { padding: 40px; text-align: center; color: #64748b; }
.state-msg.error { color: #dc2626; }
.empty-state { padding: 40px; text-align: center; color: #94a3b8; font-size: 13.5px; }

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  border-top: 1px solid #f1f5f9;
  font-size: 13px;
  color: #64748b;
}
.pagination-info { color: #94a3b8; }

/* Buttons */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 500;
  transition: background 0.12s;
}
.btn-primary svg { width: 15px; height: 15px; }
.btn-primary:hover { background: #1d4ed8; }

.btn-ghost {
  padding: 5px 10px;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #374151;
  font-size: 12.5px;
  transition: background 0.12s, border-color 0.12s;
}
.btn-ghost:hover { background: #f1f5f9; border-color: #cbd5e1; }
</style>
