<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAccounts } from '@/features/accounts/composables/useAccounts'
import { useCreatePost } from '@/features/posts/composables/usePosts'

const router = useRouter()
const { data: accountsData } = useAccounts()
const createPost = useCreatePost()

const accountId = ref('')
const platform = ref('facebook')
const contentType = ref('text')
const caption = ref('')
const hashtags = ref('')
const mediaUrls = ref('')
const scheduledAt = ref('')
const error = ref('')

async function onSubmit() {
  error.value = ''
  try {
    await createPost.mutateAsync({
      accountId: accountId.value,
      platform: platform.value,
      contentType: contentType.value,
      caption: caption.value || undefined,
      hashtags: hashtags.value ? hashtags.value.split(',').map(t => t.trim()).filter(Boolean) : undefined,
      mediaUrls: mediaUrls.value ? mediaUrls.value.split('\n').map(u => u.trim()).filter(Boolean) : undefined,
      scheduledAt: scheduledAt.value || undefined,
    })
    await router.push('/posts')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    error.value = err.response?.data?.error?.message || 'Failed to create post'
  }
}
</script>

<template>
  <div class="card">
    <h2>New Post</h2>
    <form @submit.prevent="onSubmit">
      <div class="field">
        <label>Account</label>
        <select v-model="accountId" required>
          <option value="" disabled>Select account</option>
          <option v-for="acc in accountsData?.data" :key="acc.id" :value="acc.id">
            {{ acc.platform }} — {{ acc.username }}
          </option>
        </select>
      </div>
      <div class="field">
        <label>Platform</label>
        <select v-model="platform">
          <option value="facebook">Facebook</option>
          <option value="tiktok">TikTok</option>
        </select>
      </div>
      <div class="field">
        <label>Content type</label>
        <select v-model="contentType">
          <option value="text">Text</option>
          <option value="image">Image</option>
          <option value="video">Video</option>
        </select>
      </div>
      <div class="field">
        <label>Caption</label>
        <textarea v-model="caption" rows="4" placeholder="Write your caption..."></textarea>
      </div>
      <div class="field">
        <label>Hashtags (comma-separated)</label>
        <input v-model="hashtags" placeholder="travel, food, lifestyle" />
      </div>
      <div class="field" v-if="contentType !== 'text'">
        <label>Media URLs (one per line)</label>
        <textarea v-model="mediaUrls" rows="3" placeholder="/path/to/file.jpg"></textarea>
      </div>
      <div class="field">
        <label>Schedule (optional)</label>
        <input v-model="scheduledAt" type="datetime-local" />
      </div>
      <p v-if="error" class="error">{{ error }}</p>
      <div class="actions">
        <button type="button" @click="router.back()">Cancel</button>
        <button type="submit" class="primary" :disabled="createPost.isPending.value">
          {{ createPost.isPending.value ? 'Creating...' : 'Create Post' }}
        </button>
      </div>
    </form>
  </div>
</template>

<style scoped>
.card { background: white; padding: 1.5rem; border-radius: 8px; max-width: 600px; }
h2 { margin: 0 0 1.5rem; }
.field { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 4px; }
label { font-size: 0.875rem; font-weight: 500; }
input, select, textarea { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.95rem; }
.actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
button { padding: 0.5rem 1rem; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: white; }
button.primary { background: #1877f2; color: white; border-color: #1877f2; }
button:disabled { opacity: 0.6; }
.error { color: #d32f2f; font-size: 0.875rem; }
</style>
