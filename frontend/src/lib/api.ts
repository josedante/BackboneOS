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
  page?: number
  page_size?: number
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

export const productsApi = {
  // Products CRUD
  getProducts: async (params?: ApiParams) => {
    const response = await api.get('/api/products/products/', { params })
    return response.data
  },

  getProduct: async (id: number) => {
    const response = await api.get(`/api/products/products/${id}/`)
    return response.data
  },

  createProduct: async (productData: ProductCreateData) => {
    const response = await api.post('/api/products/products/', productData)
    return response.data
  },

  updateProduct: async (id: number, productData: ProductUpdateData) => {
    const response = await api.patch(`/api/products/products/${id}/`, productData)
    return response.data
  },

  deleteProduct: async (id: number) => {
    const response = await api.delete(`/api/products/products/${id}/`)
    return response.data
  },

  // Divisions
  getDivisions: async (params?: ApiParams) => {
    const response = await api.get('/api/products/divisions/', { params })
    return response.data
  },

  getDivision: async (id: number) => {
    const response = await api.get(`/api/products/divisions/${id}/`)
    return response.data
  },

  // Categories
  getCategories: async (params?: ApiParams) => {
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
