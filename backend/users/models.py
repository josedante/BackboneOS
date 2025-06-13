
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.db import models
from django.contrib.auth import get_user_model

from backend.models import BaseUUIDModelWithActiveStatus

from our_institution.models import Division

User = get_user_model()

class UserProfile(models.Model):
    """Perfil extendido para usuarios del sistema"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)
    verification_key = models.CharField(max_length=64, blank=True)
    preferred_locale = models.CharField(max_length=10, default="es-ES")

    division = models.ForeignKey(
        Division,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="user_profiles",
        verbose_name=_("División"),
        help_text=_("División organizacional a la que pertenece el usuario."),
    )
    
    # # División organizacional
    # NULL_NONE = "NON"
    # BUSINESS_SCHOOL = "GBS"
    # UNDERGRADUATE = "UND"
    # GENERAL = "ALL"
    # DIVISION_OPTIONS = (
    #     (NULL_NONE, "Ninguna"),
    #     (BUSINESS_SCHOOL, "Escuela de Negocios"),
    #     (UNDERGRADUATE, "Pregrado"),
    #     (GENERAL, "Todas las unidades"),
    # )
    # division = models.CharField(
    #     max_length=3,
    #     choices=DIVISION_OPTIONS,
    #     default=BUSINESS_SCHOOL,
    #     verbose_name="División",
    # )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
# Signals para crear automáticamente perfiles
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()



class UserTag(models.Model):
    TYPE_OPTIONS = (
        ("default", "genérica 1 (gris)"),
        ("primary", "genérica 2 (azul)"),
        ("success", "éxito (verde)"),
        ("info", "información (celeste)"),
        ("warning", "alerta (ámbar)"),
        ("danger", "peligro (rojo)"),
        ("pink", "rosa"),
        ("orange", "naranja"),
        ("fucsia", "lila"),
    )

    name = models.CharField(max_length=100)
    tag_type = models.CharField(max_length=10, choices=TYPE_OPTIONS, default="default")
    representative = models.ForeignKey(
        User,
        limit_choices_to={"is_staff": True},
        on_delete=models.CASCADE,
        help_text="Usuario staff creador de esta etiqueta."
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "etiqueta"
        verbose_name_plural = "etiquetas"
        unique_together = ("name", "representative")
