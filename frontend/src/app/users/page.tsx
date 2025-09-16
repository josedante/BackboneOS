import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { UsersStats } from '@/components/users/users-stats'
import { UsersTable } from '@/components/users/users-table'

export default function UsersPage() {
  return (
    <DashboardLayout title="Users">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Users</h1>
            <p className="text-gray-600">Manage your team members and their permissions.</p>
          </div>
        </div>

        {/* Stats */}
        <UsersStats />

        {/* Users Table */}
        <UsersTable />
      </div>
    </DashboardLayout>
  )
}
