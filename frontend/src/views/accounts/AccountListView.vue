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
  if (confirm('Delete account?')) {
    await deleteAccount.mutateAsync(id)
  }
}

function statusColor(status: string) {
  return status === 'active' ? '#22c55e' : status === 'inactive' ? '#94a3b8' : '#ef4444'
}

function healthColor(health: string | null) {
  if (health === 'healthy') return '#22c55e'
  if (health === 'unhealthy') return '#ef4444'
  return '#94a3b8'
}
</script>

<template>
  <div>
    <div class="header">
      <h2>Accounts</h2>
      <button @click="showCreate = true">+ Add Account</button>
    </div>

    <div v-if="isPending">Loading...</div>
    <div v-else-if="isError" class="error">Failed to load accounts</div>
    <table v-else>
      <thead>
        <tr>
          <th>Platform</th>
          <th>Username</th>
          <th>Status</th>
          <th>Health</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="acc in data?.data" :key="acc.id">
          <td>{{ acc.platform }}</td>
          <td>{{ acc.username }}</td>
          <td><span class="badge" :style="{ background: statusColor(acc.status) }">{{ acc.status }}</span></td>
          <td><span class="badge" :style="{ background: healthColor(acc.healthStatus) }">{{ acc.healthStatus || 'unknown' }}</span></td>
          <td>
            <button class="sm" @click="router.push(`/accounts/${acc.id}`)">Detail</button>
            <button class="sm danger" @click="onDelete(acc.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
      <div class="modal">
        <h3>Add Account</h3>
        <select v-model="newPlatform">
          <option value="facebook">Facebook</option>
          <option value="tiktok">TikTok</option>
        </select>
        <input v-model="newUsername" placeholder="Username" />
        <div class="modal-actions">
          <button @click="showCreate = false">Cancel</button>
          <button class="primary" @click="onCreate">Create</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
h2 { margin: 0; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #f0f0f0; }
th { background: #f8f9fa; font-weight: 600; font-size: 0.875rem; }
.badge { color: white; padding: 2px 8px; border-radius: 9999px; font-size: 0.75rem; }
button { padding: 0.4rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; cursor: pointer; background: white; }
button.primary { background: #1877f2; color: white; border-color: #1877f2; }
button.danger { color: #d32f2f; border-color: #d32f2f; }
button.sm { font-size: 0.8rem; padding: 0.25rem 0.5rem; margin-right: 4px; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 100; }
.modal { background: white; padding: 1.5rem; border-radius: 8px; width: 360px; display: flex; flex-direction: column; gap: 0.75rem; }
.modal h3 { margin: 0; }
.modal select, .modal input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; }
.modal-actions { display: flex; gap: 0.5rem; justify-content: flex-end; }
.error { color: #d32f2f; }
</style>
