import { get, type RequestConfig } from '../request'
import type { ApiListParams, BackendPaginated } from './types/common'
import { normalizePaginated } from './types/common'

export interface SystemSummary {
  cpu_percent: number
  cpu_count?: number
  memory_percent: number
  disk_percent: number
  memory_used_gb?: number
  memory_total_gb?: number
  disk_used_gb?: number
  disk_total_gb?: number
  net_sent?: number
  net_recv?: number
  process_count?: number
  python_version?: string
  uptime?: number
  platform?: string
  load_1?: number
  load_5?: number
  load_15?: number
}

export interface CpuDetail {
  count_physical?: number
  count_logical?: number
  freq_current?: number
  freq_min?: number
  freq_max?: number
  per_cpu_pct?: number[]
  load_1?: number
  load_5?: number
  load_15?: number
}

export interface MemoryDetail {
  total: number
  available: number
  used: number
  free: number
  percent: number
  swap_total?: number
  swap_used?: number
  swap_free?: number
  swap_percent?: number
}

export interface DiskDetail {
  root_total?: number
  root_used?: number
  root_free?: number
  root_percent?: number
  partitions?: Array<{
    device: string
    mountpoint: string
    fstype: string
    total: number
    used: number
    free: number
    percent: number
  }>
}

export interface NetworkIo {
  bytes_sent: number
  bytes_recv: number
  packets_sent: number
  packets_recv: number
  errin: number
  errout: number
  dropin: number
  dropout: number
}

export interface HistoryPoint {
  ts: number
  cpu_pct: number
  cpu_count: number
  mem_total: number
  mem_used: number
  mem_pct: number
  disk_total: number
  disk_used: number
  disk_pct: number
  net_sent_rate: number
  net_recv_rate: number
  load_1: number
  load_5: number
  load_15: number
}

export interface ProcessInfo {
  pid: number
  name: string
  status: string
  cpu_percent: number
  memory_percent: number
  create_time: number
}

export interface ProcessQueryParams {
  sort_by?: string
  limit?: number
}

export interface ProcessListResponse {
  items: ProcessInfo[]
  total: number
  limit: number
}

export const getSystemSummaryApi = (config?: RequestConfig) =>
  get<SystemSummary>('/system/summary', undefined, config)

export const getCpuMetricsApi = (config?: RequestConfig) =>
  get<CpuDetail>('/system/cpu', undefined, config)

export const getMemoryMetricsApi = (config?: RequestConfig) =>
  get<MemoryDetail>('/system/memory', undefined, config)

export const getDiskMetricsApi = (config?: RequestConfig) =>
  get<DiskDetail>('/system/disk', undefined, config)

export const getNetworkMetricsApi = (config?: RequestConfig) =>
  get<NetworkIo>('/system/network', undefined, config)

export const getSystemHistoryApi = (params?: ApiListParams, config?: RequestConfig) =>
  get<BackendPaginated<HistoryPoint>>('/system/history', params, config).then(normalizePaginated)

export const getProcessesApi = (params?: ProcessQueryParams, config?: RequestConfig) =>
  get<ProcessListResponse>('/system/processes', params, config).then((r) => r.items || [])
