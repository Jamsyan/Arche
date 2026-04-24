<template>
  <div class="widget">
    <div class="widget-label">磁盘使用</div>
    <div class="widget-value">{{ used }} / {{ total }} GB</div>
    <a-progress :percent="percent" :size="size === 'small' ? 'mini' : 'small'" :stroke-width="6"
      :status="percent > 80 ? 'danger' : percent > 60 ? 'warning' : 'normal'" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { system } from '../../../api'

const used = ref(0)
const total = ref(0)
const percent = ref(0)
const size = defineProps({ size: { type: String, default: 'medium' } })
let timer = null

async function load() {
  try {
    const data = await system.summary()
    if (data) {
      used.value = data.disk_used_gb || 0
      total.value = data.disk_total_gb || 0
      percent.value = Math.round(data.disk_percent || 0)
    }
  } catch {}
}

onMounted(() => { load(); timer = setInterval(load, 10000) })
onUnmounted(() => { if (timer) clearInterval(timer) })
</script>

<style scoped>
.widget { display: flex; flex-direction: column; gap: 6px; }
.widget-label { font-size: 11px; color: var(--color-text-4); text-transform: uppercase; }
.widget-value { font-size: 20px; font-weight: 700; color: var(--color-text-1); }
</style>
