<script setup lang="ts">
import { useRouter } from 'vue-router'
import { NButton } from 'naive-ui'

const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="error-page">
    <div class="error-card">
      <h1>404</h1>
      <p>页面不存在或已被移除</p>
      <div class="error-actions">
        <NButton @click="goBack"> 返回上一页 </NButton>
        <NButton type="primary" @click="goHome"> 回到首页 </NButton>
      </div>
    </div>
  </div>
</template>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
  font-family: var(--font-sans);
}

.error-card {
  width: min(480px, 100%);
  text-align: center;
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-3xl);
}

h1 {
  margin: 0 0 var(--spacing-md);
  font-size: 56px;
  color: var(--text-primary);
}

p {
  margin: 0 0 var(--spacing-lg);
  color: var(--text-secondary);
}

.error-actions {
  display: flex;
  justify-content: center;
  gap: var(--spacing-md);
}
</style>
