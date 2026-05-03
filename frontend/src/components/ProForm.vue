<script setup lang="ts">
import { NCard, NForm, NGrid, NFormItemGi } from 'naive-ui'
import type { FormInst, FormRules, FormValidationError } from 'naive-ui'

withDefaults(
  defineProps<{
    model: Record<string, any>
    rules?: FormRules
    labelWidth?: number
    columns?: number
    showFeedback?: boolean
  }>(),
  {
    rules: () => ({}),
    labelWidth: 90,
    columns: 2,
    showFeedback: true
  }
)

const emit = defineEmits<{
  submit: []
  failed: [errors: FormValidationError[] | undefined]
}>()

const formRef = defineModel<FormInst | null>('formRef', {
  default: null
})

const handleSubmit = async () => {
  try {
    await formRef.value?.validate()
    emit('submit')
  } catch (error) {
    emit('failed', error as FormValidationError[] | undefined)
  }
}
</script>

<template>
  <NCard>
    <NForm
      ref="formRef"
      :model="model"
      :rules="rules"
      :label-width="labelWidth"
      :show-feedback="showFeedback"
      label-placement="left"
    >
      <NGrid :cols="columns" :x-gap="16">
        <slot />
        <NFormItemGi :span="columns">
          <slot name="actions" :submit="handleSubmit" />
        </NFormItemGi>
      </NGrid>
    </NForm>
  </NCard>
</template>
