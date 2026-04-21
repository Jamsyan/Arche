<template>
  <div class="login-page">
    <div class="login-card">
      <h1 class="login-title">Veil</h1>
      <p class="login-subtitle">登录你的账户</p>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="输入用户名"
            required
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            placeholder="输入密码"
            required
          />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" :disabled="loading" class="submit-btn">
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>

      <p class="login-footer">
        还没有账户？<router-link to="/register">立即注册</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../router/auth.js'

const router = useRouter()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!username.value || !password.value) return
  loading.value = true
  error.value = ''

  const result = await login(username.value, password.value)
  loading.value = false

  if (result.ok) {
    router.push('/')
  } else {
    error.value = result.error
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}
.login-card {
  background: #fff;
  border-radius: 8px;
  padding: 2.5rem;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.login-title {
  text-align: center;
  margin: 0 0 0.5rem;
  font-size: 1.8rem;
  color: #1a1a2e;
}
.login-subtitle {
  text-align: center;
  margin: 0 0 2rem;
  color: #666;
  font-size: 0.9rem;
}
.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.form-group label {
  font-size: 0.85rem;
  color: #444;
  font-weight: 500;
}
.form-group input {
  padding: 0.6rem 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
}
.form-group input:focus {
  border-color: #1a1a2e;
}
.error-msg {
  color: #d32f2f;
  font-size: 0.85rem;
  margin: 0;
}
.submit-btn {
  padding: 0.7rem;
  border: none;
  border-radius: 4px;
  background: #1a1a2e;
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  transition: opacity 0.2s;
}
.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.submit-btn:hover:not(:disabled) {
  opacity: 0.85;
}
.login-footer {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.85rem;
  color: #666;
}
.login-footer a {
  color: #1a1a2e;
  text-decoration: none;
}
</style>
