'use client'

/**
 * Phase 5 — split navigation: Django HTML CRM (external) vs Next.js pages (internal).
 * Migrated modules link to NEXT_PUBLIC_DJANGO_UI_BASE; Users/Analytics stay on Next until Phase 6.
 */
import {
  Home,
  Users,
  Package,
  Building2,
  MessageSquare,
  Megaphone,
  Gift,
  Settings,
  BarChart3,
} from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

import { djangoUiPath } from '@/lib/django-ui'
import { cn } from '@/lib/utils'

const djangoNavigation = [
  { name: 'Dashboard', path: '/', icon: Home },
  { name: 'Products', path: '/products/', icon: Package },
  { name: 'Entities', path: '/entities/', icon: Building2 },
  { name: 'Interactions', path: '/interactions/', icon: MessageSquare },
  { name: 'Campaigns', path: '/campaigns/', icon: Megaphone },
  { name: 'Offers', path: '/offers/', icon: Gift },
] as const

const nextNavigation = [
  { name: 'Users', href: '/users', icon: Users },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
] as const

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname()

  return (
    <>
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-black bg-opacity-50 lg:hidden"
          onClick={onClose}
        />
      )}

      <div
        className={cn(
          'fixed inset-y-0 left-0 z-50 w-64 bg-gray-900 shadow-xl transform transition-transform duration-200 ease-in-out lg:translate-x-0',
          isOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex items-center justify-between h-16 px-6 bg-primary">
          <h1 className="text-xl font-bold text-white">BackboneOS</h1>
          <button
            onClick={onClose}
            className="lg:hidden text-white hover:text-gray-200"
            type="button"
            aria-label="Close sidebar"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <nav className="mt-8 px-4">
          <p className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
            CRM (Django)
          </p>
          <div className="space-y-2">
            {djangoNavigation.map((item) => (
              <a
                key={item.name}
                href={djangoUiPath(item.path)}
                className="flex items-center px-3 py-2 rounded-lg text-sm font-medium text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
                onClick={onClose}
              >
                <item.icon className="mr-3 h-5 w-5" />
                {item.name}
              </a>
            ))}
          </div>

          <p className="px-3 mt-6 mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
            App (Next.js)
          </p>
          <div className="space-y-2">
            {nextNavigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'flex items-center px-3 py-2 rounded-lg text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-white border-r-2 border-primary'
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white'
                  )}
                  onClick={onClose}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </div>
        </nav>
      </div>
    </>
  )
}
