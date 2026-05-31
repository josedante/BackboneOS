# 📘 Users App - Gestión de Usuarios y Staff

## 🎯 Propósito

La aplicación `users` extiende el modelo de usuario base (`User`) para proporcionar funcionalidades específicas de gestión de staff en una instancia de BackboneOS CRM.

Dado que cada instancia es _single-tenant_, todos los usuarios registrados son miembros del staff de la organización propietaria del CRM, y por tanto deben ser gestionados como tales.

---

## 🏗️ Modelos Implementados

### `StaffProfile`

Perfil extendido para usuarios tipo staff.

| Campo             | Descripción                                |
| ----------------- | ------------------------------------------ |
| `user`            | Referencia al usuario (`OneToOne`)         |
| `division`        | División organizacional a la que pertenece |
| `position`        | Cargo o puesto asignado                    |
| `prefered_locale` | Localización preferida para la interfaz    |
| `verified`        | Indicador de verificación manual           |

🔗 Integra con la app `our_institution`.

---

### `UserTag`

Etiquetas personales creadas por usuarios para organización del trabajo.

| Campo            | Descripción                       |
| ---------------- | --------------------------------- |
| `name`           | Nombre visible de la etiqueta     |
| `tag_type`       | Color o estilo visual (`choices`) |
| `representative` | Usuario staff que la creó         |

📌 Soporta múltiples colores (gris, azul, verde, rojo, etc.).

---

### `UserPreference`

Preferencias personales de comunicación y notificación del usuario.

| Campo                      | Descripción                                   |
| -------------------------- | --------------------------------------------- |
| `preferred_contact_medium` | Medio favorito (email, teléfono, texto, etc.) |
| `notifications_enabled`    | Si desea recibir notificaciones               |
| `custom_filters`           | JSON con filtros o vistas personalizadas      |

---

## 🔗 Integración con Otras Aplicaciones

- `interactions` → Campos `representative`, `assigned_staff`, `operated_by`
- `our_institution` → Division y Position como estructura organizacional
- `entities` → Referencias cruzadas a personas y contactos (indirectamente)

---

## 📊 Posibles Extensiones Futuras

- 🧭 Sistema de permisos y niveles de acceso personalizados
- 📆 Registro de actividades y login tracking por staff
- 🔐 Autenticación multifactor y preferencias de seguridad
- 🧠 Recomendaciones contextuales por perfil

---

## ⚙️ Comandos de Gestión

```bash
# Crear usuarios desde shell (ejemplo)
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> u = User.objects.create_user(username="ejemplo", email="a@a.com", password="1234")
```

---

## 🛡️ Seguridad y Compliance

- Soft delete (`is_active`) habilitado en todos los modelos
- Relaciones validadas y protegidas con constraints
- Soporte para expansión modular con bajo acoplamiento

Aquí tienes una sección lista para añadir al `README.md` del módulo `users`, específicamente documentando la función `log_user_activity` y cómo integrarla correctamente:

---

## 🧾 Registro de Actividad de Usuario (`log_user_activity`)

La función `log_user_activity()` permite registrar eventos del usuario en sistemas externos como MongoDB o DynamoDB, según configuración.

### 📌 Firma de la función

```python
log_user_activity(user, activity_type, description="", metadata=None, request=None)
```

| Parámetro       | Descripción                                                                |
| --------------- | -------------------------------------------------------------------------- |
| `user`          | Instancia de `User` que genera la acción                                   |
| `activity_type` | Cadena corta que categoriza la actividad (ej. `"login"`, `"lead_created"`) |
| `description`   | Descripción libre de la acción realizada                                   |
| `metadata`      | Diccionario opcional con detalles adicionales del evento                   |
| `request`       | (opcional) Objeto `HttpRequest` para capturar IP y `user_agent`            |

---

### 🧠 Convención de `metadata` extendida

Puedes incluir en `metadata` los siguientes campos especiales:

| Clave                 | Uso recomendado                                                            |
| --------------------- | -------------------------------------------------------------------------- |
| `command_name`        | Nombre técnico del comando ejecutado. Formato: `App::Module::Action`       |
| `trigger_context`     | Clase, vista o componente que originó el evento                            |
| `related_object_uuid` | UUID del objeto relacionado (lead, interacción, etc.)                      |
| Otros                 | Cualquier otro dato será incluido en el campo `metadata` como JSON anidado |

---

### ✅ Ejemplo de uso

```python
from users.events import log_user_activity

log_user_activity(
    user=request.user,
    activity_type=\"lead_assigned\",
    description=\"Asignó un lead desde el panel de ventas\",
    metadata={
        \"command_name\": \"CRM::LeadPipeline::Assign\",
        \"trigger_context\": \"LeadAssignmentView\",
        \"related_object_uuid\": str(lead.id),
        \"lead_name\": lead.name,
        \"assigned_to\": request.user.username
    },
    request=request
)
```

---

### ⚙️ Configuración en `settings.py`

```python
# Sistema de logging de actividad
USER_ACTIVITY_BACKEND = \"mongodb\"  # o \"dynamodb\"

# Configuración para MongoDB
MONGODB_URI = os.getenv(\"MONGODB_URI\")
MONGODB_DB_NAME = \"backbone_logs\"

# Configuración para DynamoDB (si aplica)
AWS_ACCESS_KEY_ID = os.getenv(\"AWS_ACCESS_KEY_ID\")
AWS_SECRET_ACCESS_KEY = os.getenv(\"AWS_SECRET_ACCESS_KEY\")
AWS_DYNAMODB_REGION = \"us-west-2\"
AWS_DYNAMODB_ENDPOINT = os.getenv(\"AWS_DYNAMODB_ENDPOINT\", None)  # opcional
AWS_USER_ACTIVITY_TABLE = \"UserActivityLogs\"
```

## Documentación

- [docs/APPS.md](../../docs/APPS.md)
- [docs/TESTING.md](../../docs/TESTING.md) — `users/tests.py`
- [backend/README.md](../README.md)

---

© BackboneOS – App `users` para gestión de staff en instancias CRM single-tenant.
