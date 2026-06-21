<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAccount, useImportCookie, useCheckHealth } from '@/features/accounts/composables/useAccounts'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string

const { data, isPending, isError } = useAccount(id)
const importCookie = useImportCookie()
const checkHealth = useCheckHealth()

const cookieJson = ref('')
const showCookieModal = ref(false)
const healthResult = ref<{ healthy: boolean; message?: string } | null>(null)

async function onImportCookie() {
  await importCookie.mutateAsync({ id, cookieJson: cookieJson.value })
  showCookieModal.value = false
  cookieJson.value = ''
}

async function onCheckHealth() {
  const res = await checkHealth.mutateAsync(id)
  healthResult.value = { healthy: res.data.healthy, message: res.data.message }
}
</script>

<template>
  <div>
    <button @click="router.back()">← Back</button>
    <div v-if="isPending">Loading...</div>
    <div v-else-if="isError" class="error">Account not found</div>
    <div v-else-if="data?.data" class="card">
      <h2>{{ data.data.username }}</h2>
      <div class="meta">
        <span>Platform: <strong>{{ data.data.platform }}</strong></span>
        <span>Status: <strong>{{ data.data.status }}</strong></span>
        <span>Health: <strong>{{ data.data.healthStatus || 'unknown' }}</strong></span>
      </div>
      <div class="actions">
        <button @click="showCookieModal = true">Import Cookie</button>
        <button @click="onCheckHealth" :disabled="checkHealth.isPending.value">
          {{ checkHealth.isPending.value ? 'Checking...' : 'Check Health' }}
        </button>
      </div>
      <div v-if="healthResult" class="health-result" :class="healthResult.healthy ? 'ok' : 'fail'">
        Health: {{ healthResult.healthy ? '✓ Healthy' : '✗ Unhealthy' }}
        <span v-if="healthResult.message"> — {{ healthResult.message }}</span>
      </div>
    </div>

    <div v-if="showCookieModal" class="modal-overlay" @click.self="showCookieModal = false">
      <div class="modal">
        <h3>Import Cookie</h3>
        <p class="hint">Paste the JSON cookie array from browser DevTools</p>
        <textarea v-model="cookieJson" rows="6" placeholder='[{"name":"c_user","value":"..."}]'></textarea>
        <div class="modal-actions">
          <button @click="showCookieModal = false">Cancel</button>
          <button class="primary" @click="onImportCookie" :disabled="!cookieJson">Import</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
button { padding: 0.4rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: white; margin-right: 0.5rem; }
button.primary { background: #1877f2; color: white; border-color: #1877f2; }
.card { background: white; padding: 1.5rem; border-radius: 8px; margin-top: 1rem; }
h2 { margin: 0 0 1rem; }
.meta { display: flex; gap: 1.5rem; margin-bottom: 1rem; color: #555; }
.actions { display: flex; margin-bottom: 1rem; }
.health-result { padding: 0.75rem; border-radius: 4px; font-weight: 500; }
.health-result.ok { background: #dcfce7; color: #166534; }
.health-result.fail { background: #fee2e2; color: #991b1b; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: white; padding: 1.5rem; border-radius: 8px; width: 480px; display: flex; flex-direction: column; gap: 0.75rem; }
.modal h3 { margin: 0; }
.hint { margin: 0; font-size: 0.85rem; color: #666; }
textarea { border: 1px solid #ddd; border-radius: 4px; padding: 0.5rem; font-family: monospace; font-size: 0.8rem; resize: vertical; }
.modal-actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
.error { color: #d32f2f; }
</style>
