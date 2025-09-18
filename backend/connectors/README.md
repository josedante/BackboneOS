# 🌐 App Connectors – Integración de Canales y Sistemas Externos

## 🎯 Propósito

La aplicación `connectors` es la **capa de integración de BackboneOS**. Su objetivo es:

* Capturar interacciones de **fuentes externas** (websites, formularios, APIs, etc.).
* Transformarlas en **interacciones estandarizadas** (`interactions.Interaction`).
* Mantener una arquitectura extensible con **modelos abstractos y proxies** para cada tipo de conector.
* Permitir tanto el tracking de visitantes anónimos como la **desanonimización progresiva** (cuando llenan formularios o son reconocidos en otra app).

---

## 🏗️ Arquitectura

### Modelo Base Abstracto

```python
class AbstractConnectorInteraction(models.Model):
    interaction = models.OneToOneField(
        'interactions.Interaction',
        on_delete=models.CASCADE,
        related_name="%(class)s",
    )

    class Meta:
        abstract = True
```

* Define una relación **1 a 1 con `Interaction`**.
* Sirve como **superclase** para todos los conectores.
* Aporta consistencia: cualquier conector puede consultarse con `select_related("interaction")`.

### Conector de Websites

```python
class WebInteraction(AbstractConnectorInteraction):
    website = models.ForeignKey(
        'our_institution.Division',
        on_delete=models.CASCADE,
        related_name="web_interactions"
    )
    url = models.URLField()
    referrer = models.URLField(blank=True, null=True)
```

```python
class WebEvent(WebInteraction):
    EVENT_TYPES = [
        ("page_read", "Lectura de Página"),
        ("form_submit", "Envío de Formulario"),
        ("click", "Click en Elemento"),
    ]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    element_selector = models.CharField(max_length=255, blank=True)
```

* `WebInteraction`: cualquier interacción web (navegación, evento, etc.).
* `WebEvent`: eventos específicos en páginas (`pageread`, `form_submit`, etc.).

### Proxies

En casos donde se requieran **queries rápidas y legibles**, se definen proxies sin tablas:

```python
class PageReadEvent(WebEvent):
    class Meta:
        proxy = True
```

---

## 🔗 Integraciones con otras Apps

* **`interactions`**: base de todas las interacciones (herencia vía `OneToOne`).
* **`our_institution`**: cada website pertenece a una **División** de la organización propietaria.
* **`entities`**: posible desanonimización al asociar visitantes con `Person` u `Organization`.
* **`world`**: tagging semántico para categorizar interacciones externas.

---

## 📊 Casos de Uso

### 1. Tracking Anónimo

```python
WebEvent.objects.create(
    interaction=interaction,
    website=division,
    url="/landing",
    event_type="page_read"
)
```

### 2. Desanonimización Progresiva

Cuando un visitante llena un formulario:

```python
person = Person.objects.create(full_name="Jane Doe", email="jane@corp.com")
interaction.person = person
interaction.save()
```

### 3. Queries Estandarizadas

```python
# Todos los page reads
PageReadEvent.objects.select_related("interaction").filter(is_active=True)

# Eventos de formulario en un website específico
WebEvent.objects.filter(website=division, event_type="form_submit")
```

---

## ⚡ Performance

* `select_related("interaction")` en todas las consultas por defecto.
* Proxies permiten queries limpias sin duplicar tablas.
* Índices estratégicos en `event_type`, `url` y `website`.

---

## 🚀 Roadmap

* [ ] Conector de **Emails** (apertura, click, bounce).
* [ ] Conector de **WhatsApp / Chat** (mensajes entrantes/salientes).
* [ ] Conector de **CRM externos** (Zoho, HubSpot, etc.).
* [ ] **Webhooks universales** para ingestión de datos.
* [ ] **Consentimiento GDPR/CCPA** ligado a interacciones capturadas.

---

## ✅ Estado

* 🔄 **En desarrollo**: `WebInteraction` + `WebEvent` con proxies iniciales.
* 🔌 Preparado para crecer hacia otros conectores.
* 🧩 Arquitectura alineada con apps `interactions` y `our_institution`.