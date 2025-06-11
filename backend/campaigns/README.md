# 🎯 App Campaigns - Sistema de Gestión de Campañas Comerciales

## ✅ Propósito

La app `campaigns` gestiona campañas comerciales, entendidas como **estructuras organizadas y planificadas** para promocionar productos o servicios a través de múltiples canales y puntos de contacto.

Una campaña:

- Tiene una **intención estratégica** (segmentos, industrias, temporalidad, presupuesto).
- Se articula mediante **canales y touchpoints**.
- Puede tener **subcampañas** como unidades operativas independientes.
- Se integra con el campo semántico de BackboneOS para facilitar targeting y análisis.

---

## 🧱 Modelos Principales

### `Campaign`

Representa una iniciativa de marketing o ventas con alcance definido.

```python
class Campaign(models.Model):
    ...
```

#### Características clave:

- Identificación: `name`, `code`
- Temporalidad: `start_date`, `end_date`
- Presupuesto: `budget`
- Organización: `division`, `team`
- Segmentación semántica: `target_segments`, `related_industries`, etc.
- Canales: `channels` (ManyToMany con `interactions.Channel`)
- Jerarquía: `parent` (para modelar subcampañas)
- Metadatos: `metadata` (flexibilidad futura)
- Propiedad útil: `is_active_now`

---

### `CampaignTouchpoint`

Define la **relación entre una campaña y un punto de contacto específico**.

```python
class CampaignTouchpoint(models.Model):
    ...
```

#### Campos relevantes:

- `campaign`: FK a Campaign
- `touchpoint`: FK a `interactions.Touchpoint`
- `weight`: importancia relativa dentro de la campaña
- `priority`: orden propuesto
- `expected_conversions`, `budget_allocated`: variables de planificación
- `metadata`: para reglas o flags adicionales

#### Propiedades:

- `is_product_targeted`: si el touchpoint y la campaña apuntan al mismo producto
- `is_cross_product`: si hay cruce de productos

---

## 🌐 Relaciones con otras Apps

| App               | Relación                            | Propósito                               |
| ----------------- | ----------------------------------- | --------------------------------------- |
| `interactions`    | Channel, Touchpoint                 | Puntos de ejecución de la campaña       |
| `products`        | (implícito a través de touchpoints) | Producto objeto de promoción o análisis |
| `our_institution` | Division, Team                      | Organización responsable de la campaña  |
| `world`           | Industry, Function, Segment, etc.   | Segmentación semántica                  |

---

## 🤠 Diseño semántico

La app está pensada para:

- **Planificar campañas**: con canales, objetivos, segmentos, presupuesto.
- **Organizarlas jerárquicamente**: campañas madre e hijas.
- **Relacionarlas con ejecución real**: sin asumir que todos los touchpoints usados son los planeados.
- Preparar el terreno para una **app de performance o analítica**, sin mezclar funciones.

---

## 🔮 Roadmap Sugerido

- CRUD de campañas
- Planeamiento de subcampañas
- Asignación de touchpoints
- Relación con `ProductOffering`
- Editor de metadatos
- Exportación analítica
- Integración con `campaign_performance`
- A/B testing
- Visualización jerárquica

---
