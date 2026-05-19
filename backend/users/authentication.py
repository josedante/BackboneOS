from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed


class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads the access token from the 'access_token' httpOnly cookie.
    Falls back to the Authorization: Bearer header for non-browser clients
    (scripts, mobile apps, third-party integrations).
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get('access_token')
        if raw_token:
            try:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
            except (InvalidToken, AuthenticationFailed):
                pass  # Cookie present but invalid — fall through to header

        return super().authenticate(request)
