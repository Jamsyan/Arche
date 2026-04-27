export interface ApiListParams {
  page?: number
  page_size?: number
}

export interface Paginated<T> {
  total: number
  page: number
  page_size: number
  list: T[]
}

export interface BatchActionPayload {
  post_ids: string[]
}
