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
    <div class="tags-cloud">
      <button
        v-for="tag in tags.slice(0, limit)"
        :key="tag"
        class="tag-pill"
        @click="emit('select', tag)"
      >
        {{ tag }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.trending-tags {
  display: flex;
  align-items: center;
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--surface-color);
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-sm);
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 14px;
  font-size: 13px;
  line-height: 1.4;
  color: var(--text-secondary);
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: 100px;
  cursor: pointer;
  transition:
    color 0.2s ease,
    background 0.2s ease,
    border-color 0.2s ease;
  font-family: inherit;
}

.tag-pill:hover {
  color: var(--text-primary);
  background: var(--surface-strong-color);
  border-color: var(--primary-color);
}
</style>
