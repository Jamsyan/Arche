<script setup lang="ts">
defineProps<{
  tags: string[]
  limit?: number
}>()

const emit = defineEmits<{
  select: [tag: string]
}>()
</script>

<template>
  <section class="trending-tags">
    <div class="tags-row">
      <!-- 左：常驻热门标签 -->
      <div class="section-left">
        <button class="hot-tag" @click="emit('select', '热门')">🔥 热门</button>
      </div>

      <!-- 中：普通标签流式排列 -->
      <div class="section-middle">
        <button
          v-for="tag in tags.slice(0, limit)"
          :key="tag"
          class="tag-cell"
          :title="tag.length > 4 ? tag : undefined"
          @click="emit('select', tag)"
        >
          <span class="tag-text">{{ tag.slice(0, 4) }}</span>
        </button>
      </div>

      <!-- 右：预留区（未来活动等） -->
      <div class="section-right" />
    </div>
  </section>
</template>

<style scoped>
.trending-tags {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--surface-color);
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.tags-row {
  display: flex;
  align-items: flex-start;
  width: 100%;
  max-width: 860px;
  gap: var(--spacing-md);
}

/* ── 左区：常驻热门 ── */
.section-left {
  flex-shrink: 0;
  padding-top: 2px;
}

.hot-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-width: 80px;
  padding: 6px 16px;
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  line-height: 1.4;
  color: #fff;
  background: linear-gradient(135deg, #f4726a 0%, #ef4444 100%);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  font-family: inherit;
  letter-spacing: 0.03em;
}

.hot-tag:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
}

.hot-tag:active {
  transform: translateY(0);
}

/* ── 中区：普通标签流式排列 ── */
.section-middle {
  flex: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-width: 0;
}

.tag-cell {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 30px;
  padding: 0 6px;
  font-size: 13px;
  line-height: 1.4;
  color: var(--text-secondary);
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition:
    color 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease;
  font-family: inherit;
  overflow: hidden;
}

.tag-cell:hover {
  color: var(--text-primary);
  background: var(--surface-strong-color);
  border-color: var(--primary-color);
}

.tag-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

/* ── 右区：预留 ── */
.section-right {
  flex-shrink: 0;
  width: 40px;
}

/* ── 响应式 ── */
@media (max-width: 640px) {
  .tags-row {
    flex-wrap: wrap;
    gap: var(--spacing-sm);
  }

  .section-left {
    width: 100%;
    padding-top: 0;
  }

  .hot-tag {
    width: 100%;
    max-width: none;
  }

  .section-right {
    display: none;
  }
}
</style>
