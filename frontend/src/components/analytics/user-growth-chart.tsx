'use client'

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { formatNumber } from '@/lib/utils'

const data = [
  { month: 'Jan', newUsers: 65, totalUsers: 240 },
  { month: 'Feb', newUsers: 59, totalUsers: 299 },
  { month: 'Mar', newUsers: 80, totalUsers: 379 },
  { month: 'Apr', newUsers: 81, totalUsers: 460 },
  { month: 'May', newUsers: 56, totalUsers: 516 },
  { month: 'Jun', newUsers: 55, totalUsers: 571 },
  { month: 'Jul', newUsers: 40, totalUsers: 611 },
  { month: 'Aug', newUsers: 62, totalUsers: 673 },
  { month: 'Sep', newUsers: 45, totalUsers: 718 },
  { month: 'Oct', newUsers: 67, totalUsers: 785 },
  { month: 'Nov', newUsers: 78, totalUsers: 863 },
  { month: 'Dec', newUsers: 85, totalUsers: 948 },
]

export function UserGrowthChart() {
  return (
    <div className="bg-white shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
          User Growth
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip 
                formatter={(value: number, name: string) => [
                  formatNumber(value), 
                  name === 'newUsers' ? 'New Users' : 'Total Users'
                ]}
                labelFormatter={(label) => `Month: ${label}`}
              />
              <Bar 
                dataKey="newUsers" 
                fill="#10b981" 
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
