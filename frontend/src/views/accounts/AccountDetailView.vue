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

const PLATFORM_STYLE: Record<string, { backgroundColor: string; color: string }> = {
  facebook: { backgroundColor: '#1877f2', color: '#fff' },
  tiktok:   { backgroundColor: '#010101', color: '#fff' },
}
const STATUS_STYLE: Record<string, { backgroundColor: string; color: string }> = {
  active:   { backgroundColor: '#dcfce7', color: '#166534' },
  inactive: { backgroundColor: '#f1f5f9', color: '#475569' },
  deleted:  { backgroundColor: '#fee2e2', color: '#991b1b' },
}
</script>

<template>
  <div>
    <button class="back-btn" @click="router.back()">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
      </svg>
      Back
    </button>

    <div v-if="isPending" class="state-msg">Loading account…</div>
    <div v-else-if="isError" class="state-msg error">Account not found</div>

    <div v-else-if="data?.data" class="surface">
      <div class="card-header">
        <div class="account-id">
          <span class="badge" :style="PLATFORM_STYLE[data.data.platform] ?? {}">{{ data.data.platform }}</span>
          <h2>{{ data.data.username }}</h2>
        </div>
        <span class="badge" :style="STATUS_STYLE[data.data.status] ?? {}">{{ data.data.status }}</span>
      </div>

      <div class="meta-grid">
        <div class="meta-item">
          <span class="meta-label">Health status</span>
          <span class="meta-value">{{ data.data.healthStatus ?? 'unknown' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Cookie updated</span>
          <span class="meta-value">{{ data.data.cookieUpdatedAt ? new Date(data.data.cookieUpdatedAt).toLocaleString() : 'Never' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Last health check</span>
          <span class="meta-value">{{ data.data.lastHealthCheckAt ? new Date(data.data.lastHealthCheckAt).toLocaleString() : 'Never' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">Created</span>
          <span class="meta-value">{{ new Date(data.data.createdAt).toLocaleDateString() }}</span>
        </div>
      </div>

      <div v-if="healthResult" class="health-banner" :class="healthResult.healthy ? 'healthy' : 'unhealthy'">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path v-if="healthResult.healthy" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          <path v-else d="M9.75 9.75l4.5 4.5m0-4.5l-4.5 4.5M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        {{ healthResult.healthy ? 'Healthy' : 'Unhealthy' }}
        <span v-if="healthResult.message" class="health-msg">— {{ healthResult.message }}</span>
      </div>

      <div class="card-actions">
        <button class="btn-ghost" @click="showCookieModal = true">Import Cookie</button>
        <button class="btn-primary" :disabled="checkHealth.isPending.value" @click="onCheckHealth">
          {{ checkHealth.isPending.value ? 'Checking…' : 'Check Health' }}
        </button>
      </div>
    </div>

    <!-- Cookie import modal -->
    <div v-if="showCookieModal" class="modal-overlay" @click.self="showCookieModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Import Cookie</h3>
          <button class="modal-close" @click="showCookieModal = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
          </button>
        </div>
        <div class="modal-body">
          <p class="hint">Paste the JSON cookie array from browser DevTools → Application → Cookies → Export</p>
          <textarea v-model="cookieJson" rows="7" placeholder='[{"name":"c_user","value":"...","domain":".facebook.com"}]'></textarea>
        </div>
        <div class="modal-footer">
          <button class="btn-ghost" @click="showCookieModal = false">Cancel</button>
          <button class="btn-primary" :disabled="!cookieJson || importCookie.isPending.value" @click="onImportCookie">
            {{ importCookie.isPending.value ? 'Importing…' : 'Import' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  color: #475569;
  font-size: 13px;
  margin-bottom: 20px;
  transition: background 0.12s;
}
.back-btn svg { width: 15px; height: 15px; }
.back-btn:hover { background: #f1f5f9; }

.surface { background: #fff; border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,.07); overflow: hidden; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
}
.account-id { display: flex; align-items: center; gap: 12px; }
.account-id h2 { font-size: 18px; }

.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 500;
  text-transform: capitalize;
}

.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0;
  border-bottom: 1px solid #f1f5f9;
}
.meta-item {
  padding: 16px 24px;
  border-right: 1px solid #f1f5f9;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.meta-item:last-child { border-right: none; }
.meta-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; color: #94a3b8; }
.meta-value { font-size: 13.5px; color: #0f172a; font-weight: 500; }

.health-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 16px 24px 0;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13.5px;
  font-weight: 500;
}
.health-banner svg { width: 18px; height: 18px; flex-shrink: 0; }
.health-banner.healthy { background: #f0fdf4; color: #166534; }
.health-banner.unhealthy { background: #fff1f2; color: #991b1b; }
.health-msg { font-weight: 400; color: inherit; opacity: 0.8; }

.card-actions {
  display: flex;
  gap: 10px;
  padding: 20px 24px;
}

/* Buttons */
.btn-primary {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px; background: #2563eb; color: #fff;
  border: none; border-radius: 8px; font-size: 13.5px; font-weight: 500;
  transition: background 0.12s;
}
.btn-primary:hover { background: #1d4ed8; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-ghost {
  padding: 8px 16px; background: transparent;
  border: 1px solid #e2e8f0; border-radius: 8px;
  color: #374151; font-size: 13.5px;
  transition: background 0.12s, border-color 0.12s;
}
.btn-ghost:hover { background: #f1f5f9; border-color: #cbd5e1; }

/* Modal */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(15,23,42,.45);
  display: flex; align-items: center; justify-content: center;
  z-index: 100; backdrop-filter: blur(2px);
}
.modal { background: #fff; border-radius: 14px; width: 520px; box-shadow: 0 20px 60px rgba(0,0,0,.18); overflow: hidden; }
.modal-header { display: flex; justify-content: space-between; align-items: center; padding: 18px 20px 16px; border-bottom: 1px solid #f1f5f9; }
.modal-header h3 { font-size: 15px; font-weight: 600; }
.modal-close { background: transparent; border: none; padding: 4px; border-radius: 6px; color: #94a3b8; display: flex; }
.modal-close:hover { background: #f1f5f9; color: #374151; }
.modal-close svg { width: 16px; height: 16px; }
.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 10px; }
.hint { font-size: 12.5px; color: #64748b; }
textarea { width: 100%; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px; font-family: var(--font-mono); font-size: 12px; resize: vertical; color: #0f172a; outline: none; }
textarea:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.1); }
.modal-footer { display: flex; gap: 8px; justify-content: flex-end; padding: 14px 20px; background: #f8fafc; border-top: 1px solid #f1f5f9; }

.state-msg { padding: 40px; text-align: center; color: #64748b; }
.state-msg.error { color: #dc2626; }
</style>
