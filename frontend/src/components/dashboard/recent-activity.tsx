import { Users, TrendingUp, Package, Building2 } from 'lucide-react'

const activities = [
  {
    id: 1,
    type: 'user',
    description: 'New user registered: John Doe',
    time: '2 hours ago',
    icon: Users,
    color: 'bg-blue-500',
  },
  {
    id: 2,
    type: 'revenue',
    description: 'Revenue increased by 8.2%',
    time: '4 hours ago',
    icon: TrendingUp,
    color: 'bg-green-500',
  },
  {
    id: 3,
    type: 'product',
    description: 'New product added: Premium Package',
    time: '6 hours ago',
    icon: Package,
    color: 'bg-purple-500',
  },
  {
    id: 4,
    type: 'entity',
    description: 'New entity created: Acme Corp',
    time: '8 hours ago',
    icon: Building2,
    color: 'bg-orange-500',
  },
]

export function RecentActivity() {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900">
          Recent Activity
        </h3>
        <div className="mt-5">
          <div className="flow-root">
            <ul className="-mb-8">
              {activities.map((activity, activityIdx) => (
                <li key={activity.id}>
                  <div className="relative pb-8">
                    {activityIdx !== activities.length - 1 ? (
                      <span
                        className="absolute top-4 left-4 -ml-px h-full w-0.5 bg-gray-200"
                        aria-hidden="true"
                      />
                    ) : null}
                    <div className="relative flex space-x-3">
                      <div>
                        <span className={`h-8 w-8 rounded-full ${activity.color} flex items-center justify-center ring-8 ring-white`}>
                          <activity.icon className="h-4 w-4 text-white" />
                        </span>
                      </div>
                      <div className="min-w-0 flex-1 pt-1.5 flex justify-between space-x-4">
                        <div>
                          <p className="text-sm text-gray-500">
                            {activity.description}
                          </p>
                        </div>
                        <div className="text-right text-sm whitespace-nowrap text-gray-500">
                          <time>{activity.time}</time>
                        </div>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
