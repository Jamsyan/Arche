<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="not-found">
    <h1>404</h1>
    <p>页面未找到</p>
    <RouterLink to="/" class="back-home">返回首页</RouterLink>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  text-align: center;
}

h1 {
  font-size: 4rem;
  margin-bottom: 1rem;
}

p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.8;
}

.back-home {
  padding: 1rem 2rem;
  background: #1890ff;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  transition: background-color 0.3s ease;
}

.back-home:hover {
  background: #40a9ff;
}
</style>
