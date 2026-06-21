<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAccounts, useCreateAccount, useDeleteAccount } from '@/features/accounts/composables/useAccounts'

const router = useRouter()
const { data, isPending, isError } = useAccounts()
const createAccount = useCreateAccount()
const deleteAccount = useDeleteAccount()

const showCreate = ref(false)
const newPlatform = ref('facebook')
const newUsername = ref('')

async function onCreate() {
  await createAccount.mutateAsync({ platform: newPlatform.value, username: newUsername.value })
  showCreate.value = false
  newUsername.value = ''
}

async function onDelete(id: string) {
  if (confirm('Delete this account?')) {
    await deleteAccount.mutateAsync(id)
  }
}

const STATUS_STYLE: Record<string, { backgroundColor: string; color: string }> = {
  active:   { backgroundColor: '#dcfce7', color: '#166534' },
  inactive: { backgroundColor: '#f1f5f9', color: '#475569' },
  deleted:  { backgroundColor: '#fee2e2', color: '#991b1b' },
}

const HEALTH_STYLE: Record<string, { backgroundColor: string; color: string }> = {
  healthy:   { backgroundColor: '#dcfce7', color: '#166534' },
  unhealthy: { backgroundColor: '#fee2e2', color: '#991b1b' },
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
        <h2 class="page-title">Accounts</h2>
        <p class="page-sub">Manage your social media accounts</p>
      </div>
      <button class="btn-primary" @click="showCreate = true">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
        Add Account
      </button>
    </div>

    <div class="surface">
      <div v-if="isPending" class="state-msg">Loading accounts…</div>
      <div v-else-if="isError" class="state-msg error">Failed to load accounts</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Platform</th>
            <th>Username</th>
            <th>Status</th>
            <th>Health</th>
            <th>Updated</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="acc in data?.data" :key="acc.id">
            <td>
              <span class="badge" :style="PLATFORM_STYLE[acc.platform] ?? { backgroundColor: '#64748b', color: '#fff' }">
                {{ acc.platform }}
              </span>
            </td>
            <td class="username-cell">{{ acc.username }}</td>
            <td>
              <span class="badge" :style="STATUS_STYLE[acc.status] ?? STATUS_STYLE.inactive">
                {{ acc.status }}
              </span>
            </td>
            <td>
              <span class="badge" :style="HEALTH_STYLE[acc.healthStatus ?? ''] ?? { backgroundColor: '#f1f5f9', color: '#64748b' }">
                {{ acc.healthStatus ?? 'unknown' }}
              </span>
            </td>
            <td class="muted-cell">{{ acc.cookieUpdatedAt ? new Date(acc.cookieUpdatedAt).toLocaleDateString() : '—' }}</td>
            <td class="action-cell">
              <button class="btn-ghost" @click="router.push(`/accounts/${acc.id}`)">Detail</button>
              <button class="btn-danger-ghost" @click="onDelete(acc.id)">Delete</button>
            </td>
          </tr>
          <tr v-if="!data?.data?.length">
            <td colspan="6" class="empty-state">No accounts yet</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create modal -->
    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Add Account</h3>
          <button class="modal-close" @click="showCreate = false">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="field">
            <label>Platform</label>
            <select v-model="newPlatform">
              <option value="facebook">Facebook</option>
              <option value="tiktok">TikTok</option>
            </select>
          </div>
          <div class="field">
            <label>Username</label>
            <input v-model="newUsername" placeholder="e.g. my_page_name" />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-ghost" @click="showCreate = false">Cancel</button>
          <button class="btn-primary" :disabled="!newUsername || createAccount.isPending.value" @click="onCreate">
            {{ createAccount.isPending.value ? 'Creating…' : 'Create Account' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Page header */
.page-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.page-title { font-size: 20px; font-weight: 700; }
.page-sub { font-size: 13px; color: #64748b; margin-top: 2px; }

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

.username-cell { font-weight: 500; color: #0f172a; }
.muted-cell { color: #94a3b8; font-size: 13px; }
.action-cell { white-space: nowrap; }

.state-msg { padding: 40px; text-align: center; color: #64748b; }
.state-msg.error { color: #dc2626; }
.empty-state { padding: 40px; text-align: center; color: #94a3b8; font-size: 13.5px; }

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
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-ghost {
  padding: 5px 10px;
  background: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  color: #374151;
  font-size: 12.5px;
  margin-right: 6px;
  transition: background 0.12s, border-color 0.12s;
}
.btn-ghost:hover { background: #f1f5f9; border-color: #cbd5e1; }

.btn-danger-ghost {
  padding: 5px 10px;
  background: transparent;
  border: 1px solid #fecaca;
  border-radius: 6px;
  color: #dc2626;
  font-size: 12.5px;
  transition: background 0.12s;
}
.btn-danger-ghost:hover { background: #fee2e2; }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15,23,42,.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  backdrop-filter: blur(2px);
}
.modal {
  background: #fff;
  border-radius: 14px;
  width: 380px;
  box-shadow: 0 20px 60px rgba(0,0,0,.18);
  overflow: hidden;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px 16px;
  border-bottom: 1px solid #f1f5f9;
}
.modal-header h3 { font-size: 15px; font-weight: 600; }
.modal-close {
  background: transparent;
  border: none;
  padding: 4px;
  border-radius: 6px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-close:hover { background: #f1f5f9; color: #374151; }
.modal-close svg { width: 16px; height: 16px; }

.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.field { display: flex; flex-direction: column; gap: 5px; }
.field label { font-size: 12.5px; font-weight: 500; color: #374151; }
.field select, .field input {
  padding: 8px 10px;
  border: 1px solid #e2e8f0;
  border-radius: 7px;
  font-size: 13.5px;
  color: #0f172a;
  outline: none;
  transition: border-color 0.12s;
}
.field select:focus, .field input:focus { border-color: #2563eb; box-shadow: 0 0 0 3px rgba(37,99,235,.1); }

.modal-footer {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  padding: 14px 20px;
  background: #f8fafc;
  border-top: 1px solid #f1f5f9;
}
</style>
