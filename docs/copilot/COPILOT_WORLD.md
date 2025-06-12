# COPILOT: Aplicación World

## 🎯 Propósito

Sistema de **datos globales de referencia** que proporciona vocabulario empresarial y contexto semántico.

## 📊 Modelos de Referencia (15+ modelos)

### Geografía

```python
class Country(models.Model):
    name = models.CharField(max_length=100)
    iso_code_2 = models.CharField(max_length=2, unique=True)
    iso_code_3 = models.CharField(max_length=3, unique=True)
    phone_code = models.CharField(max_length=5)

class State(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country)
    state_code = models.CharField(max_length=10)

class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.ForeignKey(State)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
```

### Contexto Empresarial

```python
class Industry(models.Model):
    name = models.CharField(max_length=100)
    sector = models.CharField(max_length=50)
    description = models.TextField()
    industry_code = models.CharField(max_length=10)  # NAICS/SIC

class OrganizationType(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # for_profit, non_profit, government
    description = models.TextField()

class JobFunction(models.Model):
    name = models.CharField(max_length=100)
    department = models.CharField(max_length=50)
    seniority_level = models.CharField(max_length=20)
    description = models.TextField()
```

### Contexto Personal

```python
class EducationLevel(models.Model):
    name = models.CharField(max_length=100)
    level_order = models.PositiveIntegerField()  # 1=primary, 6=doctoral
    description = models.TextField()

class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # technical, soft, industry
    proficiency_levels = models.JSONField(default=list)

class Interest(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50)  # professional, personal, hobby
    description = models.TextField()
```

### Identificación y Compliance

```python
class IdentificationType(models.Model):
    name = models.CharField(max_length=100)
    country = models.ForeignKey(Country)
    format_pattern = models.CharField(max_length=100)  # regex pattern
    is_government_issued = models.BooleanField(default=True)

class Currency(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=3, unique=True)  # ISO 4217
    symbol = models.CharField(max_length=5)
    decimal_places = models.PositiveIntegerField(default=2)

class Language(models.Model):
    name = models.CharField(max_length=100)
    iso_code_2 = models.CharField(max_length=2)
    iso_code_3 = models.CharField(max_length=3)
    native_name = models.CharField(max_length=100)
```

## 🚀 Endpoints API

### Datos Geográficos

```
GET    /api/world/countries/                  # Lista países
GET    /api/world/countries/{id}/states/      # Estados por país
GET    /api/world/states/{id}/cities/         # Ciudades por estado
GET    /api/world/cities/?search=name         # Búsqueda de ciudades
```

### Contexto Empresarial

```
GET    /api/world/industries/                 # Lista industrias
GET    /api/world/industries/?sector=tech     # Industrias por sector
GET    /api/world/organization-types/         # Tipos de organización
GET    /api/world/job-functions/              # Funciones laborales
GET    /api/world/job-functions/?department=sales # Por departamento
```

### Contexto Personal

```
GET    /api/world/education-levels/           # Niveles educativos
GET    /api/world/skills/                     # Lista habilidades
GET    /api/world/skills/?category=technical  # Habilidades por categoría
GET    /api/world/interests/                  # Lista intereses
```

### Compliance y Localización

```
GET    /api/world/identification-types/       # Tipos de identificación
GET    /api/world/identification-types/?country={id} # Por país
GET    /api/world/currencies/                 # Lista monedas
GET    /api/world/languages/                  # Lista idiomas
```

### Endpoints Auxiliares

```
GET    /api/world/choices/{model}/            # Choices de un modelo específico
GET    /api/world/search/?q=term&model=all    # Búsqueda global
GET    /api/world/stats/                      # Estadísticas de datos de referencia
```

## 🔍 Funcionalidades Semánticas

### Vocabulario Empresarial

- Clasificación industrial estándar (NAICS/SIC)
- Tipificación de organizaciones por contexto legal
- Funciones laborales con jerarquía y departamento
- Niveles de experiencia y seniority

### Clasificación Personal

- Niveles educativos con orden jerárquico
- Habilidades categorizadas (técnicas, soft, industria)
- Intereses personales y profesionales
- Competencias con niveles de proficiencia

### Contexto Geográfico

- Datos geográficos completos con coordenadas
- Códigos ISO estándar para países
- Códigos telefónicos internacionales
- Estructura jerárquica país → estado → ciudad

### Compliance Regulatorio

- Tipos de identificación por país
- Patrones de validación de documentos
- Monedas con precisión decimal
- Idiomas con códigos ISO estándar

## 💡 Patrones de Uso

### Configuración de Perfiles

```python
# Para configurar entidades con contexto semántico
person_data = {
    "nationality": "/api/world/countries/1/",  # España
    "education_level": "/api/world/education-levels/4/",  # Universidad
    "skills": [
        "/api/world/skills/1/",  # Python
        "/api/world/skills/15/"  # Project Management
    ]
}

organization_data = {
    "industry": "/api/world/industries/5/",  # Technology
    "organization_type": "/api/world/organization-types/1/",  # Corporation
    "country": "/api/world/countries/1/"
}
```

### Filtrado Contextual

```python
# Búsquedas semánticas
/api/world/skills/?category=technical&proficiency_level=expert
/api/world/industries/?sector=technology
/api/world/job-functions/?seniority_level=senior&department=engineering
```

### Choices Dinámicos para Frontend

```python
# Obtener opciones para formularios
/api/world/choices/Industry/         # Todas las industrias como choices
/api/world/choices/EducationLevel/   # Niveles educativos como choices
/api/world/choices/Country/          # Países como choices
```

## 📈 Analytics de Referencia

### Estadísticas Globales

- Distribución geográfica de entidades
- Clasificación por industria y sector
- Análisis demográfico por nivel educativo
- Penetración por función laboral

### Inteligencia de Mercado

- Densidad empresarial por región
- Concentración de habilidades por geografía
- Análisis de competencia por industria
- Oportunidades de mercado por contexto

## ⚡ Optimizaciones

### Índices Estratégicos

- Búsqueda por código ISO (países, idiomas)
- Filtrado por categoría y sector
- Consultas jerárquicas (país → estado → ciudad)
- Búsqueda de texto completo

### Caché de Datos de Referencia

```python
# Datos altamente cacheables
CACHE_TIMEOUT = 86400  # 24 horas para datos de referencia
# Cache por categoría y búsquedas frecuentes
```

### Consultas Optimizadas

```python
# Prefetch para relaciones jerárquicas
Country.objects.prefetch_related('state_set__city_set')
Industry.objects.select_related().filter(sector='technology')
```

## 🧪 Datos de Prueba

### Fixtures Estándar

```bash
# Cargar datos de referencia básicos
docker-compose exec backend python manage.py loaddata world_countries.json
docker-compose exec backend python manage.py loaddata world_industries.json
docker-compose exec backend python manage.py loaddata world_skills.json
```

### Testing de Datos de Referencia

```bash
# Tests de integridad de datos
docker-compose exec backend python manage.py test world.tests.ReferenceDataTests

# Validación de códigos ISO
docker-compose exec backend python manage.py test world.tests.ISOValidationTests
```

## 🌍 Estándares Internacionales

### Códigos ISO Implementados

- **ISO 3166**: Códigos de países (alpha-2, alpha-3)
- **ISO 639**: Códigos de idiomas (alpha-2, alpha-3)
- **ISO 4217**: Códigos de monedas
- **NAICS/SIC**: Clasificación industrial estándar

### Compliance y Localización

- Formatos de identificación por país
- Validación de documentos gubernamentales
- Precisión decimal por moneda
- Nombres nativos de idiomas

## 🔗 Integración con Otras Apps

### Entities (Perfilado Semántico)

```python
# Enriquecimiento semántico de entidades
Person.nationality → Country
Person.education_level → EducationLevel
IndividualProfile.skills → Skill (ManyToMany)
Organization.industry → Industry
```

### Products (Clasificación)

```python
# Contexto geográfico de productos
Product.available_countries → Country (ManyToMany)
ProductCategory.target_industries → Industry (ManyToMany)
```

### Interactions (Contexto)

```python
# Análisis geográfico de interacciones
Interaction.location_country → Country
Session.language → Language
```

### Compliance (Regulatorio)

```python
# Validación por contexto geográfico
ContactDetail.country → Country (para validación)
PhysicalAddress.identification_type → IdentificationType
```
