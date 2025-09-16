import { DashboardStats } from '@/components/dashboard/dashboard-stats'
import { QuickActions } from '@/components/dashboard/quick-actions'
import { RecentActivity } from '@/components/dashboard/recent-activity'
import { DashboardLayout } from '@/components/layout/dashboard-layout'

export default function DashboardPage() {
  return (
    <DashboardLayout title="Dashboard">
      <div className="space-y-6">
        {/* Welcome Section */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome to BackboneOS
          </h1>
          <p className="text-gray-600">
            Here&apos;s what&apos;s happening with your business today.
          </p>
        </div>

        {/* Stats Grid */}
        <DashboardStats />

        {/* Quick Actions */}
        <QuickActions />

        {/* Recent Activity */}
        <RecentActivity />
      </div>
    </DashboardLayout>
  )
}
