<script setup lang="ts">
import { computed } from 'vue'

defineOptions({ name: 'ArPagination' })

const props = withDefaults(
  defineProps<{
    page: number
    pageSize: number
    itemCount: number
    pageSizes?: number[]
  }>(),
  { pageSizes: () => [10, 20, 50] }
)

const emit = defineEmits<{
  'update:page': [page: number]
  'update:pageSize': [size: number]
}>()

const totalPages = computed(() => Math.max(1, Math.ceil(props.itemCount / props.pageSize)))

/** 显示的页码按钮：首 + 末 + 当前附近最多 5 个 */
const pageButtons = computed(() => {
  const total = totalPages.value
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1)

  const current = props.page
  const pages: (number | 'ellipsis')[] = [1]

  if (current > 3) pages.push('ellipsis')

  const start = Math.max(2, current - 1)
  const end = Math.min(total - 1, current + 1)
  for (let i = start; i <= end; i++) pages.push(i)

  if (current < total - 2) pages.push('ellipsis')

  if (total > 1) pages.push(total)

  return pages
})

function goTo(p: number) {
  if (p < 1 || p > totalPages.value || p === props.page) return
  emit('update:page', p)
}

function handleSizeChange(e: Event) {
  const v = parseInt((e.target as HTMLSelectElement).value)
  emit('update:pageSize', v)
}
</script>

<template>
  <div class="ar-pagination">
    <span class="ar-pagination__info"> 共 {{ itemCount }} 条 </span>

    <div class="ar-pagination__controls">
      <button class="ar-pagination__btn" :disabled="page <= 1" @click="goTo(1)" title="首页">
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="11 17 6 12 11 7" />
          <polyline points="18 17 13 12 18 7" />
        </svg>
      </button>
      <button
        class="ar-pagination__btn"
        :disabled="page <= 1"
        @click="goTo(page - 1)"
        title="上一页"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>

      <template v-for="(btn, idx) in pageButtons" :key="typeof btn === 'number' ? btn : `e${idx}`">
        <span v-if="btn === 'ellipsis'" class="ar-pagination__ellipsis">…</span>
        <button
          v-else
          class="ar-pagination__btn ar-pagination__btn--page"
          :class="{ 'ar-pagination__btn--active': btn === page }"
          @click="goTo(btn)"
        >
          {{ btn }}
        </button>
      </template>

      <button
        class="ar-pagination__btn"
        :disabled="page >= totalPages"
        @click="goTo(page + 1)"
        title="下一页"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="9 18 15 12 9 6" />
        </svg>
      </button>
      <button
        class="ar-pagination__btn"
        :disabled="page >= totalPages"
        @click="goTo(totalPages)"
        title="末页"
      >
        <svg
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
        >
          <polyline points="13 17 18 12 13 7" />
          <polyline points="6 17 11 12 6 7" />
        </svg>
      </button>
    </div>

    <label class="ar-pagination__size">
      <select :value="pageSize" @change="handleSizeChange">
        <option v-for="s in pageSizes" :key="s" :value="s">{{ s }} 条/页</option>
      </select>
    </label>
  </div>
</template>

<style scoped>
.ar-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  background: var(--surface-color);
  flex-wrap: wrap;
}

.ar-pagination__info {
  font-size: 12px;
  color: var(--text-tertiary);
  white-space: nowrap;
}

.ar-pagination__controls {
  display: flex;
  align-items: center;
  gap: 2px;
}

.ar-pagination__btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  padding: 0 4px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: transparent;
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: inherit;
  line-height: 1;
}

.ar-pagination__btn:hover:not(:disabled):not(.ar-pagination__btn--active) {
  background: var(--primary-light-color);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.ar-pagination__btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.ar-pagination__btn--page {
  font-weight: 500;
}

.ar-pagination__btn--active {
  background: rgba(154, 90, 47, 0.18);
  border-color: var(--primary-color);
  color: var(--primary-color);
  font-weight: 700;
  box-shadow: 0 0 0 1px var(--primary-color);
}

.ar-pagination__ellipsis {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  color: var(--text-tertiary);
  font-size: 14px;
  letter-spacing: 2px;
}

.ar-pagination__size select {
  height: 28px;
  padding: 0 24px 0 8px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--surface-inset-color);
  color: var(--text-secondary);
  font-size: 12px;
  cursor: pointer;
  outline: none;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6' fill='%23888'%3E%3Cpath d='M0 0l5 6 5-6z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 6px center;
  font-family: inherit;
  transition: border-color 0.15s ease;
}

.ar-pagination__size select:hover {
  border-color: var(--primary-color);
}

@media (max-width: 640px) {
  .ar-pagination {
    gap: 8px;
    padding: 10px 8px;
  }

  .ar-pagination__info {
    order: 3;
    width: 100%;
    text-align: center;
  }
}
</style>
