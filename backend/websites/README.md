# 🌐 Websites App - BackboneOS

## 📋 Descripción General

La aplicación \`\` extiende el núcleo de interacciones de BackboneOS para capturar y organizar las interacciones provenientes de sitios web. Su objetivo principal es:

- Permitir registrar **interacciones web anónimas o autenticadas**.
- Asociar esas interacciones con **Touchpoint Classes** y **Touchpoints** del sistema.
- Resolver de forma flexible la URL donde ocurre una interacción.
- Dar trazabilidad entre **sitios web corporativos** y la **estructura organizacional** de la instancia CRM.

Esta app actúa como **conector especializado** para el canal digital `WWW`, integrando el tráfico web con el modelo unificado de `interactions`.

---

## 🏗️ Arquitectura de Modelos

### `Website`

Representa un sitio web gestionado por la organización.

- Campos: `name`, `base_url`, `active`.
- Relación: puede estar vinculado a una o varias divisiones de `our_institution`.
- Uso: fuente principal de los `WebSurface`.

### `WebSurface`

Entidad central que describe un **superficie direccionable por URL** (página o formulario) en el sitio web.

- Campos clave: `path`, `exact_match`, `regex`, `title`, `product`.
- Relación: posee un `Touchpoint Class` y un `Touchpoint` para integrarse con el core de interacciones.
- Propiedades: `matches(path)` para verificar coincidencia de URL.
- Flags: `is_form`, `is_thankyou` para clasificar superficies.

### `WebPage` / `WebForm`

Clases proxy que heredan de `WebSurface`.

- Propósito: ergonomía en consultas (`WebPage.objects.all()` vs `WebForm.objects.all()`).
- No generan nuevas tablas.

### `UrlRoutingRule`

Define **reglas de enrutamiento flexibles** para mapear URLs a un `WebSurface`.

- Modos: `exact`, `prefix`, `regex`.
- Campos: `pattern`, `priority`, `active`.
- Uso: resolución avanzada cuando no hay coincidencia directa con `WebSurface`.

### `SurfaceResolver`

Servicio helper que resuelve dinámicamente un `path` a un `WebSurface`.

- Paso 1: intenta coincidencia directa (`WebSurface.matches`).
- Paso 2: recurre a `UrlRoutingRule` activas.
- Devuelve el `WebSurface` encontrado o `None`.

---

## 🔗 Integración con Interactions App

La app `websites` **no duplica** datos ya presentes en `interactions.Interaction`.

- Cada `WebSurface` **posee** un `Touchpoint`, por lo que cualquier `Interaction` que ocurra allí se enlaza directamente.
- El \*\*canal \*\*\`\` se crea automáticamente si no existe.
- Los eventos específicos (p.ej. `page_read`, `form_submit`) se representan como `Action` en el core.

Esto asegura que:

- Las interacciones web sean **compatibles** con cualquier otra fuente de interacciones.
- La analítica y reporting se unifiquen.

---

## ⚡ Flujo de Resolución y Registro de Interacciones

1. Llega una petición desde el tracker web (ejemplo: visita a `/products/crm`).
2. `SurfaceResolver.resolve(website, path)` intenta localizar un `WebSurface`.
   - Si existe, devuelve su instancia.
   - Si no existe, opcionalmente se puede crear una superficie dinámica (configurable).
3. Se asegura la existencia del `Touchpoint` vía `WebSurface.ensure_tpi()`.
4. Se crea un `Interaction` enlazando:
   - `touchpoint_class` / `touchpoint`
   - `channel=WWW`
   - `action` según evento (`page_read`, `form_submit`)
   - `agent` (ej. navegador identificado)

---

## 📊 Casos de Uso

### 1. Medición de Páginas Estratégicas

- Definir `WebSurface` para páginas clave del producto.
- Registrar cuántas interacciones ocurren y con qué agentes.

### 2. Seguimiento de Formularios

- Marcar `is_form=True` para distinguir formularios.
- Capturar `form_submit` como acción.
- Relacionar formularios con `products` u `offers`.

### 3. Resolución Flexible de URLs

- Usar `UrlRoutingRule` para mapear rutas dinámicas.
- Ejemplo: `/blog/*` redirige a un `WebSurface` de tipo blog.

### 4. Analytics Integrado

- Agrupar interacciones web con otros canales (email, eventos presenciales, etc.).
- Analizar recorrido de usuario cross-channel.

---

## 🔮 Extensiones Futuras

- **Creación automática** de `WebSurface` al recibir interacciones en paths desconocidos.
- **Soporte multi-dominio**: permitir `Website` con múltiples `base_url`.
- **Metadata enriquecida**: registrar parámetros UTM, campañas, experimentos A/B.
- **UI de mapeo visual**: administrar `WebSurfaces` y `UrlRoutingRules` desde el panel.

---

## 📁 Estructura de Archivos

```
websites/
├── models.py              # Modelos Website, WebSurface, UrlRoutingRule
├── admin.py               # Configuración admin
├── serializers.py         # Serializers para API REST
├── views.py               # ViewSets y lógica de API
├── urls.py                # Rutas API REST
├── tests.py               # Tests unitarios y de integración
├── README.md              # Esta documentación
└── migrations/            # Migraciones iniciales
```

---

## 🎯 Valor para BackboneOS

La app `websites` convierte la **actividad anónima de la web** en interacciones trazables dentro del CRM, cerrando la brecha entre **marketing digital** y **gestión de clientes**:

- **Unificación de canales** bajo el modelo de interacciones.
- **Rastreo semántico** conectado a productos y ofertas.
- **Flexibilidad** para múltiples estructuras organizacionales.
- **Escalabilidad** para soportar reglas de enrutamiento y superficies dinámicas.

👉 En conclusión, `websites` es el puente entre el **tráfico web** y el **ecosistema CRM** de BackboneOS.

