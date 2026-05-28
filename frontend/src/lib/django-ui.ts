/**
 * Phase 5: Django HTML CRM base URL for sidebar links and landing CTAs.
 * Defaults to NEXT_PUBLIC_API_BASE (same host in dev); override when UI and API diverge.
 */
export function getDjangoUiBase(): string {
  const base =
    process.env['NEXT_PUBLIC_DJANGO_UI_BASE'] ||
    process.env['NEXT_PUBLIC_API_BASE'] ||
    'http://localhost:8000'
  return base.replace(/\/$/, '')
}

export function djangoUiPath(path: string): string {
  const normalized = path.startsWith('/') ? path : `/${path}`
  return `${getDjangoUiBase()}${normalized}`
}
