<template>
  <div class="widget">
    <div class="widget-label">资产统计</div>
    <div class="stat-row" v-if="stats.by_type">
      <span v-for="(count, type) in stats.by_type" :key="type" class="type-tag">{{ type }}: {{ count }}</span>
    </div>
    <div class="stat-row">总计: <b>{{ stats.total || 0 }}</b></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { assets } from '../../../api'

const stats = ref({})
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

async function load() {
  try {
    const d = await assets.stats()
    if (d) stats.value = d || {}
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
.type-tag { display: inline-block; background: var(--color-fill-1); padding: 1px 6px; border-radius: 4px; margin-right: 4px; font-size: 11px; }
</style>
