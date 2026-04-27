<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NInput, NFormItemGi, type FormRules } from 'naive-ui'
import ProForm from '@/components/ProForm.vue'
import { registerApi } from '@/services/api'
import { $message } from '@/utils/message'
import { LockClosedOutline } from '@/icons'

const router = useRouter()
const loading = ref(false)

const formModel = reactive({
  email: '',
  username: '',
  password: '',
  confirmPassword: ''
})

const rules: FormRules = {
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirmPassword: [
    {
      required: true,
      message: '请再次输入密码',
      trigger: 'blur'
    },
    {
      validator: () => formModel.password === formModel.confirmPassword,
      message: '两次密码不一致',
      trigger: 'blur'
    }
  ]
}

const handleRegister = async () => {
  loading.value = true
  try {
    await registerApi({
      email: formModel.email,
      username: formModel.username,
      password: formModel.password
    })
    $message.success('注册成功，请登录')
    await router.push({
      path: '/login',
      query: { identity: formModel.email || formModel.username }
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="register-page">
    <div class="register-card card-glass">
      <div class="card-header">
        <div class="logo-icon"><LockClosedOutline /></div>
        <h2>创建账号</h2>
        <p>注册后即可发布和管理你的博客内容</p>
      </div>

      <ProForm
        :model="formModel"
        :rules="rules"
        :columns="1"
        :label-width="92"
        @submit="handleRegister"
      >
        <NFormItemGi label="邮箱" path="email"
          ><NInput v-model:value="formModel.email"
        /></NFormItemGi>
        <NFormItemGi label="用户名" path="username"
          ><NInput v-model:value="formModel.username"
        /></NFormItemGi>
        <NFormItemGi label="密码" path="password">
          <NInput v-model:value="formModel.password" type="password" show-password-on="click" />
        </NFormItemGi>
        <NFormItemGi label="确认密码" path="confirmPassword">
          <NInput
            v-model:value="formModel.confirmPassword"
            type="password"
            show-password-on="click"
          />
        </NFormItemGi>
        <template #actions="{ submit }">
          <NButton type="primary" block :loading="loading" @click="submit">立即注册</NButton>
        </template>
      </ProForm>

      <div class="bottom">已有账号？<RouterLink to="/login">去登录</RouterLink></div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  width: 100%;
  max-width: 460px;
  margin: 0 auto;
  padding: var(--spacing-xl) 0;
}
.register-card {
  padding: var(--spacing-2xl);
}
.card-header {
  text-align: center;
  margin-bottom: var(--spacing-lg);
}
.logo-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  background: var(--primary-light-color);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 12px;
}
.logo-icon :deep(svg) {
  width: 30px;
  height: 30px;
  color: var(--primary-color);
}
.card-header h2 {
  margin-bottom: 8px;
}
.card-header p {
  color: var(--text-secondary);
}
.bottom {
  margin-top: 14px;
  text-align: center;
  color: var(--text-secondary);
}
</style>
