'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Save, ChevronDown, ChevronRight, Package, Edit, Trash2 } from 'lucide-react'
import { productsApi, type Product, type ProductCreateData, type CategoriesResponse, type Industry, type Skill, type MarketSegment, type FunctionOrResponsibility, type WorldDescriptor, type Tag, getResults } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { toast } from 'sonner'

export default function ProductDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const productId = params['id'] as string

  // Fetch product details
  const { data: product, isLoading, error } = useQuery({
    queryKey: ['product', productId],
    queryFn: () => productsApi.getProduct(productId),
    enabled: !!productId,
  })

  // Fetch all the data needed for the form
  const { data: categoriesResponse } = useQuery<CategoriesResponse>({
    queryKey: ['categories'],
    queryFn: () => productsApi.getCategories(),
  })

  const { data: modalitiesResponse } = useQuery({
    queryKey: ['modalities'],
    queryFn: () => productsApi.getModalities(),
  })

  const { data: customizationsResponse } = useQuery({
    queryKey: ['customizations'],
    queryFn: () => productsApi.getCustomizations(),
  })

  const { data: industriesResponse } = useQuery({
    queryKey: ['industries'],
    queryFn: () => productsApi.getIndustries(),
  })

  const { data: skillsResponse } = useQuery({
    queryKey: ['skills'],
    queryFn: () => productsApi.getSkills(),
  })

  const { data: marketSegmentsResponse } = useQuery({
    queryKey: ['market-segments'],
    queryFn: () => productsApi.getMarketSegments(),
  })

  const { data: functionsResponse } = useQuery({
    queryKey: ['functions'],
    queryFn: () => productsApi.getFunctions(),
  })

  const { data: descriptorsResponse } = useQuery({
    queryKey: ['descriptors'],
    queryFn: () => productsApi.getDescriptors(),
  })

  const { data: tagsResponse } = useQuery({
    queryKey: ['tags'],
    queryFn: () => productsApi.getTags(),
  })

  const categories = getResults(categoriesResponse)
  const modalities = getResults(modalitiesResponse)
  const customizations = getResults(customizationsResponse)
  const industries = getResults(industriesResponse)
  const skills = getResults(skillsResponse)
  const marketSegments = getResults(marketSegmentsResponse)
  const functions = getResults(functionsResponse)
  const descriptors = getResults(descriptorsResponse)
  const tags = getResults(tagsResponse)

  // Form state
  const [formData, setFormData] = useState<ProductCreateData>({
    name: '',
    code: '',
    description: '',
    canonical_url: '',
    base_price: undefined,
    currency_code: 'PEN',
    is_active: true,
    modalities_ids: [],
    target_segments_ids: [],
    related_industries_ids: [],
    related_functions_ids: [],
    related_skills_ids: [],
    descriptors_ids: [],
    tags_ids: [],
    included_products_ids: [],
  })

  // Collapsible sections state
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    pricing: true,
    classification: false,
    market: false,
    skills: false,
    tags: false,
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  // Initialize form data when product loads
  useEffect(() => {
    if (product) {
      setFormData({
        name: product.name || '',
        code: product.code || '',
        description: product.description || '',
        canonical_url: product.canonical_url || '',
        base_price: product.base_price,
        currency_code: product.currency_code || 'PEN',
        is_active: product.is_active ?? true,
        category_id: product.category ? product.category.id.toString() : undefined,
        modalities_ids: product.modalities?.map((m: any) => m.id) || [],
        customization_id: product.customization ? product.customization.id.toString() : undefined,
        duration: product.duration,
        target_segments_ids: product.target_segments?.map((s: any) => s.id) || [],
        related_industries_ids: product.related_industries?.map((i: any) => i.id) || [],
        related_functions_ids: product.related_functions?.map((f: any) => f.id) || [],
        related_skills_ids: product.related_skills?.map((s: any) => s.id) || [],
        descriptors_ids: product.descriptors?.map((d: any) => d.id) || [],
        tags_ids: product.tags?.map((t: any) => t.slug) || [],
        included_products_ids: product.included_products?.map((p: any) => p.id) || [],
      })
    }
  }, [product])

  // Update mutation
  const updateProductMutation = useMutation({
    mutationFn: (data: ProductCreateData) => productsApi.updateProduct(productId, data),
    onSuccess: () => {
      toast.success('Producto actualizado exitosamente')
      queryClient.invalidateQueries({ queryKey: ['product', productId] })
    },
    onError: (error) => {
      toast.error('Error al actualizar el producto')
      console.error('Update error:', error)
    },
  })

  // Delete mutation
  const deleteProductMutation = useMutation({
    mutationFn: () => productsApi.deleteProduct(productId),
    onSuccess: () => {
      toast.success('Producto eliminado exitosamente')
      router.push('/products')
    },
    onError: (error) => {
      toast.error('Error al eliminar el producto')
      console.error('Delete error:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateProductMutation.mutate(formData)
  }

  const handleDelete = () => {
    if (confirm('¿Está seguro de que desea eliminar este producto?')) {
      deleteProductMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <DashboardLayout title="Producto">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Cargando producto...</div>
        </div>
      </DashboardLayout>
    )
  }

  if (error || !product) {
    return (
      <DashboardLayout title="Producto">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">Error al cargar el producto</div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout title="Producto">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              size="icon"
              onClick={() => router.push('/products')}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold">{product.name}</h1>
              <p className="text-muted-foreground">Código: {product.code}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant={product.is_active ? 'default' : 'secondary'}>
              {product.is_active ? 'Activo' : 'Inactivo'}
            </Badge>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDelete}
              disabled={deleteProductMutation.isPending}
            >
              <Trash2 className="h-4 w-4 mr-2" />
              Eliminar
            </Button>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('basic')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center">
                  <Package className="h-5 w-5 mr-2" />
                  Información Básica
                </CardTitle>
                {expandedSections.basic ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.basic && (
              <CardContent className="space-y-4">
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
              </CardContent>
            )}
          </Card>

          {/* Pricing & Duration */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('pricing')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Precio y Duración</CardTitle>
                {expandedSections.pricing ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.pricing && (
              <CardContent className="space-y-4">
                <div className="grid grid-cols-3 gap-4">
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
                  <div>
                    <label className="block text-sm font-medium mb-1">Duración (días)</label>
                    <Input
                      type="number"
                      value={formData.duration ? parseInt(formData.duration) : ''}
                      onChange={(e) => {
                        const newData = { ...formData }
                        if (e.target.value) {
                          newData.duration = `${e.target.value} days`
                        } else {
                          delete newData.duration
                        }
                        setFormData(newData)
                      }}
                    />
                  </div>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Classification */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('classification')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Clasificación</CardTitle>
                {expandedSections.classification ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.classification && (
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Categoría</label>
                    <Select value={formData.category_id || ''} onValueChange={(value: string) => setFormData({ ...formData, category_id: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar categoría" />
                      </SelectTrigger>
                      <SelectContent>
                        {categories.filter((category: any) => category.id).map((category: any) => (
                          <SelectItem key={`category-${category.id}`} value={category.id}>
                            {category.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Personalización</label>
                    <Select value={formData.customization_id || ''} onValueChange={(value: string) => setFormData({ ...formData, customization_id: value })}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seleccionar personalización" />
                      </SelectTrigger>
                      <SelectContent>
                        {customizations.filter((customization: any) => customization.id).map((customization: any) => (
                          <SelectItem key={`customization-${customization.id}`} value={customization.id}>
                            {customization.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Modalidades</label>
                  <div className="grid grid-cols-3 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {modalities.filter((modality: any) => modality.id).map((modality: any) => (
                      <label key={`modality-${modality.id}`} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.modalities_ids?.includes(modality.id) || false}
                          onChange={(e) => {
                            const currentIds = formData.modalities_ids || []
                            if (e.target.checked) {
                              setFormData({ ...formData, modalities_ids: [...currentIds, modality.id] })
                            } else {
                              setFormData({ ...formData, modalities_ids: currentIds.filter(id => id !== modality.id) })
                            }
                          }}
                          className="rounded"
                        />
                        <span className="text-sm">{modality.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Target Market */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('market')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Mercado Objetivo</CardTitle>
                {expandedSections.market ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.market && (
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Segmentos de Mercado</label>
                  <div className="grid grid-cols-3 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {marketSegments.filter((segment: any) => segment.id).map((segment: any) => (
                      <label key={`segment-${segment.id}`} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.target_segments_ids?.includes(segment.id) || false}
                          onChange={(e) => {
                            const currentIds = formData.target_segments_ids || []
                            if (e.target.checked) {
                              setFormData({ ...formData, target_segments_ids: [...currentIds, segment.id] })
                            } else {
                              setFormData({ ...formData, target_segments_ids: currentIds.filter(id => id !== segment.id) })
                            }
                          }}
                          className="rounded"
                        />
                        <span className="text-sm">{segment.name}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Industrias Relacionadas</label>
                  <div className="grid grid-cols-3 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {industries.filter((industry: any) => industry.id).map((industry: any) => (
                      <label key={`industry-${industry.id}`} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.related_industries_ids?.includes(industry.id) || false}
                          onChange={(e) => {
                            const currentIds = formData.related_industries_ids || []
                            if (e.target.checked) {
                              setFormData({ ...formData, related_industries_ids: [...currentIds, industry.id] })
                            } else {
                              setFormData({ ...formData, related_industries_ids: currentIds.filter(id => id !== industry.id) })
                            }
                          }}
                          className="rounded"
                        />
                        <span className="text-sm">{industry.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Skills & Functions */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('skills')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Competencias y Funciones</CardTitle>
                {expandedSections.skills ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.skills && (
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Habilidades Relacionadas</label>
                  <div className="grid grid-cols-3 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {skills.filter((skill: any) => skill.id).map((skill: any) => (
                      <label key={`skill-${skill.id}`} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.related_skills_ids?.includes(skill.id) || false}
                          onChange={(e) => {
                            const currentIds = formData.related_skills_ids || []
                            if (e.target.checked) {
                              setFormData({ ...formData, related_skills_ids: [...currentIds, skill.id] })
                            } else {
                              setFormData({ ...formData, related_skills_ids: currentIds.filter(id => id !== skill.id) })
                            }
                          }}
                          className="rounded"
                        />
                        <span className="text-sm">{skill.name}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Funciones Relacionadas</label>
                  <div className="grid grid-cols-3 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {functions.filter((func: any) => func.id).map((func: any) => (
                      <label key={`function-${func.id}`} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.related_functions_ids?.includes(func.id) || false}
                          onChange={(e) => {
                            const currentIds = formData.related_functions_ids || []
                            if (e.target.checked) {
                              setFormData({ ...formData, related_functions_ids: [...currentIds, func.id] })
                            } else {
                              setFormData({ ...formData, related_functions_ids: currentIds.filter(id => id !== func.id) })
                            }
                          }}
                          className="rounded"
                        />
                        <span className="text-sm">{func.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Tags & Descriptors */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('tags')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Etiquetas y Descriptores</CardTitle>
                {expandedSections.tags ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.tags && (
              <CardContent className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">Etiquetas</label>
                  <div className="grid grid-cols-3 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {tags.filter((tag: any) => tag.slug).map((tag: any) => (
                      <label key={`tag-${tag.slug}`} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.tags_ids?.includes(tag.slug) || false}
                          onChange={(e) => {
                            const currentIds = formData.tags_ids || []
                            if (e.target.checked) {
                              setFormData({ ...formData, tags_ids: [...currentIds, tag.slug] })
                            } else {
                              setFormData({ ...formData, tags_ids: currentIds.filter(id => id !== tag.slug) })
                            }
                          }}
                          className="rounded"
                        />
                        <span className="text-sm">{tag.name}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Descriptores Semánticos</label>
                  <div className="grid grid-cols-3 gap-2 max-h-32 overflow-y-auto border rounded-md p-2">
                    {descriptors.filter((descriptor: any) => descriptor.id).map((descriptor: any) => (
                      <label key={`descriptor-${descriptor.id}`} className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={formData.descriptors_ids?.includes(descriptor.id) || false}
                          onChange={(e) => {
                            const currentIds = formData.descriptors_ids || []
                            if (e.target.checked) {
                              setFormData({ ...formData, descriptors_ids: [...currentIds, descriptor.id] })
                            } else {
                              setFormData({ ...formData, descriptors_ids: currentIds.filter(id => id !== descriptor.id) })
                            }
                          }}
                          className="rounded"
                        />
                        <span className="text-sm">{descriptor.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Form Actions */}
          <div className="flex justify-end gap-2 pt-4">
            <Button type="submit" disabled={updateProductMutation.isPending}>
              <Save className="h-4 w-4 mr-2" />
              {updateProductMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  )
}
