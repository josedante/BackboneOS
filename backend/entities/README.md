# App Entities - Sistema de Gestión de Entidades

## 🎯 **Propósito**

La aplicación `entities` es el **núcleo semántico de gestión de personas y organizaciones** en BackboneOS. Proporciona la infraestructura fundamental para perfilado semántico, gestión de contactos, direcciones y análisis organizacional en el contexto CRM.

## 🏗️ **Arquitectura de Modelos**

### **Entidades Principales**

#### **Person** - Personas Físicas

- **Propósito**: Gestión completa de individuos con perfilado semántico
- **Características Clave**:
  - Información demográfica completa (nombre, género, estado civil, nacionalidad)
  - Sistema de identificación robusto con tipos de documento
  - Integración semántica con app `world` (países, tipos de ID)
  - Propiedades calculadas para contacto y dirección principal
  - Método de perfilado semántico completo

#### **Organization** - Entidades Organizacionales

- **Propósito**: Gestión de empresas, instituciones y organizaciones
- **Características Clave**:
  - Información corporativa (nombre legal, tipo de organización)
  - Clasificación semántica por industria (integración con `world`)
  - Sistema de identificación organizacional
  - Gestión de direcciones múltiples (principal, facturación)
  - Perfilado semántico organizacional

#### **ContactDetail** - Gestión de Contactos

- **Propósito**: Sistema unificado de contactos para personas y organizaciones
- **Características Clave**:
  - Soporte dual: personas y organizaciones
  - Sistema de contacto principal y verificación
  - Validaciones de integridad referencial
  - Optimizado para comunicación y marketing

#### **IndividualProfile** - Perfilado Semántico Personal

- **Propósito**: Extensión semántica de personas con capacidades CRM avanzadas
- **Características Clave**:
  - Relaciones semánticas con `world` (industrias, habilidades, funciones, grados académicos)
  - Gestión de preferencias de comunicación
  - Compliance de privacidad y marketing
  - Perfilado multidimensional para segmentación

#### **PhysicalAddress** - Gestión de Direcciones

- **Propósito**: Sistema flexible de direcciones para personas y organizaciones
- **Características Clave**:
  - Soporte dual con validaciones de integridad
  - Configuración de dirección principal y facturación
  - Información geográfica completa
  - Integración con análisis geográfico

## 🔍 **Características Semánticas**

### **Integración con Campo Semántico (World)**

La aplicación está estrechamente integrada con `world` para proporcionar:

- **Perfilado Semántico Personal**: Clasificación por industrias, habilidades y funciones
- **Clasificación Organizacional**: Tipificación por industria y tipo de organización
- **Contexto Geográfico**: Países, regiones y análisis territorial
- **Identificación Regulatory**: Tipos de documentos personales y organizacionales

### **Métodos de Perfilado Semántico**

```python
# Perfil semántico de persona
person_profile = person.get_semantic_profile()
# Retorna: academic_degree, industries, skills, functions, comunicación

# Perfil semántico de organización
org_profile = organization.get_semantic_profile()
# Retorna: industry, org_type, country
```

## 📊 **Optimización de Performance**

### **Índices Estratégicos**

La aplicación cuenta con **índices optimizados** para:

- **Búsquedas Demográficas**: género, estado civil, nacionalidad
- **Filtrado Semántico**: grado académico, industrias, habilidades
- **Analytics Organizacionales**: tipo, industria, país
- **Gestión de Contactos**: principal, verificado, activo
- **Análisis Geográfico**: país-ciudad, región-ciudad

Ver [`INDEX_OPTIMIZATION.md`](./INDEX_OPTIMIZATION.md) para detalles completos.

### **Patrones de Consulta Optimizados**

```python
# Perfilado semántico optimizado
Person.objects.select_related('country_of_nationality', 'individualprofile__academic_degree')
    .prefetch_related('individualprofile__industries', 'individualprofile__skills')
    .filter(is_active=True, individualprofile__allows_marketing=True)

# Analytics organizacional
Organization.objects.select_related('industry', 'org_type', 'country')
    .filter(is_active=True, industry__parent__name="Technology")
    .values('country__name', 'org_type__name')
    .annotate(count=Count('id'))
```

## 🚀 **Casos de Uso CRM**

### **1. Perfilado de Clientes**

- Clasificación semántica multidimensional
- Segmentación por industria, habilidades y demografía
- Targeting personalizado basado en perfil

### **2. Gestión de Contactos**

- Comunicación omnicanal (email, teléfono, preferencias)
- Verificación y validación de contactos
- Compliance de privacidad y marketing

### **3. Analytics Organizacional**

- Análisis de mercado por industria y geografía
- Segmentación de organizaciones por tipo y tamaño
- Inteligencia competitiva y de mercado

### **4. Gestión de Direcciones**

- Direcciones múltiples por entidad (principal, facturación)
- Análisis geográfico y distribución territorial
- Logística y planificación de territorio

## 🔗 **Integraciones**

### **Con App World**

- `Country` → Nacionalidad y ubicación
- `Industry` → Clasificación industrial
- `Skill`, `FunctionOrResponsibility` → Perfilado profesional
- `AcademicDegree` → Nivel educativo
- `PersonalIDType`, `OrganizationalIDType` → Identificación

### **Con App Products** (Futuro)

- Recomendaciones basadas en perfil semántico
- Targeting de productos por industria y habilidades
- Personalización de catálogo

## 📈 **Métricas y KPIs**

### **Métricas de Entidades**

- Total de personas y organizaciones activas
- Distribución demográfica por país y género
- Perfiles completos vs. incompletos

### **Métricas de Contacto**

- Contactos verificados vs. no verificados
- Distribución por medio de contacto preferido
- Compliance de marketing (opt-in/opt-out)

### **Métricas Semánticas**

- Distribución por industria y grado académico
- Cobertura de skills y funciones
- Segmentación organizacional por tipo

## 🔧 **Comandos de Gestión**

```bash
# Aplicar migraciones
docker-compose exec backend python manage.py migrate entities

# Verificar modelos
docker-compose exec backend python manage.py shell -c "from entities.models import *"

# Análisis de índices
docker-compose exec backend python manage.py dbshell
```

## 🎯 **Roadmap**

### **Próximas Funcionalidades**

- [ ] Sistema de membresías (personas ↔ organizaciones)
- [ ] Log de actividades y timeline
- [ ] Scoring de perfiles y lead scoring
- [ ] Integración con sistema de comunicaciones
- [ ] Dashboard de analytics de entidades

### **Optimizaciones Pendientes**

- [ ] Cache de perfiles semánticos
- [ ] Búsqueda full-text en nombres y direcciones
- [ ] API GraphQL para consultas complejas
- [ ] Webhooks para cambios de entidades

## 🛡️ **Compliance y Seguridad**

- **GDPR Ready**: Campos de consentimiento y privacidad
- **Auditoría**: Tracking de cambios via `BaseUUIDModelWithActiveStatus`
- **Integridad**: Constraints de base de datos para validación
- **Soft Delete**: Sistema de `is_active` para preservar histórico
