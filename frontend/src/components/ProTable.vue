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
    showSizePicker: true,
    showQuickJumper: true
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
  </NSpace>
</template>
