import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { AnalyticsOverview } from '@/components/analytics/analytics-overview'
import { RevenueChart } from '@/components/analytics/revenue-chart'
import { UserGrowthChart } from '@/components/analytics/user-growth-chart'
import { TopProducts } from '@/components/analytics/top-products'
import { RecentInteractions } from '@/components/analytics/recent-interactions'

export default function AnalyticsPage() {
  return (
    <DashboardLayout title="Analytics">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600">
            Comprehensive insights into your business performance and user behavior.
          </p>
        </div>

        {/* Overview Stats */}
        <AnalyticsOverview />

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <RevenueChart />
          <UserGrowthChart />
        </div>

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TopProducts />
          <RecentInteractions />
        </div>
      </div>
    </DashboardLayout>
  )
}
