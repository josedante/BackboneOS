/** @type {import('next').NextConfig} */

// Phase 5: CRM list/detail UI lives on Django templates (see docs/consolidation/FRONTEND_CONSOLIDATION.md).
function getDjangoUiBase() {
  const base =
    process.env.NEXT_PUBLIC_DJANGO_UI_BASE ||
    process.env.NEXT_PUBLIC_API_BASE ||
    'http://localhost:8000'
  return base.replace(/\/$/, '')
}

const nextConfig = {
  // Disable ESLint during build for production deployment
  eslint: {
    ignoreDuringBuilds: true,
  },

  // External packages for server components
  serverExternalPackages: ['axios'],

  // Environment variables
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE,
    NEXT_PUBLIC_DJANGO_UI_BASE: process.env.NEXT_PUBLIC_DJANGO_UI_BASE,
    NEXT_PRIVATE_API_BASE: process.env.NEXT_PRIVATE_API_BASE,
  },

  // Image optimization
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },

  // Headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'origin-when-cross-origin',
          },
        ],
      },
    ]
  },

  // Redirects
  async redirects() {
    const djangoUi = getDjangoUiBase()

    return [
      {
        source: '/dashboard',
        destination: '/',
        permanent: false,
      },
      // Migrated CRM modules — bookmarks to :3000/products|entities go to Django HTML.
      {
        source: '/products',
        destination: `${djangoUi}/products/`,
        permanent: false,
      },
      {
        source: '/products/:path*',
        destination: `${djangoUi}/products/:path*`,
        permanent: false,
      },
      {
        source: '/entities',
        destination: `${djangoUi}/entities/`,
        permanent: false,
      },
      {
        source: '/entities/:path*',
        destination: `${djangoUi}/entities/:path*`,
        permanent: false,
      },
    ]
  },

  // Output configuration for Render.com
  output: 'standalone',

  // Disable x-powered-by header
  poweredByHeader: false,

  // Compress responses
  compress: true,
}

export default nextConfig
