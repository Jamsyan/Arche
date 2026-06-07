<script setup lang="ts">
import { computed } from 'vue'

type BadgeType = 'default' | 'primary' | 'red' | 'blue' | 'yellow' | 'green'
type BadgeSize = 'sm' | 'md'

const props = withDefaults(
  defineProps<{
    type?: BadgeType
    size?: BadgeSize
    dot?: boolean
    count?: number
  }>(),
  {
    type: 'default',
    size: 'sm',
    dot: false,
    count: 0
  }
)

const classes = computed(() => [
  'ar-badge',
  `ar-badge--${props.type}`,
  `ar-badge--${props.size}`,
  {
    'ar-badge--dot': props.dot
  }
])

const displayCount = computed(() => {
  if (props.dot) return ''
  if (props.count > 99) return '99+'
  return String(props.count)
})

const showBadge = computed(() => {
  if (props.dot) return true
  return props.count > 0
})
</script>

<template>
  <span :class="classes">
    <slot />
    <span v-if="!dot && showBadge" class="ar-badge__count">{{ displayCount }}</span>
    <span v-else-if="dot && showBadge" class="ar-badge__dot" />
  </span>
</template>

<style scoped>
.ar-badge {
  position: relative;
  display: inline-flex;
}

/* ── count number ── */
.ar-badge__count {
  position: absolute;
  top: 0;
  right: 0;
  transform: translate(50%, -50%);
  border-radius: var(--radius-full);
  font-family: var(--font-sans);
  font-weight: var(--font-weight-semibold);
  font-variant-numeric: tabular-nums;
  line-height: 1;
  white-space: nowrap;
  text-align: center;
  box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.15);
  pointer-events: none;
}

/* ── dot ── */
.ar-badge__dot {
  position: absolute;
  top: 0;
  right: 0;
  transform: translate(50%, -50%);
  border-radius: var(--radius-full);
  pointer-events: none;
}

/* ── sizes ── */
.ar-badge--sm .ar-badge__count {
  min-width: 16px;
  height: 16px;
  font-size: 10px;
  padding: 0 4px;
  line-height: 16px;
}

.ar-badge--md .ar-badge__count {
  min-width: 20px;
  height: 20px;
  font-size: 12px;
  padding: 0 5px;
  line-height: 20px;
}

.ar-badge--sm .ar-badge__dot {
  width: 8px;
  height: 8px;
}

.ar-badge--md .ar-badge__dot {
  width: 10px;
  height: 10px;
}

/* ── type / default ── */
.ar-badge--default .ar-badge__count,
.ar-badge--default .ar-badge__dot {
  background-color: var(--text-tertiary);
  color: #fff;
}

/* ── type / primary ── */
.ar-badge--primary .ar-badge__count,
.ar-badge--primary .ar-badge__dot {
  background-color: var(--primary-color);
  color: #fff;
}

/* ── type / red ── */
.ar-badge--red .ar-badge__count,
.ar-badge--red .ar-badge__dot {
  background-color: var(--accent-red);
  color: #fff;
}

/* ── type / blue ── */
.ar-badge--blue .ar-badge__count,
.ar-badge--blue .ar-badge__dot {
  background-color: var(--accent-blue);
  color: #fff;
}

/* ── type / yellow ── */
.ar-badge--yellow .ar-badge__count,
.ar-badge--yellow .ar-badge__dot {
  background-color: var(--accent-yellow);
  color: #fff;
}

/* ── type / green ── */
.ar-badge--green .ar-badge__count,
.ar-badge--green .ar-badge__dot {
  background-color: var(--accent-green);
  color: #fff;
}
</style>
