<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { usePosts } from '@/features/posts/composables/usePosts'

const router = useRouter()
const statusFilter = ref('')
const platformFilter = ref('')

const { data, isPending, isError } = usePosts({
  status: statusFilter.value || undefined,
  platform: platformFilter.value || undefined,
})

const STATUS_COLORS: Record<string, string> = {
  pending: '#94a3b8',
  queued: '#60a5fa',
  publishing: '#f59e0b',
  published: '#22c55e',
  failed: '#ef4444',
  cancelled: '#6b7280',
}
</script>

<template>
  <div>
    <div class="header">
      <h2>Posts</h2>
      <button @click="router.push('/posts/create')">+ New Post</button>
    </div>

    <div class="filters">
      <select v-model="statusFilter">
        <option value="">All statuses</option>
        <option v-for="s in ['pending','queued','publishing','published','failed','cancelled']" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="platformFilter">
        <option value="">All platforms</option>
        <option value="facebook">Facebook</option>
        <option value="tiktok">TikTok</option>
      </select>
    </div>

    <div v-if="isPending">Loading...</div>
    <div v-else-if="isError" class="error">Failed to load posts</div>
    <table v-else>
      <thead>
        <tr><th>Platform</th><th>Caption</th><th>Status</th><th>Scheduled</th><th>Actions</th></tr>
      </thead>
      <tbody>
        <tr v-for="post in data?.data" :key="post.id">
          <td>{{ post.platform }}</td>
          <td class="caption">{{ post.caption?.slice(0, 60) || '—' }}</td>
          <td><span class="badge" :style="{ background: STATUS_COLORS[post.status] || '#888' }">{{ post.status }}</span></td>
          <td>{{ post.scheduledAt ? new Date(post.scheduledAt).toLocaleString() : '—' }}</td>
          <td><button class="sm" @click="router.push(`/posts/${post.id}`)">Detail</button></td>
        </tr>
      </tbody>
    </table>
    <div v-if="data && data.data.length === 0" class="empty">No posts found.</div>
  </div>
</template>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
h2 { margin: 0; }
.filters { display: flex; gap: 0.5rem; margin-bottom: 1rem; }
select { padding: 0.4rem 0.5rem; border: 1px solid #ddd; border-radius: 4px; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #f0f0f0; }
th { background: #f8f9fa; font-weight: 600; font-size: 0.875rem; }
.caption { max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.badge { color: white; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; }
button { padding: 0.4rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: white; }
button.sm { font-size: 0.8rem; padding: 0.25rem 0.5rem; }
.empty, .error { padding: 2rem; text-align: center; color: #888; }
.error { color: #d32f2f; }
</style>
