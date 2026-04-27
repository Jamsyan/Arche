<template>
  <div class="login-page">
    <div class="login-card card-glass">
      <div class="card-header">
        <div class="logo-icon">
          <LockClosedOutline />
        </div>
        <h2>欢迎回来</h2>
        <p>选择身份登录管理后台</p>
      </div>

      <div class="login-form">
        <div class="form-item">
          <label>登录身份</label>
          <NSelect
            v-model:value="selectedRole"
            :options="roleOptions"
            placeholder="请选择登录身份"
          />
        </div>

        <div class="form-tip">
          <p>演示环境无需输入账号密码，直接选择身份登录即可</p>
        </div>

        <NButton type="primary" size="large" block :loading="loading" @click="handleLogin">
          立即登录
        </NButton>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { NSelect, NButton } from 'naive-ui'
import { useUserStore } from '@/store/modules/user'
import { $message } from '@/utils/message'
import { LockClosedOutline } from '@/icons'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const selectedRole = ref<'user' | 'admin' | 'guest'>('user')

const roleOptions = [
  { label: '普通用户', value: 'user' },
  { label: '管理员', value: 'admin' },
  { label: '访客', value: 'guest' }
]

const handleLogin = async () => {
  loading.value = true
  try {
    await userStore.loginAsRole(selectedRole.value)
    $message.success(`欢迎回来，${selectedRole.value === 'admin' ? '管理员' : '用户'}`)

    // 根据角色跳转到对应页面
    if (selectedRole.value === 'admin') {
      await router.push('/admin')
    } else if (selectedRole.value === 'user') {
      await router.push('/posts')
    } else {
      await router.push('/')
    }
  } catch {
    $message.error('登录失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
  padding: var(--spacing-xl) 0;
}

.login-card {
  padding: var(--spacing-2xl);
}

.card-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.logo-icon {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-lg);
  background: var(--primary-light-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  margin: 0 auto var(--spacing-md);
}

.logo-icon svg {
  width: 32px;
  height: 32px;
  color: var(--primary-color);
}

.card-header h2 {
  margin: 0 0 var(--spacing-xs) 0;
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
}

.card-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-item label {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-primary);
}

.form-tip {
  background: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.form-tip p {
  margin: 0;
  color: var(--primary-color);
  font-size: 13px;
  line-height: 1.6;
}
</style>
