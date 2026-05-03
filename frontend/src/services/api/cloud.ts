import { del, get, post, type RequestConfig } from '../request'
import type { ApiListParams, Paginated } from './types/common'

export interface CloudJob {
  id: string
  name: string
  status: string
  created_at?: string
}

export interface CreateCloudJobPayload {
  name: string
  repo_url?: string
  provider?: string
  gpu_type?: string
}

export interface CloudInstance {
  id: string
  status: string
  gpu_type?: string
}

export interface CloudCosts {
  total_cost: number
  currency?: string
}

export const getCloudStatsApi = (config?: RequestConfig) =>
  get<Record<string, unknown>>('/cloud/stats', undefined, config)

export const getCloudJobsApi = (
  params?: ApiListParams & { status?: string },
  config?: RequestConfig
) => get<Paginated<CloudJob>>('/cloud/jobs', params, config)

export const getCloudJobDetailApi = (jobId: string, config?: RequestConfig) =>
  get<CloudJob>(`/cloud/jobs/${jobId}`, undefined, config)

export const createCloudJobApi = (payload: CreateCloudJobPayload, config?: RequestConfig) =>
  post<CloudJob>('/cloud/jobs', payload, config)

export const deleteCloudJobApi = (jobId: string, config?: RequestConfig) =>
  del<void>(`/cloud/jobs/${jobId}`, undefined, config)

export const startCloudJobApi = (jobId: string, config?: RequestConfig) =>
  post<void>(`/cloud/jobs/${jobId}/start`, undefined, config)

export const stopCloudJobApi = (jobId: string, config?: RequestConfig) =>
  post<void>(`/cloud/jobs/${jobId}/stop`, undefined, config)

export const getCloudJobLogsApi = (jobId: string, lines?: number, config?: RequestConfig) =>
  get<string[]>(`/cloud/jobs/${jobId}/logs`, { lines }, config)

export const getCloudInstancesApi = (jobId: string, config?: RequestConfig) =>
  get<CloudInstance[]>(`/cloud/jobs/${jobId}/instances`, undefined, config)

export const getCloudCostsApi = (
  params?: { job_id?: string; start_date?: string; end_date?: string },
  config?: RequestConfig
) => get<CloudCosts>('/cloud/costs', params, config)
