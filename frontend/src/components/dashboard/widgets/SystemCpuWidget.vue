<template>
  <div class="widget">
    <div class="widget-label">CPU 使用率</div>
    <div class="widget-value" :class="cpuColor">{{ cpuPercent }}%</div>
    <a-progress :percent="cpuPercent" :size="size === 'small' ? 'mini' : 'small'" :stroke-width="6"
      :status="cpuPercent > 80 ? 'danger' : cpuPercent > 60 ? 'warning' : 'normal'" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { system } from '../../../api'

const cpuPercent = ref(0)
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

async function load() {
  try {
    const data = await system.summary()
    if (data) cpuPercent.value = Math.round(data.cpu_percent || 0)
  } catch {}
}

const cpuColor = ''

onMounted(() => { load(); timer = setInterval(load, 10000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 6px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
.widget-value { font-size: 24px; font-weight: 700; color: var(--color-text-1); }
</style>
