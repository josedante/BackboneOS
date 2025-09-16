# Frontend Components Documentation

## Component Architecture Overview

The BackboneOS frontend follows a modular component architecture with clear separation of concerns. Components are organized by feature and functionality, making the codebase maintainable and scalable.

## Layout Components

### DashboardLayout

**Location**: `src/components/layout/dashboard-layout.tsx`

**Purpose**: Main layout wrapper for authenticated pages providing consistent structure.

**Props**:
```typescript
interface DashboardLayoutProps {
  children: React.ReactNode
  title: string
}
```

**Features**:
- Responsive sidebar management
- Mobile-friendly design
- Consistent page structure
- Header integration

**Usage**:
```tsx
<DashboardLayout title="Users">
  <div>Page content</div>
</DashboardLayout>
```

### Sidebar

**Location**: `src/components/layout/sidebar.tsx`

**Purpose**: Navigation sidebar with responsive behavior and active state management.

**Props**:
```typescript
interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}
```

**Features**:
- Icon-based navigation
- Active state indicators
- Mobile overlay
- Responsive design
- Navigation items:
  - Dashboard
  - Users
  - Products
  - Entities
  - Interactions
  - Campaigns
  - Offers
  - Analytics
  - Settings

**Navigation Structure**:
```typescript
const navigation = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Users', href: '/users', icon: Users },
  { name: 'Products', href: '/products', icon: Package },
  { name: 'Entities', href: '/entities', icon: Building2 },
  { name: 'Interactions', href: '/interactions', icon: MessageSquare },
  { name: 'Campaigns', href: '/campaigns', icon: Megaphone },
  { name: 'Offers', href: '/offers', icon: Gift },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Settings', href: '/settings', icon: Settings },
]
```

### Header

**Location**: `src/components/layout/header.tsx`

**Purpose**: Top navigation bar with user information and controls.

**Props**:
```typescript
interface HeaderProps {
  onMenuClick: () => void
  title: string
}
```

**Features**:
- User profile display
- Notification bell with badge
- Logout functionality
- Mobile menu toggle
- Responsive design

**User Information Display**:
- User avatar (initials)
- Full name and email
- Logout button

## Dashboard Components

### DashboardStats

**Location**: `src/components/dashboard/dashboard-stats.tsx`

**Purpose**: Displays key performance indicators and metrics.

**Features**:
- Grid layout with responsive columns
- Icon-based stat cards
- Change indicators (positive/negative)
- Hover effects

**Stats Displayed**:
- Total Users: 1,234 (+12%)
- Products: 89 (+5.2%)
- Entities: 156 (+8.1%)
- Revenue: $45,231 (+8.2%)
- Growth Rate: 23.1% (+2.1%)
- Active Sessions: 89 (-3.2%)

**Stat Card Structure**:
```typescript
interface Stat {
  name: string
  value: string
  change: string
  changeType: 'positive' | 'negative'
  icon: LucideIcon
}
```

### QuickActions

**Location**: `src/components/dashboard/quick-actions.tsx`

**Purpose**: Provides shortcut buttons for common tasks.

**Features**:
- Action buttons for quick access
- Icon-based design
- Responsive layout

### RecentActivity

**Location**: `src/components/dashboard/recent-activity.tsx`

**Purpose**: Shows recent system activities and updates.

**Features**:
- Activity feed
- Timestamp display
- User attribution
- Action categorization

## User Management Components

### UsersTable

**Location**: `src/components/users/users-table.tsx`

**Purpose**: Comprehensive user management interface with CRUD operations.

**Features**:
- **Search Functionality**: Real-time search across user data
- **Filtering**: Role-based filtering (Admin/User)
- **Pagination**: Handles large datasets efficiently
- **Sorting**: Column-based sorting
- **Actions**: View, edit, delete operations
- **Responsive Design**: Mobile-friendly table layout

**Table Columns**:
- User (avatar, name, username)
- Email
- Role (Admin/User badge)
- Status (Active/Inactive badge)
- Joined date
- Actions (view, edit, delete, more)

**State Management**:
```typescript
const [searchTerm, setSearchTerm] = useState('')
const [currentPage, setCurrentPage] = useState(1)
const [pageSize] = useState(10)
```

**Data Fetching**:
```typescript
const { data: users, isLoading, error } = useQuery({
  queryKey: ['users', currentPage, pageSize, searchTerm],
  queryFn: () => usersApi.getUsers({
    page: currentPage,
    page_size: pageSize,
    search: searchTerm,
  }),
})
```

**Loading States**:
- Skeleton loading animation
- Error state handling
- Empty state display

### UsersStats

**Location**: `src/components/users/users-stats.tsx`

**Purpose**: Displays user-related statistics and metrics.

**Features**:
- User count metrics
- Growth indicators
- Role distribution
- Activity metrics

## Analytics Components

### AnalyticsOverview

**Location**: `src/components/analytics/analytics-overview.tsx`

**Purpose**: High-level analytics summary with key performance indicators.

**Features**:
- KPI cards with trends
- Revenue metrics
- User growth indicators
- Conversion rates

### RevenueChart

**Location**: `src/components/analytics/revenue-chart.tsx`

**Purpose**: Revenue visualization with interactive charts.

**Features**:
- Line/bar chart visualization
- Time period selection
- Interactive tooltips
- Responsive design
- Data export capabilities

**Chart Library**: Recharts

### UserGrowthChart

**Location**: `src/components/analytics/user-growth-chart.tsx`

**Purpose**: User acquisition and growth trend visualization.

**Features**:
- Growth trend lines
- Period comparison
- User acquisition metrics
- Retention indicators

### TopProducts

**Location**: `src/components/analytics/top-products.tsx`

**Purpose**: Best-performing products display.

**Features**:
- Product ranking
- Performance metrics
- Sales data
- Category breakdown

### RecentInteractions

**Location**: `src/components/analytics/recent-interactions.tsx`

**Purpose**: Latest user interactions and activities.

**Features**:
- Activity timeline
- Interaction types
- User attribution
- Timestamp display

## Page Components

### Dashboard Page

**Location**: `src/app/page.tsx`

**Purpose**: Main dashboard landing page.

**Components Used**:
- `DashboardLayout`
- `DashboardStats`
- `QuickActions`
- `RecentActivity`

**Layout Structure**:
```tsx
<DashboardLayout title="Dashboard">
  <div className="space-y-6">
    <div>Welcome Section</div>
    <DashboardStats />
    <QuickActions />
    <RecentActivity />
  </div>
</DashboardLayout>
```

### Users Page

**Location**: `src/app/users/page.tsx`

**Purpose**: User management interface.

**Components Used**:
- `DashboardLayout`
- `UsersStats`
- `UsersTable`

**Layout Structure**:
```tsx
<DashboardLayout title="Users">
  <div className="space-y-6">
    <div>Header Section</div>
    <UsersStats />
    <UsersTable />
  </div>
</DashboardLayout>
```

### Analytics Page

**Location**: `src/app/analytics/page.tsx`

**Purpose**: Comprehensive analytics dashboard.

**Components Used**:
- `DashboardLayout`
- `AnalyticsOverview`
- `RevenueChart`
- `UserGrowthChart`
- `TopProducts`
- `RecentInteractions`

**Layout Structure**:
```tsx
<DashboardLayout title="Analytics">
  <div className="space-y-6">
    <div>Header Section</div>
    <AnalyticsOverview />
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <RevenueChart />
      <UserGrowthChart />
    </div>
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <TopProducts />
      <RecentInteractions />
    </div>
  </div>
</DashboardLayout>
```

### Login Page

**Location**: `src/app/login/page.tsx`

**Purpose**: User authentication interface.

**Features**:
- Form validation
- Loading states
- Error handling
- Success feedback
- Automatic redirect

**Form Fields**:
- Username (required)
- Password (required)

**State Management**:
```typescript
const [isLoading, setIsLoading] = useState(false)
```

**Authentication Flow**:
1. Form submission
2. Server Action call
3. Token storage
4. User data storage
5. Redirect to dashboard

## Shared Components

### Providers

**Location**: `src/app/providers.tsx`

**Purpose**: Application-wide context providers.

**Providers**:
- `QueryClientProvider`: React Query configuration
- `Toaster`: Notification system

**Configuration**:
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000, // 1 minute
      retry: 1,
    },
  },
})
```

## Component Patterns

### Loading States

All data-fetching components implement consistent loading patterns:

```tsx
if (isLoading) {
  return (
    <div className="animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
      <div className="space-y-3">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-4 bg-gray-200 rounded"></div>
        ))}
      </div>
    </div>
  )
}
```

### Error Handling

Consistent error display across components:

```tsx
if (error) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-md p-4">
      <div className="text-red-700">
        Error loading data: {error instanceof Error ? error.message : 'Unknown error'}
      </div>
    </div>
  )
}
```

### Responsive Design

All components use Tailwind CSS responsive utilities:

```tsx
<div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
  {/* Content */}
</div>
```

## Styling Guidelines

### CSS Classes

**Button Variants**:
- `.btn`: Base button styles
- `.btn-primary`: Primary action buttons
- `.btn-secondary`: Secondary actions
- `.btn-destructive`: Delete/danger actions
- `.btn-outline`: Outlined buttons
- `.btn-ghost`: Minimal buttons

**Size Variants**:
- `.btn-sm`: Small buttons
- `.btn-lg`: Large buttons

**Form Elements**:
- `.input`: Standard input styling

**Cards**:
- `.card`: Card container styling

### Color System

**Primary Colors**:
- Primary: `hsl(var(--primary))` - Blue
- Secondary: `hsl(var(--secondary))` - Gray
- Success: Green variants
- Warning: Yellow variants
- Error: Red variants

**Status Indicators**:
- Active: Green badges
- Inactive: Red badges
- Admin: Green badges
- User: Blue badges

## Component Testing

### Testing Strategy

1. **Unit Tests**: Individual component functionality
2. **Integration Tests**: Component interactions
3. **Visual Tests**: UI consistency
4. **Accessibility Tests**: Screen reader compatibility

### Test Patterns

```tsx
// Component rendering test
test('renders user table with data', () => {
  render(<UsersTable />)
  expect(screen.getByText('Users')).toBeInTheDocument()
})

// Interaction test
test('handles search input', () => {
  render(<UsersTable />)
  const searchInput = screen.getByPlaceholderText('Search users...')
  fireEvent.change(searchInput, { target: { value: 'john' } })
  expect(searchInput.value).toBe('john')
})
```

## Performance Considerations

### Optimization Techniques

1. **Code Splitting**: Dynamic imports for large components
2. **Memoization**: React.memo for expensive components
3. **Virtual Scrolling**: For large data tables
4. **Image Optimization**: Next.js Image component
5. **Bundle Analysis**: Regular bundle size monitoring

### Best Practices

1. **Lazy Loading**: Load components on demand
2. **Error Boundaries**: Graceful error handling
3. **Loading States**: Consistent loading indicators
4. **Accessibility**: ARIA labels and keyboard navigation
5. **SEO**: Proper meta tags and structured data

## Future Enhancements

### Planned Components

1. **ProductTable**: Product management interface
2. **EntityTable**: Entity management interface
3. **InteractionTable**: Interaction tracking interface
4. **CampaignTable**: Campaign management interface
5. **OfferTable**: Offer management interface
6. **SettingsForm**: System configuration interface
7. **UserForm**: User creation/editing modal
8. **ProductForm**: Product creation/editing modal

### Component Improvements

1. **Advanced Filtering**: Multi-column filtering
2. **Bulk Operations**: Multi-select actions
3. **Export Functionality**: Data export capabilities
4. **Real-time Updates**: WebSocket integration
5. **Drag and Drop**: Reorderable lists
6. **Keyboard Shortcuts**: Power user features

---

*Last updated: December 2024*
*Version: 0.1.0*
