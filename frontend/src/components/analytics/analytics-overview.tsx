import { TrendingUp, Users, DollarSign, Activity, Package, Building2 } from 'lucide-react'
import { formatCurrency, formatNumber, formatPercentage } from '@/lib/utils'

const overviewStats = [
  {
    name: 'Total Revenue',
    value: '$124,567',
    change: '+12.5%',
    changeType: 'positive',
    icon: DollarSign,
    color: 'text-green-600',
  },
  {
    name: 'Active Users',
    value: '2,456',
    change: '+8.2%',
    changeType: 'positive',
    icon: Users,
    color: 'text-blue-600',
  },
  {
    name: 'Growth Rate',
    value: '23.1%',
    change: '+2.1%',
    changeType: 'positive',
    icon: TrendingUp,
    color: 'text-purple-600',
  },
  {
    name: 'Products Sold',
    value: '1,234',
    change: '+15.3%',
    changeType: 'positive',
    icon: Package,
    color: 'text-orange-600',
  },
  {
    name: 'New Entities',
    value: '89',
    change: '+5.7%',
    changeType: 'positive',
    icon: Building2,
    color: 'text-indigo-600',
  },
  {
    name: 'Engagement',
    value: '87.2%',
    change: '+3.4%',
    changeType: 'positive',
    icon: Activity,
    color: 'text-pink-600',
  },
]

export function AnalyticsOverview() {
  return (
    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      {overviewStats.map((stat) => (
        <div
          key={stat.name}
          className="bg-white overflow-hidden shadow rounded-lg"
        >
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <stat.icon className={`h-6 w-6 ${stat.color}`} />
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    {stat.name}
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-semibold text-gray-900">
                      {stat.value}
                    </div>
                    <div
                      className={`ml-2 flex items-baseline text-sm font-semibold ${
                        stat.changeType === 'positive'
                          ? 'text-green-600'
                          : 'text-red-600'
                      }`}
                    >
                      {stat.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
