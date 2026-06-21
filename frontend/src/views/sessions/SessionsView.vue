<script setup lang="ts">
import { computed } from 'vue'
import { useSessions } from '@/features/sessions/composables/useSessions'

const { data, isPending } = useSessions()

const sessions = computed(() => data.value?.data ?? [])
const total = computed(() => sessions.value.length)
const idle = computed(() => sessions.value.filter(s => s.status === 'idle').length)
const busy = computed(() => sessions.value.filter(s => s.status === 'busy').length)
const crashed = computed(() => sessions.value.filter(s => s.status === 'crashed').length)

const STATUS_COLOR: Record<string, string> = {
  idle: '#22c55e',
  busy: '#f59e0b',
  crashed: '#ef4444',
  starting: '#60a5fa',
}
</script>

<template>
  <div>
    <h2>Browser Sessions</h2>
    <div class="stats">
      <div class="stat"><span class="num">{{ total }}</span><span class="lbl">Total</span></div>
      <div class="stat ok"><span class="num">{{ idle }}</span><span class="lbl">Idle</span></div>
      <div class="stat warn"><span class="num">{{ busy }}</span><span class="lbl">Busy</span></div>
      <div class="stat err"><span class="num">{{ crashed }}</span><span class="lbl">Crashed</span></div>
    </div>
    <div v-if="isPending">Loading...</div>
    <table v-else>
      <thead>
        <tr><th>Account ID</th><th>Node</th><th>Status</th><th>Last Activity</th></tr>
      </thead>
      <tbody>
        <tr v-for="s in sessions" :key="s.id">
          <td class="mono">{{ s.accountId }}</td>
          <td>{{ s.nodeId }}</td>
          <td><span class="dot" :style="{ background: STATUS_COLOR[s.status] || '#888' }"></span> {{ s.status }}</td>
          <td>{{ new Date(s.lastActivityAt).toLocaleString() }}</td>
        </tr>
        <tr v-if="sessions.length === 0"><td colspan="4" class="empty">No active sessions</td></tr>
      </tbody>
    </table>
    <p class="hint">Auto-refreshes every 5 seconds</p>
  </div>
</template>

<style scoped>
h2 { margin: 0 0 1rem; }
.stats { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.stat { background: white; padding: 1rem 1.5rem; border-radius: 8px; display: flex; flex-direction: column; align-items: center; min-width: 80px; }
.stat.ok .num { color: #22c55e; }
.stat.warn .num { color: #f59e0b; }
.stat.err .num { color: #ef4444; }
.num { font-size: 2rem; font-weight: bold; }
.lbl { font-size: 0.8rem; color: #888; }
table { width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }
th, td { padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #f0f0f0; }
th { background: #f8f9fa; font-weight: 600; font-size: 0.875rem; }
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; vertical-align: middle; }
.mono { font-family: monospace; font-size: 0.85rem; }
.empty { text-align: center; color: #888; }
.hint { font-size: 0.8rem; color: #999; margin-top: 0.5rem; }
</style>
