<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/useAuthStore'
import { authApi } from '@/api/endpoints/auth.api'

const router = useRouter()
const authStore = useAuthStore()

const email    = ref('')
const password = ref('')
const error    = ref('')
const loading  = ref(false)
const showPass = ref(false)

async function onSubmit() {
  error.value   = ''
  loading.value = true
  try {
    const res = await authApi.login(email.value, password.value)
    authStore.setToken(res.data.access_token)
    authStore.setUser(res.data.user)
    await router.push('/dashboard')
  } catch (e: unknown) {
    const err = e as { response?: { data?: { error?: { message?: string } } } }
    error.value = err.response?.data?.error?.message || 'Invalid email or password'
  } finally {
    loading.value = false
  }
}

const features = [
  {
    iconPath: 'M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5',
    title: 'Multi-platform Publishing',
    desc: 'Facebook & TikTok from one place',
  },
  {
    iconPath: 'M12 6v6h4.5m4.5 0a9 9 0 11-18 0 9 9 0 0118 0z',
    title: 'Scheduled Automation',
    desc: 'Queue posts and let the platform handle timing',
  },
  {
    iconPath: 'M9 17.25v1.007a3 3 0 01-.879 2.122L7.5 21h9l-.621-.621A3 3 0 0115 18.257V17.25m6-12V15a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 15V5.25m18 0A2.25 2.25 0 0018.75 3H5.25A2.25 2.25 0 003 5.25m18 0V12a2.25 2.25 0 01-2.25 2.25H5.25A2.25 2.25 0 013 12V5.25',
    title: 'Browser Farm',
    desc: 'Parallel sessions for high-volume output',
  },
]
</script>

<template>
  <div class="page">
    <!-- Left panel -->
    <div class="panel-left">
      <div class="panel-content">
        <!-- Logo -->
        <div class="brand">
          <div class="logo-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          </div>
          <span class="brand-name">Publisher</span>
        </div>

        <div class="hero">
          <h1 class="hero-title">Automate your<br>social media at scale</h1>
          <p class="hero-sub">Manage accounts, schedule content, and monitor your publishing farm from a single dashboard.</p>
        </div>

        <div class="feature-list">
          <div v-for="f in features" :key="f.title" class="feature-item">
            <div class="feature-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                <path :d="f.iconPath" />
              </svg>
            </div>
            <div>
              <div class="feature-title">{{ f.title }}</div>
              <div class="feature-desc">{{ f.desc }}</div>
            </div>
          </div>
        </div>

        <!-- Decorative glow blobs -->
        <div class="blob blob-1"></div>
        <div class="blob blob-2"></div>
      </div>
    </div>

    <!-- Right panel -->
    <div class="panel-right">
      <div class="form-box">
        <div class="form-header">
          <h2 class="form-title">Welcome back</h2>
          <p class="form-sub">Sign in to your Publisher account</p>
        </div>

        <form @submit.prevent="onSubmit" novalidate>
          <div class="field">
            <label for="email">Email address</label>
            <div class="input-wrap">
              <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
              </svg>
              <input
                id="email"
                v-model="email"
                type="email"
                autocomplete="email"
                placeholder="you@example.com"
                required
              />
            </div>
          </div>

          <div class="field">
            <label for="password">Password</label>
            <div class="input-wrap">
              <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                <path d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
              </svg>
              <input
                id="password"
                v-model="password"
                :type="showPass ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="••••••••"
                required
              />
              <button type="button" class="toggle-pass" @click="showPass = !showPass" tabindex="-1">
                <!-- eye-slash when visible, eye when hidden -->
                <svg v-if="showPass" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" /><path d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </button>
            </div>
          </div>

          <div v-if="error" class="error-box">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
            </svg>
            {{ error }}
          </div>

          <button type="submit" class="btn-submit" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? 'Signing in…' : 'Sign in' }}
            <svg v-if="!loading" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </button>
        </form>
      </div>

      <p class="copy">© {{ new Date().getFullYear() }} Publisher Platform</p>
    </div>
  </div>
</template>

<style scoped>
/* ── Layout ─────────────────────────────────────── */
.page {
  display: flex;
  min-height: 100svh;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* ── Left panel ─────────────────────────────────── */
.panel-left {
  position: relative;
  width: 48%;
  background: #0f172a;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 56px 52px;
  height: 100%;
}

/* Brand */
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 56px;
}
.logo-icon {
  width: 38px;
  height: 38px;
  background: #2563eb;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.logo-icon svg { width: 20px; height: 20px; color: #fff; }
.brand-name { font-size: 18px; font-weight: 700; color: #f8fafc; letter-spacing: -0.3px; }

/* Hero text */
.hero { margin-bottom: 48px; }
.hero-title {
  font-size: clamp(28px, 3vw, 38px);
  font-weight: 800;
  color: #f8fafc;
  line-height: 1.2;
  letter-spacing: -0.8px;
  margin-bottom: 16px;
}
.hero-sub {
  font-size: 15px;
  color: #94a3b8;
  line-height: 1.6;
  max-width: 380px;
}

/* Feature list */
.feature-list { display: flex; flex-direction: column; gap: 24px; }
.feature-item { display: flex; align-items: flex-start; gap: 14px; }
.feature-icon {
  width: 36px;
  height: 36px;
  border-radius: 9px;
  background: rgba(37, 99, 235, 0.18);
  border: 1px solid rgba(37, 99, 235, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 1px;
}
.feature-icon svg { width: 16px; height: 16px; color: #60a5fa; }
.feature-title { font-size: 13.5px; font-weight: 600; color: #e2e8f0; margin-bottom: 2px; }
.feature-desc  { font-size: 12.5px; color: #64748b; line-height: 1.4; }

/* Glow blobs */
.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}
.blob-1 {
  width: 320px; height: 320px;
  background: rgba(37, 99, 235, 0.14);
  top: -60px; right: -80px;
}
.blob-2 {
  width: 260px; height: 260px;
  background: rgba(124, 58, 237, 0.1);
  bottom: 40px; left: -60px;
}

/* ── Right panel ────────────────────────────────── */
.panel-right {
  flex: 1;
  background: #f1f5f9;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 32px;
}

.form-box {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 1px 2px rgba(0,0,0,.05), 0 4px 16px rgba(0,0,0,.07);
  padding: 36px 36px 32px;
}

.form-header { margin-bottom: 28px; }
.form-title {
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
  letter-spacing: -0.4px;
  margin-bottom: 5px;
}
.form-sub { font-size: 13.5px; color: #64748b; }

/* Fields */
.field { display: flex; flex-direction: column; gap: 6px; margin-bottom: 18px; }
label { font-size: 13px; font-weight: 500; color: #374151; }

.input-wrap { position: relative; }
.input-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 15px;
  height: 15px;
  color: #94a3b8;
  pointer-events: none;
}
.input-wrap input {
  width: 100%;
  padding: 10px 40px 10px 36px;
  border: 1.5px solid #e2e8f0;
  border-radius: 9px;
  font-size: 14px;
  color: #0f172a;
  background: #fff;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
}
.input-wrap input::placeholder { color: #cbd5e1; }
.input-wrap input:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12);
}

.toggle-pass {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: transparent;
  border: none;
  padding: 4px;
  color: #94a3b8;
  display: flex;
  align-items: center;
  border-radius: 5px;
  cursor: pointer;
  transition: color 0.12s;
}
.toggle-pass:hover { color: #475569; }
.toggle-pass svg { width: 15px; height: 15px; }

/* Error */
.error-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 13px;
  background: #fff1f2;
  border: 1px solid #fecdd3;
  border-radius: 8px;
  font-size: 13px;
  color: #be123c;
  margin-bottom: 18px;
}
.error-box svg { width: 15px; height: 15px; flex-shrink: 0; }

/* Submit button */
.btn-submit {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 20px;
  background: #2563eb;
  color: #fff;
  border: none;
  border-radius: 9px;
  font-size: 14.5px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, box-shadow 0.15s, transform 0.1s;
  letter-spacing: -0.1px;
  margin-top: 4px;
}
.btn-submit svg { width: 15px; height: 15px; }
.btn-submit:hover:not(:disabled) {
  background: #1d4ed8;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.35);
  transform: translateY(-1px);
}
.btn-submit:active:not(:disabled) { transform: translateY(0); }
.btn-submit:disabled { opacity: 0.65; cursor: not-allowed; }

/* Spinner */
.spinner {
  width: 15px;
  height: 15px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Footer */
.copy {
  margin-top: 28px;
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
}

/* ── Responsive ─────────────────────────────────── */
@media (max-width: 768px) {
  .panel-left { display: none; }
  .panel-right { background: #f1f5f9; }
}
</style>
