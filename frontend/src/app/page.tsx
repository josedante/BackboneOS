/**
 * Phase 5 — legacy Next shell at :3000.
 * The CRM dashboard home is Django `dashboard:home` at GET / (session auth).
 * This page orients developers who still run the Next dev server for /users and /analytics.
 */
import Link from 'next/link'

import { djangoUiPath } from '@/lib/django-ui'

export default function HomePage() {
  const crmUrl = djangoUiPath('/')

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="max-w-lg w-full bg-white shadow rounded-lg p-8 space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">BackboneOS CRM</h1>
          <p className="mt-2 text-gray-600">
            The operator dashboard, products catalog, and entities CRM are served by Django
            templates with session authentication.
          </p>
        </div>
        <a
          href={crmUrl}
          className="inline-flex w-full justify-center rounded-lg bg-primary px-4 py-3 text-sm font-medium text-white hover:opacity-90"
        >
          Open CRM dashboard
        </a>
        <p className="text-sm text-gray-500">
          Still on Next.js until Phase 6:{' '}
          <Link href="/users" className="text-primary hover:underline">
            Users
          </Link>
          {', '}
          <Link href="/analytics" className="text-primary hover:underline">
            Analytics
          </Link>
        </p>
      </div>
    </main>
  )
}
