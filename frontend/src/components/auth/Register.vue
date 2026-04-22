<template>
  <div class="auth-page">
    <!-- 左侧：几何动画面板 -->
    <div class="auth-art">
      <div class="art-bg">
        <div class="shape circle c1"></div>
        <div class="shape circle c2"></div>
        <div class="shape circle c3"></div>
        <div class="shape circle c4"></div>
        <div class="shape circle c5"></div>
        <div class="shape ring r1"></div>
        <div class="shape ring r2"></div>
        <div class="shape line l1"></div>
        <div class="shape line l2"></div>
        <div class="shape dot d1"></div>
        <div class="shape dot d2"></div>
        <div class="shape dot d3"></div>
        <div class="shape dot d4"></div>
        <div class="shape dot d5"></div>
      </div>
    </div>

    <!-- 右侧：表单面板 -->
    <div class="auth-form-side">
      <div class="auth-form-inner">
        <div class="form-header">
          <h2 class="form-title">创建账户</h2>
          <p class="form-subtitle">注册一个免费账号</p>
        </div>

        <a-form :model="form" layout="vertical" @submit="handleRegister">
          <a-form-item field="email" label="邮箱">
            <a-input v-model="form.email" placeholder="输入邮箱地址" allow-clear :max-length="128" />
          </a-form-item>
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

          <a-button type="primary" html-type="submit" long :loading="loading" class="submit-btn">
            注册
          </a-button>
        </a-form>

        <div class="auth-footer">
          <a-typography-text type="secondary">
            已有账户？
            <a class="auth-link" @click="$router.push('/login')">立即登录</a>
          </a-typography-text>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../../router/auth.js'

const router = useRouter()
const { register } = useAuth()

const form = reactive({ email: '', username: '', password: '', confirmPassword: '' })
const loading = ref(false)
const error = ref('')

function validateEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

async function handleRegister() {
  error.value = ''
  if (!validateEmail(form.email)) {
    error.value = '请输入有效的邮箱地址'
    return
  }
  if (form.password !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }
  if (form.password.length < 6) {
    error.value = '密码至少 6 位'
    return
  }
  loading.value = true
  const result = await register(form.email, form.username, form.password)
  loading.value = false
  if (result.ok) {
    router.push('/platform')
  } else {
    error.value = result.error
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  height: 80vh;
  margin: auto;
  margin-top: 20px;
  width: 83%;
  border-radius: var(--border-radius-large);
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,0.08);
  background: var(--color-bg-1);
}

/* ===== 左侧几何动画面板 ===== */
.auth-art {
  flex: 1;
  position: relative;
  background: var(--color-bg-1);
  overflow: hidden;
}

.art-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
}

/* 基础形状样式 */
.shape {
  position: absolute;
}

/* 圆形 — 主色系，更高对比度 */
.circle {
  border-radius: 50%;
}
.c1 {
  width: 320px; height: 320px;
  background: var(--color-primary);
  opacity: 0.12;
  top: -80px; left: -60px;
  animation: floatA 20s ease-in-out infinite;
}
.c2 {
  width: 220px; height: 220px;
  background: var(--color-primary-light-2);
  opacity: 0.15;
  bottom: 10%; right: 5%;
  animation: floatB 16s ease-in-out infinite;
}
.c3 {
  width: 160px; height: 160px;
  background: var(--color-primary-dark-1);
  opacity: 0.18;
  top: 45%; left: 20%;
  animation: floatC 22s ease-in-out infinite;
}
.c4 {
  width: 110px; height: 110px;
  background: var(--color-primary);
  opacity: 0.1;
  bottom: 30%; left: 50%;
  animation: floatA 14s ease-in-out infinite reverse;
}
.c5 {
  width: 140px; height: 140px;
  background: var(--color-primary-light-3);
  opacity: 0.12;
  top: 10%; right: 25%;
  animation: floatB 18s ease-in-out infinite 3s;
}

/* 环形 — 空心圆，更高对比度 */
.ring {
  border-radius: 50%;
  border: 2px solid var(--color-primary);
  opacity: 0.15;
}
.r1 {
  width: 180px; height: 180px;
  top: 25%; left: 40%;
  animation: floatC 24s ease-in-out infinite 1s;
}
.r2 {
  width: 120px; height: 120px;
  bottom: 15%; right: 30%;
  animation: floatA 16s ease-in-out infinite 4s;
}

/* 线条 */
.line {
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--color-primary), transparent);
  opacity: 0.15;
}
.l1 {
  width: 70%;
  top: 30%;
  left: 15%;
  animation: slideLine 9s ease-in-out infinite;
}
.l2 {
  width: 50%;
  top: 70%;
  left: 25%;
  animation: slideLine 12s ease-in-out infinite 3s;
}

/* 小点 */
.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary);
  opacity: 0.3;
}
.d1 { top: 20%; left: 55%; animation: pulse 4s ease-in-out infinite; }
.d2 { top: 60%; left: 15%; animation: pulse 5s ease-in-out infinite 1s; }
.d3 { bottom: 25%; right: 10%; animation: pulse 6s ease-in-out infinite 2s; }
.d4 { top: 75%; left: 60%; animation: pulse 4.5s ease-in-out infinite 0.5s; }
.d5 { top: 40%; left: 70%; animation: pulse 5.5s ease-in-out infinite 1.5s; }

/* 动画 */
@keyframes floatA {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, 40px) scale(1.08); }
}
@keyframes floatB {
  0%, 100% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(-25px, -30px) rotate(12deg); }
}
@keyframes floatC {
  0%, 100% { transform: translate(0, 0); }
  33% { transform: translate(20px, -25px); }
  66% { transform: translate(-15px, 20px); }
}
@keyframes slideLine {
  0%, 100% { opacity: 0.1; transform: translateX(-20px); }
  50% { opacity: 0.2; transform: translateX(20px); }
}
@keyframes pulse {
  0%, 100% { opacity: 0.15; transform: scale(1); }
  50% { opacity: 0.45; transform: scale(2); }
}

/* ===== 右侧表单面板 ===== */
.auth-form-side {
  width: 420px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-1);
  overflow: hidden;
}

.auth-form-inner {
  width: 100%;
  max-width: 320px;
  padding: 0;
}

.form-header {
  text-align: center;
  margin-bottom: 20px;
}

.form-title {
  font-size: 22px;
  font-weight: 700;
  color: var(--color-text-1);
  margin: 0 0 4px;
}

.form-subtitle {
  font-size: 13px;
  color: var(--color-text-4);
  margin: 0;
}

/* 紧凑表单间距 */
.auth-form-inner :deep(.arco-form-item) {
  margin-bottom: 12px;
}

.auth-form-inner :deep(.arco-form-item-label) {
  font-size: 13px;
  color: var(--color-text-3);
}

.submit-btn :deep(.arco-btn) {
  border-radius: var(--border-radius-medium);
  height: 36px;
}

.auth-footer {
  text-align: center;
  margin-top: 12px;
  font-size: 13px;
}

.auth-link {
  color: var(--color-primary);
  cursor: pointer;
  text-decoration: none;
}
.auth-link:hover {
  text-decoration: underline;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .auth-art { display: none; }
  .auth-form-side { width: 100%; }
}
</style>
