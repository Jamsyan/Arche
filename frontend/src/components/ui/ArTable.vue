<script setup lang="ts">
import { NDataTable, NPagination } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

interface PaginationProps {
  page: number
  pageSize: number
  itemCount: number
  pageSizes?: number[]
}

// eslint-disable-next-line no-unused-vars, @typescript-eslint/no-unused-vars
const _props = withDefaults(
  defineProps<{
    columns: DataTableColumns<any>
    data: Record<string, any>[]
    loading?: boolean
    bordered?: boolean
    singleLine?: boolean
    striped?: boolean
    size?: 'small' | 'medium' | 'large'
    pagination?: PaginationProps
  }>(),
  {
    loading: false,
    bordered: false,
    singleLine: true,
    striped: true,
    size: 'small'
  }
)

const emit = defineEmits<{
  'update:page': [page: number]
  'update:pageSize': [size: number]
}>()

const themeOverrides = {
  common: {
    fontSizeSmall: '12px',
    fontSizeMedium: '13px',
    fontSizeLarge: '14px',
    fontFamily: 'var(--font-sans)',
    borderColor: 'var(--border-color)',
    actionColor: 'var(--surface-color)',
    actionDividerColor: 'var(--border-color)'
  },
  DataTable: {
    tdColor: 'var(--surface-color)',
    tdColorStriped: 'var(--surface-inset-color)',
    thColor: 'var(--surface-strong-color)',
    thTextColor: 'var(--text-secondary)',
    tdTextColor: 'var(--text-primary)',
    borderColor: 'var(--border-color)',
    thFontWeight: '600',
    thFontSizeSmall: '11px',
    thFontSizeMedium: '12px',
    thFontSizeLarge: '13px',
    tdFontSizeSmall: '12px',
    tdFontSizeMedium: '13px',
    tdFontSizeLarge: '14px',
    borderRadius: 'var(--radius-md)',
    borderBottomLeftRadius: 'var(--radius-md)',
    borderBottomRightRadius: 'var(--radius-md)',
    borderTopLeftRadius: 'var(--radius-md)',
    borderTopRightRadius: 'var(--radius-md)',
    thPaddingSmall: '8px 12px',
    thPaddingMedium: '10px 14px',
    thPaddingLarge: '12px 16px',
    tdPaddingSmall: '8px 12px',
    tdPaddingMedium: '10px 14px',
    tdPaddingLarge: '12px 16px',
    boxShadowBefore: 'none',
    boxShadowAfter: 'none',
    loadingColor: 'var(--primary-color)',
    loadingSize: '20px'
  }
}

function handlePageChange(p: number) {
  emit('update:page', p)
}

function handlePageSizeChange(s: number) {
  emit('update:pageSize', s)
}
</script>

<template>
  <div class="ar-table">
    <NDataTable
      :columns="columns"
      :data="data"
      :loading="loading"
      :bordered="bordered"
      :single-line="singleLine"
      :striped="striped"
      :size="size"
      :theme-overrides="themeOverrides"
      class="ar-table__inner"
    />
    <div v-if="pagination" class="ar-table__pagination">
      <NPagination
        :page="pagination.page"
        :page-size="pagination.pageSize"
        :item-count="pagination.itemCount"
        :page-sizes="pagination.pageSizes || [10, 20, 50]"
        :show-size-picker="true"
        :theme-overrides="{
          itemFontSizeSmall: '12px',
          inputWidthSmall: '50px',
          selectWidthSmall: '80px',
          itemTextColor: 'var(--text-secondary)',
          itemTextColorHover: 'var(--primary-color)',
          itemTextColorActive: 'var(--primary-color)',
          itemColor: 'transparent',
          itemColorHover: 'var(--primary-light-color)',
          itemColorActive: 'var(--primary-light-color)',
          itemBorder: '1px solid var(--border-color)',
          itemBorderHover: '1px solid var(--primary-color)',
          itemBorderActive: '1px solid var(--primary-color)',
          itemBorderRadius: 'var(--radius-sm)',
          itemFontSizeActive: '12px',
          buttonColor: 'transparent',
          buttonColorHover: 'var(--primary-light-color)',
          buttonBorder: '1px solid var(--border-color)',
          buttonBorderHover: '1px solid var(--primary-color)',
          buttonIconColor: 'var(--text-tertiary)',
          buttonIconColorHover: 'var(--primary-color)',
          inputBorderColor: 'var(--border-color)',
          inputBorderColorHover: 'var(--primary-color)',
          inputBorderColorFocus: 'var(--primary-color)',
          selectBorderColor: 'var(--border-color)',
          selectBorderColorHover: 'var(--primary-color)',
          selectBorderColorFocus: 'var(--primary-color)',
          suffixFontSize: '12px'
        }"
        @update:page="handlePageChange"
        @update:page-size="handlePageSizeChange"
      />
    </div>
  </div>
</template>

<style scoped>
.ar-table {
  font-family: var(--font-sans);
}

.ar-table__inner {
  overflow: hidden;
}

.ar-table__pagination {
  display: flex;
  justify-content: center;
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  background: var(--surface-color);
}
</style>
