# Docker Development Setup

This project now has separate Docker configurations for development and production environments.

## Development Setup

For local development, use the development Dockerfile which provides:
- Hot reloading with `npm run dev`
- Volume mounting for live code changes
- Development-optimized environment variables
- Faster startup times

### Running Development Environment

```bash
# Start all services in development mode
docker-compose up

# Or start specific services
docker-compose up frontend backend
```

The development setup uses:
- `Dockerfile.dev` for the frontend (Next.js dev server)
- Volume mounting for live code changes
- Development environment variables

## Production Setup

For production deployment, use the production configuration:

```bash
# Start all services in production mode
docker-compose -f docker-compose.prod.yml up

# Build and start in detached mode
docker-compose -f docker-compose.prod.yml up -d --build
```

The production setup uses:
- `Dockerfile` for the frontend (optimized Next.js build)
- No volume mounting (uses built images)
- Production environment variables

## Key Differences

| Feature | Development | Production |
|---------|-------------|------------|
| Frontend Dockerfile | `Dockerfile.dev` | `Dockerfile` |
| Hot Reloading | ✅ Yes | ❌ No |
| Volume Mounting | ✅ Yes | ❌ No |
| Build Optimization | ❌ No | ✅ Yes |
| Environment | `development` | `production` |
| API Base URL | `http://localhost:8000` | `https://backend.proyecto-opensource.orb.local` |

## Environment Variables

### Development
- `NODE_ENV=development`
- `NEXT_TELEMETRY_DISABLED=1`
- `NEXT_PUBLIC_API_BASE=http://localhost:8000`

### Production
- `NODE_ENV=production`
- `NEXT_TELEMETRY_DISABLED=1`
- `NEXT_PUBLIC_API_BASE=https://backend.proyecto-opensource.orb.local`
