<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { NDataTable, NPagination, NSpace } from 'naive-ui'
import type { DataTableColumns } from 'naive-ui'

interface ProTableRequestParams {
  page: number
  pageSize: number
}

interface ProTableResult<T> {
  list: T[]
  total: number
}

// eslint-disable-next-line no-unused-vars
type ProTableRequest = (_params: ProTableRequestParams) => Promise<ProTableResult<any>>

const props = withDefaults(
  defineProps<{
    columns: DataTableColumns<any>
    data?: any[]
    rowKey?: string
    page?: number
    pageSize?: number
    pageSizes?: number[]
    showSizePicker?: boolean
    showQuickJumper?: boolean
    request?: ProTableRequest
  }>(),
  {
    data: () => [],
    rowKey: 'key',
    page: 1,
    pageSize: 10,
    pageSizes: () => [10, 20, 50],
    showSizePicker: false,
    showQuickJumper: false
  }
)
void props.request

const loading = ref(false)
const innerPage = ref(props.page)
const innerPageSize = ref(props.pageSize)
const innerData = ref<any[]>(props.data)
const total = ref(props.data.length)

const pagination = computed(() => ({
  page: innerPage.value,
  pageSize: innerPageSize.value,
  itemCount: total.value,
  pageSizes: props.pageSizes ?? [10, 20, 50],
  showSizePicker: true
}))

const fetchData = async () => {
  if (!props.request) {
    innerData.value = props.data
    total.value = props.data.length
    return
  }

  loading.value = true
  try {
    const result = await props.request({
      page: innerPage.value,
      pageSize: innerPageSize.value
    })
    innerData.value = result.list
    total.value = result.total
  } finally {
    loading.value = false
  }
}

const handleUpdatePage = (page: number) => {
  innerPage.value = page
  fetchData()
}

const handleUpdatePageSize = (pageSize: number) => {
  innerPageSize.value = pageSize
  innerPage.value = 1
  fetchData()
}

watch(
  () => props.data,
  (nextData) => {
    if (!props.request) {
      innerData.value = nextData
      total.value = nextData.length
    }
  },
  { immediate: true, deep: true }
)
</script>

<template>
  <NSpace vertical :size="16">
    <NDataTable
      :columns="columns"
      :data="innerData"
      :loading="loading"
      :row-key="(row: any) => row[rowKey]"
      single-line
    />
    <div class="pager">
      <NPagination
        :page="innerPage"
        :page-size="innerPageSize"
        :item-count="pagination.itemCount"
        :page-sizes="pagination.pageSizes"
        :show-size-picker="showSizePicker"
        :show-quick-jumper="showQuickJumper"
        @update:page="handleUpdatePage"
        @update:page-size="handleUpdatePageSize"
      />
    </div>
  </NSpace>
</template>

<style scoped>
.pager {
  display: flex;
  justify-content: center;
  padding-top: 4px;
}
</style>

<style>
.n-pagination {
  --n-item-color-disabled: transparent !important;
  --n-button-border: 1px solid rgba(130, 95, 65, 0.14) !important;
  --n-button-border-hover: 1px solid rgba(130, 95, 65, 0.14) !important;
  --n-button-border-pressed: 1px solid rgba(130, 95, 65, 0.14) !important;
}

.n-data-table {
  --n-th-color: rgba(255, 248, 236, 0.52) !important;
  --n-td-color: rgba(255, 248, 236, 0.52) !important;
  --n-td-color-hover: rgba(154, 90, 47, 0.04) !important;
  --n-border-color: rgba(130, 95, 65, 0.1) !important;
  --n-th-text-color: var(--text-secondary) !important;
  --n-td-text-color: var(--text-primary) !important;
  --n-th-icon-color: var(--text-tertiary) !important;
  --n-th-icon-color-active: var(--primary-color) !important;
}
</style>
