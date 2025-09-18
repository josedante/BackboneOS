# apps/websites/api.py
from rest_framework import serializers, views, status
from rest_framework.response import Response
from urllib.parse import urlsplit

from .models import Website, WebInteraction
from .routing import SurfaceResolver  # optional: keep resolver in routing.py
from interactions.models import Interaction, Action

class WebEventIngestSerializer(serializers.Serializer):
    website_base = serializers.URLField()
    full_url = serializers.URLField()
    referrer = serializers.URLField(required=False, allow_blank=True)
    action_code = serializers.CharField()  # "page_view" | "click" | "form_submit" | "search"
    session_id = serializers.CharField(required=False, allow_blank=True)
    cookie_id = serializers.CharField(required=False, allow_blank=True)
    user_agent = serializers.CharField(required=False, allow_blank=True)
    client_hints = serializers.JSONField(required=False)
    ip = serializers.IPAddressField(required=False)
    utm_source = serializers.CharField(required=False, allow_blank=True)
    utm_medium = serializers.CharField(required=False, allow_blank=True)
    utm_campaign = serializers.CharField(required=False, allow_blank=True)
    utm_content = serializers.CharField(required=False, allow_blank=True)
    utm_term = serializers.CharField(required=False, allow_blank=True)
    element = serializers.CharField(required=False, allow_blank=True)
    payload = serializers.JSONField(required=False)
    idempotency_key = serializers.CharField(required=False, allow_blank=True)

class WebEventIngestView(views.APIView):
    def post(self, request, *args, **kwargs):
        ser = WebEventIngestSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        result = ingest_webevent(**data, remote_addr=request.META.get("REMOTE_ADDR"))
        return Response(result, status=status.HTTP_201_CREATED)
