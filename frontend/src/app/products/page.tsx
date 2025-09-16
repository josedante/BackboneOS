'use client'

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Filter, Edit, Trash2, Eye, Package } from 'lucide-react'
import { productsApi, type Product, type ProductCreateData, type ProductsResponse, type CategoriesResponse, getResults } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Pagination, PaginationInfo } from '@/components/ui/pagination'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { toast } from 'sonner'

// Mock data for testing
const mockProducts: Product[] = [
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
]

export default function ProductsPage() {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const queryClient = useQueryClient()

  // Calculate offset from current page and page size
  const offset = (currentPage - 1) * pageSize

  // Fetch products
  const { data: productsResponse, isLoading, error } = useQuery<ProductsResponse>({
    queryKey: ['products', { search: searchTerm, category: selectedCategory, offset, limit: pageSize }],
    queryFn: () => productsApi.getProducts({ 
      ...(searchTerm && { search: searchTerm }),
      ...(selectedCategory !== 'all' && { category: selectedCategory }),
      offset,
      limit: pageSize,
    }),
  })

  const products = getResults(productsResponse)
  const totalItems = productsResponse?.count || 0
  const totalPages = Math.ceil(totalItems / pageSize)

  // Debug pagination response (remove in production)
  if (productsResponse) {
    console.log('Pagination Response:', {
      count: productsResponse.count,
      next: productsResponse.next,
      previous: productsResponse.previous,
      resultsLength: productsResponse.results?.length,
      currentPage,
      pageSize,
      offset
    })
  }

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, selectedCategory])

  // Fetch categories for filter
  const { data: categoriesResponse } = useQuery<CategoriesResponse>({
    queryKey: ['categories'],
    queryFn: () => productsApi.getCategories(),
  })

  const categories = getResults(categoriesResponse)

  // Delete product mutation
  const deleteProductMutation = useMutation({
    mutationFn: (id: string) => productsApi.deleteProduct(parseInt(id)),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] })
      toast.success('Producto eliminado exitosamente')
    },
    onError: (error) => {
      toast.error('Error al eliminar el producto')
      console.error('Delete error:', error)
    },
  })

  const handleDeleteProduct = (product: Product) => {
    if (confirm(`¿Estás seguro de que quieres eliminar "${product.name}"?`)) {
      deleteProductMutation.mutate(product.id)
    }
  }

  const handleEditProduct = (product: Product) => {
    setEditingProduct(product)
    setIsCreateDialogOpen(true)
  }

  // Products are already filtered on the server, so we use them directly
  const filteredProducts = products

  if (error) {
    return (
      <DashboardLayout title="Products">
        <div className="space-y-6">
          <Card>
            <CardContent className="p-6">
              <div className="text-center text-red-600">
                <p>Error al cargar los productos: {error.message}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout title="Products">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Gestión de Productos</h1>
            <p className="text-gray-600">
              Administra tu catálogo de productos y servicios
            </p>
          </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button onClick={() => setEditingProduct(null)}>
              <Plus className="mr-2 h-4 w-4" />
              Nuevo Producto
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>
                {editingProduct ? 'Editar Producto' : 'Crear Nuevo Producto'}
              </DialogTitle>
              <DialogDescription>
                {editingProduct 
                  ? 'Modifica la información del producto seleccionado'
                  : 'Completa la información para crear un nuevo producto'
                }
              </DialogDescription>
            </DialogHeader>
            <ProductForm 
              product={editingProduct}
              onSuccess={() => {
                setIsCreateDialogOpen(false)
                setEditingProduct(null)
                queryClient.invalidateQueries({ queryKey: ['products'] })
              }}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
                <Input
                  placeholder="Buscar productos..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={selectedCategory} onValueChange={(value: string) => setSelectedCategory(value)}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Categoría" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Todas las categorías</SelectItem>
                {categories.map((category: any) => (
                  <SelectItem key={category.id} value={category.id.toString()}>
                    {category.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Products Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Package className="h-5 w-5" />
            Productos ({filteredProducts.length})
          </CardTitle>
          <CardDescription>
            Lista de todos los productos en el catálogo
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <p className="mt-2 text-muted-foreground">Cargando productos...</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Producto</TableHead>
                  <TableHead>Código</TableHead>
                  <TableHead>Categoría</TableHead>
                  <TableHead>Precio</TableHead>
                  <TableHead>Duración</TableHead>
                  <TableHead>Estado</TableHead>
                  <TableHead>Acciones</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredProducts.map((product: Product) => (
                  <TableRow key={product.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{product.name}</div>
                        <div className="text-sm text-muted-foreground line-clamp-2">
                          {product.description}
                        </div>
                        {product.is_bundle && (
                          <Badge className="mt-1">
                            Bundle ({product.included_products_count} productos)
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <code className="text-sm bg-muted px-2 py-1 rounded">
                        {product.code}
                      </code>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {product.category_name || 'Sin categoría'}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{product.price_display}</div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">{product.duration_display || 'No especificada'}</div>
                    </TableCell>
                    <TableCell>
                      <Badge>
                        {product.is_active ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button
                          onClick={() => handleEditProduct(product)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          onClick={() => handleDeleteProduct(product)}
                          disabled={deleteProductMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}

          {/* Pagination Controls */}
          {!isLoading && products.length > 0 && (
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 mt-6">
              <PaginationInfo
                currentPage={currentPage}
                totalPages={totalPages}
                totalItems={totalItems}
                itemsPerPage={pageSize}
              />
              
              <div className="flex items-center gap-4">
                {/* Page Size Selector */}
                <div className="flex items-center gap-2">
                  <label className="text-sm text-muted-foreground">Mostrar:</label>
                  <Select value={pageSize.toString()} onValueChange={(value: string) => {
                    setPageSize(parseInt(value))
                    setCurrentPage(1)
                  }}>
                    <SelectTrigger className="w-20">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="10">10</SelectItem>
                      <SelectItem value="20">20</SelectItem>
                      <SelectItem value="50">50</SelectItem>
                      <SelectItem value="100">100</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Pagination */}
                <Pagination
                  currentPage={currentPage}
                  totalPages={totalPages}
                  onPageChange={setCurrentPage}
                />
              </div>
            </div>
          )}
          
          {!isLoading && filteredProducts.length === 0 && (
            <div className="text-center py-8">
              <Package className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
              <h3 className="text-lg font-medium mb-2">No se encontraron productos</h3>
              <p className="text-muted-foreground mb-4">
                {searchTerm || selectedCategory !== 'all' 
                  ? 'Intenta ajustar los filtros de búsqueda'
                  : 'Comienza creando tu primer producto'
                }
              </p>
              {(!searchTerm && selectedCategory === 'all') && (
                <Button onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Crear Producto
                </Button>
              )}
            </div>
          )}
        </CardContent>
      </Card>
      </div>
    </DashboardLayout>
  )
}

// Product Form Component
interface ProductFormProps {
  product?: Product | null
  onSuccess: () => void
}

function ProductForm({ product, onSuccess }: ProductFormProps) {
  const [formData, setFormData] = useState<ProductCreateData>({
    name: product?.name || '',
    code: product?.code || '',
    description: product?.description || '',
    canonical_url: product?.canonical_url || '',
    base_price: product?.base_price,
    currency_code: product?.currency_code || 'PEN',
    is_active: product?.is_active ?? true,
  })

  const createProductMutation = useMutation({
    mutationFn: (data: ProductCreateData) => 
      product 
        ? productsApi.updateProduct(parseInt(product.id), data)
        : productsApi.createProduct(data),
    onSuccess: () => {
      toast.success(product ? 'Producto actualizado exitosamente' : 'Producto creado exitosamente')
      onSuccess()
    },
    onError: (error) => {
      toast.error(product ? 'Error al actualizar el producto' : 'Error al crear el producto')
      console.error('Form error:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createProductMutation.mutate(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Nombre *</label>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Código *</label>
          <Input
            value={formData.code}
            onChange={(e) => setFormData({ ...formData, code: e.target.value })}
            required
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Descripción</label>
        <textarea
          className="w-full p-2 border rounded-md"
          rows={3}
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">URL Canónica</label>
        <Input
          type="url"
          value={formData.canonical_url}
          onChange={(e) => setFormData({ ...formData, canonical_url: e.target.value })}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Precio Base</label>
          <Input
            type="number"
            step="0.01"
            value={formData.base_price || ''}
            onChange={(e) => setFormData({ ...formData, base_price: parseFloat(e.target.value) || undefined })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Moneda</label>
          <Select value={formData.currency_code || 'PEN'} onValueChange={(value: string) => setFormData({ ...formData, currency_code: value })}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="PEN">PEN (Soles)</SelectItem>
              <SelectItem value="USD">USD (Dólares)</SelectItem>
              <SelectItem value="EUR">EUR (Euros)</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        <input
          type="checkbox"
          id="is_active"
          checked={formData.is_active}
          onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
          className="rounded"
        />
        <label htmlFor="is_active" className="text-sm font-medium">
          Producto activo
        </label>
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={onSuccess}>
          Cancelar
        </Button>
        <Button type="submit" disabled={createProductMutation.isPending}>
          {createProductMutation.isPending 
            ? 'Guardando...' 
            : product ? 'Actualizar' : 'Crear'
          }
        </Button>
      </div>
    </form>
  )
}
