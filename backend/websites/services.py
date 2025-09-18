# apps/websites/services.py
from urllib.parse import urlsplit
from django.db import transaction
from .models import Website, WebInteraction
from interactions.models import Interaction, Action
from .routing import SurfaceResolver
from connectors.outbox import emit_outbox  # your outbox helper

def ingest_webevent(
    *, website_base: str, full_url: str, referrer: str = "",
    action_code: str, session_id: str = "", cookie_id: str = "",
    user_agent: str = "", client_hints: dict | None = None, ip: str | None = None,
    utm_source: str = "", utm_medium: str = "", utm_campaign: str = "",
    utm_content: str = "", utm_term: str = "",
    element: str = "", payload: dict | None = None, idempotency_key: str = "",
    remote_addr: str | None = None
) -> dict:

    client_hints = client_hints or {}
    payload = payload or {}

    # 1) Website + path
    website = Website.objects.get(base_url=website_base)
    path = urlsplit(full_url).path

    # 2) Resolve surface → TPI (no duplication)
    surface = SurfaceResolver.resolve(website, path)
    if not surface:
        # policy: either auto-create a default surface/TPI, or write to a generic TPI
        raise ValueError(f"No route for {website_base}{path}")

    tpi = surface.touchpoint

    # 3) Action
    action = Action.objects.get(code=action_code)

    # 4) Idempotency (optional but recommended)
    # e.g., unique (action_code, cookie_id, session_id, tpi, last 30s)
    # You can also store a hash row for (idempotency_key) to short-circuit duplicates.

    with transaction.atomic():
        # 5) Create Interaction (canonical)
        interaction = Interaction.objects.create(
            action=action,
            touchpoint=tpi,
            referrer_url=referrer or "",
            # actor/agent fields per your schema; include UA/IP in agent if desired
        )

        # 6) Create WebInteraction (addon)
        webx = WebInteraction.objects.create(
            interaction=interaction,
            website=website,
            session_id=session_id,
            visitor_cookie=cookie_id,
            user_agent=user_agent,
            client_hints=client_hints,
            ip=ip or remote_addr,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_campaign=utm_campaign,
            utm_content=utm_content,
            utm_term=utm_term,
            element=element,
            payload=payload,
        )

    # 7) Outbox for async enrichment
    emit_outbox("web_event_created", {
        "interaction_id": str(interaction.id),
        "web_interaction_id": str(webx.interaction_id),
        "action_code": action_code,
        "tpi_id": str(tpi.id),
    })

    return {"interaction_id": str(interaction.id)}
