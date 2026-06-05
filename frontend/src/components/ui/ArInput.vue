<script setup lang="ts">
import { computed, ref } from 'vue'
import { NInput } from 'naive-ui'

type InputVariant = 'outlined' | 'filled'

const props = withDefaults(
  defineProps<{
    variant?: InputVariant
    value?: string | null
    placeholder?: string
    disabled?: boolean
    readonly?: boolean
    size?: 'small' | 'medium' | 'large'
    type?: 'text' | 'textarea' | 'password'
    rows?: number
    autosize?: boolean | { minRows?: number; maxRows?: number }
    showPasswordOn?: 'click' | 'mousedown'
    clearable?: boolean
    maxlength?: number
    showCount?: boolean
    status?: 'success' | 'warning' | 'error'
  }>(),
  {
    variant: 'outlined',
    size: 'medium'
  }
)

const emit = defineEmits<{
  'update:value': [val: string | null]
  change: [val: string | null]
  blur: [e: FocusEvent]
  focus: [e: FocusEvent]
  input: [val: string | null]
  clear: []
}>()

const inputRef = ref<InstanceType<typeof NInput> | null>(null)

const inputClasses = computed(() => [
  'ar-input',
  `ar-input--${props.variant}`,
  `ar-input--${props.size}`,
  {
    'is-disabled': props.disabled
  }
])

const nInputProps = computed(() => {
  const p: Record<string, unknown> = {}
  if (props.value !== undefined) p.value = props.value
  if (props.placeholder !== undefined) p.placeholder = props.placeholder
  if (props.disabled !== undefined) p.disabled = props.disabled
  if (props.readonly !== undefined) p.readonly = props.readonly
  if (props.size !== undefined) p.size = props.size
  if (props.type !== undefined) p.type = props.type
  if (props.rows !== undefined) p.rows = props.rows
  if (props.autosize !== undefined) p.autosize = props.autosize
  if (props.showPasswordOn !== undefined) p['show-password-on'] = props.showPasswordOn
  if (props.clearable !== undefined) p.clearable = props.clearable
  if (props.maxlength !== undefined) p.maxlength = props.maxlength
  if (props.showCount !== undefined) p['show-count'] = props.showCount
  if (props.status !== undefined) p.status = props.status
  return p
})

function handleUpdateValue(val: string | null) {
  emit('update:value', val)
}

function handleChange(val: string | null) {
  emit('change', val)
}

function handleBlur(e: FocusEvent) {
  emit('blur', e)
}

function handleFocus(e: FocusEvent) {
  emit('focus', e)
}

function handleInput(val: string | null) {
  emit('input', val)
}

function handleClear() {
  emit('clear')
}

function focus() {
  inputRef.value?.focus()
}

function blur() {
  inputRef.value?.blur()
}

defineExpose({
  focus,
  blur,
  inputRef
})
</script>

<template>
  <div :class="inputClasses">
    <NInput
      ref="inputRef"
      v-bind="nInputProps"
      :theme-overrides="{
        borderRadius: 'var(--radius-md)',
        color: props.variant === 'filled' ? 'var(--surface-inset-color)' : 'transparent',
        colorFocus: props.variant === 'filled' ? 'var(--surface-inset-color)' : 'transparent',
        border:
          props.variant === 'filled' ? '1px solid transparent' : '1px solid var(--border-color)',
        borderFocus:
          props.variant === 'filled'
            ? '1px solid var(--primary-color)'
            : '1px solid var(--primary-color)',
        borderHover:
          props.variant === 'filled'
            ? '1px solid var(--border-color)'
            : '1px solid var(--border-color)',
        boxShadowFocus: '0 0 0 3px var(--primary-light-color)',
        textColor: 'var(--text-primary)',
        placeholderColor: 'var(--text-tertiary)',
        caretColor: 'var(--primary-color)',
        fontSizeTiny: '12px',
        fontSizeSmall: '13px',
        fontSizeMedium: '14px',
        fontSizeLarge: '16px',
        heightTiny: '24px',
        heightSmall: '30px',
        heightMedium: '36px',
        heightLarge: '44px',
        paddingTiny: '0 8px',
        paddingSmall: '0 10px',
        paddingMedium: '0 12px',
        paddingLarge: '0 16px',
        iconSize: '16px',
        colorDisabled: 'transparent',
        borderDisabled: '1px solid var(--border-color)',
        textColorDisabled: 'var(--text-disabled)',
        loadingColor: 'var(--primary-color)',
        loadingColorError: 'var(--error-color)',
        clearColor: 'var(--text-tertiary)',
        clearSize: '16px',
        countTextColor: 'var(--text-tertiary)'
      }"
      @update:value="handleUpdateValue"
      @change="handleChange"
      @blur="handleBlur"
      @focus="handleFocus"
      @input="handleInput"
      @clear="handleClear"
    >
      <template v-if="$slots.prefix" #prefix>
        <slot name="prefix" />
      </template>
      <template v-if="$slots.suffix" #suffix>
        <slot name="suffix" />
      </template>
    </NInput>
  </div>
</template>

<style scoped>
.ar-input {
  font-family: var(--font-sans);
  transition: all var(--transition-fast);
}

/* ── focus ring (complement to Naive UI's own) ── */
.ar-input {
  border-radius: var(--radius-md);
  transition: box-shadow var(--transition-fast);
}

/* ── filled variant background ── */
.ar-input--filled {
  background: var(--surface-inset-color);
  border-radius: var(--radius-md);
}

/* ── outlined variant ── */
.ar-input--outlined {
  background: transparent;
}
</style>
