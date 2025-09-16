export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  date_joined: string
  is_staff?: boolean
  is_active?: boolean
}

export interface Product {
  id: number
  name: string
  description: string
  price: number
  category: number
  division: number
  modality: number
  customization: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProductCreateData {
  name: string
  description: string
  price: number
  category: number
  division: number
  modality?: number
  customization?: number
  is_active?: boolean
}

export interface ProductUpdateData {
  name?: string
  description?: string
  price?: number
  category?: number
  division?: number
  modality?: number
  customization?: number
  is_active?: boolean
}

export interface Division {
  id: number
  name: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProductCategory {
  id: number
  name: string
  description: string
  division: number
  parent: number | null
  level: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Modality {
  id: number
  name: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Customization {
  id: number
  name: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Entity {
  id: number
  name: string
  type: string
  created_at: string
  updated_at: string
}

export interface Interaction {
  id: number
  entity: number
  type: string
  description: string
  created_at: string
  updated_at: string
}

export interface Campaign {
  id: number
  name: string
  description: string
  start_date: string
  end_date: string
  status: string
  created_at: string
  updated_at: string
}

export interface Offer {
  id: number
  name: string
  description: string
  discount_percentage: number
  valid_from: string
  valid_until: string
  created_at: string
  updated_at: string
}

export interface ApiResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

export interface DashboardStats {
  total_users: number
  total_products: number
  total_entities: number
  total_interactions: number
  revenue: number
  growth_rate: number
}

export interface AnalyticsData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    backgroundColor?: string
    borderColor?: string
  }[]
}
