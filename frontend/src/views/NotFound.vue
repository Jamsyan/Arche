<script setup lang="ts">
import { useRouter } from 'vue-router'
import { NButton, NCard, NSpace } from 'naive-ui'

const router = useRouter()

const goBack = () => {
  router.back()
}

const goHome = () => {
  router.push('/')
}
</script>

<template>
  <div class="not-found-page">
    <NCard class="not-found-card card-glass">
      <h1>404</h1>
      <p>页面不存在或已被移除</p>
      <NSpace justify="center">
        <NButton @click="goBack"> 返回上一页 </NButton>
        <NButton type="primary" @click="goHome"> 回到首页 </NButton>
      </NSpace>
    </NCard>
  </div>
</template>

<style scoped>
.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
}

.not-found-card {
  width: min(480px, 100%);
  text-align: center;
}

h1 {
  margin: 0 0 var(--spacing-md);
  font-size: 56px;
}

p {
  margin: 0 0 var(--spacing-lg);
  color: var(--text-secondary);
}
</style>
