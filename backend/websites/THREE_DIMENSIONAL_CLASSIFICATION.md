# 🎯 Sistema de Clasificación Tridimensional - Websites App

## 📋 Resumen

La app `websites` implementa un sistema de clasificación tridimensional que separa claramente las diferentes dimensiones de una interacción web, evitando solapamientos y proporcionando análisis granular.

## 🏗️ Arquitectura del Sistema

### **Modelo de Datos Actualizado**

```python
# interactions/models.py - Touchpoint model
class Touchpoint(BaseUUIDModelWithActiveStatus):
    # Three-dimensional classification
    channel = models.ForeignKey(Channel, ...)      # WHERE
    medium = models.ForeignKey(Medium, ...)       # HOW  
    touchpoint_type = models.ForeignKey(TouchpointType, ...)  # WHAT
```

### **Dimensiones de Clasificación**

#### **1. Channel (WHERE) - Dónde ocurrió la interacción**
- **Propósito**: Identifica el contexto/lugar donde ocurrió la interacción
- **Ejemplos**: `esan.edu.pe`, `alpha.com`, `mobile_app`
- **Lógica**: Se determina desde la URL del sitio web donde ocurrió la interacción
- **No es**: El origen del tráfico (eso es responsabilidad del medium)

#### **2. Medium (HOW) - Cómo se comunica**
- **Propósito**: Identifica el método de comunicación
- **Ejemplos**: `organic`, `social`, `paid`, `email`, `referral`, `direct`
- **Lógica**: Se determina desde parámetros UTM, análisis de referrer, o defaults
- **Análisis**: UTM medium tiene prioridad, luego inferencia desde referrer

#### **3. TouchpointType (WHAT) - Qué tipo de touchpoint**
- **Propósito**: Identifica el tipo funcional de touchpoint (web-específico)
- **Ejemplos**: `web_page`, `web_form`, `link`, `button`, `web_download`
- **Lógica**: Se determina desde el tipo de evento, con clasificación inteligente de clicks
- **Sin solapamiento**: No se solapa con el campo `action` de `interactions.Interaction`

## 🔧 Implementación Técnica

### **WebTouchpointResolver - Lógica de Clasificación**

```python
def _get_or_create_touchpoint(self, hint: TouchpointHint) -> Touchpoint:
    # 1. Channel (WHERE) - Dónde ocurrió la interacción
    channel = self._determine_channel_from_subject(hint)
    
    # 2. Medium (HOW) - Cómo se comunica  
    medium = self._determine_medium_from_subject(hint)
    
    # 3. TouchpointType (WHAT) - Qué tipo de touchpoint
    touchpoint_type = self._get_enhanced_touchpoint_class_code(hint)
    
    # Crear touchpoint con las tres dimensiones
    touchpoint = Touchpoint.objects.create(
        channel=channel,
        medium=medium,
        touchpoint_type=touchpoint_type,
        # ... otros campos
    )
```

### **Determinación de Channel (WHERE)**

```python
def _determine_channel_from_subject(self, hint: TouchpointHint) -> str:
    """Determina el canal desde la URL del sitio web donde ocurrió la interacción"""
    # Prioridad: website_url > current_url > page_url > default
    if hint.metadata and 'website_url' in hint.metadata:
        return self._extract_domain_from_url(hint.metadata['website_url'])
    # ... más lógica
    return 'web'  # Default para interacciones web
```

### **Determinación de Medium (HOW)**

```python
def _determine_medium_from_subject(self, hint: TouchpointHint) -> str:
    """Determina el medium desde UTM y análisis de referrer"""
    # Prioridad: UTM medium > referrer analysis > default
    if hint.metadata and 'utm_medium' in hint.metadata:
        return hint.metadata['utm_medium'].lower()
    
    # Análisis de referrer para inferir medium
    if hint.metadata and 'referrer_url' in hint.metadata:
        return self._analyze_referrer_medium(hint.metadata['referrer_url'])
    
    return 'direct'  # Default
```

### **Determinación de TouchpointType (WHAT)**

```python
def _get_enhanced_touchpoint_class_code(self, hint: TouchpointHint) -> str:
    """Determina el tipo funcional de touchpoint web-específico"""
    event_type = hint.metadata.get('event_type', '') if hint.metadata else ''
    code = hint.code or ''
    
    # Mapeo a tipos web-específicos
    if 'page_view' in event_type.lower():
        return 'web_page'
    elif 'form_submit' in event_type.lower():
        return 'web_form'
    elif 'click' in event_type.lower():
        # Clasificación inteligente de clicks
        if hint.metadata and 'selector' in hint.metadata:
            selector = hint.metadata['selector']
            if 'a' in selector.lower() or 'link' in selector.lower():
                return 'link'
            elif 'button' in selector.lower() or 'btn' in selector.lower():
                return 'button'
        return 'link'  # Default para clicks
    # ... más mapeos
    
    return 'web_page'  # Default para interacciones web
```

## 📊 Ejemplos de Clasificación

### **Ejemplo 1: Página vista desde Google**
```
Interacción: "Visita a página de productos desde Google"
- Channel: "esan.edu.pe" (WHERE: ocurrió en ESAN)
- Medium: "organic" (HOW: llegó desde búsqueda orgánica)
- TouchpointType: "web_page" (WHAT: vista de página web)
```

### **Ejemplo 2: Click en botón desde Facebook**
```
Interacción: "Click en botón CTA desde Facebook"
- Channel: "alpha.com" (WHERE: ocurrió en Alpha)
- Medium: "social" (HOW: llegó desde red social)
- TouchpointType: "button" (WHAT: click en botón)
```

### **Ejemplo 3: Envío de formulario desde email**
```
Interacción: "Envío de formulario de contacto desde email"
- Channel: "esan.edu.pe" (WHERE: ocurrió en ESAN)
- Medium: "email" (HOW: llegó desde email)
- TouchpointType: "web_form" (WHAT: envío de formulario)
```

## 🔄 Migración y Compatibilidad

### **Cambios en el Modelo de Datos**

#### **Antes (Sistema Anterior):**
```python
# TouchpointClass basado en medium
touchpoint_class = TouchpointClass.objects.create(
    code='web.social_traffic',  # Se solapaba con medium
    name='Social Media Traffic'
)

# Channel con medium
channel = Channel.objects.create(
    code='facebook',
    medium=medium  # Medium estaba en Channel
)
```

#### **Ahora (Sistema Tridimensional):**
```python
# TouchpointType funcional
touchpoint_type = TouchpointType.objects.create(
    code='web_form',  # Tipo funcional, no de tráfico
    name='Web Form'
)

# Touchpoint con tres dimensiones
touchpoint = Touchpoint.objects.create(
    channel=channel,        # WHERE
    medium=medium,          # HOW
    touchpoint_type=touchpoint_type,  # WHAT
)
```

### **Actualización de Código**

#### **Resolvers Actualizados:**
- `WebTouchpointResolver._get_or_create_touchpoint()` - Implementa clasificación tridimensional
- `WebTouchpointResolver._determine_channel_from_subject()` - Determina WHERE
- `WebTouchpointResolver._determine_medium_from_subject()` - Determina HOW
- `WebTouchpointResolver._get_enhanced_touchpoint_class_code()` - Determina WHAT

#### **Tipos de TouchpointType Actualizados:**
```python
# Antes (se solapaba con action)
OLD_TYPES = ['page_view', 'form_submit', 'click', 'download']

# Ahora (web-específico, sin solapamiento)
NEW_TYPES = ['web_page', 'web_form', 'link', 'button', 'web_download']
```

## 🎯 Beneficios del Sistema Tridimensional

### **1. Análisis Granular**
- Cada dimensión puede analizarse independientemente
- Filtros y agrupaciones flexibles por cualquier dimensión
- Reporting más detallado y preciso

### **2. ML/IA Mejorado**
- Mejor extracción de features para modelos predictivos
- Separación clara de responsabilidades para algoritmos
- Datos más estructurados para análisis avanzado

### **3. Sin Solapamiento**
- TouchpointType no se solapa con el campo `action`
- Channel no se confunde con origen del tráfico
- Medium tiene su propio propósito claro

### **4. Escalabilidad**
- Fácil extensión para nuevos tipos de interacciones
- Soporte para múltiples canales y medios
- Arquitectura preparada para futuras funcionalidades

## 🧪 Testing

### **Casos de Prueba Cubiertos:**
- Clasificación tridimensional correcta
- Determinación de channel desde diferentes fuentes
- Análisis de medium desde UTM y referrer
- Clasificación inteligente de clicks (link vs button)
- Compatibilidad con datos existentes

### **Ejecutar Tests:**
```bash
# Tests específicos de clasificación tridimensional
python manage.py test websites.tests.test_three_dimensional_classification

# Tests completos de la app
python manage.py test websites
```

## 📚 Referencias

- [Interactions App - Three-Dimensional Classification](../interactions/README.md)
- [Websites App - Main Documentation](./README.md)
- [Touchpoint Resolution System](../connectors/README.md)
