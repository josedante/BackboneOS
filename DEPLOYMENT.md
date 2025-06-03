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

# CORS (Production domains)
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### Frontend (.env)

```bash
# API Configuration
NUXT_PUBLIC_API_BASE=https://api.yourdomain.com
NODE_ENV=production
```

## Security Checklist for Production

### Backend (Django)
- ✅ Set `DEBUG=False`
- ✅ Use strong `SECRET_KEY`
- ✅ Configure `ALLOWED_HOSTS`
- ✅ Set specific `CORS_ALLOWED_ORIGINS`
- ✅ Use HTTPS
- ✅ Secure database credentials
- ✅ Enable Django security middleware

### Frontend (Nuxt.js)
- ✅ Set `NODE_ENV=production`
- ✅ Use HTTPS API URLs
- ✅ Cookies automatically secure in production
- ✅ Build with `npm run build`

### Infrastructure
- ✅ HTTPS/TLS certificates
- ✅ Secure database connections
- ✅ Firewall rules
- ✅ Regular security updates

## Deployment Commands

### Staging
```bash
# Backend
export DEBUG=False
export CORS_ALLOWED_ORIGINS=https://staging.yourdomain.com
docker-compose -f docker-compose.staging.yml up --build

# Frontend  
export NODE_ENV=staging
export NUXT_PUBLIC_API_BASE=https://api-staging.yourdomain.com
npm run build
```

### Production
```bash
# Backend
export DEBUG=False
export CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
docker-compose -f docker-compose.prod.yml up --build

# Frontend
export NODE_ENV=production
export NUXT_PUBLIC_API_BASE=https://api.yourdomain.com
npm run build
```

## Cookie Security by Environment

| Environment | Secure | SameSite | Domain | Notes |
|-------------|--------|----------|---------|-------|
| Development | false | lax | undefined | Works with HTTP |
| Staging | true | lax | undefined | Requires HTTPS |
| Production | true | strict | configured | Maximum security |

The authentication system automatically adapts to the environment for optimal security and functionality.