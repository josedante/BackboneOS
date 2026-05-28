/**
 * Test-only product fixtures (Phase 5).
 * Shapes are not synced with DRF — CRM product UI moved to Django templates.
 */
export interface MockProduct {
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

export interface MockProductCategory {
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

export const mockProducts: MockProduct[] = [
  {
    id: '1',
    name: 'Curso de React Avanzado',
    code: 'REACT-001',
    description: 'Curso completo de React con hooks y context',
    canonical_url: 'https://example.com/react-course',
    category: '1',
    category_name: 'Desarrollo Web',
    category_full_path: 'Tecnología > Desarrollo Web',
    customization_name: 'Personalizable',
    duration: 'P30D',
    base_price: 299.99,
    currency_code: 'PEN',
    price_display: 'PEN 299.99',
    duration_display: '30 días',
    target_audience: 'Desarrolladores',
    modalities_display: 'Online, Presencial',
    has_canonical_url: true,
    skills_count: 5,
    industries_count: 3,
    segments_count: 2,
    included_products_count: 0,
    is_bundle: false,
    is_active: true,
    created_at: '2024-01-15T10:00:00Z',
    updated_at: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    name: 'Consultoría en Transformación Digital',
    code: 'CONS-001',
    description: 'Servicio de consultoría para transformación digital empresarial',
    category: '2',
    category_name: 'Consultoría',
    category_full_path: 'Servicios > Consultoría',
    duration: 'P90D',
    base_price: 5000.00,
    currency_code: 'PEN',
    price_display: 'PEN 5,000.00',
    duration_display: '90 días',
    target_audience: 'Empresas',
    modalities_display: 'Presencial, Híbrido',
    has_canonical_url: false,
    skills_count: 8,
    industries_count: 5,
    segments_count: 3,
    included_products_count: 2,
    is_bundle: true,
    is_active: true,
    created_at: '2024-01-10T09:00:00Z',
    updated_at: '2024-01-20T14:30:00Z',
  },
  {
    id: '3',
    name: 'Producto Inactivo',
    code: 'INACT-001',
    description: 'Este producto está inactivo',
    category: '1',
    category_name: 'Desarrollo Web',
    category_full_path: 'Tecnología > Desarrollo Web',
    duration: 'P7D',
    base_price: 99.99,
    currency_code: 'PEN',
    price_display: 'PEN 99.99',
    duration_display: '7 días',
    target_audience: 'Estudiantes',
    modalities_display: 'Online',
    has_canonical_url: false,
    skills_count: 2,
    industries_count: 1,
    segments_count: 1,
    included_products_count: 0,
    is_bundle: false,
    is_active: false,
    created_at: '2024-01-05T08:00:00Z',
    updated_at: '2024-01-05T08:00:00Z',
  },
]

export const mockCategories: MockProductCategory[] = [
  {
    id: 1,
    name: 'Desarrollo Web',
    description: 'Cursos de desarrollo web',
    division: 1,
    parent: null,
    level: 0,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    name: 'Consultoría',
    description: 'Servicios de consultoría',
    division: 2,
    parent: null,
    level: 0,
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
]

export const mockApiResponses = {
  products: {
    success: {
      data: mockProducts,
      count: mockProducts.length,
      next: null,
      previous: null,
    },
    empty: {
      data: [],
      count: 0,
      next: null,
      previous: null,
    },
    error: new Error('Failed to fetch products'),
  },
  categories: {
    success: {
      data: mockCategories,
      count: mockCategories.length,
      next: null,
      previous: null,
    },
    error: new Error('Failed to fetch categories'),
  },
  deleteProduct: {
    success: { message: 'Product deleted successfully' },
    error: new Error('Failed to delete product'),
  },
  createProduct: {
    success: mockProducts[0],
    error: new Error('Failed to create product'),
  },
  updateProduct: {
    success: { ...mockProducts[0], name: 'Updated Product Name' },
    error: new Error('Failed to update product'),
  },
}
