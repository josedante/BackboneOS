import { Package, TrendingUp, DollarSign } from 'lucide-react'

import { formatCurrency, formatNumber } from '@/lib/utils'

const topProducts = [
  {
    id: 1,
    name: 'Premium Package',
    sales: 234,
    revenue: 12500,
    growth: '+12.5%',
    icon: Package,
  },
  {
    id: 2,
    name: 'Basic Plan',
    sales: 189,
    revenue: 9450,
    growth: '+8.2%',
    icon: Package,
  },
  {
    id: 3,
    name: 'Enterprise Suite',
    sales: 156,
    revenue: 18750,
    growth: '+15.3%',
    icon: Package,
  },
  {
    id: 4,
    name: 'Starter Kit',
    sales: 98,
    revenue: 4900,
    growth: '+5.7%',
    icon: Package,
  },
  {
    id: 5,
    name: 'Professional',
    sales: 87,
    revenue: 8700,
    growth: '+3.4%',
    icon: Package,
  },
]

export function TopProducts() {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          Top Products
        </h3>
        <div className="space-y-4">
          {topProducts.map((product, index) => (
            <div key={product.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="flex items-center space-x-4">
                <div className="flex-shrink-0">
                  <div className="h-10 w-10 bg-primary rounded-lg flex items-center justify-center">
                    <product.icon className="h-5 w-5 text-white" />
                  </div>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900">
                    #{index + 1} {product.name}
                  </h4>
                  <div className="flex items-center space-x-4 text-sm text-gray-500">
                    <span className="flex items-center">
                      <TrendingUp className="h-4 w-4 mr-1" />
                      {formatNumber(product.sales)} sales
                    </span>
                    <span className="flex items-center">
                      <DollarSign className="h-4 w-4 mr-1" />
                      {formatCurrency(product.revenue)}
                    </span>
                  </div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-green-600">
                  {product.growth}
                </div>
                <div className="text-xs text-gray-500">
                  vs last month
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
