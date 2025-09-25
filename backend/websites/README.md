# 🌐 Websites App - BackboneOS

## 📋 Descripción General

La aplicación `websites` extiende el núcleo de interacciones de BackboneOS para capturar y organizar las interacciones provenientes de sitios web. Su objetivo principal es:

- Permitir registrar **interacciones web anónimas o autenticadas**.
- Asociar esas interacciones con **Touchpoint Classes** y **Touchpoints** del sistema.
- Resolver de forma flexible la URL donde ocurre una interacción.
- Dar trazabilidad entre **sitios web corporativos** y la **estructura organizacional** de la instancia CRM.
- **Resolución automática de touchpoints** con análisis avanzado de tráfico (UTM, referrer, user agent).

Esta app actúa como **conector especializado** para el canal digital `WWW`, integrando el tráfico web con el modelo unificado de `interactions` y el **sistema de resolución de touchpoints**.

## 🎉 Estado: IMPLEMENTACIÓN COMPLETADA

### ✅ Sistema de Resolución de Touchpoints con Clasificación Tridimensional
- **Resolución automática**: Touchpoints creados automáticamente al guardar `WebInteraction`
- **Clasificación tridimensional**: Channel (WHERE), Medium (HOW), TouchpointType (WHAT)
- **Canales específicos por sitio**: Códigos de canal basados en dominio (ej: `alpha.com`, `esan.edu.pe`)
- **Análisis de tráfico mejorado**: UTM, referrer, y análisis de user agent
- **Tipos de touchpoint web-específicos**: `web_page`, `web_form`, `link`, `button` (sin solapamiento con action)
- **Detección de apps nativas**: Análisis de user agent para tráfico de apps móviles
- **Cobertura de pruebas**: 28 tests pasando con cobertura completa

---

## 🎯 Sistema de Clasificación Tridimensional

La app `websites` implementa un sistema de clasificación tridimensional que separa claramente las diferentes dimensiones de una interacción web:

### **Channel (WHERE) - Dónde ocurrió la interacción**
- **Propósito**: Identifica el contexto/lugar donde ocurrió la interacción
- **Ejemplos**: `esan.edu.pe`, `alpha.com`, `mobile_app`
- **Lógica**: Se determina desde la URL del sitio web donde ocurrió la interacción
- **No es**: El origen del tráfico (eso es responsabilidad del medium)

### **Medium (HOW) - Cómo se comunica**
- **Propósito**: Identifica el método de comunicación
- **Ejemplos**: `organic`, `social`, `paid`, `email`, `referral`, `direct`
- **Lógica**: Se determina desde parámetros UTM, análisis de referrer, o defaults
- **Análisis**: UTM medium tiene prioridad, luego inferencia desde referrer

### **TouchpointType (WHAT) - Qué tipo de touchpoint**
- **Propósito**: Identifica el tipo funcional de touchpoint (web-específico)
- **Ejemplos**: `web_page`, `web_form`, `link`, `button`, `web_download`
- **Lógica**: Se determina desde el tipo de evento, con clasificación inteligente de clicks
- **Sin solapamiento**: No se solapa con el campo `action` de `interactions.Interaction`

### **Ejemplo de Clasificación Completa:**
```
Interacción: "Envío de formulario de contacto en ESAN"
- Channel: "esan.edu.pe" (WHERE: ocurrió en el sitio de ESAN)
- Medium: "organic" (HOW: llegó desde búsqueda orgánica)
- TouchpointType: "web_form" (WHAT: envío de formulario web)
```

### **Beneficios del Sistema Tridimensional:**
- **Análisis granular**: Cada dimensión puede analizarse independientemente
- **ML/IA mejorado**: Mejor extracción de features para modelos predictivos
- **Reporting flexible**: Agrupaciones y filtros por cualquier dimensión
- **Sin solapamiento**: Separación clara de responsabilidades
- **Escalabilidad**: Fácil extensión para nuevos tipos de interacciones

> 📖 **Documentación Técnica Detallada**: Ver [THREE_DIMENSIONAL_CLASSIFICATION.md](./THREE_DIMENSIONAL_CLASSIFICATION.md) para implementación técnica completa, ejemplos de código, y guía de migración.

---

## 🔧 Sistema de Resolución de Touchpoints

### **WebTouchpointResolver**
Resolvedor especializado que extiende el framework genérico con lógica específica para web:

- **Clasificación tridimensional**: Implementa Channel (WHERE), Medium (HOW), TouchpointType (WHAT)
- **Análisis UTM**: Prioriza parámetros UTM para determinar medium de comunicación
- **Análisis de referrer**: Detecta tráfico orgánico, social, y de referencia para medium
- **Análisis de user agent**: Identifica tráfico de apps nativas y WebViews
- **Canales específicos por sitio**: Usa el dominio del sitio web como código de canal (WHERE)
- **Tipos web-específicos**: TouchpointType basado en funcionalidad web (`web_page`, `web_form`, `link`, `button`)
- **Clasificación inteligente de clicks**: Distingue entre `link` y `button` basado en selector

### **WebMappingProvider**
Proveedor de reglas de mapeo específico para web:

- **Identificación de fuente**: Extrae URL del sitio web como identificador
- **Reglas configurables**: Permite override de comportamiento por sitio web
- **Cache optimizado**: Mejora rendimiento con cache de reglas de mapeo

### **WebTouchpointAdapter**
Adaptador que implementa la inferencia de touchpoints:

- **Mapeo de eventos**: Convierte tipos de evento web a códigos de touchpoint
- **Análisis de contexto**: Extrae información de UTM, referrer, y user agent
- **Metadatos enriquecidos**: Incluye información contextual en el hint

### **Flujo de Resolución**
1. `WebInteraction.save()` → `_ensure_touchpoint()`
2. `infer_touchpoint_hint()` → Crea hint con análisis especializado
3. `WebTouchpointResolver.resolve()` → Aplica reglas y crea touchpoint
4. Touchpoint asignado automáticamente a la interacción

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

### `WebInteraction`

Modelo que extiende `AbstractConnectorInteraction` e implementa `TouchpointInferenceProtocol`:

- **Campos de navegador**: `session_id`, `visitor_cookie`, `user_agent`, `client_hints`, `ip`
- **Atribución UTM**: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
- **Eventos**: `element`, `payload`, `is_bot`
- **Resolución automática**: Implementa `infer_touchpoint_hint()` y `_ensure_touchpoint()`
- **Integración**: Se conecta automáticamente con el sistema de touchpoints

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

La app `websites` **no duplica** datos ya presentes en `interactions.Interaction` y ahora incluye **resolución automática de touchpoints**.

### **Integración Tradicional**
- Cada `WebSurface` **posee** un `Touchpoint`, por lo que cualquier `Interaction` que ocurra allí se enlaza directamente.
- El canal `web` se crea automáticamente si no existe.
- Los eventos específicos (p.ej. `page_read`, `form_submit`) se representan como `Action` en el core.

### **Nueva Integración con Touchpoint Resolution**
- **Resolución automática**: `WebInteraction` crea touchpoints automáticamente al guardarse
- **Canales específicos por sitio**: Cada sitio web tiene su propio canal (ej: `alpha.com`, `esan.edu.pe`)
- **Análisis de tráfico**: UTM, referrer, y user agent se analizan para determinar el medio
- **Clasificación semántica**: TouchpointClass basado en medio de tráfico (ej: `web.social_traffic`)
- **Diferenciación de canales**: Distinción entre canal de captura vs. canal de origen

Esto asegura que:

- Las interacciones web sean **compatibles** con cualquier otra fuente de interacciones.
- La analítica y reporting se unifiquen.
- **Mejor atribución**: Análisis avanzado de tráfico para mejor comprensión del customer journey.

---

## ⚡ Flujo de Resolución y Registro de Interacciones

### **Flujo Tradicional**
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

### **Nuevo Flujo con Clasificación Tridimensional**
1. Se crea un `WebInteraction` con datos de navegador, UTM, referrer, etc.
2. `WebInteraction.save()` → `_ensure_touchpoint()` se ejecuta automáticamente
3. `infer_touchpoint_hint()` analiza el contexto y crea un hint especializado
4. `WebTouchpointResolver.resolve()` aplica reglas y crea el touchpoint con clasificación tridimensional:
   - **Channel (WHERE)**: Determina desde URL del sitio web donde ocurrió la interacción
   - **Medium (HOW)**: Análisis UTM y referrer para determinar método de comunicación
   - **TouchpointType (WHAT)**: Tipo funcional web-específico (`web_page`, `web_form`, `link`, `button`)
   - **Clasificación inteligente**: Distingue entre `link` y `button` basado en selector
5. Touchpoint se asigna automáticamente a la interacción con las tres dimensiones

---

## 🔄 Cambios Recientes y Migración

### **Actualización del Sistema de Clasificación (Enero 2025)**

La app `websites` ha sido actualizada para implementar el nuevo sistema de clasificación tridimensional del core `interactions`:

#### **Cambios en el Modelo de Datos:**
- **Medium movido**: De `Channel` a `Touchpoint` para mejor separación de responsabilidades
- **TouchpointClass → TouchpointType**: Renombrado para mayor claridad
- **Relaciones actualizadas**: Touchpoint ahora tiene `channel`, `medium`, y `touchpoint_type`

#### **Cambios en la Lógica de Clasificación:**
- **Channel**: Ahora representa WHERE ocurrió la interacción (sitio web), no el origen del tráfico
- **Medium**: Representa HOW se comunica (organic, social, paid, etc.)
- **TouchpointType**: Tipos web-específicos que no se solapan con el campo `action`

#### **Tipos de TouchpointType Actualizados:**
```python
# Antes (se solapaba con action)
'page_view', 'form_submit', 'click', 'download'

# Ahora (web-específico, sin solapamiento)
'web_page', 'web_form', 'link', 'button', 'web_download'
```

#### **Migración Automática:**
- Las migraciones existentes han sido actualizadas
- El sistema es compatible con datos existentes
- No se requiere intervención manual

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

## 🧪 Testing y Calidad

### **Cobertura de Pruebas**
- **28 tests pasando**: Cobertura completa de toda la funcionalidad
- **Tests de modelos**: Website, WebSurface, WebInteraction
- **Tests de resolvers**: WebTouchpointResolver con todos los escenarios
- **Tests de adapters**: WebTouchpointAdapter con diferentes tipos de eventos
- **Tests de integración**: Flujo completo de resolución de touchpoints
- **Tests de mapping providers**: WebMappingProvider y cache

### **Escenarios de Prueba**
- **Análisis UTM**: Diferentes combinaciones de parámetros UTM
- **Análisis de referrer**: Tráfico orgánico, social, de referencia
- **Análisis de user agent**: Apps nativas, WebViews, navegadores
- **Canales específicos**: Diferentes dominios de sitios web
- **Clasificación semántica**: Diferentes medios de tráfico
- **Resolución automática**: Creación automática de touchpoints

## 📁 Estructura de Archivos

```
websites/
├── models.py              # Modelos Website, WebSurface, WebInteraction, UrlRoutingRule
├── resolvers.py           # WebTouchpointResolver y CachedWebTouchpointResolver
├── mapping_providers.py   # WebMappingProvider y CachedWebMappingProvider
├── adapters.py            # WebTouchpointAdapter (infer_web_touchpoint_hint)
├── admin.py               # Configuración admin
├── serializers.py         # Serializers para API REST
├── views.py               # ViewSets y lógica de API
├── urls.py                # Rutas API REST
├── tests.py               # 28 tests unitarios y de integración
├── README.md              # Esta documentación
├── THREE_DIMENSIONAL_CLASSIFICATION.md  # Documentación técnica detallada
└── migrations/            # Migraciones iniciales
```

---

## 🎯 Valor para BackboneOS

La app `websites` convierte la **actividad anónima de la web** en interacciones trazables dentro del CRM, cerrando la brecha entre **marketing digital** y **gestión de clientes**:

### **Valor Tradicional**
- **Unificación de canales** bajo el modelo de interacciones.
- **Rastreo semántico** conectado a productos y ofertas.
- **Flexibilidad** para múltiples estructuras organizacionales.
- **Escalabilidad** para soportar reglas de enrutamiento y superficies dinámicas.

### **Nuevo Valor con Touchpoint Resolution**
- **Resolución automática**: Touchpoints creados automáticamente sin intervención manual
- **Atribución avanzada**: Análisis de UTM, referrer, y user agent para mejor comprensión del tráfico
- **Canales específicos**: Cada sitio web tiene su propio canal para análisis granular
- **Clasificación semántica**: TouchpointClass basado en medio de tráfico para mejor categorización
- **Detección de apps nativas**: Identificación de tráfico de apps móviles vs. navegadores web
- **Diferenciación de canales**: Distinción entre canal de captura vs. canal de origen
- **Mejor customer journey**: Comprensión más profunda del recorrido del cliente

👉 En conclusión, `websites` es el puente entre el **tráfico web** y el **ecosistema CRM** de BackboneOS, ahora con capacidades avanzadas de análisis y resolución automática de touchpoints.

