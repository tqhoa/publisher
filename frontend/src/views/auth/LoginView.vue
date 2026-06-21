<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'
import { authApi } from '@/api/endpoints/auth.api'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function onSubmit() {
  error.value = ''
  loading.value = true
  try {
    const res = await authApi.login(email.value, password.value)
    authStore.setToken(res.data.accessToken)
    authStore.setUser(res.data.user)
    await router.push('/dashboard')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    error.value = err.response?.data?.error?.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap">
    <div class="login-card">
      <h1>Publisher</h1>
      <form @submit.prevent="onSubmit">
        <div class="field">
          <label for="email">Email</label>
          <input id="email" v-model="email" type="email" autocomplete="email" required />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input id="password" v-model="password" type="password" autocomplete="current-password" required />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" :disabled="loading">
          {{ loading ? 'Signing in...' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: #f5f5f5;
}
.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  width: 100%;
  max-width: 400px;
}
h1 { margin: 0 0 1.5rem; font-size: 1.5rem; }
.field { margin-bottom: 1rem; display: flex; flex-direction: column; gap: 4px; }
label { font-size: 0.875rem; font-weight: 500; }
input { padding: 0.5rem 0.75rem; border: 1px solid #ddd; border-radius: 4px; font-size: 1rem; }
button { width: 100%; padding: 0.6rem; background: #1877f2; color: white; border: none; border-radius: 4px; font-size: 1rem; cursor: pointer; margin-top: 0.5rem; }
button:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #d32f2f; font-size: 0.875rem; margin: 0.5rem 0; }
</style>
