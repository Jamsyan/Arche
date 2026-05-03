import { get, type RequestConfig } from '../request'
import type { ApiListParams, Paginated } from './types/common'

export interface SystemSummary {
  cpu_usage: number
  memory_usage: number
  disk_usage: number
}

export interface MetricPoint {
  timestamp: string
  value: number
}

export interface ProcessInfo {
  pid: number
  name: string
  cpu_percent: number
  memory_percent: number
}

export interface ProcessQueryParams {
  sort_by?: string
  limit?: number
}

export const getSystemSummaryApi = (config?: RequestConfig) =>
  get<SystemSummary>('/system/summary', undefined, config)

export const getCpuMetricsApi = (config?: RequestConfig) =>
  get<MetricPoint[]>('/system/cpu', undefined, config)

export const getMemoryMetricsApi = (config?: RequestConfig) =>
  get<MetricPoint[]>('/system/memory', undefined, config)

export const getDiskMetricsApi = (config?: RequestConfig) =>
  get<MetricPoint[]>('/system/disk', undefined, config)

export const getNetworkMetricsApi = (config?: RequestConfig) =>
  get<MetricPoint[]>('/system/network', undefined, config)

export const getSystemHistoryApi = (params?: ApiListParams, config?: RequestConfig) =>
  get<Paginated<Record<string, unknown>>>('/system/history', params, config)

export const getProcessesApi = (params?: ProcessQueryParams, config?: RequestConfig) =>
  get<ProcessInfo[]>('/system/processes', params, config)
