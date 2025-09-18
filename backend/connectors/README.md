# 🌐 App Connectors – Framework de Integración de Canales Externos

## 🎯 Propósito

La aplicación `connectors` es el **framework abstracto de integración de BackboneOS**. Su objetivo es:

* Proporcionar una **base común** para todos los conectores de canales externos.
* Establecer **patrones consistentes** para extender interacciones con datos específicos de cada canal.
* Mantener una arquitectura extensible con **modelos abstractos** que otros conectores pueden heredar.
* Permitir tanto el tracking de visitantes anónimos como la **desanonimización progresiva** (cuando llenan formularios o son reconocidos en otra app).

> **Nota**: Esta app proporciona el framework base. Las implementaciones concretas se encuentran en apps especializadas como `websites`, `emails`, etc.

---

## 🏗️ Arquitectura

### Modelo Base Abstracto

```python
class AbstractConnectorInteraction(models.Model):
    interaction = models.OneToOneField(
        'interactions.Interaction',
        on_delete=models.CASCADE,
        related_name="%(class)s",  # Dynamic related_name based on subclass
        primary_key=True,
    )
    
    # Active status field
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

    # Helper properties for accessing related data
    @property
    def action_code(self) -> str:
        return getattr(self.interaction.action, "code", "")

    @property
    def touchpoint(self):
        return getattr(self.interaction, "touchpoint", None)

    @property
    def person(self):
        return getattr(self.interaction, "person", None)

    @property
    def organization(self):
        return getattr(self.interaction, "organization", None)
```

* Define una relación **1 a 1 con `Interaction`** usando el campo `interaction` como clave primaria.
* Sirve como **superclase** para todos los conectores especializados.
* Proporciona **propiedades helper** para acceder fácilmente a datos relacionados.
* Incluye campo `is_active` para control de estado.

### Implementaciones Especializadas

#### Websites App (Implementación Completa)

La app `websites` implementa un conector completo para interacciones web:

```python
# En websites/models.py
class WebInteraction(AbstractConnectorInteraction):
    website = models.ForeignKey(Website, on_delete=models.CASCADE, related_name="events")
    
    # Browser identity
    session_id = models.CharField(max_length=64, db_index=True, blank=True, default="")
    visitor_cookie = models.CharField(max_length=64, db_index=True, blank=True, default="")
    user_agent = models.TextField(blank=True, default="")
    client_hints = models.JSONField(default=dict, blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    
    # UTM Attribution
    utm_source = models.CharField(max_length=100, blank=True, default="")
    utm_medium = models.CharField(max_length=100, blank=True, default="")
    utm_campaign = models.CharField(max_length=150, blank=True, default="")
    # ... más campos UTM
    
    # Event extras
    element = models.CharField(max_length=200, blank=True, default="")
    payload = models.JSONField(default=dict, blank=True)
```

**Características de la implementación websites:**
* **Integración completa** con `TouchPoint` y `TouchPointClass`
* **Resolución automática** de URLs a `WebSurface`
* **API REST** para ingestión de eventos web
* **Soporte UTM** para tracking de campañas
* **Sistema de routing** flexible para URLs

#### Futuras Implementaciones

```python
# Ejemplo: Email Connector (futuro)
class EmailInteraction(AbstractConnectorInteraction):
    email_provider = models.CharField(max_length=50)  # Gmail, Outlook, etc.
    message_id = models.CharField(max_length=255)
    subject = models.TextField(blank=True)
    recipient = models.EmailField()
    # ... más campos específicos de email
```

---

## 🔗 Integraciones con otras Apps

* **`interactions`**: base de todas las interacciones (herencia vía `OneToOne`).
* **`websites`**: implementación concreta del conector web con `WebInteraction`.
* **`our_institution`**: estructura organizacional para asociar conectores con divisiones.
* **`entities`**: posible desanonimización al asociar visitantes con `Person` u `Organization`.
* **`world`**: tagging semántico para categorizar interacciones externas.

---

## 📊 Casos de Uso

### 1. Crear un Nuevo Conector

```python
# Ejemplo: Conector de WhatsApp
class WhatsAppInteraction(AbstractConnectorInteraction):
    phone_number = models.CharField(max_length=20)
    message_type = models.CharField(max_length=20)  # text, image, document
    message_content = models.TextField(blank=True)
    whatsapp_message_id = models.CharField(max_length=255)
    
    class Meta:
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['whatsapp_message_id']),
        ]
```

### 2. Usar Propiedades Helper

```python
# Acceder a datos relacionados fácilmente
web_interaction = WebInteraction.objects.select_related('interaction').first()

# Usar propiedades helper del framework base
print(web_interaction.action_code)  # "page_view"
print(web_interaction.person)       # Person object or None
print(web_interaction.touchpoint)   # Touchpoint object
print(web_interaction.occurred_at)  # datetime
```

### 3. Queries Estandarizadas

```python
# Todos los WebInteractions activos
WebInteraction.objects.filter(is_active=True)

# Interacciones web con persona asociada
WebInteraction.objects.filter(
    is_active=True,
    interaction__person__isnull=False
).select_related('interaction__person')

# Interacciones por canal
WebInteraction.objects.filter(
    interaction__channel__code='WWW'
)
```

---

## ⚡ Performance

* **Clave primaria optimizada**: Usa el campo `interaction` como PK, evitando joins innecesarios.
* **Propiedades helper**: Acceso directo a datos relacionados sin consultas adicionales.
* **Índices estratégicos**: Cada implementación puede definir sus propios índices según necesidades.
* **Sin duplicación de datos**: Los datos core se mantienen en `Interaction`, los específicos en el conector.

---

## 🚀 Roadmap

* [ ] Conector de **Emails** (apertura, click, bounce).
* [ ] Conector de **WhatsApp / Chat** (mensajes entrantes/salientes).
* [ ] Conector de **CRM externos** (Zoho, HubSpot, etc.).
* [ ] **Webhooks universales** para ingestión de datos.
* [ ] **Consentimiento GDPR/CCPA** ligado a interacciones capturadas.

---

## ✅ Estado

* ✅ **Framework base implementado**: `AbstractConnectorInteraction` con propiedades helper.
* ✅ **Websites app integrada**: `WebInteraction` hereda correctamente del framework base.
* ✅ **Sin conflictos de PK**: Arquitectura limpia sin duplicación de claves primarias.
* ✅ **Importación funcional**: `connectors.base` exporta correctamente la clase base.
* 🔌 **Preparado para expansión**: Framework listo para nuevos conectores (email, WhatsApp, etc.).
* 🧩 **Arquitectura alineada**: Integración completa con apps `interactions`, `websites` y `our_institution`.

---

## 📁 Estructura de Archivos

```
connectors/
├── models.py              # AbstractConnectorInteraction base class
├── base.py                # Re-export for backward compatibility
├── proxies.py             # Proxy utilities (optional)
├── admin.py               # Admin configuration
├── apps.py                # App configuration
├── README.md              # Esta documentación
└── migrations/            # Migraciones (vacías - modelo abstracto)
```

---

## 🎯 Valor para BackboneOS

El framework `connectors` proporciona una **base sólida y consistente** para todos los conectores de canales externos:

* **Consistencia**: Todos los conectores siguen el mismo patrón de herencia.
* **Flexibilidad**: Cada conector puede agregar campos específicos sin afectar otros.
* **Performance**: Clave primaria optimizada y propiedades helper eficientes.
* **Mantenibilidad**: Código base centralizado con implementaciones especializadas.
* **Escalabilidad**: Fácil agregar nuevos tipos de conectores siguiendo el patrón establecido.