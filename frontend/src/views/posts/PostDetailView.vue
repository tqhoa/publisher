<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { usePost, usePublishNow, useRetryPost } from '@/features/posts/composables/usePosts'

const route = useRoute()
const router = useRouter()
const postId = computed(() => route.params.id as string)

const { data, isPending, isError, refetch } = usePost(postId)
const publishNow = usePublishNow()
const retryPost = useRetryPost()

async function onPublish() {
  await publishNow.mutateAsync(postId.value)
  await refetch()
}

async function onRetry() {
  await retryPost.mutateAsync(postId.value)
  await refetch()
}

const STATUS_COLORS: Record<string, string> = {
  pending: '#94a3b8', queued: '#60a5fa', publishing: '#f59e0b',
  published: '#22c55e', failed: '#ef4444', cancelled: '#6b7280',
}
</script>

<template>
  <div>
    <button @click="router.back()">← Back</button>
    <div v-if="isPending">Loading...</div>
    <div v-else-if="isError" class="error">Post not found</div>
    <div v-else-if="data?.data" class="card">
      <div class="top">
        <h2>Post Detail</h2>
        <span class="badge" :style="{ background: STATUS_COLORS[data.data.status] || '#888' }">{{ data.data.status }}</span>
      </div>

      <div class="meta">
        <div><strong>Platform:</strong> {{ data.data.platform }}</div>
        <div><strong>Account:</strong> {{ data.data.accountId }}</div>
        <div><strong>Content type:</strong> {{ data.data.contentType }}</div>
        <div v-if="data.data.scheduledAt"><strong>Scheduled:</strong> {{ new Date(data.data.scheduledAt).toLocaleString() }}</div>
        <div v-if="data.data.publishedAt"><strong>Published:</strong> {{ new Date(data.data.publishedAt).toLocaleString() }}</div>
        <div><strong>Retries:</strong> {{ data.data.retryCount }}</div>
      </div>

      <div v-if="data.data.caption" class="caption">
        <strong>Caption</strong>
        <p>{{ data.data.caption }}</p>
      </div>

      <div v-if="data.data.errorMessage" class="error-box">
        <strong>Error:</strong> {{ data.data.errorMessage }}
      </div>

      <div class="actions">
        <button
          v-if="data.data.status === 'pending'"
          @click="onPublish"
          :disabled="publishNow.isPending.value"
          class="primary"
        >
          Publish Now
        </button>
        <button
          v-if="data.data.status === 'failed'"
          @click="onRetry"
          :disabled="retryPost.isPending.value"
          class="primary"
        >
          {{ retryPost.isPending.value ? 'Retrying...' : 'Retry' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
button { padding: 0.4rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: white; margin-bottom: 1rem; }
button.primary { background: #1877f2; color: white; border-color: #1877f2; }
button:disabled { opacity: 0.6; }
.card { background: white; padding: 1.5rem; border-radius: 8px; }
.top { display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }
.top h2 { margin: 0; }
.badge { color: white; padding: 4px 12px; border-radius: 9999px; font-size: 0.85rem; }
.meta { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-bottom: 1rem; color: #555; }
.caption { background: #f8f9fa; padding: 1rem; border-radius: 4px; margin-bottom: 1rem; }
.caption p { margin: 0.5rem 0 0; }
.error-box { background: #fee2e2; color: #991b1b; padding: 0.75rem; border-radius: 4px; margin-bottom: 1rem; }
.actions { display: flex; gap: 0.5rem; }
.error { color: #d32f2f; }
</style>
