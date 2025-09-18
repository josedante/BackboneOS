Great catch. Yes—we’re missing a **first-class bridge** from connector payloads → `Interaction.touchpoint` (and, by extension, `Channel` & `Medium`). Below is a concrete plan and drop-in code to wire this up cleanly without tangling `connectors` to `interactions` internals.

# What we want

1. Every connector record (e.g., `WebEvent`) should deterministically produce a **Touchpoint** (and therefore a `channel`/`medium`).
2. Mappings must be **configurable per property/source** (website, inbox, number, account), not hard-coded.
3. No duplicate logic in each connector; use a **registry + adapters**.
4. Backfill existing data safely and idempotently.

# Design overview

* **Connector→Touchpoint Resolver**: a small, pluggable service in `connectors` that decides which `Touchpoint` to attach to the parent `Interaction`.
* **Per-source mapping model** (e.g., per website): admins can override defaults (e.g., landing pages = “Web | Organic”; contact form = “Web | Lead Form”).
* **Lightweight UTM analyzer**: when present, infer `Channel/Medium` from `utm_source/utm_medium/utm_campaign`, referrer, or connector type.
* **Save hooks** in each concrete connector model to apply the resolver.
* **Management command** to backfill old interactions.

This keeps `connectors` opinionated about integration, but **dependent only on the public surface** of `interactions` (Touchpoint, Channel, Medium, Interaction.touchpoint). It fits the goal stated in your `connectors/README.md` (capture externals → standardize into `interactions.Interaction`) .

---

# 1) Core interfaces (connectors/resolution.py)

```python
# connectors/resolution.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Protocol

from django.db import transaction
from interactions.models import Touchpoint  # has fields: code, channel, medium, etc.

@dataclass(frozen=True)
class TouchpointHint:
    """Optional hints coming from a connector payload."""
    code: Optional[str] = None              # e.g. "web.page_read", "web.form_submit"
    channel_code: Optional[str] = None      # e.g. "web", "email", "chat", "phone"
    medium_code: Optional[str] = None       # e.g. "organic", "paid", "referral", "social", "whatsapp"
    label: Optional[str] = None             # human friendly name (for new tp creation)
    extra_tags: tuple[str, ...] = ()        # semantic categories

class SupportsTpInference(Protocol):
    """Connector records implement this to provide inference hints."""
    def infer_touchpoint_hint(self) -> TouchpointHint: ...

class TouchpointResolver(Protocol):
    def resolve(self, subject: SupportsTpInference) -> Touchpoint: ...

class DefaultTouchpointResolver:
    """
    Strategy:
    1) Ask the connector for a hint (code/channel/medium).
    2) Apply per-source mapping overrides (DB table).
    3) Fallback to global defaults per connector class.
    4) get_or_create() the Touchpoint by `code`; set channel/medium if newly created.
    """

    def __init__(self, mapping_provider: "MappingProvider"):
        self.mapping_provider = mapping_provider

    @transaction.atomic
    def resolve(self, subject: SupportsTpInference) -> Touchpoint:
        hint = subject.infer_touchpoint_hint()

        # 2) Per-source overrides (e.g., Website, Inbox, WA number, etc.)
        override = self.mapping_provider.lookup(subject=subject, hint=hint)
        code = (override.code if override and override.code else hint.code) or self._default_code(subject)
        channel_code = (override.channel_code if override and override.channel_code else hint.channel_code) or self._default_channel(subject)
        medium_code  = (override.medium_code  if override and override.medium_code  else hint.medium_code)  or self._default_medium(subject)

        tp, created = Touchpoint.objects.get_or_create(
            code=code,
            defaults={
                "label": hint.label or code.replace(".", " ").title(),
                "channel_code": channel_code,
                "medium_code": medium_code,
                "is_active": True,
            },
        )
        # Optional: update channel/medium if blank on existing tp.
        if not created:
            dirty = False
            if channel_code and not getattr(tp, "channel_code", None):
                tp.channel_code = channel_code; dirty = True
            if medium_code and not getattr(tp, "medium_code", None):
                tp.medium_code = medium_code; dirty = True
            if dirty: tp.save(update_fields=["channel_code", "medium_code"])
        return tp

    # --- connector-specific defaults ---
    def _default_code(self, subject) -> str:
        cls = subject.__class__.__name__.lower()
        return f"{cls}.generic"

    def _default_channel(self, subject) -> str:
        # Web connectors → "web" by default
        return "web" if subject.__class__.__name__.lower().startswith("web") else "other"

    def _default_medium(self, subject) -> str:
        return "unknown"


# Provider looks up per-source overrides (below).
class MappingProvider(Protocol):
    def lookup(self, subject: SupportsTpInference, hint: TouchpointHint) -> Optional["MappingRule"]:
        ...
```

---

# 2) Per-source mapping model (connectors/models.py)

```python
# connectors/models.py (additions)
from django.db import models

class TouchpointMappingRule(models.Model):
    """
    Declarative overrides. Scope by source (website/inbox/number/account) + hint.code.
    Example: For Website A, event_code "web.page_read" -> Touchpoint "web.page_read",
             channel=web, medium=organic.
    """
    # Scope — pick one FK per connector type (nullable for global)
    website = models.ForeignKey("our_institution.Division", null=True, blank=True,
                                on_delete=models.CASCADE, related_name="touchpoint_mapping_rules")
    # For future connectors:
    # inbox = models.ForeignKey("email.Inbox", null=True, blank=True, ...)
    # wa_number = models.ForeignKey("whatsapp.Number", null=True, blank=True, ...)

    event_code = models.CharField(max_length=100)  # connector's hint.code (e.g., "web.form_submit")
    # The resulting touchpoint code (stable primary identifier in interactions)
    touchpoint_code = models.CharField(max_length=100)

    # Optional enforced channel/medium
    channel_code = models.CharField(max_length=50, blank=True)
    medium_code  = models.CharField(max_length=50, blank=True)

    active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["event_code"]),
            models.Index(fields=["website", "event_code"]),
        ]
        unique_together = [("website", "event_code")]
```

And a DB-backed provider:

```python
# connectors/resolution_db.py
from .resolution import MappingProvider, TouchpointHint
from .models import TouchpointMappingRule

class DbMappingProvider(MappingProvider):
    def lookup(self, subject, hint: TouchpointHint):
        website = getattr(subject, "website", None)  # e.g., WebEvent.website
        if website and hint.code:
            return TouchpointMappingRule.objects.filter(
                website=website, event_code=hint.code, active=True
            ).first()
        if hint.code:
            return TouchpointMappingRule.objects.filter(
                website__isnull=True, event_code=hint.code, active=True
            ).first()
        return None
```

---

# 3) Connector adapters (Web)

```python
# connectors/web/adapters.py
from urllib.parse import urlparse, parse_qs
from .models import WebEvent
from connectors.resolution import TouchpointHint

UTM_MEDIUM_MAP = {
    "cpc": "paid",
    "ppc": "paid",
    "paid": "paid",
    "email": "email",
    "social": "social",
    "referral": "referral",
}

def _infer_medium_from_utm(url: str, referrer: str | None) -> tuple[str, str]:
    # Returns (channel_code, medium_code)
    # Channel fixed to "web", medium inferred from utm_medium/referrer
    medium = "organic"
    try:
        qs = parse_qs(urlparse(url).query)
        if m := qs.get("utm_medium", [None])[0]:
            medium = UTM_MEDIUM_MAP.get(m.lower(), m.lower())
        elif referrer:
            host = urlparse(referrer).hostname or ""
            if "facebook" in host or "twitter" in host or "linkedin" in host or "bsky" in host:
                medium = "social"
            elif host:
                medium = "referral"
    except Exception:
        pass
    return ("web", medium)

def web_event_hint(e: WebEvent) -> TouchpointHint:
    if e.event_type == "form_submit":
        code = "web.form_submit"
        label = "Web Form Submit"
    elif e.event_type == "click":
        code = "web.click"
        label = "Web Click"
    else:
        code = "web.page_read"
        label = "Web Page Read"

    channel, medium = _infer_medium_from_utm(e.url or "", e.referrer)
    return TouchpointHint(code=code, channel_code=channel, medium_code=medium, label=label)
```

---

# 4) Apply on save (connectors/web/models.py)

```python
# connectors/web/models.py
from django.db import models
from connectors.models import AbstractConnectorInteraction
from our_institution.models import Division
from connectors.resolution import DefaultTouchpointResolver
from connectors.resolution_db import DbMappingProvider
from .adapters import web_event_hint

resolver = DefaultTouchpointResolver(mapping_provider=DbMappingProvider())

class WebInteraction(AbstractConnectorInteraction):
    website = models.ForeignKey(Division, on_delete=models.CASCADE, related_name="web_interactions")
    url = models.URLField()
    referrer = models.URLField(blank=True, null=True)

    # implement protocol for inference
    def infer_touchpoint_hint(self):
        # Generic web interaction -> treat as page read by default
        from connectors.web.adapters import _infer_medium_from_utm
        ch, md = _infer_medium_from_utm(self.url or "", self.referrer)
        return TouchpointHint(code="web.generic", channel_code=ch, medium_code=md, label="Web")

    def _ensure_touchpoint(self):
        if not self.interaction.touchpoint_id:
            tp = resolver.resolve(self)
            self.interaction.touchpoint = tp
            self.interaction.save(update_fields=["touchpoint"])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._ensure_touchpoint()

class WebEvent(WebInteraction):
    EVENT_TYPES = [("page_read", "Page Read"), ("form_submit", "Form Submit"), ("click", "Click")]
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    element_selector = models.CharField(max_length=255, blank=True)

    def infer_touchpoint_hint(self):
        return web_event_hint(self)
```

> Why on the connector model’s `save`? Because `AbstractConnectorInteraction` is abstract; we can’t attach a generic signal there. Alternatively, you can register a `post_save` receiver per concrete model.

---

# 5) Channel/Medium “disconnect” solved

Once `Interaction.touchpoint` is set, you can **normalize `channel` & `medium` exclusively through `Touchpoint`**. If your `Interaction` table also stores denormalized `channel_code/medium_code`, add a signal to stamp them from the chosen touchpoint:

```python
# interactions/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Interaction

@receiver(pre_save, sender=Interaction)
def stamp_channel_medium(sender, instance: Interaction, **kwargs):
    if instance.touchpoint_id and instance.touchpoint:
        instance.channel_code = instance.touchpoint.channel_code
        instance.medium_code = instance.touchpoint.medium_code
```

This gives you:

* `Interaction.touchpoint` → single source of truth for semantics.
* Fast filters: `Interaction.objects.filter(channel_code="web", medium_code="organic")`.

---

# 6) Admin UX (recommended)

* Add an **inline** on `Division` admin for `TouchpointMappingRule` so ops can set:

  * `event_code = "web.form_submit"` → `touchpoint_code = "web.form_submit"` | medium override = “paid”.
* Add a “Preview Resolution” admin action on `WebEvent` to show how it would map today.

---

# 7) Backfill command

```python
# connectors/management/commands/backfill_touchpoints.py
from django.core.management.base import BaseCommand
from connectors.web.models import WebInteraction, WebEvent
from connectors.resolution_db import DbMappingProvider
from connectors.resolution import DefaultTouchpointResolver

class Command(BaseCommand):
    help = "Backfill Interaction.touchpoint from connector records."

    def handle(self, *args, **opts):
        resolver = DefaultTouchpointResolver(DbMappingProvider())

        def backfill(qs):
            for obj in qs.select_related("interaction").iterator(chunk_size=500):
                if obj.interaction and not obj.interaction.touchpoint_id:
                    tp = resolver.resolve(obj)
                    obj.interaction.touchpoint = tp
                    obj.interaction.save(update_fields=["touchpoint"])
        backfill(WebEvent.objects.all())
        backfill(WebInteraction.objects.exclude(webevent__isnull=False))
        self.stdout.write(self.style.SUCCESS("Backfill completed."))
```

---

# 8) Example queries you unlock

```python
# All organic web page reads on Division X
Interaction.objects.filter(
    touchpoint__code="web.page_read",
    channel_code="web",
    medium_code="organic",
    webinteraction__website=division_x,
)

# Funnel: form submits that followed a page read within 30 minutes for the same person
from django.utils import timezone
from datetime import timedelta

cutoff = timezone.now() - timedelta(minutes=30)
reads = Interaction.objects.filter(
    touchpoint__code="web.page_read", person__isnull=False
).values_list("person_id", "occurred_at")
submits = Interaction.objects.filter(
    touchpoint__code="web.form_submit", person__isnull=False, occurred_at__gte=cutoff
)
# Build a join in SQL or do a small in-memory pass depending on volume.
```

---

# 9) Why this is safe & extensible

* **No cross-app import hell**: `connectors` depends only on `interactions` public models.
* **Open/Closed**: Add `EmailEvent`, `WhatsAppMessage`, etc., each implements `infer_touchpoint_hint()`. The same resolver handles them.
* **Runtime configurability**: Ops can fix mapping in admin without redeploys.
* **Determinism**: `Touchpoint.code` is the stable key for analytics & segmentation.

---

# 10) Minimal migration plan

1. Migrate: add `TouchpointMappingRule`.
2. Release code paths (`infer_touchpoint_hint`, resolver).
3. Run `backfill_touchpoints`.
4. Add admin policy to maintain mapping rules for new campaigns or sources.

---

If you want, I can tailor the `EmailEvent`/`WhatsAppMessage` adapters next (with bounce/open/click & inbound/outbound semantics) so they drop into the exact same resolver path. The shape is identical to `WebEvent`, so adding them won’t require touching analytics or downstream code.&#x20;
