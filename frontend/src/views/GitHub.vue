<template>
  <div class="page-shell">
    <div class="page-heading">
      <h1>GitHub</h1>
      <p class="page-desc">项目开源仓库，欢迎 Star 和贡献</p>
    </div>
    <div class="placeholder-card">
      <p>正在跳转到 GitHub...</p>
      <a :href="repoUrl" target="_blank" rel="noopener noreferrer" class="repo-link">
        {{ repoUrl }}
      </a>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

const repoUrl = 'https://github.com/jamnodesmith/Arche'

onMounted(() => {
  window.open(repoUrl, '_blank', 'noopener')
})
</script>

<style scoped>
.page-shell {
  width: min(900px, 100%);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--layout-gap);
}

.page-heading h1 {
  margin: 0 0 6px;
  font-size: 28px;
}

.page-desc {
  margin: 0;
  color: var(--text-secondary);
}

.placeholder-card {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--spacing-3xl);
  text-align: center;
  color: var(--text-tertiary);
}

.repo-link {
  display: inline-block;
  margin-top: 8px;
  color: var(--primary-color);
  text-decoration: none;
}

.repo-link:hover {
  text-decoration: underline;
}
</style>
