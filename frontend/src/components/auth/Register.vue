<template>
  <div class="auth-page">
    <a-card class="auth-card" :bordered="false">
      <a-typography-title :heading="3" class="auth-title">Veil</a-typography-title>
      <a-typography-text type="secondary" class="auth-subtitle">创建新账户</a-typography-text>

      <a-form :model="form" layout="vertical" @submit="handleRegister">
        <a-form-item field="username" label="用户名">
          <a-input v-model="form.username" placeholder="输入用户名" allow-clear :max-length="64" />
        </a-form-item>
        <a-form-item field="password" label="密码">
          <a-input-password v-model="form.password" placeholder="至少 6 位" />
        </a-form-item>
        <a-form-item field="confirmPassword" label="确认密码">
          <a-input-password v-model="form.confirmPassword" placeholder="再次输入密码" />
        </a-form-item>

        <a-alert v-if="error" type="error" :content="error" style="margin-bottom: 16px" />

        <a-button type="primary" html-type="submit" long :loading="loading">
          注册
        </a-button>
      </a-form>

      <div class="auth-footer">
        <a-typography-text type="secondary">
          已有账户？
          <a-link @click="$router.push('/login')">立即登录</a-link>
        </a-typography-text>
      </div>
    </a-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../router/auth.js'

const router = useRouter()
const { register } = useAuth()

const form = reactive({ username: '', password: '', confirmPassword: '' })
const loading = ref(false)
const error = ref('')

async function handleRegister() {
  error.value = ''
  if (form.password !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }
  if (form.password.length < 6) {
    error.value = '密码至少 6 位'
    return
  }
  loading.value = true
  const result = await register(form.username, form.password)
  loading.value = false
  if (result.ok) {
    router.push('/')
  } else {
    error.value = result.error
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: var(--color-fill-2);
}
.auth-card { width: 400px; padding: 32px; }
.auth-title { text-align: center; margin-bottom: 4px; }
.auth-subtitle { display: block; text-align: center; margin-bottom: 24px; }
.auth-footer { text-align: center; margin-top: 16px; }
</style>
