<script setup lang="ts">
import { computed } from 'vue'

type TagColor = 'default' | 'primary' | 'red' | 'blue' | 'yellow' | 'green'
type TagSize = 'sm' | 'md'
type TagType = 'filled' | 'light'

const props = withDefaults(
  defineProps<{
    color?: TagColor
    size?: TagSize
    closable?: boolean
    type?: TagType
  }>(),
  {
    color: 'default',
    size: 'sm',
    closable: false,
    type: 'filled'
  }
)

const emit = defineEmits<{
  close: [e: MouseEvent]
}>()

const classes = computed(() => [
  'ar-tag',
  `ar-tag--${props.color}`,
  `ar-tag--${props.size}`,
  `ar-tag--${props.type}`
])

function handleClose(e: MouseEvent) {
  e.stopPropagation()
  emit('close', e)
}
</script>

<template>
  <span :class="classes">
    <span class="ar-tag__text">
      <slot />
    </span>
    <button
      v-if="closable"
      class="ar-tag__close"
      @click="handleClose"
      aria-label="关闭"
      type="button"
    >
      <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
        <path
          d="M1 1L9 9M9 1L1 9"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
        />
      </svg>
    </button>
  </span>
</template>

<style scoped>
.ar-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  font-family: var(--font-sans);
  font-weight: var(--font-weight-medium);
  line-height: 1;
  border-radius: var(--radius-sm);
  transition:
    background-color var(--transition-fast),
    border-color var(--transition-fast);
}

.ar-tag__text {
  display: inline-block;
}

/* ── sizes ── */
.ar-tag--sm {
  font-size: 11px;
  padding: 2px 8px;
  height: 20px;
}

.ar-tag--md {
  font-size: 13px;
  padding: 4px 12px;
  height: 26px;
}

/* ── colors / filled ── */
.ar-tag--default.ar-tag--filled {
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.ar-tag--primary.ar-tag--filled {
  background-color: var(--primary-color);
  color: #fff;
  border: 1px solid var(--primary-color);
}

.ar-tag--red.ar-tag--filled {
  background-color: var(--accent-red);
  color: #fff;
  border: 1px solid var(--accent-red);
}

.ar-tag--blue.ar-tag--filled {
  background-color: var(--accent-blue);
  color: #fff;
  border: 1px solid var(--accent-blue);
}

.ar-tag--yellow.ar-tag--filled {
  background-color: var(--accent-yellow);
  color: #fff;
  border: 1px solid var(--accent-yellow);
}

.ar-tag--green.ar-tag--filled {
  background-color: var(--accent-green);
  color: #fff;
  border: 1px solid var(--accent-green);
}

/* ── colors / light ── */
.ar-tag--default.ar-tag--light {
  background-color: rgba(26, 24, 23, 0.06);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
}

.ar-tag--primary.ar-tag--light {
  background-color: var(--primary-light-color);
  color: var(--primary-color);
  border: 1px solid color-mix(in srgb, var(--primary-color) 20%, transparent);
}

.ar-tag--red.ar-tag--light {
  background-color: rgba(194, 58, 43, 0.1);
  color: var(--accent-red);
  border: 1px solid rgba(194, 58, 43, 0.2);
}

.ar-tag--blue.ar-tag--light {
  background-color: rgba(74, 124, 148, 0.1);
  color: var(--accent-blue);
  border: 1px solid rgba(74, 124, 148, 0.2);
}

.ar-tag--yellow.ar-tag--light {
  background-color: rgba(212, 160, 23, 0.1);
  color: var(--accent-yellow);
  border: 1px solid rgba(212, 160, 23, 0.2);
}

.ar-tag--green.ar-tag--light {
  background-color: rgba(45, 90, 58, 0.1);
  color: var(--accent-green);
  border: 1px solid rgba(45, 90, 58, 0.2);
}

/* ── close button ── */
.ar-tag__close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
  color: inherit;
  opacity: 0.6;
  transition: opacity var(--transition-fast);
}

.ar-tag__close:hover {
  opacity: 1;
}
</style>
