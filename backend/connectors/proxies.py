from django.db import models

class ProxyDefaultsQuerySet(models.QuerySet):
    def with_defaults(self):
        model = self.model
        qs = self
        srels = getattr(model, "default_select_related", ())
        prels = getattr(model, "default_prefetch_related", ())
        if srels:
            qs = qs.select_related(*srels)
        if prels:
            qs = qs.prefetch_related(*prels)
        return qs

class ProxyManager(models.Manager.from_queryset(ProxyDefaultsQuerySet)):
    def __init__(self, *, base_filters=None):
        super().__init__()
        self._base_filters = base_filters or {}

    def get_queryset(self):
        qs = super().get_queryset()
        if self._base_filters:
            qs = qs.filter(**self._base_filters)
        return qs.with_defaults()

def manager_for_action(action_code: str) -> ProxyManager:
    return ProxyManager(base_filters={"action__code": action_code})


class InteractionProxyMixin(models.Model):
    """
    Abstract mixin for all Interaction proxies (any connector).
    """
    default_select_related = (
        "action", "action__type",
        "touchpoint_instance", "touchpoint_instance__touchpoint",
        "actor_person", "actor_org",
        "agent",
    )
    default_prefetch_related = ()

    class Meta:
        abstract = True

    # ergonomic shorthands
    @property
    def web(self):
        # present for web-origin interactions; None otherwise
        return getattr(self, "web", None)
