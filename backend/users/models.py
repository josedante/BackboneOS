from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# class UserProfile(models.Model):
#     """Perfil extendido para usuarios del sistema"""
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     verified = models.BooleanField(default=False)
#     verification_key = models.CharField(max_length=64, blank=True)
#     preferred_locale = models.CharField(max_length=10, default="es-ES")
    
#     # # División organizacional
#     # NULL_NONE = "NON"
#     # BUSINESS_SCHOOL = "GBS"
#     # UNDERGRADUATE = "UND"
#     # GENERAL = "ALL"
#     # DIVISION_OPTIONS = (
#     #     (NULL_NONE, "Ninguna"),
#     #     (BUSINESS_SCHOOL, "Escuela de Negocios"),
#     #     (UNDERGRADUATE, "Pregrado"),
#     #     (GENERAL, "Todas las unidades"),
#     # )
#     # division = models.CharField(
#     #     max_length=3,
#     #     choices=DIVISION_OPTIONS,
#     #     default=BUSINESS_SCHOOL,
#     #     verbose_name="División",
#     # )
    
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         verbose_name = "Perfil de Usuario"
#         verbose_name_plural = "Perfiles de Usuario"
    
#     def __str__(self):
#         return f"Perfil de {self.user.username}"
    
# # Signals para crear automáticamente perfiles
# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         UserProfile.objects.create(user=instance)


# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     if hasattr(instance, 'profile'):
#         instance.profile.save()
