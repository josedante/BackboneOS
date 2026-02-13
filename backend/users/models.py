from django.db import models
from django.contrib.auth import get_user_model
from backend.models import BaseUUIDModelWithActiveStatus
from our_institution.models import Division, Position

User = get_user_model()

class StaffProfile(BaseUUIDModelWithActiveStatus):
    """Perfil extendido para usuarios staff"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="staff_profile")
    division = models.ForeignKey(Division, null=True, blank=True, on_delete=models.SET_NULL)
    position = models.ForeignKey(Position, null=True, blank=True, on_delete=models.SET_NULL)

    # Campos existentes
    prefered_locale = models.CharField(max_length=10, default="es-PE")
    verified = models.BooleanField(default=False)
    
    # NUEVOS CAMPOS para el frontend CRM
    employee_id = models.CharField(max_length=20, unique=True, null=True, blank=True, 
                                  help_text="ID único del empleado")
    hire_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    extension = models.CharField(max_length=10, blank=True)
    profile_picture = models.ImageField(upload_to='staff_profiles/', null=True, blank=True)
    
    # Manager jerárquico
    manager = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL,
                               related_name='subordinates')

    class Meta:
        verbose_name = "Perfil de Staff"
        verbose_name_plural = "Perfiles de Staff"
        indexes = [
            models.Index(fields=["is_active"]),
            models.Index(fields=["verified"]),
        ]

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"
    
    @property
    def full_name_with_position(self):
        """Nombre completo con posición para el frontend"""
        name = self.user.get_full_name() or self.user.username
        if self.position:
            return f"{name} - {self.position.name}"
        return name


class UserTag(BaseUUIDModelWithActiveStatus):
    """Etiquetas personales creadas por un usuario staff"""
    TAG_TYPE_OPTIONS = (
        ("default", "Genérica (gris)"),
        ("primary", "Principal (azul)"),
        ("success", "Éxito (verde)"),
        ("info", "Informativa (celeste)"),
        ("warning", "Alerta (ámbar)"),
        ("danger", "Peligro (rojo)"),
        ("pink", "Rosa"),
        ("orange", "Naranja"),
        ("fucsia", "Fucsia"),
    )

    name = models.CharField(max_length=100)
    tag_type = models.CharField(max_length=10, choices=TAG_TYPE_OPTIONS, default="default")
    representative = models.ForeignKey(
        User,
        limit_choices_to={"is_staff": True},
        on_delete=models.CASCADE,
        related_name="user_tags"
    )

    class Meta:
        verbose_name = "Etiqueta de Usuario"
        verbose_name_plural = "Etiquetas de Usuario"
        unique_together = ("representative", "name")
        indexes = [
            models.Index(fields=["tag_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.representative.username})"


class UserPreference(BaseUUIDModelWithActiveStatus):
    """Preferencias personales del usuario"""
    MEDIUM_CHOICES = (
        ("EM", "Email"),
        ("TX", "Texto"),
        ("PH", "Teléfono"),
        ("VD", "Videollamada"),
        ("IP", "Presencial"),
        ("NN", "Desconocido"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="preferences")
    preferred_contact_medium = models.CharField(max_length=2, choices=MEDIUM_CHOICES, default="EM")
    notifications_enabled = models.BooleanField(default=True)
    custom_filters = models.JSONField(blank=True, default=dict)

    class Meta:
        verbose_name = "Preferencias del Usuario"
        verbose_name_plural = "Preferencias del Usuario"
        indexes = [
            models.Index(fields=["preferred_contact_medium"]),
            models.Index(fields=["notifications_enabled"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"Preferencias de {self.user.username}"


class UserSession(BaseUUIDModelWithActiveStatus):
    """Sesiones de usuario para analytics del dashboard"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Campos calculados para reportes rápidos
    session_duration_minutes = models.IntegerField(null=True, blank=True)
    
    class Meta:
        verbose_name = "Sesión de Usuario"
        verbose_name_plural = "Sesiones de Usuario"
        # Particionado por fecha para escalabilidad
        indexes = [
            models.Index(fields=["user", "login_time"]),
            models.Index(fields=["login_time"]),
        ]

    def save(self, *args, **kwargs):
        if self.logout_time and self.login_time:
            duration = self.logout_time - self.login_time
            self.session_duration_minutes = int(duration.total_seconds() / 60)
        super().save(*args, **kwargs)


# Para eventos críticos que necesitan integridad inmediata
class CriticalUserEvent(BaseUUIDModelWithActiveStatus):
    """Eventos críticos del usuario (login, cambios de permisos, etc.)"""
    EVENT_TYPES = [
        ('login_success', 'Login Exitoso'),
        ('login_failed', 'Login Fallido'),
        ('password_changed', 'Cambio de Contraseña'),
        ('permissions_changed', 'Cambio de Permisos'),
        ('profile_updated', 'Perfil Actualizado'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="critical_events")
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Evento Crítico de Usuario"
        verbose_name_plural = "Eventos Críticos de Usuario"
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["event_type", "timestamp"]),
        ]