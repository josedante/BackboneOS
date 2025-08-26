# BackboneOS Render Deployment Guide

This guide will help you deploy your BackboneOS CRM ecosystem to Render using the provided `render.yaml` blueprint.

## ⚠️ CRITICAL WARNINGS

### 🗄️ Database Data Loss Risk
**FREE TIER POSTGRESQL EXPIRES IN 90 DAYS**

- **Risk**: Your database will be automatically deleted after 90 days on the free tier
- **Impact**: All your CRM data will be permanently lost
- **Solution**: Upgrade to a paid PostgreSQL plan ($7/month) before the 90-day limit
- **Recommendation**: Upgrade within 60 days to ensure smooth transition

### 💰 Cost Optimization
**OPTIONAL SERVICES CAN BE DELETED**

- **Flower Monitor**: Costs $7/month - delete if Celery monitoring is not needed
- **Celery Beat**: Only needed if you have scheduled tasks - can be disabled
- **Multiple Workers**: Start with 1 worker, scale up as needed

### 🔒 Security Improvements
**PRODUCTION-READY CONFIGURATION**

- **Database Migrations**: Automatically run on every deployment with advisory locks
- **Gunicorn Workers**: Optimized to 2 workers for Render Starter Plan
- **ALLOWED_HOSTS**: Secured to only allow Render domains
- **Health Checks**: Proper monitoring endpoints configured
- **Security Headers**: HSTS, CSRF, XSS protection enabled
- **HTTPS Enforcement**: SSL redirect and secure cookies
- **Flower Protection**: Basic auth enabled for monitoring

## 🚀 Quick Start

### Prerequisites
- [Render account](https://render.com) (free tier available)
- GitHub repository with your BackboneOS code
- Git installed locally

### Step 1: Prepare Your Repository

1. **Ensure your repository structure matches:**
```
backboneos/
├── render.yaml              # Render blueprint (already created)
├── backend/
│   ├── Dockerfile.prod      # Production Dockerfile (already created)
│   ├── requirements.txt     # Python dependencies
│   └── backend/
│       ├── settings.py      # Django settings (updated for Render)
│       └── urls.py          # Django URLs (with health check)
├── frontend/
│   ├── package.json         # Node.js dependencies
│   └── nuxt.config.ts       # Nuxt configuration
└── README.md
```

2. **Commit and push your changes:**
```bash
git add .
git commit -m "Add Render deployment configuration"
git push origin main
```

### Step 2: Deploy to Render

1. **Go to [Render Dashboard](https://dashboard.render.com)**

2. **Click "New +" → "Blueprint"**

3. **Connect your GitHub repository**

4. **Select your repository and branch (main)**

5. **Render will automatically detect the `render.yaml` file**

6. **Configure environment variables:**
   - `SECRET_KEY`: Generate a secure Django secret key
   - Any other secrets marked with `sync: false`

7. **Click "Apply" to deploy**

## 📋 Services Overview

Your deployment will create the following services:

### 🗄️ Database & Cache
- **PostgreSQL Database** (`backboneos-db`)
  - Plan: Starter (free tier)
  - Private network only
  - Automatic backups
  - ⚠️ **CRITICAL**: Free tier expires in 90 days - upgrade to paid plan to prevent data loss

- **Redis Cache** (`backboneos-redis`)
  - Plan: Free tier
  - Private network only
  - Used for sessions and Celery

### 🔧 Backend Services
- **Django API** (`backboneos-backend`)
  - Runtime: Docker
  - Health check: `/health/`
  - Auto-deploy enabled

- **Celery Worker** (`backboneos-celery-worker`)
  - Background task processing
  - Concurrency: 2 workers

- **Celery Beat** (`backboneos-celery-beat`)
  - Scheduled task scheduler

- **Flower Monitor** (`backboneos-flower`)
  - Celery task monitoring dashboard
  - ⚠️ **OPTIONAL**: Costs ~$7/month on Starter Plan
  - **Recommendation**: Delete this service to save costs if monitoring is not needed

### 🎨 Frontend Service
- **Nuxt.js App** (`backboneos-frontend`)
  - Runtime: Node.js
  - Build command: `npm install && npm run build`
  - Start command: `npm run preview`

## 🔧 Configuration Details

### ✅ Recent Improvements Made

1. **Database Migrations**: Safe migrations with advisory locks via entrypoint script
2. **Zero-Downtime Deployments**: Auto-scaling (2-3 instances) for web services
3. **Gunicorn Optimization**: Optimized workers, timeouts, and request limits
4. **Security Hardening**: Complete security headers, CSRF, HSTS, and HTTPS enforcement
5. **Redis Optimization**: Upgraded to Starter plan, result expiration, memory management
6. **Observability**: Sentry integration for error tracking and performance monitoring
7. **Flower Security**: Basic auth protection for monitoring dashboard
8. **Cost Optimization**: Clear warnings and optional service identification

### Environment Variables

The `render.yaml` automatically configures:

```yaml
# Database
DATABASE_URL: postgresql://user:pass@host:port/db

# Redis
REDIS_URL: redis://host:port

# Django Settings
DEBUG: False
ALLOWED_HOSTS: backboneos-backend.onrender.com

# CORS
CORS_ALLOWED_ORIGINS: https://backboneos-frontend.onrender.com

# Celery
CELERY_BROKER_URL: redis://host:port
CELERY_RESULT_BACKEND: redis://host:port
```

### Manual Configuration Required

You'll need to set these in the Render dashboard:

1. **SECRET_KEY** (for all Django services)
   ```bash
   # Generate a secure key
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Custom domains** (optional)
   - Add your domain in the service settings
   - Configure DNS records

## 🔍 Monitoring & Health Checks

### Health Check Endpoints
- **Backend**: `https://backboneos-backend.onrender.com/health/`
- **Frontend**: `https://backboneos-frontend.onrender.com/`

### Monitoring
- **Logs**: Available in Render dashboard
- **Metrics**: CPU, memory, and request metrics
- **Flower**: `https://backboneos-flower.onrender.com/` (Celery monitoring)

## 🚀 Scaling Options

### Free Tier Limits
- **Web Services**: 750 hours/month
- **Worker Services**: 750 hours/month
- **PostgreSQL**: 90 days, 1GB storage ⚠️ **DATA LOSS RISK**
- **Redis**: 25MB storage

### Upgrade Path
When you need more resources:

1. **Upgrade to Starter Plan** ($7/month per service)
   - More CPU and memory
   - No time limits
   - Custom domains

2. **Upgrade Database** ($7/month)
   - More storage
   - Better performance
   - Longer retention

3. **Add Auto-scaling**
   ```yaml
   scaling:
     minInstances: 1
     maxInstances: 3
     targetCPUPercent: 70
   ```

## 🔧 Troubleshooting

### Common Issues

1. **Build Failures**
   ```bash
   # Check build logs in Render dashboard
   # Common issues:
   # - Missing dependencies in requirements.txt
   # - Docker build errors
   # - Node.js version conflicts
   ```

2. **Database Connection Issues**
   ```bash
   # Verify DATABASE_URL is set correctly
   # Check if database is accessible from service
   # Ensure SSL mode is enabled
   ```

3. **Redis Connection Issues**
   ```bash
   # Verify REDIS_URL is set correctly
   # Check Redis service is running
   # Ensure private network connectivity
   ```

4. **CORS Errors**
   ```bash
   # Update CORS_ALLOWED_ORIGINS in settings
   # Add your frontend domain to allowed origins
   # Check browser console for specific errors
   ```

### Debug Commands

1. **Check service logs:**
   ```bash
   # In Render dashboard → Service → Logs
   # Or use Render CLI
   render logs backboneos-backend
   ```

2. **SSH into service:**
   ```bash
   # In Render dashboard → Service → Shell
   # Useful for debugging and running commands
   ```

3. **Check environment variables:**
   ```bash
   # In Render dashboard → Service → Environment
   # Verify all required variables are set
   ```

## 🔄 Deployment Workflow

### Development Workflow
1. **Make changes locally**
2. **Test with Docker Compose**
3. **Commit and push to GitHub**
4. **Render auto-deploys from main branch**

### Production Workflow
1. **Create feature branch**
2. **Test changes**
3. **Create pull request**
4. **Merge to main**
5. **Render auto-deploys**

### Manual Deployment
```bash
# Force redeploy from Render dashboard
# Or use Render CLI
render deploy backboneos-backend
```

## 💰 Cost Estimation

### Free Tier (Development)
- **Backend**: Free (750 hours/month)
- **Frontend**: Free (750 hours/month)
- **Workers**: Free (750 hours/month)
- **Database**: Free (90 days)
- **Redis**: Free (25MB)
- **Total**: $0/month

### Starter Plan (Production)
- **Backend**: $7/month (auto-scaling 2-3 instances)
- **Frontend**: $7/month (auto-scaling 2-3 instances)
- **Workers**: $7/month each
- **Database**: $7/month
- **Redis**: $6/month (Starter plan for stability)
- **Flower Monitor**: $7/month (optional - can be deleted)
- **Total**: ~$34-41/month (depending on Flower service)

## 🔐 Security Best Practices

1. **Environment Variables**
   - Never commit secrets to Git
   - Use `sync: false` for sensitive data
   - Rotate secrets regularly

2. **Database Security**
   - Use private network connections
   - Enable SSL for database connections
   - Regular backups

3. **Application Security**
   - Keep dependencies updated
   - Use HTTPS only in production
   - Implement proper CORS policies
   - Security headers enabled (HSTS, XSS protection)
   - CSRF protection with trusted origins

## 🚀 Production Features

### **Zero-Downtime Deployments**
- **Auto-scaling**: 2-3 instances for web services
- **Health checks**: Automatic failover
- **Graceful shutdowns**: 30-second timeouts

### **Performance Optimization**
- **Gunicorn tuning**: Optimized workers and timeouts
- **Redis management**: Result expiration and memory policies
- **Database connections**: Connection pooling and SSL

### **Monitoring & Observability**
- **Sentry integration**: Error tracking and performance monitoring
- **Health endpoints**: `/health/` for all services
- **Flower dashboard**: Celery monitoring with basic auth

### **Security Hardening**
- **HTTPS enforcement**: SSL redirect and secure cookies
- **Security headers**: HSTS, XSS protection, content type sniffing
- **CSRF protection**: Trusted origins configuration
- **Private networking**: Database and Redis isolation

## 📞 Support

- **Render Documentation**: [docs.render.com](https://docs.render.com)
- **Render Support**: Available in dashboard
- **BackboneOS Issues**: GitHub repository issues

## 🎯 Next Steps

After successful deployment:

1. **Set up custom domain** (optional)
2. **Configure monitoring alerts**
3. **Set up CI/CD pipeline**
4. **Implement backup strategy**
5. **Performance optimization**

---

**Happy deploying! 🚀**

Your BackboneOS CRM ecosystem is now ready for production on Render.
