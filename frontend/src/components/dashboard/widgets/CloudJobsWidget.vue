<template>
  <div class="widget">
    <div class="widget-label">训练任务</div>
    <div class="stat-row">总计: <b>{{ stats.total || 0 }}</b></div>
    <div class="stat-row" v-if="stats.by_status">
      <span v-for="(count, status) in stats.by_status" :key="status" class="status-tag">{{ status }}: {{ count }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { cloud } from '../../../api'

const stats = ref({})
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

async function load() {
  try {
    const d = await cloud.listJobs({ page: 1, page_size: 1 })
    if (d) {
      stats.value = { total: d.total || 0 }
    }
  } catch {}
}

onMounted(() => { load(); timer = setInterval(load, 30000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 6px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
.stat-row { font-size: 12px; color: var(--color-text-3); }
.stat-row b { color: var(--color-text-1); font-weight: 600; }
.status-tag { display: inline-block; background: var(--color-fill-1); padding: 1px 6px; border-radius: 4px; margin-right: 4px; font-size: 11px; }
</style>
