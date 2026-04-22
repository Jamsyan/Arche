<template>
  <div class="widget-picker">
    <div class="picker-header">
      <icon-apps class="header-icon" />
      <span>Widget 库</span>
      <icon-left class="collapse-btn" @click="$emit('close')" />
    </div>
    <div class="picker-body">
      <div v-for="(widgets, category) in categories" :key="category" class="picker-category">
        <div class="category-title">{{ category }}</div>
        <div class="category-widgets">
          <div v-for="w in widgets" :key="w.type" class="picker-widget">
            <div class="picker-info">
              <component :is="getIcon(w.icon)" class="picker-icon" />
              <span class="picker-name">{{ w.title }}</span>
            </div>
            <a-button size="mini" type="outline" @click="add(w.type)">添加</a-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { IconApps, IconLeft, IconDashboard, IconDesktop, IconBug, IconCloud, IconStorage, IconUser } from '@arco-design/web-vue/es/icon'
import { getWidgetCategories } from './widgets/widgetRegistry.js'

const emit = defineEmits(['close', 'add'])
const categories = computed(() => getWidgetCategories())

const iconMap = {
  IconDashboard, IconDesktop, IconBug, IconCloud, IconStorage, IconApps, IconUser,
}

function getIcon(name) {
  return iconMap[name] || IconApps
}

function add(type) {
  emit('add', type)
}
</script>

<style scoped>
.widget-picker {
  width: 280px;
  background: rgba(255,255,255,0.9);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0,0,0,0.06);
  border-radius: var(--border-radius-large);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  display: flex; flex-direction: column;
  overflow: hidden;
}

.picker-header {
  display: flex; align-items: center; gap: 8px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border-1);
  font-size: 13px; font-weight: 600; color: var(--color-text-2);
}
.header-icon { width: 14px; height: 14px; }
.collapse-btn {
  width: 14px; height: 14px; margin-left: auto;
  cursor: pointer; color: var(--color-text-4);
}
.collapse-btn:hover { color: var(--color-text-1); }

.picker-body {
  flex: 1; overflow-y: auto; padding: 12px;
}

.picker-category { margin-bottom: 12px; }
.category-title {
  font-size: 11px; color: var(--color-text-4); text-transform: uppercase;
  margin-bottom: 6px; font-weight: 600;
}

.category-widgets { display: flex; flex-direction: column; gap: 6px; }

.picker-widget {
  display: flex; align-items: center; justify-content: space-between;
  padding: 6px 8px;
  background: var(--color-fill-1);
  border-radius: 6px;
  transition: background 0.15s;
}
.picker-widget:hover { background: var(--color-fill-2); }

.picker-info { display: flex; align-items: center; gap: 6px; }
.picker-icon { width: 14px; height: 14px; color: var(--color-primary); }
.picker-name { font-size: 12px; color: var(--color-text-2); }
</style>
