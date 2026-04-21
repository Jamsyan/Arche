<template>
  <div class="register-page">
    <div class="register-card">
      <h1 class="register-title">注册 Veil</h1>
      <p class="register-subtitle">创建你的账户</p>

      <form @submit.prevent="handleRegister" class="register-form">
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
            autocomplete="new-password"
            placeholder="设置密码"
            required
            minlength="6"
          />
        </div>

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input
            id="confirmPassword"
            v-model="confirmPassword"
            type="password"
            autocomplete="new-password"
            placeholder="再次输入密码"
            required
          />
        </div>

        <p v-if="error" class="error-msg">{{ error }}</p>

        <button type="submit" :disabled="loading" class="submit-btn">
          {{ loading ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="register-footer">
        已有账户？<router-link to="/login">返回登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../router/auth.js'

const router = useRouter()
const { register } = useAuth()

const username = ref('')
const password = ref('')
const confirmPassword = ref('')
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  if (!username.value || !password.value) return
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  if (password.value.length < 6) {
    error.value = '密码长度至少 6 个字符'
    return
  }

  loading.value = true
  error.value = ''

  const result = await register(username.value, password.value)
  loading.value = false

  if (result.ok) {
    router.push('/')
  } else {
    error.value = result.error
  }
}
</script>

<style scoped>
.register-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}
.register-card {
  background: #fff;
  border-radius: 8px;
  padding: 2.5rem;
  width: 100%;
  max-width: 380px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
}
.register-title {
  text-align: center;
  margin: 0 0 0.5rem;
  font-size: 1.8rem;
  color: #1a1a2e;
}
.register-subtitle {
  text-align: center;
  margin: 0 0 2rem;
  color: #666;
  font-size: 0.9rem;
}
.register-form {
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
.register-footer {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.85rem;
  color: #666;
}
.register-footer a {
  color: #1a1a2e;
  text-decoration: none;
}
</style>
