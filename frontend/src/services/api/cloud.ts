import { del, get, post, type RequestConfig } from '../request'
import type { ApiListParams, BackendPaginated } from './types/common'
import { normalizePaginated } from './types/common'

export interface CloudJob {
  id: string
  name: string
  status: string
  created_at?: string
  orchestrator_step?: string
}

export interface CreateCloudJobPayload {
  name: string
  repo_url?: string
  provider?: string
  gpu_type?: string
  config?: Record<string, unknown>
  repo_branch?: string
  repo_token?: string
  dataset_config?: Record<string, unknown>
  training_script?: string
  requirements_file?: string
  log_pattern?: string
  instance_name?: string
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

export interface CloudStats {
  running_jobs: number
  running_instances: number
}

export const getCloudStatsApi = (config?: RequestConfig) =>
  get<CloudStats>('/cloud/stats', undefined, config)

export const getCloudJobsApi = (
  params?: ApiListParams & { status?: string },
  config?: RequestConfig
) => get<BackendPaginated<CloudJob>>('/cloud/jobs', params, config).then(normalizePaginated)

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

export const getCloudInstancesApi = (
  jobId: string,
  params?: ApiListParams,
  config?: RequestConfig
) =>
  get<BackendPaginated<CloudInstance>>(`/cloud/jobs/${jobId}/instances`, params, config).then(
    normalizePaginated
  )

export const getCloudCostsApi = (
  params?: { job_id?: string; start_date?: string; end_date?: string },
  config?: RequestConfig
) => get<CloudCosts>('/cloud/costs', params, config)
