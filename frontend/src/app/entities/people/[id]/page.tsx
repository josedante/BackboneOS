'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Save, ChevronDown, ChevronRight, User, Edit, Trash2, Mail, Phone, MapPin, Calendar, IdCard } from 'lucide-react'
import { entitiesApi, type Person, type PersonCreateData, type ContactDetail, type PhysicalAddress, getResults } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { toast } from 'sonner'

export default function PersonDetailPage() {
  const params = useParams()
  const router = useRouter()
  const queryClient = useQueryClient()
  const personId = params.id as string

  // Fetch person details
  const { data: person, isLoading, error } = useQuery({
    queryKey: ['person', personId],
    queryFn: () => entitiesApi.getPerson(personId),
    enabled: !!personId,
  })

  // Form state
  const [formData, setFormData] = useState<PersonCreateData>({
    first_name: '',
    middle_name: '',
    last_name: '',
    second_last_name: '',
    gender: '',
    birthday: '',
    marital_status: '',
    country_of_nationality: '',
    id_type: '',
    id_number: '',
    is_active: true,
  })

  // Collapsible sections state
  const [expandedSections, setExpandedSections] = useState({
    basic: true,
    contact: false,
    address: false,
    profile: false,
  })

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }))
  }

  // Initialize form data when person loads
  useEffect(() => {
    if (person) {
      setFormData({
        first_name: person.first_name || '',
        middle_name: person.middle_name || '',
        last_name: person.last_name || '',
        second_last_name: person.second_last_name || '',
        gender: person.gender || '',
        birthday: person.birthday || '',
        marital_status: person.marital_status || '',
        country_of_nationality: person.country_of_nationality || '',
        id_type: person.id_type || '',
        id_number: person.id_number || '',
        is_active: person.is_active ?? true,
      })
    }
  }, [person])

  // Update mutation
  const updatePersonMutation = useMutation({
    mutationFn: (data: PersonCreateData) => entitiesApi.updatePerson(personId, data),
    onSuccess: () => {
      toast.success('Persona actualizada exitosamente')
      queryClient.invalidateQueries({ queryKey: ['person', personId] })
    },
    onError: (error) => {
      toast.error('Error al actualizar la persona')
      console.error('Update error:', error)
    },
  })

  // Delete mutation
  const deletePersonMutation = useMutation({
    mutationFn: () => entitiesApi.deletePerson(personId),
    onSuccess: () => {
      toast.success('Persona eliminada exitosamente')
      router.push('/entities')
    },
    onError: (error) => {
      toast.error('Error al eliminar la persona')
      console.error('Delete error:', error)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    updatePersonMutation.mutate(formData)
  }

  const handleDelete = () => {
    if (confirm('¿Está seguro de que desea eliminar esta persona?')) {
      deletePersonMutation.mutate()
    }
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Cargando persona...</div>
        </div>
      </DashboardLayout>
    )
  }

  if (error || !person) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="text-lg text-red-600">Error al cargar la persona</div>
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
              <h1 className="text-2xl font-bold">{person.full_name}</h1>
              <p className="text-muted-foreground">
                {person.primary_contact ? person.primary_contact.value : 'Sin contacto principal'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge variant={person.is_active ? 'default' : 'secondary'}>
              {person.is_active ? 'Activo' : 'Inactivo'}
            </Badge>
            <Button
              variant="destructive"
              size="sm"
              onClick={handleDelete}
              disabled={deletePersonMutation.isPending}
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
                  <User className="h-5 w-5 mr-2" />
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

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-1">Fecha de Nacimiento</label>
                    <Input
                      type="date"
                      value={formData.birthday}
                      onChange={(e) => setFormData({ ...formData, birthday: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-1">País de Nacionalidad</label>
                    <Input
                      value={formData.country_of_nationality}
                      onChange={(e) => setFormData({ ...formData, country_of_nationality: e.target.value })}
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
                {person.contacts && person.contacts.length > 0 ? (
                  <div className="space-y-3">
                    {person.contacts.map((contact: ContactDetail) => (
                      <div key={contact.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div className="flex items-center space-x-3">
                          {contact.email ? (
                            <Mail className="h-4 w-4 text-blue-500" />
                          ) : (
                            <Phone className="h-4 w-4 text-green-500" />
                          )}
                          <div>
                            <div className="font-medium">
                              {contact.email || contact.phone}
                            </div>
                            <div className="text-sm text-muted-foreground">
                              {contact.email ? 'Email' : 'Teléfono'}
                              {contact.is_primary && ' • Principal'}
                            </div>
                          </div>
                        </div>
                        <Badge variant={contact.verified ? 'default' : 'secondary'}>
                          {contact.verified ? 'Verificado' : 'No verificado'}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <Mail className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No hay información de contacto disponible</p>
                  </div>
                )}
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
                {person.addresses && person.addresses.length > 0 ? (
                  <div className="space-y-3">
                    {person.addresses.map((address: PhysicalAddress) => (
                      <div key={address.id} className="p-3 border rounded-lg">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start space-x-3">
                            <MapPin className="h-4 w-4 text-gray-500 mt-1" />
                            <div>
                              <div className="font-medium">
                                {address.address_line_1}
                                {address.address_line_2 && `, ${address.address_line_2}`}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {address.city}
                                {address.state_province && `, ${address.state_province}`}
                                {address.postal_code && ` ${address.postal_code}`}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {address.country_name}
                              </div>
                            </div>
                          </div>
                          {address.is_primary && (
                            <Badge variant="default">Principal</Badge>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <MapPin className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No hay direcciones registradas</p>
                  </div>
                )}
              </CardContent>
            )}
          </Card>

          {/* Profile Information */}
          <Card>
            <CardHeader 
              className="pb-3 cursor-pointer hover:bg-gray-50"
              onClick={() => toggleSection('profile')}
            >
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg flex items-center">
                  <IdCard className="h-5 w-5 mr-2" />
                  Perfil Individual
                </CardTitle>
                {expandedSections.profile ? <ChevronDown className="h-5 w-5" /> : <ChevronRight className="h-5 w-5" />}
              </div>
            </CardHeader>
            {expandedSections.profile && (
              <CardContent className="space-y-4">
                {person.profile ? (
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-1">Grado Académico</label>
                        <div className="text-sm text-muted-foreground">
                          {person.profile.academic_degree_name || 'No especificado'}
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm font-medium mb-1">Medio de Contacto Preferido</label>
                        <div className="text-sm text-muted-foreground">
                          {person.profile.preferred_contact_medium || 'No especificado'}
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-3 gap-4">
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold text-blue-600">{person.profile.industries_count}</div>
                        <div className="text-sm text-muted-foreground">Industrias</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold text-green-600">{person.profile.skills_count}</div>
                        <div className="text-sm text-muted-foreground">Habilidades</div>
                      </div>
                      <div className="text-center p-3 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold text-purple-600">{person.profile.functions_count}</div>
                        <div className="text-sm text-muted-foreground">Funciones</div>
                      </div>
                    </div>

                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={person.profile.allows_marketing}
                        disabled
                        className="rounded"
                      />
                      <label className="text-sm font-medium">
                        Permite marketing
                      </label>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-muted-foreground">
                    <IdCard className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>No hay perfil individual creado</p>
                    <Button variant="outline" className="mt-4">
                      Crear Perfil
                    </Button>
                  </div>
                )}
              </CardContent>
            )}
          </Card>

          {/* Form Actions */}
          <div className="flex justify-end gap-2 pt-4">
            <Button type="submit" disabled={updatePersonMutation.isPending}>
              <Save className="h-4 w-4 mr-2" />
              {updatePersonMutation.isPending ? 'Guardando...' : 'Guardar Cambios'}
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  )
}
