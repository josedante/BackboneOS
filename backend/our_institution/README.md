# Aplicación Our Institution - Estructura Organizacional

## 🎯 Propósito

La aplicación `our_institution` implementa un **sistema completo de gestión de estructura organizacional** para BackboneOS, proporcionando una representación jerárquica y semánticamente rica de la organización propietaria del sistema CRM.

### Características Principales

- ✅ **Jerarquía Organizacional Limpia**: `Organization → Division → Unit → Position` y `Organization → Division → Team`
- ✅ **Relaciones Sin Redundancia**: Arquitectura optimizada sin referencias circulares
- ✅ **Constraints Únicos Contextuales**: Códigos únicos por nivel jerárquico
- ✅ **API REST Completa**: Endpoints optimizados con filtrado avanzado
- ✅ **Tests Comprensivos**: 14 tests unitarios con 100% de éxito

---

## 🏗️ Arquitectura de Modelos

### Jerarquía Organizacional

```
OurOrganization (Organización Propietaria)
├── Division (Divisiones Empresariales)
│   ├── Unit (Unidades Organizacionales) [Jerárquica]
│   │   └── Position (Cargos/Posiciones)
│   └── Team (Equipos Transversales)
└── Seat (Sedes/Oficinas)
```

### Modelos Implementados

#### `OurOrganization` - Organización Propietaria

- Identidad institucional única del sistema BackboneOS
- **Constraint**: Solo una organización puede estar activa
- **Integración**: Conectada con `world.Country`, `world.Industry`, `world.OrganizationType`
- **Métricas**: Conteos automáticos de divisiones, sedes, unidades, equipos y posiciones

#### `Division` - Divisiones Empresariales

- Grandes áreas organizacionales (Tecnología, Comercial, Operaciones)
- **Constraint**: `(organization, name)` y `(organization, code)` únicos
- **Métricas**: Conteos de unidades, equipos y posiciones por división

#### `Unit` - Unidades Organizacionales (Jerárquica)

- Estructura jerárquica con soporte padre-hijo ilimitado
- **Constraint**: `(division, code)` único por división
- **Navegación**: Path completo automático (`division > parent > unit`)
- **Relación**: `division` obligatorio (CASCADE)

#### `Position` - Cargos/Posiciones

- Posiciones específicas dentro de unidades organizacionales
- **Constraint**: `(unit, code)` único por unidad
- **Navegación**: Acceso a organización vía `unit.division.organization`
- **Relación**: `unit` obligatorio (CASCADE)

#### `Team` - Equipos Transversales

- Equipos que cruzan múltiples unidades dentro de una división
- **Constraint**: `(division, code)` y `(division, name)` únicos
- **Relación**: `division` obligatorio (CASCADE)

#### `Seat` - Sedes/Oficinas

- Ubicaciones físicas de la organización
- **Categorías**: HQT (Sede Principal), BRC (Sucursal), WHS (Almacén), FAC (Fábrica)
- **Relación**: Directa con organización

---

## 🔌 API REST Completa

### Endpoints Disponibles

```bash
# Gestión organizacional
GET /api/our-institution/organization/     # Organización propietaria
GET /api/our-institution/divisions/        # Divisiones empresariales
GET /api/our-institution/seats/            # Sedes y oficinas

# Estructura jerárquica
GET /api/our-institution/units/            # Unidades (con jerarquía)
GET /api/our-institution/positions/        # Posiciones/cargos
GET /api/our-institution/teams/            # Equipos transversales
```

### Capacidades de Filtrado

#### Filtros Jerárquicos

```bash
# Unidades por división
/api/our-institution/units/?division=<div_id>

# Posiciones por unidad y división
/api/our-institution/positions/?unit=<unit_id>&unit__division=<div_id>

# Equipos por división
/api/our-institution/teams/?division=<div_id>
```

#### Búsquedas y Ordenamiento

```bash
# Búsqueda de texto en nombres, códigos y descripciones
?search=<término>

# Ordenamiento multifacético
?ordering=name,created_at
```

### Respuestas Optimizadas

Todos los serializers incluyen:

- **Información Contextual**: Nombres de división, organización
- **Métricas Calculadas**: Conteos de elementos relacionados
- **Navegación Jerárquica**: Paths completos y relaciones parent-child
- **Datos Relacionados**: Foreign keys con información descriptiva

---

## ⚙️ Administración Django

Panel administrativo completo con:

- **Gestión Visual**: Interface intuitiva para jerarquías organizacionales
- **Filtros Inteligentes**: Por división, organización, estado activo
- **Búsquedas Optimizadas**: En nombres, códigos y descripciones
- **Campos Calculados**: Métricas en tiempo real en listados

---

## 🧪 Sistema de Pruebas

### Tests Implementados (14 tests, 100% éxito)

```bash
# Ejecutar todos los tests
docker-compose exec backend python manage.py test our_institution

# Tests de modelo
OurOrganizationModelTest (unicidad, creación)
DivisionModelTest (constraints únicos)
UnitModelTest (jerarquía, paths, constraints)
PositionModelTest (vinculación, constraints)
TeamModelTest (creación, constraints)

# Test de integración
IntegrationTest (estructura organizacional completa)
```

---

## 🛠️ Comandos de Gestión

### Comando Principal: `create_organization_structure`

```bash
# Crear estructura organizacional completa
docker-compose exec backend python manage.py create_organization_structure

# Recrear desde cero (elimina datos existentes)
docker-compose exec backend python manage.py create_organization_structure --reset
```

### Estructura Creada Automáticamente

**Organización**: BackboneOS (Backbone Operating Systems SAC)

- **País**: Perú
- **Industria**: Tecnología de la Información
- **Tipo**: SAC (Sociedad Anónima Cerrada)

**3 Divisiones**:

- Tecnología y Desarrollo (TECH)
- Comercial y Marketing (COMM)
- Operaciones y Finanzas (OPER)

**8 Unidades** con jerarquía:

```
Tecnología y Desarrollo
├── Gerencia de Desarrollo
│   ├── Equipo Frontend
│   ├── Equipo Backend
│   └── DevOps e Infraestructura
└── QA y Testing

Comercial y Marketing
├── Gerencia Comercial
│   ├── Ventas Empresariales
│   └── Marketing Digital
```

**10 Posiciones** distribuidas:

- Gerente de Desarrollo, Tech Leads, Desarrolladores Senior/Junior
- QA Lead, QA Tester, DevOps Engineer

**4 Equipos** transversales:

- Squad CRM, Squad Analytics (Tecnología)
- Equipo Growth, Equipo Contenido (Comercial)

**2 Sedes**:

- Sede Principal (HQ01)
- Oficina Comercial (COM01)

---

## 📊 Verificación de Funcionamiento

### Tests de API

```bash
# Verificar organización
curl "http://localhost:8000/api/our-institution/organization/" | jq

# Verificar divisiones con métricas
curl "http://localhost:8000/api/our-institution/divisions/" | jq

# Verificar unidades con jerarquía completa
curl "http://localhost:8000/api/our-institution/units/" | jq

# Verificar posiciones con contexto organizacional
curl "http://localhost:8000/api/our-institution/positions/" | jq
```

### Métricas Esperadas

- **Organización**: 1 activa
- **Divisiones**: 3 (TECH, COMM, OPER)
- **Sedes**: 2 (Principal, Comercial)
- **Unidades**: 8 (con jerarquía padre-hijo)
- **Posiciones**: 10 (distribuidas por unidades)
- **Equipos**: 4 (transversales por división)

---

## 📁 Estructura de Archivos

```
our_institution/
├── admin.py                    # ✅ Interface administrativa completa
├── models.py                   # ✅ Modelos con arquitectura optimizada
├── serializers.py              # ✅ Serializers con información contextual
├── views.py                    # ✅ ViewSets optimizados con select_related
├── urls.py                     # ✅ URLs con DefaultRouter
├── tests.py                    # ✅ 14 tests unitarios e integración
├── README.md                   # ✅ Esta documentación
├── README.md                   # Este archivo
├── management/
│   ├── __init__.py             # ✅ Estructura de comandos
│   └── commands/
│       ├── __init__.py         # ✅
│       ├── init_organization.py        # ✅ Comando básico
│       └── create_organization_structure.py  # ✅ Comando completo
└── migrations/
    └── 0001_initial.py         # ✅ Migración limpia aplicada
```

---

## 🎯 Valor para BackboneOS CRM

### Gestión Organizacional Nativa

- **Representación Fiel**: Estructura empresarial real en el CRM
- **Flexibilidad**: Soporte para reorganizaciones futuras
- **Trazabilidad**: Historial de cambios organizacionales

### Integración CRM Avanzada

- **Asignación de Responsabilidades**: Base para ownership en leads/oportunidades
- **Contexto Organizacional**: Estructura para reporting y analytics
- **Workflow Empresarial**: Ruteo de procesos por división/unidad

### Inteligencia Organizacional

- **Métricas Automatizadas**: Dashboards de estructura organizacional
- **Navegación Semántica**: Búsquedas por contexto empresarial
- **APIs Preparadas**: Integración con sistemas externos

---

## ✅ Estado del Proyecto

**ESTADO**: ✅ **COMPLETAMENTE FUNCIONAL**

- ✅ Arquitectura de modelos optimizada y sin redundancias
- ✅ Migraciones aplicadas exitosamente sin conflictos
- ✅ API REST completamente operativa con filtrado avanzado
- ✅ Tests unitarios ejecutándose exitosamente (14/14)
- ✅ Serializers optimizados para nueva arquitectura
- ✅ ViewSets con consultas eficientes (select_related/prefetch_related)
- ✅ Admin interface completamente funcional
- ✅ Comandos de gestión para automatización
- ✅ Estructura organizacional de prueba creada y validada
- ✅ Endpoints verificados y respondiendo correctamente

La aplicación `our_institution` está lista para uso en producción y proporciona una base sólida para la gestión organizacional en BackboneOS.

---

© BackboneOS – Propiedad de la instancia garantizada.
