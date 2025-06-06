# Interactions App - BackboneOS

La aplicación `interactions` constituye la columna vertebral del sistema CRM BackboneOS. Su propósito es registrar, analizar y contextualizar cada interacción entre la organización (que opera la instancia del CRM) y personas u organizaciones externas.

---

## Conceptos fundamentales

- **Interacción (`Interaction`)**: Unidad mínima de análisis. Representa un evento puntual entre un cliente potencial y la organización.
- **Agente (`Agent`)**: Entidad (persona, navegador, bot, etc.) que intermedia la interacción. Puede representar a alguien más o ser el operador directo.
- **Punto de contacto (`Touchpoint`)**: Infraestructura diseñada por la organización para permitir interacciones.
- **Canal (`Channel`)** y **Medio (`Medium`)**: Categorías que describen el entorno tecnológico o físico de la interacción.
- **Acción (`Action`)** y **Tipo de acción (`ActionType`)**: Describen lo que ocurrió durante la interacción.

---

## Campos clave

### En `Agent`

- `agent_type`: Define el tipo (ej. navegador, humano, AI).
- `operated_by`: Persona que maneja el agente (opcional).
- `represents_person` / `represents_organization`: Entidad representada.

### En `Touchpoint`

- `assigned_staff`: Usuario responsable del canal.
- `product`: Producto principal asociado al punto de contacto.
- `semantic segmentation`: Descriptores del segmento al que apunta.
- `funnel_stage`: Etapas estratégicas (texto plano).

### En `Interaction`

- `person` / `organization`: Cliente potencial involucrado.
- `agent`: Medio por el cual ocurre la interacción.
- `representative`: Usuario de la organización que ejecutó la acción.
- `product`: Producto relacionado (hereda de `Touchpoint` si no se define).
- `jtbd_stage`: Etapas estratégicas (texto plano).

---

## Validaciones automáticas

- Se valida que la persona/organización en `Interaction` coincida (si aplica) con la representada por el `Agent`.
- Si no se asigna `representative`, se hereda desde `Touchpoint.assigned_staff`.
- Si no se define `product`, se hereda desde `Touchpoint.product`.

---

## Fixtures incluidos

- Tipos de acción (`initial_action_types.json`)
- Acciones básicas (`initial_actions.json`)
- Canales iniciales
- Medios iniciales

---

## Consideraciones futuras

- Agregar soporte para jerarquías en `Touchpoint` y `TouchpointClass`.
- Incluir eventos derivados o automatismos según `action` o `jtbd_stage`.
- Potenciar analítica sobre desempeño por `representative` o canal.

---

Este diseño ofrece un balance entre estructura flexible y trazabilidad precisa, permitiendo el crecimiento gradual del CRM conforme a las necesidades estratégicas de la organización.
