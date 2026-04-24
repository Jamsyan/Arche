<template>
  <div class="todo-panel">
    <div class="todo-header">
      <icon-pushpin class="header-icon" />
      <span>待办任务</span>
      <a-tag v-if="activeTodos.length > 0" color="red" size="mini">{{ activeTodos.length }}</a-tag>
    </div>
    <div class="todo-list">
      <div v-if="activeTodos.length === 0" class="todo-empty">
        暂无待办任务
      </div>
      <div v-for="todo in activeTodos" :key="todo.id" class="todo-item" :class="`priority-${todo.priority}`">
        <div class="todo-icon-wrap">
          <component :is="todo.icon" class="todo-icon" />
        </div>
        <div class="todo-content">
          <div class="todo-title">{{ todo.title }}</div>
          <div class="todo-desc">{{ todo.desc }}</div>
        </div>
        <a-button size="mini" type="text" @click="ack(todo.id)">
          <template #icon><icon-check /></template>
        </a-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { IconPushpin, IconCheck, IconBug, IconCheckCircle, IconStorage } from '@arco-design/web-vue/es/icon'
import { blog, crawler, oss } from '../../api'

const todos = ref([])
let timer = null

// 仅显示未被 ack 的
const ackedIds = ref(new Set())
const activeTodos = computed(() => todos.value.filter(t => !ackedIds.value.has(t.id)))

function ack(id) {
  ackedIds.value.add(id)
}

// 手动锚定
function addTodo(todo) {
  todos.value.push({ ...todo, id: `manual_${Date.now()}`, priority: 'normal' })
}

async function detectTodos() {
  const token = localStorage.getItem('veil_token')
  if (!token) return
  const newTodos = []

  // 审核任务
  try {
    const d = await blog.moderationPending({ page: 1, page_size: 1 })
    if (d?.total > 0) {
      newTodos.push({
        id: 'moderation_pending',
        title: '帖子审核',
        desc: `${d.total} 篇帖子待审核`,
        icon: IconCheckCircle,
        priority: 'high',
      })
    }
  } catch {}

  // 爬虫状态
  try {
    const d = await crawler.status()
    if (!d?.running) {
      newTodos.push({
        id: 'crawler_stopped',
        title: '爬虫已停止',
        desc: '爬虫服务未运行，请检查状态',
        icon: IconBug,
        priority: 'high',
      })
    }
  } catch {}

  // 存储告警
  try {
    const d = await oss.adminStats()
    if (d?.disk_percent > 80) {
      newTodos.push({
        id: 'disk_warning',
        title: '磁盘空间不足',
        desc: `磁盘使用率 ${d.disk_percent}%`,
        icon: IconStorage,
        priority: 'medium',
      })
    }
  } catch {}

  // 替换自动检测的 todo（保留手动添加的）
  const autoIds = new Set(newTodos.map(t => t.id))
  todos.value = todos.value.filter(t => t.id.startsWith('manual_') || autoIds.has(t.id))
  for (const t of newTodos) {
    if (!todos.value.find(existing => existing.id === t.id)) {
      todos.value.push(t)
    }
  }
}

onMounted(() => { detectTodos(); timer = setInterval(detectTodos, 30000) })
onUnmounted(() => { if (timer) clearInterval(timer) })

defineExpose({ addTodo })
</script>

<style scoped>
.todo-panel {
  background: rgba(255,255,255,0.75);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: var(--border-radius-large);
  box-shadow: 0 1px 4px rgba(0,0,0,0.03);
  overflow: hidden;
}

.todo-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--color-border-1);
  font-size: 13px; font-weight: 600; color: var(--color-text-2);
}
.header-icon { width: 14px; height: 14px; color: var(--color-primary); }

.todo-list { padding: 8px; }
.todo-empty {
  padding: 20px; text-align: center;
  color: var(--color-text-4); font-size: 13px;
}

.todo-item {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  transition: background 0.15s;
}
.todo-item:hover { background: var(--color-fill-1); }
.todo-item.priority-high { border-left: 3px solid #cf222e; }
.todo-item.priority-medium { border-left: 3px solid #d4a72c; }
.todo-item.priority-normal { border-left: 3px solid var(--color-primary); }

.todo-icon-wrap {
  width: 32px; height: 32px;
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  background: var(--color-fill-1);
  flex-shrink: 0;
}
.todo-icon { width: 16px; height: 16px; color: var(--color-text-2); }

.todo-content { flex: 1; min-width: 0; }
.todo-title { font-size: 13px; font-weight: 600; color: var(--color-text-1); }
.todo-desc { font-size: 11px; color: var(--color-text-3); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
</style>
