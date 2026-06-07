<template>
  <footer v-if="visible" class="footer-bar">
    <div class="footer-content">
      <p class="copyright">© 2024 锦年志 · 时光日志</p>
      <p class="footer-link">
        <RouterLink to="/about">关于</RouterLink>
      </p>
      <p class="record">
        <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer">
          苏ICP备2026004054号-1
        </a>
      </p>
      <p class="record">
        <a
          href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=32068202000798"
          target="_blank"
          rel="noopener noreferrer"
        >
          苏公网安备32068202000798号
        </a>
      </p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router'

withDefaults(
  defineProps<{
    visible?: boolean
  }>(),
  {
    visible: true
  }
)
</script>

<style scoped>
.footer-bar {
  border-top: 1px solid var(--border-color);
  padding: var(--spacing-md) var(--content-padding);
  margin-top: auto;
}

.footer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.copyright,
.record,
.footer-link {
  margin: 0;
  color: var(--text-tertiary);
  font-size: var(--font-size-sm, 12px);
}

.record a,
.footer-link a {
  color: var(--text-tertiary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.record a:hover,
.footer-link a:hover {
  color: var(--primary-color);
}
</style>
