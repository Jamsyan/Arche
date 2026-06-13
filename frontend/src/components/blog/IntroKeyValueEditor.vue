<template>
  <div class="intro-kv-editor">
    <div class="intro-kv-header">
      <span class="intro-kv-title">引言</span>
    </div>
    <div class="intro-kv-list">
      <div v-for="(item, index) in items" :key="index" class="intro-kv-row">
        <input
          v-model="item.key"
          class="kv-key-input"
          placeholder="Key（可选）"
          maxlength="20"
          @input="emitUpdate"
        />
        <input
          v-model="item.value"
          class="kv-value-input"
          :placeholder="item.key ? `输入 ${item.key} 的值…` : '输入文本…'"
          maxlength="200"
          @input="emitUpdate"
        />
        <button class="kv-remove-btn" title="删除" @click="removeItem(index)">
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="18" y1="6" x2="6" y2="18" />
            <line x1="6" y1="6" x2="18" y2="18" />
          </svg>
        </button>
      </div>
    </div>
    <button class="kv-add-btn" @click="addItem">
      <svg
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2"
      >
        <line x1="12" y1="5" x2="12" y2="19" />
        <line x1="5" y1="12" x2="19" y2="12" />
      </svg>
      添加一项
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

export interface IntroItem {
  key?: string
  value: string
}

const props = defineProps<{
  modelValue: IntroItem[]
}>()

const emit = defineEmits<{
  'update:modelValue': [items: IntroItem[]]
}>()

const items = ref<IntroItem[]>([])

watch(
  () => props.modelValue,
  (val) => {
    items.value = val.map((item) => ({ ...item }))
  },
  { immediate: true, deep: true }
)

function emitUpdate() {
  emit('update:modelValue', [...items.value])
}

function addItem() {
  items.value.push({ key: '', value: '' })
  emitUpdate()
}

function removeItem(index: number) {
  items.value.splice(index, 1)
  emitUpdate()
}
</script>

<style scoped>
.intro-kv-editor {
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 8px;
  background: var(--intro-bg, #fafafa);
}

.intro-kv-header {
  padding: 8px 12px;
  border-bottom: 1px solid var(--border-color, #e8e6e4);
}

.intro-kv-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-tertiary, #999);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.intro-kv-list {
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.intro-kv-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.kv-key-input {
  width: 120px;
  padding: 6px 10px;
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 6px;
  font-size: 0.8125rem;
  outline: none;
  background: var(--bg-color, #fff);
  color: var(--text-color, #333);
  flex-shrink: 0;
}

.kv-key-input:focus {
  border-color: var(--primary-color, #b83a2a);
}

.kv-value-input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid var(--border-color, #e8e6e4);
  border-radius: 6px;
  font-size: 0.8125rem;
  outline: none;
  background: var(--bg-color, #fff);
  color: var(--text-color, #333);
}

.kv-value-input:focus {
  border-color: var(--primary-color, #b83a2a);
}

.kv-remove-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--text-muted, #bbb);
  cursor: pointer;
  flex-shrink: 0;
  transition: all 0.15s;
}

.kv-remove-btn:hover {
  background: var(--danger-bg, #fef2f2);
  color: var(--danger-color, #ef4444);
}

.kv-add-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin: 4px 12px 8px;
  padding: 6px 12px;
  border: 1px dashed var(--border-color, #ddd);
  border-radius: 6px;
  background: transparent;
  color: var(--text-muted, #999);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.15s;
}

.kv-add-btn:hover {
  border-color: var(--primary-color, #b83a2a);
  color: var(--primary-color, #b83a2a);
  background: var(--primary-light-color, rgba(184, 58, 42, 0.08));
}
</style>
