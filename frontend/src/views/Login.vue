<template>
  <div class="login-page">
    <div class="login-card card-glass">
      <div class="card-header">
        <div class="logo-icon">
          <LockClosedOutline />
        </div>
        <h2>欢迎回来</h2>
        <p>{{ useMockLogin ? '选择身份登录管理后台' : '请输入账号信息登录' }}</p>
      </div>

      <ProForm :model="formModel" :columns="1" :label-width="80" @submit="handleLogin">
        <NFormItemGi v-if="useMockLogin" label="登录身份" path="role" :span="1">
          <NSelect
            v-model:value="formModel.role"
            :options="roleOptions"
            placeholder="请选择登录身份"
          />
        </NFormItemGi>
        <NFormItemGi v-else label="账号" path="identity" :span="1">
          <NInput v-model:value="formModel.identity" placeholder="请输入用户名或邮箱" />
        </NFormItemGi>
        <NFormItemGi v-if="!useMockLogin" label="密码" path="password" :span="1">
          <NInput
            v-model:value="formModel.password"
            type="password"
            show-password-on="click"
            placeholder="请输入密码"
          />
        </NFormItemGi>
        <NFormItemGi :span="1">
          <div class="form-tip">
            <p>
              {{
                useMockLogin
                  ? '演示环境无需输入账号密码，直接选择身份登录即可'
                  : '生产链路将调用后端 /api/auth/login 接口'
              }}
            </p>
          </div>
        </NFormItemGi>
        <template #actions="{ submit }">
          <NButton type="primary" size="large" block :loading="loading" @click="submit">
            立即登录
          </NButton>
        </template>
      </ProForm>
      <div class="register-entry">还没账号？<RouterLink to="/register">立即注册</RouterLink></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { NSelect, NButton, NFormItemGi, NInput } from 'naive-ui'
import { useUserStore } from '@/store/modules/user'
import { $message } from '@/utils/message'
import { LockClosedOutline } from '@/icons'
import ProForm from '@/components/ProForm.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const useMockLogin = import.meta.env.VITE_USE_MOCK_LOGIN === 'true'

const loading = ref(false)
const formModel = ref<{
  role: 'user' | 'admin' | 'guest'
  identity: string
  password: string
}>({
  role: 'user',
  identity: '',
  password: ''
})

const roleOptions = [
  { label: '普通用户', value: 'user' },
  { label: '管理员', value: 'admin' },
  { label: '访客', value: 'guest' }
]

if (typeof route.query.identity === 'string') {
  formModel.value.identity = route.query.identity
}

const handleLogin = async () => {
  loading.value = true
  try {
    if (useMockLogin) {
      await userStore.loginAsRole(formModel.value.role)
      $message.success(`欢迎回来，${formModel.value.role === 'admin' ? '管理员' : '用户'}`)
    } else {
      await userStore.login({
        identity: formModel.value.identity,
        password: formModel.value.password
      })
      $message.success(
        `欢迎回来，${userStore.userInfo?.nickname || userStore.userInfo?.username || '用户'}`
      )
    }

    // 根据角色跳转到对应页面
    const currentRole = userStore.userInfo?.role || formModel.value.role
    if (currentRole === 'admin') {
      await router.push('/admin')
    } else if (currentRole === 'user') {
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

.register-entry {
  margin-top: 14px;
  text-align: center;
  color: var(--text-secondary);
}
</style>
