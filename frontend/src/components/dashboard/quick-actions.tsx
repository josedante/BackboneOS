import Link from 'next/link'
import { Plus, Users, Package, Building2, MessageSquare } from 'lucide-react'

const quickActions = [
  {
    name: 'Add User',
    description: 'Create a new user account',
    href: '/users/new',
    icon: Users,
    color: 'bg-blue-500',
  },
  {
    name: 'Add Product',
    description: 'Add a new product to catalog',
    href: '/products/new',
    icon: Package,
    color: 'bg-green-500',
  },
  {
    name: 'Add Entity',
    description: 'Create a new business entity',
    href: '/entities/new',
    icon: Building2,
    color: 'bg-purple-500',
  },
  {
    name: 'Log Interaction',
    description: 'Record a new interaction',
    href: '/interactions/new',
    icon: MessageSquare,
    color: 'bg-orange-500',
  },
]

export function QuickActions() {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Quick Actions
        </h3>
        <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {quickActions.map((action) => (
            <Link
              key={action.name}
              href={action.href}
              className="relative group bg-white p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-primary rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
            >
              <div>
                <span className={`rounded-lg inline-flex p-3 ${action.color} text-white`}>
                  <action.icon className="h-6 w-6" />
                </span>
              </div>
              <div className="mt-4">
                <h3 className="text-lg font-medium text-gray-900">
                  {action.name}
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  {action.description}
                </p>
              </div>
              <span
                className="pointer-events-none absolute top-6 right-6 text-gray-300 group-hover:text-gray-400"
                aria-hidden="true"
              >
                <Plus className="h-5 w-5" />
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  )
}
