# COPILOT: Aplicación Entities

## 🎯 Propósito

Sistema de gestión de **personas y organizaciones** como núcleo semántico del CRM.

## 📊 Modelos Principales

### Person

```python
# Persona física con información demográfica
class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    # Relaciones semánticas con world app
    nationality = models.ForeignKey('world.Country')
    education_level = models.ForeignKey('world.EducationLevel')
```

### Organization

```python
# Entidad corporativa con clasificación industrial
class Organization(models.Model):
    name = models.CharField(max_length=200)
    organization_type = models.ForeignKey('world.OrganizationType')
    industry = models.ForeignKey('world.Industry')
    founded_date = models.DateField(null=True, blank=True)
    employee_count_range = models.CharField(max_length=20)
```

### ContactDetail

```python
# Sistema unificado de contactos
class ContactDetail(models.Model):
    contact_type = models.CharField(max_length=20)  # email, phone, etc.
    value = models.CharField(max_length=255)
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    # Generic foreign key para Person o Organization
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
```

### IndividualProfile

```python
# Extensión semántica personal para CRM
class IndividualProfile(models.Model):
    person = models.OneToOneField(Person)
    current_role = models.CharField(max_length=100)
    industry_experience_years = models.PositiveIntegerField()
    skills = models.ManyToManyField('world.Skill')
    interests = models.ManyToManyField('world.Interest')
```

### PhysicalAddress

```python
# Gestión de direcciones múltiples
class PhysicalAddress(models.Model):
    address_line_1 = models.CharField(max_length=255)
    city = models.ForeignKey('world.City')
    state = models.ForeignKey('world.State')
    country = models.ForeignKey('world.Country')
    postal_code = models.CharField(max_length=20)
    address_type = models.CharField(max_length=20)  # home, work, billing
```

## 🚀 Endpoints API

### Personas

```
GET    /api/entities/people/              # Lista de personas
POST   /api/entities/people/              # Crear persona
GET    /api/entities/people/{id}/         # Detalle de persona
PUT    /api/entities/people/{id}/         # Actualizar persona
DELETE /api/entities/people/{id}/         # Eliminar persona
GET    /api/entities/people/{id}/profile/ # Perfil semántico
```

### Organizaciones

```
GET    /api/entities/organizations/           # Lista organizaciones
POST   /api/entities/organizations/           # Crear organización
GET    /api/entities/organizations/{id}/      # Detalle organización
GET    /api/entities/organizations/{id}/analytics/ # Analytics organizacional
```

### Contactos

```
GET    /api/entities/contacts/              # Lista contactos
POST   /api/entities/contacts/              # Crear contacto
PUT    /api/entities/contacts/{id}/         # Actualizar contacto
POST   /api/entities/contacts/{id}/verify/  # Verificar contacto
```

## 🔍 Funcionalidades CRM

### Perfilado Semántico

- Clasificación por industria y función
- Análisis de habilidades e intereses
- Contexto geográfico y cultural
- Integración con vocabulario empresarial (world app)

### Analytics Organizacional

- Segmentación por industria
- Análisis demográfico
- Métricas de penetración de mercado
- Inteligencia empresarial

### Gestión de Contactos

- Comunicación omnicanal
- Verificación de contactos
- Preferencias de comunicación
- Compliance GDPR

## 💡 Patrones de Uso

### Crear Persona Completa

```python
# Con perfil semántico y contactos
person_data = {
    "first_name": "Ana",
    "last_name": "García",
    "nationality": country_id,
    "education_level": education_id,
    "contacts": [
        {"contact_type": "email", "value": "ana@empresa.com", "is_primary": True},
        {"contact_type": "phone", "value": "+34600123456"}
    ],
    "profile": {
        "current_role": "Product Manager",
        "skills": [skill_id1, skill_id2]
    }
}
```

### Búsqueda Semántica

```python
# Filtrar por contexto empresarial
/api/entities/people/?industry=technology&education_level=university
/api/entities/organizations/?organization_type=corporation&employee_count=50-200
```

### Analytics Empresarial

```python
# Inteligencia de mercado
/api/entities/organizations/analytics/?group_by=industry
/api/entities/people/analytics/?segment_by=education_level
```

## ⚡ Optimizaciones

### Índices Estratégicos

- Búsqueda por nombre completo
- Filtrado por industria y tipo de organización
- Consultas por ubicación geográfica
- Clasificación por nivel educativo

### Consultas Optimizadas

```python
# Prefetch para evitar N+1
Person.objects.select_related(
    'nationality', 'education_level'
).prefetch_related(
    'contacts', 'profile__skills'
)
```

## 🧪 Testing

```bash
# Tests específicos de entities
docker-compose exec backend python manage.py test entities

# Tests con datos de prueba
docker-compose exec backend python manage.py shell
>>> from entities.create_test_data import create_sample_entities
>>> create_sample_entities()
```

## 📈 Métricas de Performance

- Documentado en `backend/entities/PERFORMANCE_REPORT.md`
- Optimizaciones en `backend/entities/INDEX_OPTIMIZATION.md`
- Tests de performance en `performance_tests.py`

## 🔗 Integración con Otras Apps

- **World**: Datos de referencia semántica
- **Interactions**: Customer journey de entidades
- **Products**: Preferencias y historial de productos
- **Offers**: Segmentación para ofertas personalizadas
- **Campaigns**: Targeting semántico de campañas
