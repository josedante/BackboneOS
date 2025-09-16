'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Save, ChevronDown, ChevronRight, Building2, Edit, Trash2, Mail, Phone, MapPin, Users, Briefcase } from 'lucide-react'
import { entitiesApi, type Organization, type OrganizationCreateData, type ContactDetail, type PhysicalAddress, getResults } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { toast } from 'sonner'

export default function OrganizationDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const organizationId = params.id as string

  // Fetch organization details
  const { data: organization, isLoading, error } = useQuery({
    queryKey: ['organization', organizationId],
    queryFn: () => entitiesApi.getOrganization(organizationId),
    enabled: !!organizationId,
  })

  // Form state
  const [formData, setFormData] = useState<OrganizationCreateData>({
    name: '',
    legal_name: '',
    org_type: '',
    industry: '',
    country: '',
    id_type: '',
    id_number: '',
    main_address: '',
    is_active: true,
  })

  // Collapsible sections state
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    contact: false,
    address: false,
    details: false,
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  // Initialize form data when organization loads
  useEffect(() => {
    if (organization) {
      setFormData({
        name: organization.name || '',
        legal_name: organization.legal_name || '',
        org_type: organization.org_type || '',
        industry: organization.industry || '',
        country: organization.country || '',
        id_type: organization.id_type || '',
        id_number: organization.id_number || '',
        main_address: organization.main_address || '',
        is_active: organization.is_active ?? true,
      })
    }
  }, [organization])

  // Update mutation
  const updateOrganizationMutation = useMutation({
    mutationFn: (data: OrganizationCreateData) => entitiesApi.updateOrganization(organizationId, data),
    onSuccess: () => {
      toast.success('Organización actualizada exitosamente')
      queryClient.invalidateQueries({ queryKey: ['organization', organizationId] })
    },
    onError: (error) => {
      toast.error('Error al actualizar la organización')
      console.error('Update error:', error)
    },
  })

  // Delete mutation
  const deleteOrganizationMutation = useMutation({
    mutationFn: () => entitiesApi.deleteOrganization(organizationId),
    onSuccess: () => {
      toast.success('Organización eliminada exitosamente')
      router.push('/entities')
    },
    onError: (error) => {
      toast.error('Error al eliminar la organización')
      console.error('Delete error:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updateOrganizationMutation.mutate(formData)
  }

  const handleDelete = () => {
    if (confirm('¿Está seguro de que desea eliminar esta organización?')) {
      deleteOrganizationMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Cargando organización...</div>
        </div>
      </DashboardLayout>
    )
  }

  if (error || !organization) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">Error al cargar la organización</div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Button
              variant="outline"
              size="icon"
              onClick={() => router.push('/entities')}
            >
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <div>
              <h1 className="text-2xl font-bold">{organization.name}</h1>
              <p className="text-muted-foreground">
                {organization.legal_name || 'Sin nombre legal'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant={organization.is_active ? 'default' : 'secondary'}>
              {organization.is_active ? 'Activo' : 'Inactivo'}
            </Badge>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDelete}
              disabled={deleteOrganizationMutation.isPending}
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
                  <Building2 className="h-5 w-5 mr-2" />
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
                    <label className="block text-sm font-medium mb-1">Nombre Legal</label>
                    <Input
                      value={formData.legal_name}
                      onChange={(e) => setFormData({ ...formData, legal_name: e.target.value })}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Tipo de Organización</label>
                    <Input
                      value={formData.org_type}
                      onChange={(e) => setFormData({ ...formData, org_type: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Industria</label>
                    <Input
                      value={formData.industry}
                      onChange={(e) => setFormData({ ...formData, industry: e.target.value })}
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">País</label>
                    <Input
                      value={formData.country}
                      onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Número de Identificación</label>
                    <Input
                      value={formData.id_number}
                      onChange={(e) => setFormData({ ...formData, id_number: e.target.value })}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Dirección Principal</label>
                  <Input
                    value={formData.main_address}
                    onChange={(e) => setFormData({ ...formData, main_address: e.target.value })}
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
                    Organización activa
                  </label>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Contact Information */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('contact')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center">
                  <Mail className="h-5 w-5 mr-2" />
                  Información de Contacto
                </CardTitle>
                {expandedSections.contact ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.contact && (
              <CardContent className="space-y-4">
                <div className="text-center py-8 text-muted-foreground">
                  <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No hay información de contacto disponible</p>
                  <Button variant="outline" className="mt-4">
                    Agregar Contacto
                  </Button>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Address Information */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('address')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center">
                  <MapPin className="h-5 w-5 mr-2" />
                  Direcciones
                </CardTitle>
                {expandedSections.address ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.address && (
              <CardContent className="space-y-4">
                <div className="text-center py-8 text-muted-foreground">
                  <MapPin className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No hay direcciones registradas</p>
                  <Button variant="outline" className="mt-4">
                    Agregar Dirección
                  </Button>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Organization Details */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('details')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center">
                  <Briefcase className="h-5 w-5 mr-2" />
                  Detalles de la Organización
                </CardTitle>
                {expandedSections.details ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.details && (
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Tipo de Organización</label>
                    <div className="text-sm text-muted-foreground">
                      {organization.org_type_name || 'No especificado'}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Industria</label>
                    <div className="text-sm text-muted-foreground">
                      {organization.industry_name || 'No especificado'}
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">País</label>
                    <div className="text-sm text-muted-foreground">
                      {organization.country_name || 'No especificado'}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">Número de Identificación</label>
                    <div className="text-sm text-muted-foreground">
                      {organization.id_number || 'No especificado'}
                    </div>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-1">Dirección Principal</label>
                  <div className="text-sm text-muted-foreground">
                    {organization.main_address || 'No especificada'}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 mt-6">
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-blue-600">0</div>
                    <div className="text-sm text-muted-foreground">Empleados</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-green-600">0</div>
                    <div className="text-sm text-muted-foreground">Contactos</div>
                  </div>
                  <div className="text-center p-3 bg-gray-50 rounded-lg">
                    <div className="text-2xl font-bold text-purple-600">0</div>
                    <div className="text-sm text-muted-foreground">Proyectos</div>
                  </div>
                </div>
              </CardContent>
            )}
          </Card>

          {/* Form Actions */}
          <div className="flex justify-end gap-2 pt-4">
            <Button type="submit" disabled={updateOrganizationMutation.isPending}>
              <Save className="h-4 w-4 mr-2" />
              {updateOrganizationMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  )
}
