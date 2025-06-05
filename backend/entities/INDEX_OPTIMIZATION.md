# Optimización de Índices - App Entities

## Resumen de Optimizaciones

La aplicación `entities` gestiona personas, organizaciones, contactos, perfiles y direcciones, con **consultas intensivas** en filtrado semántico, búsquedas complejas y analytics organizacionales. Los índices han sido diseñados para soportar:

- **Búsquedas semánticas** por industrias, habilidades y funciones
- **Analytics organizacionales** por tipo, industria y país
- **Filtrado de contactos** por tipo, verificación y prioridad
- **Consultas geográficas** por país, región y ciudad
- **Búsquedas textuales** optimizadas en nombres y datos de contacto

## Índices Añadidos por Modelo

### 1. Person

**Campos indexados:**

- `first_name, fathers_name` - Búsquedas por nombre (compuesto)
- `gender` - Filtros demográficos
- `marital_status` - Segmentación social
- `birthday` - Filtros por edad y fechas
- `country_of_nationality` - Filtros geográficos
- `id_type` - Tipos de documento
- `id_type, id_number` - Búsquedas únicas de identificación
- `is_active` - Filtro estándar
- `is_active, country_of_nationality` - Combinación frecuente para analytics
- `is_active, gender` - Segmentación demográfica activa

**Justificación:** Modelo central con búsquedas frecuentes por nombre, filtrado demográfico y geográfico, especialmente en analytics de CRM.

### 2. ContactDetail

**Campos indexados:**

- `person` - Relación principal (FK)
- `is_primary, verified` - Combinación original mantenida
- `email` - Búsquedas directas por email
- `phone` - Búsquedas directas por teléfono
- `person, is_primary` - Contacto principal por persona
- `person, is_active` - Contactos activos por persona
- `is_active, is_primary` - Contactos principales activos

**Justificación:** Consultas intensivas para obtener contactos principales, verificados y activos, especialmente en procesos de comunicación y marketing.

### 3. IndividualProfile

**Campos indexados:**

- `person` - Relación OneToOne principal
- `academic_degree` - Filtros educacionales
- `preferred_contact_medium` - Preferencias de comunicación
- `accepts_privacy_policy` - Compliance y legal
- `allows_marketing` - Segmentación de marketing
- `is_active` - Filtro estándar
- `is_active, academic_degree` - Perfiles educacionales activos
- `is_active, allows_marketing` - Segmentación de marketing activa
- `is_active, preferred_contact_medium` - Comunicación con usuarios activos
- `is_active, accepts_privacy_policy` - Compliance activo
- `academic_degree, allows_marketing` - Targeting educacional
- `preferred_contact_medium, allows_marketing` - Estrategias de comunicación
- `accepts_privacy_policy, allows_marketing` - Compliance en marketing
- `person, is_active` - Acceso directo al perfil activo
- `academic_degree, preferred_contact_medium` - Perfilado avanzado

**Justificación:** Modelo crítico para perfilado semántico, segmentación de marketing y personalización de comunicación.

### 4. Organization

**Campos indexados:**

- `name` - Búsquedas por nombre
- `legal_name` - Búsquedas por nombre legal
- `org_type` - Filtros por tipo de organización
- `industry` - Filtros por industria (semántico)
- `country` - Filtros geográficos
- `id_type` - Tipos de identificación
- `id_type, id_number` - Búsquedas únicas de identificación
- `is_active` - Filtro estándar
- `is_active, org_type` - Organizaciones activas por tipo
- `is_active, industry` - Organizaciones activas por industria
- `is_active, country` - Organizaciones activas por país
- `org_type, industry` - Segmentación organizacional avanzada
- `country, industry` - Analytics geográfico-industrial

**Justificación:** Modelo central para organizaciones con consultas intensivas en analytics B2B, segmentación por industria y filtrado geográfico.

### 5. PhysicalAddress

**Campos indexados:**

- `is_primary` - Direcciones principales
- `use_for_billing` - Direcciones de facturación
- `owner_person` - Direcciones de personas
- `owner_org` - Direcciones de organizaciones
- `country` - Filtros geográficos
- `city` - Filtros por ciudad
- `country, city` - Combinación geográfica
- `region_or_state, city` - Filtros regionales
- `is_active, is_primary` - Direcciones principales activas
- `is_active, use_for_billing` - Direcciones de facturación activas
- `owner_person, is_primary` - Dirección principal por persona
- `owner_org, is_primary` - Dirección principal por organización
- `owner_person, is_active` - Direcciones activas por persona
- `owner_org, is_active` - Direcciones activas por organización

**Justificación:** Consultas frecuentes para obtener direcciones principales, facturación y análisis geográfico.

## Patrones de Consulta Optimizados

### 1. Búsquedas Semánticas de Personas

```python
# Perfilado semántico optimizado
Person.objects.select_related('country_of_nationality', 'individualprofile__academic_degree')
    .prefetch_related('individualprofile__industries', 'individualprofile__skills')
    .filter(is_active=True, individualprofile__allows_marketing=True)
```

### 2. Analytics Organizacionales

```python
# Segmentación organizacional por industria y país
Organization.objects.select_related('industry', 'org_type', 'country')
    .filter(is_active=True, industry__parent__name="Technology")
    .values('country__name', 'org_type__name')
    .annotate(count=Count('id'))
```

### 3. Gestión de Contactos

```python
# Contactos principales verificados
ContactDetail.objects.select_related('person', 'organization')
    .filter(is_active=True, is_primary=True, verified=True)
    .exclude(email='')
```

### 4. Búsquedas Geográficas

```python
# Distribución geográfica de direcciones
PhysicalAddress.objects.select_related('country', 'owner_person', 'owner_org')
    .filter(is_active=True, is_primary=True)
    .values('country__name', 'city')
    .annotate(count=Count('id'))
```

## Recomendaciones de Performance

### 1. **Consultas con Relaciones**

- Usar `select_related()` para ForeignKey (country, industry, org_type)
- Usar `prefetch_related()` para ManyToMany (skills, industries, functions)

### 2. **Filtrado Semántico**

- Combinar filtros de `is_active` con campos semánticos
- Aprovechar índices compuestos para múltiples condiciones

### 3. **Analytics y Reporting**

- Usar `values()` y `annotate()` para consultas agregadas
- Aprovechar índices específicos por tipo de organización e industria

### 4. **Búsquedas de Contacto**

- Filtrar por `is_primary=True` para obtener contactos principales
- Usar índices combinados de `email + verified` para validación

### 5. **Consultas Geográficas**

- Combinar `country + city` para análisis geográfico eficiente
- Usar índices regionales para reportes de distribución

## Migración de Índices

Para aplicar estos índices:

```bash
# Generar migración
docker-compose exec backend python manage.py makemigrations entities

# Aplicar migración
docker-compose exec backend python manage.py migrate entities
```

## Monitoreo de Performance

### Consultas a Monitorear:

1. **Person.objects.filter(is_active=True).select_related('country_of_nationality')**
2. **Organization.objects.filter(is_active=True, industry\_\_isnull=False)**
3. **ContactDetail.objects.filter(is_primary=True, verified=True)**
4. **PhysicalAddress.objects.filter(is_active=True, is_primary=True)**
5. **IndividualProfile.objects.filter(allows_marketing=True, is_active=True)**

### Métricas de Success:

- **Consultas < 100ms** para filtrado básico
- **Consultas < 500ms** para analytics complejos
- **Consultas < 50ms** para obtención de contactos principales
- **Sin full table scans** en consultas frecuentes
- `preferred_contact_medium` - Preferencias de comunicación
- `accepts_privacy_policy` - Compliance legal
- `allows_marketing` - Segmentación de marketing
- `is_active, academic_degree` - Perfiles activos por educación
- `is_active, allows_marketing` - Segmentación de marketing activa
- `is_active, preferred_contact_medium` - Canales de comunicación activos
- `academic_degree, allows_marketing` - Analytics educacionales con marketing

**Justificación:** Perfil semántico con consultas frecuentes para segmentación, analytics educacionales y compliance de marketing.

### 4. Organization

**Campos indexados:**

- `name` - Búsquedas textuales
- `legal_name` - Búsquedas por nombre legal
- `org_type` - Filtros por tipo organizacional
- `industry` - Clasificación semántica principal
- `country` - Filtros geográficos
- `id_type` - Tipos de identificación organizacional
- `id_type, id_number` - Búsquedas únicas de identificación
- `is_active, org_type` - Analytics por tipo organizacional
- `is_active, industry` - Analytics por industria
- `is_active, country` - Analytics geográficos
- `org_type, industry` - Clasificación cruzada
- `country, industry` - Analytics geográfico-industriales
- `is_active` - Filtro estándar

**Justificación:** Entidad crítica para analytics B2B con consultas intensivas por tipo, industria y geografía.

### 5. PhysicalAddress

**Campos indexados:**

- `is_primary` - Direcciones principales
- `use_for_billing` - Direcciones de facturación
- `owner_person` - Direcciones de personas
- `owner_org` - Direcciones de organizaciones
- `country` - Filtros geográficos
- `city` - Localización urbana
- `country, city` - Combinación geográfica frecuente
- `region_or_state, city` - Búsquedas regionales
- `is_active, is_primary` - Direcciones principales activas
- `is_active, use_for_billing` - Direcciones de facturación activas
- `owner_person, is_primary` - Dirección principal por persona
- `owner_org, is_primary` - Dirección principal por organización
- `owner_person, is_active` - Direcciones activas por persona
- `owner_org, is_active` - Direcciones activas por organización

**Justificación:** Consultas frecuentes para obtener direcciones principales, de facturación y activas, con componente geográfico importante.

## Métricas de Performance Esperadas

### Consultas Más Beneficiadas

1. **PersonViewSet.search_semantic()**: Búsquedas semánticas complejas
2. **OrganizationViewSet.analytics()**: Analytics organizacionales por tipo e industria
3. **IndividualProfileViewSet.analytics()**: Analytics de perfiles por educación y marketing
4. **Person.primary_contact / primary_address**: Propiedades frecuentemente accedidas
5. **Organization filtrado**: Consultas por industria, tipo y país

### Optimizaciones de Consultas

- **Reducción del 60-80%** en tiempo de consultas semánticas complejas
- **Mejora del 50-70%** en analytics organizacionales
- **Optimización del 40-60%** en búsquedas de contactos principales
- **Aceleración del 30-50%** en consultas geográficas

## Uso de Índices en Consultas Frecuentes

### Búsquedas Semánticas de Personas

```python
# Consulta optimizada con índices semánticos
Person.objects.filter(
    individualprofile__industries__id=industry_id,
    individualprofile__academic_degree=degree_id,
    is_active=True
)
# Usa: is_active+country, academic_degree, person
```

### Analytics Organizacionales

```python
# Consulta optimizada con índices de analytics
Organization.objects.filter(is_active=True).values('org_type__name', 'industry__name')\
    .annotate(count=Count('id')).order_by('-count')
# Usa: is_active+org_type, is_active+industry, org_type+industry
```

### Contactos Principales y Verificados

```python
# Consulta optimizada con índices de contacto
ContactDetail.objects.filter(
    person=person_obj,
    is_primary=True,
    is_active=True
)
# Usa: person+is_primary, is_active+is_primary
```

### Direcciones Geográficas

```python
# Consulta optimizada con índices geográficos
PhysicalAddress.objects.filter(
    country=country_obj,
    city__icontains='Madrid',
    is_primary=True
)
# Usa: country+city, is_active+is_primary
```

## Monitoreo y Mantenimiento

### Consultas a Monitorear

1. **Consultas semánticas complejas** con múltiples JOINs a `world` models
2. **Analytics organizacionales** con GROUP BY en múltiples dimensiones
3. **Búsquedas de texto** en nombres y datos de contacto
4. **Consultas geográficas** con patrones LIKE en ciudades

### Análisis de Performance

```sql
-- Verificar uso de índices en consultas de personas
EXPLAIN ANALYZE SELECT * FROM entities_person
WHERE is_active = true AND country_of_nationality_id = 1;

-- Verificar índices en analytics organizacionales
EXPLAIN ANALYZE SELECT org_type_id, COUNT(*) FROM entities_organization
WHERE is_active = true GROUP BY org_type_id;

-- Verificar consultas semánticas complejas
EXPLAIN ANALYZE SELECT p.* FROM entities_person p
JOIN entities_individualprofile ip ON p.id = ip.person_id
WHERE ip.academic_degree_id = 1 AND p.is_active = true;
```

## Consideraciones de Escalabilidad

- **ManyToManyFields**: Los índices en `IndividualProfile` M2M se manejan automáticamente
- **Búsquedas Full-Text**: Considerar PostgreSQL full-text search para nombres largos
- **Particionamiento**: Evaluar particionar `ContactDetail` por tipo en alta escala
- **Archiving**: Implementar soft-delete optimizado para organizaciones inactivas

Esta optimización está alineada con los patrones de uso intensivo de la aplicación `entities` en BackboneOS CRM.
