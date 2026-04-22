<template>
  <div class="widget-canvas" ref="canvasRef">
    <div v-if="widgetInstances.length === 0" class="canvas-empty">
      <icon-apps class="empty-icon" />
      <p>从右侧 Widget 库拖拽卡片到此处</p>
      <p class="hint">或点击 Widget 库中的「添加」按钮</p>
    </div>
    <div v-else class="widget-grid">
      <div
        v-for="(inst, index) in widgetInstances"
        :key="inst.id"
        class="widget-cell"
        :class="`size-${inst.size}`"
        :data-index="index"
      >
        <div class="widget-frame">
          <div class="widget-toolbar">
            <span class="widget-title">{{ inst.title }}</span>
            <div class="toolbar-actions">
              <a-tooltip content="锚定到待办">
                <icon-pushpin class="toolbar-btn" :class="{ pinned: isPinned(inst.id) }"
                  @click="togglePin(inst.id)" />
              </a-tooltip>
              <icon-close class="toolbar-btn" @click="removeWidget(inst.id)" />
            </div>
          </div>
          <div class="widget-content">
            <component :is="loadedComponents[inst.id]" :size="inst.size" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, defineAsyncComponent } from 'vue'
import { IconApps, IconClose, IconPushpin } from '@arco-design/web-vue/es/icon'
import { getWidgetComponent } from './widgets/widgetRegistry.js'

const STORAGE_KEY = 'veil_dashboard_widgets'

const props = defineProps({
  pinnedIds: { type: Set, default: () => new Set() },
  onTogglePin: { type: Function, default: () => {} },
})

const emit = defineEmits(['update:widgets'])

const widgetInstances = ref([])
const loadedComponents = ref({})
const canvasRef = ref(null)

// 从 localStorage 加载
function loadLayout() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (stored) {
      widgetInstances.value = JSON.parse(stored)
      // 加载所有组件
      for (const inst of widgetInstances.value) {
        const def = getWidgetComponent(inst.type)
        if (def) {
          loadedComponents.value[inst.id] = defineAsyncComponent(def.component)
        }
      }
    }
  } catch {}
}

function saveLayout() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(widgetInstances.value))
  emit('update:widgets', widgetInstances.value)
}

function addWidget(type) {
  const def = getWidgetComponent(type)
  if (!def) return
  const id = `w_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`
  const inst = { id, type, title: def.title, size: 'medium', order: widgetInstances.value.length }
  widgetInstances.value.push(inst)
  loadedComponents.value[id] = defineAsyncComponent(def.component)
  saveLayout()
}

function removeWidget(id) {
  widgetInstances.value = widgetInstances.value.filter(w => w.id !== id)
  delete loadedComponents.value[id]
  saveLayout()
}

function isPinned(id) {
  return props.pinnedIds.has(id)
}

function togglePin(id) {
  props.onTogglePin(id)
}

// SortableJS 拖拽排序
let sortable = null

onMounted(() => {
  loadLayout()

  // 延迟初始化 Sortable（等待 DOM 渲染）
  setTimeout(async () => {
    if (!canvasRef.value) return
    const grid = canvasRef.value.querySelector('.widget-grid')
    if (!grid) return

    const Sortable = (await import('sortablejs')).default
    sortable = Sortable.create(grid, {
      animation: 150,
      handle: '.widget-toolbar',
      ghostClass: 'sortable-ghost',
      onEnd: (evt) => {
        // 重新排序
        const items = [...widgetInstances.value]
        const [moved] = items.splice(evt.oldIndex, 1)
        items.splice(evt.newIndex, 0, moved)
        widgetInstances.value = items
        saveLayout()
      },
    })
  }, 100)
})

onUnmounted(() => {
  if (sortable) sortable.destroy()
})

// 暴露方法给父组件
defineExpose({ addWidget })
</script>

<style scoped>
.widget-canvas { min-height: 120px; }
.canvas-empty {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 48px 24px; color: var(--color-text-4); font-size: 14px;
  border: 2px dashed var(--color-border-2); border-radius: var(--border-radius-large);
}
.empty-icon { width: 40px; height: 40px; color: var(--color-border-3); }
.hint { font-size: 12px; color: var(--color-text-5); }

.widget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.widget-cell { min-height: 100px; }
.widget-cell.size-small { grid-column: span 1; }
.widget-cell.size-medium { grid-column: span 1; }
.widget-cell.size-large { grid-column: span 2; }

.widget-frame {
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: var(--border-radius-large);
  padding: 12px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  transition: box-shadow 0.15s;
}
.widget-frame:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}

.widget-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 10px; padding-bottom: 8px;
  border-bottom: 1px solid var(--color-border-1);
  cursor: grab;
}
.widget-toolbar:active { cursor: grabbing; }
.widget-title { font-size: 12px; font-weight: 600; color: var(--color-text-2); }
.toolbar-actions { display: flex; gap: 4px; }
.toolbar-btn {
  width: 16px; height: 16px; cursor: pointer;
  color: var(--color-text-4);
  transition: color 0.15s;
}
.toolbar-btn:hover { color: var(--color-text-2); }
.toolbar-btn.pinned { color: var(--color-primary); }

.widget-content { font-size: 12px; }

.sortable-ghost { opacity: 0.4; }

@media (max-width: 900px) {
  .widget-grid { grid-template-columns: 1fr 1fr; }
  .widget-cell.size-large { grid-column: span 2; }
}
</style>
