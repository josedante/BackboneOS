# 📋 Aplicación `sales`

La aplicación `sales` define los modelos vinculados a la gestión de oportunidades, sesiones comerciales y listas de contacto para fines de seguimiento y conversión dentro del CRM BackboneOS.

---

## 🔍 Modelos principales

### `SalesOpportunity`

Representa una oportunidad comercial con una persona y/u organización interesada en un producto determinado.

**Campos clave:**

- `person`, `organization`: cliente potencial.
- `product`, `offering`: producto y oferta asociada.
- `expected_value`, `currency_code`: valor esperado.
- `stage`: etapa del ciclo comercial (`new`, `interested`, `evaluating`, `won`, `lost`, etc.).
- `source`, `source_detail`: canal declarado de origen.
- `channel`: canal de ventas (se infiere si no se especifica).
- `representative`: usuario del staff responsable.

**Reglas automáticas:**

- Si no se especifica un canal, se intenta inferir desde la última interacción relevante o desde la división del producto.
- El campo `expected_closing_date` es obligatorio si el estado es `won`.
- El campo `notes` es obligatorio si el estado es `lost`.

---

### `SalesSession`

Subclase de `Interaction` que registra sesiones de contacto comerciales.

**Campos clave:**

- `opportunity`: oportunidad asociada.
- `representative`: usuario responsable de la sesión.
- `contacted_via`, `initiated_by`: medio de contacto y origen de la sesión.
- `how_long`: duración.
- `lead_state`, `progress`: estado del cliente.
- `outcome`, `notes`, `metadata`.

**Comportamiento automático:**

- Se crea o reutiliza una instancia de `TouchpointInstance` adecuada al medio y producto.
- Si no hay canal definido, se sugiere uno según la división del producto.

---

### `SalesSource`

Catálogo editable de fuentes declaradas de oportunidades:

- `code`, `label`: identificación de la fuente.
- `group`: agrupación por tipo (web, email, call, etc.).

---

### `ContactList`

Representa una lista de oportunidades filtradas para seguimiento comercial.

**Campos clave:**

- `product`, `offering`: contexto de la lista.
- `created_by`: staff creador.
- `filters`: campo JSON con reglas flexibles.
- `build_in_background`, `building_task_uuid`: soporte opcional para construcción en segundo plano.

**Importante:**

- El campo `filters` contiene las reglas de selección. No hay campos fijos predefinidos.
- La propiedad `members` debe implementarse manualmente según la semántica del `filters` en cada caso de uso.

---

## 📈 Siguientes pasos sugeridos

- Interfaz visual de construcción de `ContactList`.
- Soporte para campañas vinculadas a listas.
- Métricas automáticas de conversión por etapa.
- Reglas de automatización para mover oportunidades entre etapas.
- Integración con `LeadEngagement` (futura app) para gestión longitudinal.
