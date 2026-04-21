<template>
  <span class="level-badge" :style="badgeStyle">{{ label }}</span>
</template>

<script setup>
const LEVELS = {
  0: { label: 'P0', bg: '#1a7f37', color: '#fff' },
  1: { label: 'P1', bg: '#6e40c9', color: '#fff' },
  2: { label: 'P2', bg: '#0969da', color: '#fff' },
  3: { label: 'P3', bg: '#8250df', color: '#fff' },
  4: { label: 'P4', bg: '#6e7781', color: '#fff' },
  5: { label: 'P5', bg: '#eaeef2', color: '#57606a' },
}

const props = defineProps({ level: { type: Number, default: 5 } })
const info = LEVELS[props.level] ?? LEVELS[5]
const label = info.label
const badgeStyle = { backgroundColor: info.bg, color: info.color }
</script>

<style scoped>
.level-badge {
  display: inline-block;
  padding: 0 7px;
  font-size: 12px;
  font-weight: 500;
  line-height: 18px;
  border-radius: 2em;
  white-space: nowrap;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
}
</style>
