# Deployment Guide

## Environment Configuration

This application is designed to work across development, staging, and production environments with proper security configurations.

### Development Environment

- Cookies: `secure: false`, `sameSite: 'lax'`
- CORS: Allows all origins
- Debug mode enabled
- Uses `http://localhost` URLs

### Production Environment

- Cookies: `secure: true`, `sameSite: 'strict'`
- CORS: Restricted to specific origins
- Debug mode disabled
- Requires HTTPS

## Environment Variables

### Backend (.env)

```bash
# Security (REQUIRED in production)
SECRET_KEY=your-very-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database
DATABASE_NAME=backboneos_prod
DATABASE_USER=backboneos_user
DATABASE_PASSWORD=secure-password-here
DATABASE_HOST=db.yourdomain.com
DATABASE_PORT=5432

# Redis Configuration
DJANGO_REDIS_URL=redis://redis.yourdomain.com:6379/1
USE_REDIS_SESSIONS=true

# Celery Configuration
CELERY_BROKER_URL=redis://redis.yourdomain.com:6379/0
CELERY_RESULT_BACKEND=redis://redis.yourdomain.com:6379/2

# CORS (Production domains)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

> Tras la [consolidación del frontend](../consolidation/FRONTEND_CONSOLIDATION.md) no hay servicio de frontend separado: el CRM HTML lo sirve el propio backend Django. El CSS (Tailwind) se compila en la fase builder de `Dockerfile.prod` (`npm ci && npm run tailwind:build`) y se sirve con WhiteNoise tras `collectstatic`.

## Security Checklist for Production

### Backend (Django) + CRM HTML

- ✅ Set `DEBUG=False`
- ✅ Use strong `SECRET_KEY`
- ✅ Configure `ALLOWED_HOSTS`
- ✅ Set specific `CORS_ALLOWED_ORIGINS` (solo clientes externos de la API; el CRM es same-origin)
- ✅ Configurar `CSRF_TRUSTED_ORIGINS` para el dominio del CRM
- ✅ Use HTTPS; cookies de sesión `Secure`/`HttpOnly`
- ✅ Secure database credentials
- ✅ Enable Django security middleware
- ✅ `collectstatic` ejecutado y WhiteNoise sirviendo `static/dist/`

### Infrastructure

- ✅ HTTPS/TLS certificates
- ✅ Secure database connections
- ✅ Firewall rules
- ✅ Regular security updates

## Deployment Commands

### Staging

```bash
export DEBUG=False
export CORS_ALLOWED_ORIGINS=https://staging.yourdomain.com
docker-compose -f docker-compose.staging.yml up --build
```

### Production

```bash
export DEBUG=False
export CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
docker-compose -f docker-compose.prod.yml up --build
```

> El CRM HTML se despliega con el backend (misma imagen/proceso); no hay paso de build de frontend separado.

## Cookie Security by Environment

| Environment | Secure | SameSite | Domain     | Notes            |
| ----------- | ------ | -------- | ---------- | ---------------- |
| Development | false  | lax      | undefined  | Works with HTTP  |
| Staging     | true   | lax      | undefined  | Requires HTTPS   |
| Production  | true   | strict   | configured | Maximum security |

The authentication system automatically adapts to the environment for optimal security and functionality.
