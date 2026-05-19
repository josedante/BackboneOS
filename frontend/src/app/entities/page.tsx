'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Search, Filter, Edit, Trash2, Eye, Users, Building2, User, ChevronDown, ChevronRight } from 'lucide-react'
import { entitiesApi, type Person, type Organization, type PersonCreateData, type OrganizationCreateData, type PeopleResponse, type OrganizationsResponse, getResults } from '@/lib/api'
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

type TabType = 'people' | 'organizations'

export default function EntitiesPage() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<TabType>('people')
  const [searchTerm, setSearchTerm] = useState('')
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingEntity, setEditingEntity] = useState<Person | Organization | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)
  const queryClient = useQueryClient()

  // Calculate offset from current page and page size
  const offset = (currentPage - 1) * pageSize

  // Fetch people
  const { data: peopleResponse, isLoading: peopleLoading, error: peopleError } = useQuery<PeopleResponse>({
    queryKey: ['people', { search: searchTerm, offset, limit: pageSize }],
    queryFn: () => entitiesApi.getPeople({ 
      ...(searchTerm && { search: searchTerm }),
      offset,
      limit: pageSize,
    }),
    enabled: activeTab === 'people',
  })

  // Fetch organizations
  const { data: organizationsResponse, isLoading: organizationsLoading, error: organizationsError } = useQuery<OrganizationsResponse>({
    queryKey: ['organizations', { search: searchTerm, offset, limit: pageSize }],
    queryFn: () => entitiesApi.getOrganizations({ 
      ...(searchTerm && { search: searchTerm }),
      offset,
      limit: pageSize,
    }),
    enabled: activeTab === 'organizations',
  })

  const people = getResults(peopleResponse)
  const organizations = getResults(organizationsResponse)
  const totalPeople = peopleResponse?.count ?? 0
  const totalOrganizations = organizationsResponse?.count ?? 0
  const totalItems = activeTab === 'people' ? totalPeople : totalOrganizations
  const totalPages = Math.ceil(totalItems / pageSize)
  const isLoading = activeTab === 'people' ? peopleLoading : organizationsLoading
  const error = activeTab === 'people' ? peopleError : organizationsError

  // Reset to first page when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, activeTab])

  // Delete mutations
  const deletePersonMutation = useMutation({
    mutationFn: (id: string) => entitiesApi.deletePerson(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['people'] })
      toast.success('Persona eliminada exitosamente')
    },
    onError: (error) => {
      toast.error('Error al eliminar la persona')
      console.error('Delete error:', error)
    },
  })

  const deleteOrganizationMutation = useMutation({
    mutationFn: (id: string) => entitiesApi.deleteOrganization(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] })
      toast.success('Organización eliminada exitosamente')
    },
    onError: (error) => {
      toast.error('Error al eliminar la organización')
      console.error('Delete error:', error)
    },
  })

  const handleDeleteEntity = (entity: Person | Organization) => {
    const entityType = 'id' in entity && 'first_name' in entity ? 'persona' : 'organización'
    const entityName = 'first_name' in entity ? `${entity.first_name} ${entity.last_name}` : entity.name
    
    if (confirm(`¿Estás seguro de que quieres eliminar la ${entityType} "${entityName}"?`)) {
      if ('first_name' in entity) {
        deletePersonMutation.mutate(entity.id)
      } else {
        deleteOrganizationMutation.mutate(entity.id)
      }
    }
  }

  const handleEditEntity = (entity: Person | Organization) => {
    setEditingEntity(entity)
    setIsCreateDialogOpen(true)
  }

  const handleViewEntity = (entity: Person | Organization) => {
    const entityType = 'id' in entity && 'first_name' in entity ? 'people' : 'organizations'
    router.push(`/entities/${entityType}/${entity.id}`)
  }

  if (error) {
    return (
      <DashboardLayout title="Entities">
        <div className="space-y-6">
          <Card>
            <CardContent className="p-6">
              <div className="text-center text-red-600">
                <p>Error al cargar las entidades: {error.message}</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout title="Entities">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Gestión de Entidades</h1>
            <p className="text-gray-600">
              Administra personas y organizaciones en tu CRM
            </p>
          </div>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={() => setEditingEntity(null)}>
                <Plus className="mr-2 h-4 w-4" />
                {activeTab === 'people' ? 'Nueva Persona' : 'Nueva Organización'}
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>
                  {editingEntity 
                    ? `Editar ${activeTab === 'people' ? 'Persona' : 'Organización'}`
                    : `Crear Nueva ${activeTab === 'people' ? 'Persona' : 'Organización'}`
                  }
                </DialogTitle>
                <DialogDescription>
                  {editingEntity 
                    ? `Modifica la información de la ${activeTab === 'people' ? 'persona' : 'organización'} seleccionada`
                    : `Completa la información para crear una nueva ${activeTab === 'people' ? 'persona' : 'organización'}`
                  }
                </DialogDescription>
              </DialogHeader>
              {activeTab === 'people' ? (
                <PersonForm 
                  person={editingEntity as Person}
                  onSuccess={() => {
                    setIsCreateDialogOpen(false)
                    setEditingEntity(null)
                    queryClient.invalidateQueries({ queryKey: ['people'] })
                  }}
                />
              ) : (
                <OrganizationForm 
                  organization={editingEntity as Organization}
                  onSuccess={() => {
                    setIsCreateDialogOpen(false)
                    setEditingEntity(null)
                    queryClient.invalidateQueries({ queryKey: ['organizations'] })
                  }}
                />
              )}
            </DialogContent>
          </Dialog>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg w-fit">
          <button
            onClick={() => setActiveTab('people')}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'people'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <User className="mr-2 h-4 w-4" />
            Personas ({totalPeople})
          </button>
          <button
            onClick={() => setActiveTab('organizations')}
            className={`flex items-center px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'organizations'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            <Building2 className="mr-2 h-4 w-4" />
            Organizaciones ({totalOrganizations})
          </button>
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
                    placeholder={`Buscar ${activeTab === 'people' ? 'personas' : 'organizaciones'}...`}
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="pl-10"
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Entities Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {activeTab === 'people' ? <Users className="h-5 w-5" /> : <Building2 className="h-5 w-5" />}
              {activeTab === 'people' ? 'Personas' : 'Organizaciones'} ({totalItems})
            </CardTitle>
            <CardDescription>
              Lista de todas las {activeTab === 'people' ? 'personas' : 'organizaciones'} en el sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="mt-2 text-muted-foreground">Cargando {activeTab === 'people' ? 'personas' : 'organizaciones'}...</p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    {activeTab === 'people' ? (
                      <>
                        <TableHead>Nombre</TableHead>
                        <TableHead>Contacto</TableHead>
                        <TableHead>País</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead>Acciones</TableHead>
                      </>
                    ) : (
                      <>
                        <TableHead>Organización</TableHead>
                        <TableHead>Tipo</TableHead>
                        <TableHead>Industria</TableHead>
                        <TableHead>País</TableHead>
                        <TableHead>Estado</TableHead>
                        <TableHead>Acciones</TableHead>
                      </>
                    )}
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {activeTab === 'people' ? (
                    people.map((person: Person) => (
                      <TableRow key={person.id}>
                        <TableCell>
                          <div>
                            <div 
                              className="font-medium cursor-pointer hover:text-blue-600 hover:underline"
                              onClick={() => handleViewEntity(person)}
                            >
                              {person.full_name}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {person.id_number && `ID: ${person.id_number}`}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          {person.primary_contact ? (
                            <div className="text-sm">
                              <div className="font-medium">{person.primary_contact.value}</div>
                              <Badge variant={person.primary_contact.verified ? 'default' : 'secondary'} className="text-xs">
                                {person.primary_contact.verified ? 'Verificado' : 'No verificado'}
                              </Badge>
                            </div>
                          ) : (
                            <span className="text-muted-foreground text-sm">Sin contacto</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">{person.country_name || 'No especificado'}</div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={person.is_active ? 'default' : 'secondary'}>
                            {person.is_active ? 'Activo' : 'Inactivo'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleViewEntity(person)}
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              Ver
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditEntity(person)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteEntity(person)}
                              disabled={deletePersonMutation.isPending}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    organizations.map((organization: Organization) => (
                      <TableRow key={organization.id}>
                        <TableCell>
                          <div>
                            <div 
                              className="font-medium cursor-pointer hover:text-blue-600 hover:underline"
                              onClick={() => handleViewEntity(organization)}
                            >
                              {organization.name}
                            </div>
                            {organization.legal_name && (
                              <div className="text-sm text-muted-foreground">
                                {organization.legal_name}
                              </div>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">{organization.org_type_name || 'No especificado'}</div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">{organization.industry_name || 'No especificado'}</div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">{organization.country_name || 'No especificado'}</div>
                        </TableCell>
                        <TableCell>
                          <Badge variant={organization.is_active ? 'default' : 'secondary'}>
                            {organization.is_active ? 'Activo' : 'Inactivo'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleViewEntity(organization)}
                            >
                              <Eye className="h-4 w-4 mr-1" />
                              Ver
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleEditEntity(organization)}
                            >
                              <Edit className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleDeleteEntity(organization)}
                              disabled={deleteOrganizationMutation.isPending}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            )}

            {/* Pagination Controls */}
            {!isLoading && (people.length > 0 || organizations.length > 0) && (
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
            
            {!isLoading && people.length === 0 && organizations.length === 0 && (
              <div className="text-center py-8">
                {activeTab === 'people' ? <Users className="h-12 w-12 text-muted-foreground mx-auto mb-4" /> : <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />}
                <h3 className="text-lg font-medium mb-2">
                  No se encontraron {activeTab === 'people' ? 'personas' : 'organizaciones'}
                </h3>
                <p className="text-muted-foreground mb-4">
                  {searchTerm 
                    ? 'Intenta ajustar los filtros de búsqueda'
                    : `Comienza creando tu primera ${activeTab === 'people' ? 'persona' : 'organización'}`
                  }
                </p>
                {!searchTerm && (
                  <Button onClick={() => setIsCreateDialogOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    {activeTab === 'people' ? 'Crear Persona' : 'Crear Organización'}
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

// Person Form Component
interface PersonFormProps {
  person?: Person | null
  onSuccess: () => void
}

function PersonForm({ person, onSuccess }: PersonFormProps) {
  const router = useRouter()
  const [formData, setFormData] = useState<PersonCreateData>({
    first_name: person?.first_name || '',
    middle_name: person?.middle_name || '',
    last_name: person?.last_name || '',
    second_last_name: person?.second_last_name || '',
    gender: person?.gender || '',
    birthday: person?.birthday || '',
    marital_status: person?.marital_status || '',
    country_of_nationality: person?.country_of_nationality || '',
    id_type: person?.id_type || '',
    id_number: person?.id_number || '',
    is_active: person?.is_active ?? true,
  })

  const createPersonMutation = useMutation({
    mutationFn: (data: PersonCreateData) => 
      person 
        ? entitiesApi.updatePerson(person.id, data)
        : entitiesApi.createPerson(data),
    onSuccess: (newPerson) => {
      if (person) {
        toast.success('Persona actualizada exitosamente')
        onSuccess()
      } else {
        toast.success('Persona creada exitosamente')
        onSuccess()
        router.push(`/entities/people/${newPerson.id}`)
      }
    },
    onError: (error) => {
      toast.error(person ? 'Error al actualizar la persona' : 'Error al crear la persona')
      console.error('Form error:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createPersonMutation.mutate(formData)
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Nombre *</label>
          <Input
            value={formData.first_name}
            onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Apellido *</label>
          <Input
            value={formData.last_name}
            onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Segundo Nombre</label>
          <Input
            value={formData.middle_name}
            onChange={(e) => setFormData({ ...formData, middle_name: e.target.value })}
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Segundo Apellido</label>
          <Input
            value={formData.second_last_name}
            onChange={(e) => setFormData({ ...formData, second_last_name: e.target.value })}
          />
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
          Persona activa
        </label>
      </div>

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={onSuccess}>
          Cancelar
        </Button>
        <Button type="submit" disabled={createPersonMutation.isPending}>
          {createPersonMutation.isPending ? 'Guardando...' : (person ? 'Actualizar' : 'Crear Persona')}
        </Button>
      </div>
    </form>
  )
}

// Organization Form Component
interface OrganizationFormProps {
  organization?: Organization | null
  onSuccess: () => void
}

function OrganizationForm({ organization, onSuccess }: OrganizationFormProps) {
  const router = useRouter()
  const [formData, setFormData] = useState<OrganizationCreateData>({
    name: organization?.name || '',
    legal_name: organization?.legal_name || '',
    org_type: organization?.org_type || '',
    industry: organization?.industry || '',
    country: organization?.country || '',
    id_type: organization?.id_type || '',
    id_number: organization?.id_number || '',
    main_address: organization?.main_address || '',
    is_active: organization?.is_active ?? true,
  })

  const createOrganizationMutation = useMutation({
    mutationFn: (data: OrganizationCreateData) => 
      organization 
        ? entitiesApi.updateOrganization(organization.id, data)
        : entitiesApi.createOrganization(data),
    onSuccess: (newOrganization) => {
      if (organization) {
        toast.success('Organización actualizada exitosamente')
        onSuccess()
      } else {
        toast.success('Organización creada exitosamente')
        onSuccess()
        router.push(`/entities/organizations/${newOrganization.id}`)
      }
    },
    onError: (error) => {
      toast.error(organization ? 'Error al actualizar la organización' : 'Error al crear la organización')
      console.error('Form error:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    createOrganizationMutation.mutate(formData)
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
          <label className="block text-sm font-medium mb-1">Nombre Legal</label>
          <Input
            value={formData.legal_name}
            onChange={(e) => setFormData({ ...formData, legal_name: e.target.value })}
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

      <div className="flex justify-end gap-2 pt-4">
        <Button type="button" variant="outline" onClick={onSuccess}>
          Cancelar
        </Button>
        <Button type="submit" disabled={createOrganizationMutation.isPending}>
          {createOrganizationMutation.isPending ? 'Guardando...' : (organization ? 'Actualizar' : 'Crear Organización')}
        </Button>
      </div>
    </form>
  )
}
