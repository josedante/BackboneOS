'use client'

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

import { formatCurrency } from '@/lib/utils'

const data = [
  { month: 'Jan', revenue: 4000, users: 240 },
  { month: 'Feb', revenue: 3000, users: 139 },
  { month: 'Mar', revenue: 2000, users: 980 },
  { month: 'Apr', revenue: 2780, users: 390 },
  { month: 'May', revenue: 1890, users: 480 },
  { month: 'Jun', revenue: 2390, users: 380 },
  { month: 'Jul', revenue: 3490, users: 430 },
  { month: 'Aug', revenue: 4200, users: 520 },
  { month: 'Sep', revenue: 3800, users: 480 },
  { month: 'Oct', revenue: 4500, users: 550 },
  { month: 'Nov', revenue: 5200, users: 620 },
  { month: 'Dec', revenue: 5800, users: 680 },
]

export function RevenueChart() {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          Revenue Trend
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip 
                formatter={(value: number) => [formatCurrency(value), 'Revenue']}
                labelFormatter={(label) => `Month: ${label}`}
              />
              <Line 
                type="monotone" 
                dataKey="revenue" 
                stroke="#3b82f6" 
                strokeWidth={2}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
