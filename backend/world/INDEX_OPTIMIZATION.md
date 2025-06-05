# Optimización de Índices - App World

## Resumen de Optimizaciones Realizadas

Este documento describe las optimizaciones de índices aplicadas a los modelos de la app `world` para mejorar el rendimiento de las consultas más comunes.

## Metodología de Análisis

Se revisaron los siguientes archivos para identificar patrones de consulta:

- `views.py` - ViewSets y filtros utilizados
- `admin.py` - Campos de búsqueda y filtros del admin
- `serializers.py` - Campos relacionados y consultas join
- Frontend - Patrones de uso en componentes Vue

## Índices Añadidos por Modelo

### 1. Country

**Campos indexados:**

- `is_active` - Filtro principal en todas las consultas
- `name` - Búsquedas de texto y ordenamiento
- `is_active, name` - Índice compuesto para consultas frecuentes
- `timezone` - Filtros por zona horaria
- `currency_code` - Filtros por moneda

**Justificación:** País es un modelo de referencia usado frecuentemente en selects y filtros.

### 2. Industry

**Campos indexados:**

- `is_active` - Filtro estándar
- `parent` - Consultas jerárquicas frecuentes
- `is_active, parent` - Filtros combinados para estructuras activas
- `display_order, name` - Ordenamiento principal
- `ciiu_code` - Búsquedas por código CIIU
- `name`, `code` - Búsquedas de texto

**Justificación:** Modelo jerárquico con consultas complejas para árboles de industrias.

### 3. FunctionOrResponsibility

**Campos indexados:**

- `is_active` - Filtro estándar
- `parent` - Navegación jerárquica
- `is_active, parent` - Filtros combinados
- `typical_level` - Filtros por nivel organizacional
- `display_order, name` - Ordenamiento
- `name`, `code` - Búsquedas

**Justificación:** Estructura jerárquica similar a Industry con filtros adicionales por nivel.

### 4. Skill

**Campos indexados:**

- `is_active` - Filtro estándar
- `skill_type` - Filtro principal por tipo de habilidad
- `typical_level_required` - Filtros por nivel requerido
- `skill_type, display_order, name` - Ordenamiento completo
- `is_active, skill_type` - Filtros combinados más frecuentes
- `name`, `code` - Búsquedas

**Justificación:** Modelo con categorización múltiple (tipo y nivel) usado en filtros complejos.

### 5. PersonalIDType & OrganizationalIDType

**Campos indexados:**

- `is_active` - Filtro estándar
- `country` - Relación principal (FK)
- `is_active, country` - Filtros combinados frecuentes
- `country, display_order, name` - Ordenamiento por país
- `name`, `code` - Búsquedas

**Justificación:** Modelos relacionados con Country, filtrados frecuentemente por país.

### 6. OrganizationType

**Campos indexados:**

- `is_active` - Filtro estándar
- `ownership_type` - Clasificación principal
- `typical_size` - Filtro secundario
- `is_active, ownership_type` - Combinación más frecuente
- `display_order, name` - Ordenamiento
- `name`, `code` - Búsquedas

**Justificación:** Modelo con clasificaciones múltiples usado en formularios de registro.

### 7. DescriptorFamily

**Campos indexados:**

- `is_active` - Filtro estándar
- `name` - Búsquedas y ordenamiento
- `is_active, name` - Combinación frecuente

**Justificación:** Modelo de referencia simple pero usado frecuentemente.

### 8. WorldDescriptor

**Campos indexados:**

- `is_active` - Filtro estándar
- `family` - Relación principal (FK)
- `parent` - Navegación jerárquica opcional
- `is_active, family` - Filtros combinados principales
- `family, name` - Ordenamiento por familia
- `family, parent` - Navegación jerárquica por familia
- `name`, `code` - Búsquedas

**Justificación:** Modelo complejo con relaciones múltiples y estructura jerárquica opcional.

### 9. MarketSegment

**Campos indexados:**

- `is_active` - Filtro estándar
- `segment_type` - Clasificación principal (B2B, B2C, B2G)
- `is_active, segment_type` - Filtros combinados frecuentes
- `display_order, name` - Ordenamiento
- `name`, `code` - Búsquedas

**Justificación:** Modelo con clasificación tipo segmento y relaciones M2M múltiples.

### 10. Tag

**Campos indexados:**

- `is_active` - Filtro estándar
- `name` - Búsquedas de texto
- `is_active, name` - Combinación frecuente
- `created_at`, `updated_at` - Filtros temporales para actividad reciente

**Justificación:** Tags son buscados frecuentemente y ordenados por actividad.

### 11. AcademicDegree

**Campos indexados:**

- `is_active` - Filtro estándar
- `code` - Ordenamiento principal (numérico)
- `name` - Búsquedas
- `is_active, code` - Ordenamiento filtrado

**Justificación:** Modelo de referencia ordenado por código numérico.

### 12. Position

**Campos indexados:**

- `is_active` - Filtro estándar
- `name` - Ordenamiento principal y búsquedas
- `code` - Búsquedas por código
- `is_active, name` - Ordenamiento filtrado

**Justificación:** Modelo de referencia simple ordenado alfabéticamente.

## Beneficios Esperados

### Rendimiento de Consultas

1. **Filtros por `is_active`**: Todas las consultas de objetos activos serán más rápidas
2. **Búsquedas de texto**: Búsquedas por name/code optimizadas
3. **Consultas jerárquicas**: Navegación parent/child más eficiente
4. **Filtros combinados**: Consultas con múltiples condiciones optimizadas
5. **Ordenamiento**: Consultas ordenadas por display_order/name más rápidas

### Casos de Uso Específicos

- **Admin Django**: Filtros y búsquedas en el panel administrativo
- **API REST**: Endpoints con filtros múltiples
- **Frontend**: Selects y autocompletes más responsivos
- **Formularios**: Carga rápida de opciones en dropdowns

## Consideraciones de Mantenimiento

### Espacio en Disco

- Los índices añadidos aumentan el tamaño de la base de datos
- Índices compuestos son más eficientes que múltiples índices simples
- Se priorizaron los filtros más frecuentes

### Actualizaciones

- Los índices pueden ralentizar INSERT/UPDATE
- El impacto es mínimo dado que estos son modelos de referencia (pocas escrituras)
- Los beneficios en consultas superan el costo de mantenimiento

## Migración Aplicada

- **Archivo**: `0002_academicdegree_world_acade_is_acti_c4ce00_idx_and_more.py`
- **Total de índices**: 65 índices nuevos
- **Estado**: ✅ Aplicada exitosamente

## Monitoreo Recomendado

1. **Uso de índices**: Revisar estadísticas de PostgreSQL para confirmar uso
2. **Rendimiento de consultas**: Comparar tiempos antes/después
3. **Tamaño de DB**: Monitorear crecimiento del espacio usado
4. **Consultas lentas**: Identificar oportunidades adicionales de optimización

---

_Optimización realizada el 5 de junio de 2025_
_BackboneOS - World App Database Optimization_
