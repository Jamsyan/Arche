import { get, type RequestConfig } from '../request'
import type { ApiListParams, Paginated } from './types/common'

export interface AssetItem {
  id: string
  name: string
  asset_type: string
  created_at?: string
}

export interface AssetStats {
  total: number
  by_type: Record<string, number>
}

export interface AssetQueryParams extends ApiListParams {
  asset_type?: string
}

export interface AssetSearchParams extends AssetQueryParams {
  keyword?: string
  date_from?: string
  date_to?: string
}

export const getAssetsApi = (params?: AssetQueryParams, config?: RequestConfig) =>
  get<Paginated<AssetItem>>('/assets', params, config)

export const searchAssetsApi = (params?: AssetSearchParams, config?: RequestConfig) =>
  get<Paginated<AssetItem>>('/assets/search', params, config)

export const getAssetStatsApi = (config?: RequestConfig) =>
  get<AssetStats>('/assets/stats', undefined, config)
