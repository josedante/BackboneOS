import uuid
from django.db import models


class BaseUUIDModel(models.Model):
    """Modelo base con UUID primary key"""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="ID"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class BaseUUIDModelWithActiveStatus(BaseUUIDModel):
    """Modelo base con UUID y soft delete"""
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        abstract = True