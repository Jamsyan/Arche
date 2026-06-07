<template>
  <div class="page-shell">
    <div class="page-heading">
      <h1>调度器</h1>
      <p class="page-desc">管理模型训练任务与爬虫调度</p>
    </div>
    <div class="placeholder-card">
      <p>调度器功能开发中，敬请期待</p>
    </div>
  </div>
</template>

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
</style>
