# apps/websites/routing.py
from django.db import transaction
from .models import Website, WebSurface, UrlRoutingRule
from interactions.models import TouchPointClass, TouchPoint, Channel

class AutoProvisionPolicy:
    STRICT = "strict"
    PERMISSIVE = "permissive"

def get_www_touchpoint_classes():
    www, _ = Channel.objects.get_or_create(code="WWW", defaults={"name": "World Wide Web"})
    tp_page, _ = TouchPointClass.objects.get_or_create(code="WWW_PAGE", defaults={"name": "Website Page", "channel": www})
    tp_form, _ = TouchPointClass.objects.get_or_create(code="WWW_FORM", defaults={"name": "Website Form", "channel": www})
    return tp_page, tp_form

class SurfaceResolver:
    @staticmethod
    def resolve(website: Website, path: str, *, allow_autocreate: bool = True) -> WebSurface | None:
        # 1) Try direct WebSurface match (fast)
        qs = WebSurface.objects.filter(website=website).only("id", "path", "match_kind", "regex", "is_form")
        for s in qs:
            if s.matches(path):
                return s

        # 2) Try UrlRoutingRule
        for r in UrlRoutingRule.objects.filter(website=website, active=True).select_related("surface"):
            if r.matches(path):  # tiny helper like in your snippet
                return r.surface

        # 3) Auto-provision (if allowed)
        if not allow_autocreate or website.auto_provision_mode == AutoProvisionPolicy.STRICT:
            return None

        return SurfaceResolver._autocreate_surface(website, path)

    @staticmethod
    @transaction.atomic
    def _autocreate_surface(website: Website, path: str) -> WebSurface:
        # Guardrails: basic allow/deny, rate limit, per-day caps, etc. (omitted for brevity)
        tpc_page, tpc_form = get_www_touchpoint_classes()
        looks_like_form = path.endswith("/thank-you") or "form" in path  # naive heuristic; improve as needed
        tpc = tpc_form if looks_like_form else tpc_page

        # Idempotent upsert by (website, path)
        surface, created = WebSurface.objects.get_or_create(
            website=website, path=path,
            defaults={
                "match_kind": "exact",
                "is_form": looks_like_form,
                "is_thankyou": path.endswith("/thank-you"),
                "is_placeholder": True,
                "review_status": "pending",
                "touchpoint": None,  # set below
            }
        )

        if surface.touchpoint_id:
            return surface

        tpi = TouchPoint.objects.create(
            touchpoint=tp,
            title=path,                # the curator can rename later
            url=f"{website.base_url.rstrip('/')}{path}",
            metadata={"discovered": True}
        )
        surface.touchpoint = tpi
        surface.save(update_fields=["touchpoint"])
        return surface
