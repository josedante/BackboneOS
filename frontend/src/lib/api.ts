import https from 'https'

import axios from 'axios'

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
  // Development mode warning - SSL verification disabled
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

// World entities interfaces
export interface Industry {
  id: string
  name: string
  code: string
  description: string
  parent?: string
  level: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Skill {
  id: string
  name: string
  code: string
  description: string
  skill_type: string
  typical_level_required: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface MarketSegment {
  id: string
  name: string
  code: string
  description: string
  segment_type: string
  display_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface FunctionOrResponsibility {
  id: string
  name: string
  code: string
  description: string
  level: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface WorldDescriptor {
  id: string
  name: string
  code: string
  description: string
  family: string
  parent?: string
  level: number
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

// Token refresh state to prevent multiple simultaneous refresh attempts
let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: unknown) => void
  reject: (error: Error) => void
}> = []

// Process failed requests after token refresh
const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) {
      reject(error)
    } else {
      resolve(token)
    }
  })
  
  failedQueue = []
}

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const authTokens = localStorage.getItem('auth_tokens')
    if (authTokens) {
      try {
        const tokens = JSON.parse(authTokens)
        if (tokens.access) {
          config.headers.Authorization = `Bearer ${tokens.access}`
        }
      } catch (error) {
        console.error('Error parsing auth tokens:', error)
        localStorage.removeItem('auth_tokens')
      }
    }
  }
  return config
})

// Response interceptor to handle auth errors and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // If already refreshing, queue this request
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then(token => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        }).catch(err => {
          return Promise.reject(err)
        })
      }

      originalRequest._retry = true
      isRefreshing = true

      try {
        const authTokens = localStorage.getItem('auth_tokens')
        if (!authTokens) {
          throw new Error('No refresh token available')
        }

        const tokens = JSON.parse(authTokens)
        if (!tokens.refresh) {
          throw new Error('No refresh token available')
        }

        // Attempt to refresh the token
        const response = await fetch(`${process.env['NEXT_PUBLIC_API_BASE'] || 'https://backend.proyecto-opensource.orb.local'}/users/jwt/refresh/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ refresh: tokens.refresh }),
        })

        if (!response.ok) {
          throw new Error('Token refresh failed')
        }

        const data = await response.json()
        
        // Update tokens in localStorage
        const newTokens = {
          access: data.access,
          refresh: data.refresh || tokens.refresh // Use new refresh token if provided
        }
        localStorage.setItem('auth_tokens', JSON.stringify(newTokens))

        // Update the original request with new token
        originalRequest.headers.Authorization = `Bearer ${data.access}`
        
        // Process queued requests
        processQueue(null, data.access)
        
        // Retry the original request
        return api(originalRequest)
      } catch (refreshError) {
        console.error('Token refresh failed:', refreshError)
        
        // Clear auth data and redirect to login
        localStorage.removeItem('auth_tokens')
        localStorage.removeItem('user')
        
        // Process queued requests with error
        processQueue(refreshError as Error, null)
        
        if (typeof window !== 'undefined') {
          window.location.href = '/login'
        }
        
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
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

  getProduct: async (id: string): Promise<ProductDetail> => {
    const response = await api.get(`/api/products/products/${id}/`)
    return response.data
  },

  createProduct: async (productData: ProductCreateData): Promise<ProductDetail> => {
    const response = await api.post('/api/products/products/', productData)
    return response.data
  },

  updateProduct: async (id: string, productData: ProductUpdateData): Promise<ProductDetail> => {
    const response = await api.patch(`/api/products/products/${id}/`, productData)
    return response.data
  },

  deleteProduct: async (id: string): Promise<void> => {
    const response = await api.delete(`/api/products/products/${id}/`)
    return response.data
  },

  // Divisions
  getDivisions: async (params?: ApiParams): Promise<DivisionsResponse> => {
    const response = await api.get('/api/products/divisions/', { params })
    return response.data
  },

  getDivision: async (id: string): Promise<Division> => {
    const response = await api.get(`/api/products/divisions/${id}/`)
    return response.data
  },

  // Categories
  getCategories: async (params?: ApiParams): Promise<CategoriesResponse> => {
    const response = await api.get('/api/products/categories/', { params })
    return response.data
  },

  getCategory: async (id: string) => {
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

  // World entities for advanced product fields
  getIndustries: async (params?: ApiParams) => {
    const response = await api.get('/api/world/industries/', { params })
    return response.data
  },

  getSkills: async (params?: ApiParams) => {
    const response = await api.get('/api/world/skills/', { params })
    return response.data
  },

  getMarketSegments: async (params?: ApiParams) => {
    const response = await api.get('/api/world/market-segments/', { params })
    return response.data
  },

  getFunctions: async (params?: ApiParams) => {
    const response = await api.get('/api/world/functions/', { params })
    return response.data
  },

  getDescriptors: async (params?: ApiParams) => {
    const response = await api.get('/api/world/world-descriptors/', { params })
    return response.data
  },

  getTags: async (params?: ApiParams) => {
    const response = await api.get('/api/world/tags/', { params })
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

// Entities API Types
export interface Person {
  id: string
  first_name: string
  middle_name?: string
  last_name: string
  second_last_name?: string
  full_name: string
  gender?: string
  birthday?: string
  marital_status?: string
  country_of_nationality?: string
  country_name?: string
  id_type?: string
  id_number?: string
  portrait?: string
  primary_contact?: {
    type: 'email' | 'phone'
    value: string
    verified: boolean
  }
  contacts?: ContactDetail[]
  profile?: IndividualProfile
  addresses?: PhysicalAddress[]
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface Organization {
  id: string
  name: string
  legal_name?: string
  org_type?: string
  org_type_name?: string
  industry?: string
  industry_name?: string
  country?: string
  country_name?: string
  id_type?: string
  id_number?: string
  main_address?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ContactDetail {
  id: string
  person?: string
  organization?: string
  email?: string
  phone?: string
  is_primary: boolean
  verified: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface IndividualProfile {
  id: string
  person: string
  academic_degree?: string
  academic_degree_name?: string
  industries: string[]
  skills: string[]
  functions: string[]
  preferred_contact_medium?: string
  allows_marketing: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PhysicalAddress {
  id: string
  person?: string
  organization?: string
  address_line_1: string
  address_line_2?: string
  city: string
  state_province?: string
  postal_code?: string
  country: string
  country_name?: string
  is_primary: boolean
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface PersonCreateData {
  first_name: string
  middle_name?: string
  last_name: string
  second_last_name?: string
  gender?: string
  birthday?: string
  marital_status?: string
  country_of_nationality?: string
  id_type?: string
  id_number?: string
  is_active?: boolean
}

export interface OrganizationCreateData {
  name: string
  legal_name?: string
  org_type?: string
  industry?: string
  country?: string
  id_type?: string
  id_number?: string
  main_address?: string
  is_active?: boolean
}

export interface ContactDetailCreateData {
  person?: string
  organization?: string
  email?: string
  phone?: string
  is_primary?: boolean
  verified?: boolean
  is_active?: boolean
}

export interface PhysicalAddressCreateData {
  person?: string
  organization?: string
  address_line_1: string
  address_line_2?: string
  city: string
  state_province?: string
  postal_code?: string
  country: string
  is_primary?: boolean
  is_active?: boolean
}

// API Response Types
export type PeopleResponse = PaginatedResponse<Person>
export type OrganizationsResponse = PaginatedResponse<Organization>
export type ContactsResponse = PaginatedResponse<ContactDetail>
export type AddressesResponse = PaginatedResponse<PhysicalAddress>

export const entitiesApi = {
  // People CRUD
  getPeople: async (params?: ApiParams): Promise<PeopleResponse> => {
    const response = await api.get('/api/entities/people/', { params })
    return response.data
  },

  getPerson: async (id: string): Promise<Person> => {
    const response = await api.get(`/api/entities/people/${id}/`)
    return response.data
  },

  createPerson: async (personData: PersonCreateData): Promise<Person> => {
    const response = await api.post('/api/entities/people/', personData)
    return response.data
  },

  updatePerson: async (id: string, personData: Partial<PersonCreateData>): Promise<Person> => {
    const response = await api.patch(`/api/entities/people/${id}/`, personData)
    return response.data
  },

  deletePerson: async (id: string): Promise<void> => {
    const response = await api.delete(`/api/entities/people/${id}/`)
    return response.data
  },

  // Organizations CRUD
  getOrganizations: async (params?: ApiParams): Promise<OrganizationsResponse> => {
    const response = await api.get('/api/entities/organizations/', { params })
    return response.data
  },

  getOrganization: async (id: string): Promise<Organization> => {
    const response = await api.get(`/api/entities/organizations/${id}/`)
    return response.data
  },

  createOrganization: async (organizationData: OrganizationCreateData): Promise<Organization> => {
    const response = await api.post('/api/entities/organizations/', organizationData)
    return response.data
  },

  updateOrganization: async (id: string, organizationData: Partial<OrganizationCreateData>): Promise<Organization> => {
    const response = await api.patch(`/api/entities/organizations/${id}/`, organizationData)
    return response.data
  },

  deleteOrganization: async (id: string): Promise<void> => {
    const response = await api.delete(`/api/entities/organizations/${id}/`)
    return response.data
  },

  // Contacts CRUD
  getContacts: async (params?: ApiParams): Promise<ContactsResponse> => {
    const response = await api.get('/api/entities/contacts/', { params })
    return response.data
  },

  getContact: async (id: string): Promise<ContactDetail> => {
    const response = await api.get(`/api/entities/contacts/${id}/`)
    return response.data
  },

  createContact: async (contactData: ContactDetailCreateData): Promise<ContactDetail> => {
    const response = await api.post('/api/entities/contacts/', contactData)
    return response.data
  },

  updateContact: async (id: string, contactData: Partial<ContactDetailCreateData>): Promise<ContactDetail> => {
    const response = await api.patch(`/api/entities/contacts/${id}/`, contactData)
    return response.data
  },

  deleteContact: async (id: string): Promise<void> => {
    const response = await api.delete(`/api/entities/contacts/${id}/`)
    return response.data
  },

  // Addresses CRUD
  getAddresses: async (params?: ApiParams): Promise<AddressesResponse> => {
    const response = await api.get('/api/entities/addresses/', { params })
    return response.data
  },

  getAddress: async (id: string): Promise<PhysicalAddress> => {
    const response = await api.get(`/api/entities/addresses/${id}/`)
    return response.data
  },

  createAddress: async (addressData: PhysicalAddressCreateData): Promise<PhysicalAddress> => {
    const response = await api.post('/api/entities/addresses/', addressData)
    return response.data
  },

  updateAddress: async (id: string, addressData: Partial<PhysicalAddressCreateData>): Promise<PhysicalAddress> => {
    const response = await api.patch(`/api/entities/addresses/${id}/`, addressData)
    return response.data
  },

  deleteAddress: async (id: string): Promise<void> => {
    const response = await api.delete(`/api/entities/addresses/${id}/`)
    return response.data
  },

  // Choices and reference data
  getChoices: async () => {
    const response = await api.get('/api/entities/choices/')
    return response.data
  },

  // Analytics
  getPeopleAnalytics: async () => {
    const response = await api.get('/api/entities/people/analytics/')
    return response.data
  },

  getOrganizationsAnalytics: async () => {
    const response = await api.get('/api/entities/organizations/analytics/')
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
