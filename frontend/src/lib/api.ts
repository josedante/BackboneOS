import axios from 'axios'
import https from 'https'

const API_BASE = process.env['NEXT_PUBLIC_API_BASE'] || 'https://backend.proyecto-opensource.orb.local'

// Only create HTTPS agent that ignores self-signed certificates in development
const isDevelopment = process.env.NODE_ENV === 'development' || 
                     process.env['NEXT_PUBLIC_NODE_ENV'] === 'development' ||
                     API_BASE.includes('localhost') ||
                     API_BASE.includes('orb.local')

const httpsAgent = isDevelopment ? new https.Agent({
  rejectUnauthorized: false
}) : undefined

// Log warning in development
if (isDevelopment && httpsAgent) {
  console.warn('⚠️  DEVELOPMENT MODE: SSL certificate verification disabled for self-signed certificates')
}

// Django REST Framework Response Types
export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Helper function to extract results from DRF paginated response
export const getResults = <T>(response: PaginatedResponse<T> | undefined): T[] => {
  return response?.results || []
}

// Type definitions
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  date_joined: string
}

export interface UserCreateData {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
}

export interface UserUpdateData {
  username?: string
  email?: string
  first_name?: string
  last_name?: string
}

export interface Product {
  id: string
  name: string
  code: string
  description: string
  canonical_url?: string
  category?: string
  category_name?: string
  category_full_path?: string
  customization_name?: string
  duration?: string
  base_price?: number
  currency_code: string
  price_display: string
  duration_display?: string
  target_audience: string
  modalities_display: string
  has_canonical_url: boolean
  skills_count: number
  industries_count: number
  segments_count: number
  included_products_count: number
  is_bundle: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ProductDetail extends Omit<Product, 'category'> {
  category?: ProductCategory
  modalities: Modality[]
  customization?: Customization
  target_segments: MarketSegment[]
  related_industries: Industry[]
  related_functions: FunctionOrResponsibility[]
  related_skills: Skill[]
  descriptors: WorldDescriptor[]
  tags: Tag[]
  included_products: Product[]
  parent_products: Product[]
  is_customizable: boolean
  bundle_price_display: string
  skills_summary: Record<string, string[]>
}

export interface ProductCreateData {
  name: string
  code: string
  description?: string
  canonical_url?: string
  category_id?: string
  modalities_ids?: string[]
  customization_id?: string
  duration?: string
  base_price?: number | undefined
  currency_code?: string
  target_segments_ids?: string[]
  related_industries_ids?: string[]
  related_functions_ids?: string[]
  related_skills_ids?: string[]
  descriptors_ids?: string[]
  tags_ids?: string[]
  included_products_ids?: string[]
  is_active?: boolean
}

export interface ProductUpdateData {
  name?: string
  code?: string
  description?: string
  canonical_url?: string
  category_id?: string
  modalities_ids?: string[]
  customization_id?: string
  duration?: string
  base_price?: number | undefined
  currency_code?: string
  target_segments_ids?: string[]
  related_industries_ids?: string[]
  related_functions_ids?: string[]
  related_skills_ids?: string[]
  descriptors_ids?: string[]
  tags_ids?: string[]
  included_products_ids?: string[]
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
  id: string
  name: string
  description: string
  products_count: number
  is_active: boolean
  created_at: string
  updated_at: string
}

// World entities
export interface Industry {
  id: string
  name: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Skill {
  id: string
  name: string
  description: string
  skill_type: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface MarketSegment {
  id: string
  name: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface FunctionOrResponsibility {
  id: string
  name: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface WorldDescriptor {
  id: string
  name: string
  description: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Tag {
  id: string
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
  action_type: string
  channel: string
  medium: string
  created_at: string
}

export interface Campaign {
  id: number
  name: string
  description: string
  start_date: string
  end_date: string
  status: string
}

export interface Offer {
  id: number
  name: string
  description: string
  discount_percentage: number
  valid_from: string
  valid_to: string
}

export interface ApiParams {
  offset?: number
  limit?: number
  search?: string
  ordering?: string
  [key: string]: unknown
}

// Create axios instance
export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  ...(httpsAgent && { httpsAgent }),
})

// Add request logging
api.interceptors.request.use((config) => {
  console.log('Making API request:', {
    method: config.method,
    url: config.url,
    baseURL: config.baseURL,
    fullURL: `${config.baseURL}${config.url}`,
    data: config.data
  })
  return config
})

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const authApi = {
  login: async (username: string, password: string) => {
    const response = await api.post('/users/jwt/login/', { username, password })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/users/user/')
    return response.data
  },

  logout: async () => {
    const response = await api.post('/users/jwt/logout/')
    return response.data
  },
}

export const usersApi = {
  getUsers: async (params?: ApiParams) => {
    const response = await api.get('/api/users/', { params })
    return response.data
  },

  getUser: async (id: number) => {
    const response = await api.get(`/api/users/${id}/`)
    return response.data
  },

  createUser: async (userData: UserCreateData) => {
    const response = await api.post('/api/users/', userData)
    return response.data
  },

  updateUser: async (id: number, userData: UserUpdateData) => {
    const response = await api.patch(`/api/users/${id}/`, userData)
    return response.data
  },

  deleteUser: async (id: number) => {
    const response = await api.delete(`/api/users/${id}/`)
    return response.data
  },
}

// API Response Types
export type ProductsResponse = PaginatedResponse<Product>
export type CategoriesResponse = PaginatedResponse<ProductCategory>
export type DivisionsResponse = PaginatedResponse<Division>
export type ModalitiesResponse = PaginatedResponse<Modality>
export type CustomizationsResponse = PaginatedResponse<Customization>

export const productsApi = {
  // Products CRUD
  getProducts: async (params?: ApiParams): Promise<ProductsResponse> => {
    const response = await api.get('/api/products/products/', { params })
    return response.data
  },

  getProduct: async (id: number): Promise<ProductDetail> => {
    const response = await api.get(`/api/products/products/${id}/`)
    return response.data
  },

  createProduct: async (productData: ProductCreateData): Promise<ProductDetail> => {
    const response = await api.post('/api/products/products/', productData)
    return response.data
  },

  updateProduct: async (id: number, productData: ProductUpdateData): Promise<ProductDetail> => {
    const response = await api.patch(`/api/products/products/${id}/`, productData)
    return response.data
  },

  deleteProduct: async (id: number): Promise<void> => {
    const response = await api.delete(`/api/products/products/${id}/`)
    return response.data
  },

  // Divisions
  getDivisions: async (params?: ApiParams): Promise<DivisionsResponse> => {
    const response = await api.get('/api/products/divisions/', { params })
    return response.data
  },

  getDivision: async (id: number): Promise<Division> => {
    const response = await api.get(`/api/products/divisions/${id}/`)
    return response.data
  },

  // Categories
  getCategories: async (params?: ApiParams): Promise<CategoriesResponse> => {
    const response = await api.get('/api/products/categories/', { params })
    return response.data
  },

  getCategory: async (id: number) => {
    const response = await api.get(`/api/products/categories/${id}/`)
    return response.data
  },

  getCategoriesTree: async () => {
    const response = await api.get('/api/products/categories/tree/')
    return response.data
  },

  // Modalities and Customizations
  getModalities: async (params?: ApiParams) => {
    const response = await api.get('/api/products/modalities/', { params })
    return response.data
  },

  getCustomizations: async (params?: ApiParams) => {
    const response = await api.get('/api/products/customizations/', { params })
    return response.data
  },

  // Analytics
  getAnalytics: async (type: string) => {
    const response = await api.get(`/api/products/analytics/${type}/`)
    return response.data
  },

  getAnalyticsDashboard: async () => {
    const response = await api.get('/api/products/analytics/dashboard/')
    return response.data
  },

  getDivisionAnalytics: async () => {
    const response = await api.get('/api/products/analytics/divisions/')
    return response.data
  },

  getCategoryAnalytics: async () => {
    const response = await api.get('/api/products/analytics/categories/')
    return response.data
  },

  getMarketSegmentationAnalytics: async () => {
    const response = await api.get('/api/products/analytics/market-segmentation/')
    return response.data
  },

  getPricingAnalytics: async () => {
    const response = await api.get('/api/products/analytics/pricing/')
    return response.data
  },

  getGrowthAnalytics: async () => {
    const response = await api.get('/api/products/analytics/growth/')
    return response.data
  },

  getProductRecommendations: async () => {
    const response = await api.get('/api/products/analytics/recommendations/')
    return response.data
  },

  // Advanced features
  searchProducts: async (query: string, params?: ApiParams) => {
    const response = await api.get('/api/products/products/search_advanced/', { 
      params: { search: query, ...params } 
    })
    return response.data
  },

  duplicateProduct: async (id: number) => {
    const response = await api.post(`/api/products/products/${id}/duplicate/`)
    return response.data
  },

  getProductStats: async () => {
    const response = await api.get('/api/products/products/stats/')
    return response.data
  },
}

export const entitiesApi = {
  getEntities: async (params?: ApiParams) => {
    const response = await api.get('/api/entities/', { params })
    return response.data
  },

  getEntity: async (id: number) => {
    const response = await api.get(`/api/entities/${id}/`)
    return response.data
  },
}

export const interactionsApi = {
  getInteractions: async (params?: ApiParams) => {
    const response = await api.get('/api/interactions/', { params })
    return response.data
  },

  getInteraction: async (id: number) => {
    const response = await api.get(`/api/interactions/${id}/`)
    return response.data
  },
}

export const campaignsApi = {
  getCampaigns: async (params?: ApiParams) => {
    const response = await api.get('/api/campaigns/', { params })
    return response.data
  },

  getCampaign: async (id: number) => {
    const response = await api.get(`/api/campaigns/${id}/`)
    return response.data
  },
}

export const offersApi = {
  getOffers: async (params?: ApiParams) => {
    const response = await api.get('/api/offers/', { params })
    return response.data
  },

  getOffer: async (id: number) => {
    const response = await api.get(`/api/offers/${id}/`)
    return response.data
  },
}

export default api
