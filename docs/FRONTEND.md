# BackboneOS Frontend Documentation

## Overview

The BackboneOS frontend is a modern, responsive web application built with Next.js 15, TypeScript, and Tailwind CSS. It provides a comprehensive CRM dashboard interface for managing users, products, entities, interactions, campaigns, and offers.

## Architecture

### Technology Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript for type safety
- **Styling**: Tailwind CSS with custom design system
- **State Management**: React Query (TanStack Query) for server state
- **Forms**: React Hook Form with Zod validation
- **Charts**: Recharts for data visualization
- **Icons**: Lucide React
- **Notifications**: Sonner for toast notifications
- **Authentication**: JWT-based with automatic token refresh

### Rendering Strategy

The application uses a hybrid rendering approach:

- **Server Components**: For static content and initial data loading
- **Client Components**: For interactive features and real-time updates
- **Server Actions**: For mutations and form submissions (BFF pattern)
- **React Query**: For client-side data fetching and caching

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── analytics/         # Analytics dashboard
│   │   ├── users/            # User management
│   │   ├── products/         # Product management (planned)
│   │   ├── entities/         # Entity management (planned)
│   │   ├── interactions/     # Interaction management (planned)
│   │   ├── campaigns/        # Campaign management (planned)
│   │   ├── offers/           # Offer management (planned)
│   │   ├── settings/         # Settings page (planned)
│   │   ├── login/            # Authentication
│   │   ├── layout.tsx        # Root layout
│   │   ├── page.tsx          # Dashboard home
│   │   ├── providers.tsx     # React Query provider
│   │   └── globals.css       # Global styles
│   ├── components/           # Reusable UI components
│   │   ├── analytics/        # Analytics components
│   │   ├── dashboard/        # Dashboard components
│   │   ├── layout/           # Layout components
│   │   └── users/            # User management components
│   ├── lib/                  # Utility functions and configurations
│   │   ├── api.ts           # API client and endpoints
│   │   ├── server-actions.ts # Server Actions for mutations
│   │   └── utils.ts         # Utility functions
│   └── types/               # TypeScript type definitions
│       └── index.ts         # Shared types
├── public/                  # Static assets
├── Dockerfile              # Production Docker image
├── Dockerfile.dev          # Development Docker image
├── next.config.js          # Next.js configuration
├── tailwind.config.js      # Tailwind CSS configuration
├── package.json            # Dependencies and scripts
└── README.md               # Project documentation
```

## Core Features

### 1. Authentication System

**Login Page** (`/login`)
- JWT-based authentication
- Form validation with error handling
- Automatic token storage in localStorage
- Redirect to dashboard on successful login

**Authentication Flow**:
1. User submits credentials via Server Action
2. Backend validates and returns JWT token
3. Token stored in localStorage (development) or httpOnly cookies (production)
4. Automatic token injection in API requests
5. Token refresh handling for expired tokens

### 2. Dashboard Layout

**Responsive Design**:
- Mobile-first approach with responsive breakpoints
- Collapsible sidebar for mobile devices
- Fixed header with user information and notifications

**Navigation Structure**:
- Dashboard (home)
- Users management
- Products management
- Entities management
- Interactions management
- Campaigns management
- Offers management
- Analytics dashboard
- Settings

### 3. User Management

**Users Page** (`/users`)
- Comprehensive user table with search and filtering
- User statistics overview
- CRUD operations for user management
- Role-based access control display
- Pagination for large datasets

**Features**:
- Real-time search functionality
- Role filtering (Admin/User)
- Status indicators (Active/Inactive)
- Action buttons for view, edit, delete operations
- Responsive table design

### 4. Analytics Dashboard

**Analytics Page** (`/analytics`)
- Revenue charts and trends
- User growth analytics
- Top products performance
- Recent interactions overview
- Comprehensive business metrics

**Components**:
- `AnalyticsOverview`: Key performance indicators
- `RevenueChart`: Revenue trends over time
- `UserGrowthChart`: User acquisition metrics
- `TopProducts`: Best-performing products
- `RecentInteractions`: Latest user interactions

## API Integration

### Server Actions (BFF Pattern)

The frontend uses Next.js Server Actions as a Backend-for-Frontend (BFF) layer to handle mutations:

```typescript
// Authentication
loginAction(formData: FormData)
logoutAction()

// User Management
createUserAction(formData: FormData)
updateUserAction(id: number, formData: FormData)
deleteUserAction(id: number)

// Product Management
createProductAction(formData: FormData)
updateProductAction(id: number, formData: FormData)
deleteProductAction(id: number)
```

### Client-side API

For data fetching, the application uses a centralized API client:

```typescript
// API Modules
authApi        // Authentication endpoints
usersApi       // User management
productsApi    // Product management
entitiesApi    // Entity management
interactionsApi // Interaction management
campaignsApi   // Campaign management
offersApi      // Offer management
```

### API Client Features

- **Automatic Token Injection**: JWT tokens automatically added to requests
- **Error Handling**: Centralized error handling with 401 redirects
- **Request Logging**: Development-mode request logging
- **SSL Configuration**: Automatic SSL certificate handling for development

## Component Architecture

### Layout Components

**DashboardLayout**
- Main layout wrapper for authenticated pages
- Manages sidebar state and responsive behavior
- Provides consistent page structure

**Sidebar**
- Navigation menu with active state indicators
- Responsive design with mobile overlay
- Icon-based navigation with labels

**Header**
- Top navigation bar with user information
- Notification bell with badge
- Logout functionality
- Mobile menu toggle

### Feature Components

**Dashboard Components**:
- `DashboardStats`: Key metrics cards
- `QuickActions`: Shortcut buttons for common tasks
- `RecentActivity`: Latest system activities

**User Management Components**:
- `UsersTable`: Comprehensive user data table
- `UsersStats`: User-related statistics

**Analytics Components**:
- `AnalyticsOverview`: KPI summary cards
- `RevenueChart`: Revenue visualization
- `UserGrowthChart`: User growth trends
- `TopProducts`: Product performance
- `RecentInteractions`: Latest interactions

## Styling System

### Design System

**Color Palette**:
- Primary: Blue (#3B82F6)
- Secondary: Gray variants
- Success: Green
- Warning: Yellow
- Error: Red
- Neutral: Gray scale

**Typography**:
- Font: Inter (Google Fonts)
- Responsive text sizing
- Consistent font weights

**Spacing**:
- Tailwind CSS spacing scale
- Consistent component padding
- Responsive margins

### Custom CSS Classes

```css
/* Button variants */
.btn, .btn-primary, .btn-secondary, .btn-destructive
.btn-outline, .btn-ghost
.btn-sm, .btn-lg

/* Form elements */
.input

/* Cards */
.card
```

## State Management

### React Query Configuration

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

### Data Flow

1. **Server Components**: Initial data loading with `fetch()`
2. **Client Components**: Real-time updates with React Query
3. **Mutations**: Server Actions for form submissions
4. **Cache Management**: Automatic revalidation and cache updates

## Security Features

### Authentication Security

- JWT token-based authentication
- Automatic token refresh
- Secure token storage (localStorage in dev, httpOnly cookies in prod)
- Automatic logout on token expiration

### Request Security

- CSRF protection via Server Actions
- XSS prevention through React's built-in protection
- Content Security Policy headers
- Secure HTTP headers configuration

### SSL Configuration

- Development: SSL certificate verification disabled for self-signed certificates
- Production: Full SSL certificate verification enforced
- Automatic environment detection

## Performance Optimizations

### Next.js Optimizations

- **Server Components**: Reduced client-side JavaScript
- **Streaming**: RSC streaming for faster page loads
- **Image Optimization**: Next.js Image component
- **Font Optimization**: Next.js Font optimization
- **Bundle Optimization**: Tree shaking and code splitting

### Caching Strategy

- **Server-side**: Smart revalidation with `fetch()`
- **Client-side**: React Query caching with stale-while-revalidate
- **Static Assets**: CDN-ready static file serving

## Development Workflow

### Available Scripts

```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript type checking
```

### Environment Configuration

**Development**:
```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
NODE_ENV=development
```

**Production**:
```bash
NEXT_PUBLIC_API_BASE=https://your-backend-url.onrender.com
NODE_ENV=production
```

## Deployment

### Docker Configuration

**Production Dockerfile**:
- Multi-stage build for optimization
- Node.js 20 Alpine base image
- Standalone output for smaller images
- Non-root user for security

**Development Dockerfile**:
- Development dependencies
- Hot reload support
- Volume mounting for live updates

### Render.com Deployment

- **Build Command**: `npm run build`
- **Start Command**: `npm start`
- **Environment Variables**: Configured for production
- **Health Checks**: Built-in health check endpoint

### Build Configuration

- **Output**: `standalone` for Docker deployment
- **Compression**: Enabled for better performance
- **Security Headers**: Configured for production
- **Image Optimization**: Next.js Image component

## Testing Strategy

### Component Testing

- Unit tests for individual components
- Integration tests for component interactions
- Visual regression testing for UI consistency

### API Testing

- Mock API responses for development
- Integration tests with real backend
- Error handling validation

## Future Enhancements

### Planned Features

1. **Product Management**: Complete CRUD interface for products
2. **Entity Management**: Business entity management system
3. **Interaction Tracking**: Customer interaction logging
4. **Campaign Management**: Marketing campaign tools
5. **Offer Management**: Promotional offer system
6. **Settings Page**: System configuration interface
7. **Real-time Updates**: WebSocket integration for live data
8. **Advanced Analytics**: More detailed reporting and insights

### Technical Improvements

1. **PWA Support**: Progressive Web App capabilities
2. **Offline Support**: Service worker implementation
3. **Advanced Caching**: More sophisticated caching strategies
4. **Performance Monitoring**: Real-time performance tracking
5. **Accessibility**: Enhanced accessibility features
6. **Internationalization**: Multi-language support

## Contributing

### Development Setup

1. Clone the repository
2. Install dependencies: `npm install`
3. Set up environment variables
4. Start development server: `npm run dev`

### Code Standards

- TypeScript for all new code
- ESLint configuration for code quality
- Prettier for code formatting
- Conventional commits for version control

### Pull Request Process

1. Create feature branch
2. Implement changes with tests
3. Run linting and type checking
4. Submit pull request with description
5. Code review and approval process

## Troubleshooting

### Common Issues

**SSL Certificate Errors**:
- Development: Automatically handled for localhost/orb.local
- Production: Ensure valid SSL certificates

**API Connection Issues**:
- Check `NEXT_PUBLIC_API_BASE` environment variable
- Verify backend server is running
- Check network connectivity

**Build Errors**:
- Clear `.next` directory
- Reinstall dependencies
- Check TypeScript errors

### Debug Mode

Enable debug logging by setting:
```bash
NODE_ENV=development
```

This will show detailed API request logs and error information.

## Support

For technical support or questions about the frontend:

1. Check the troubleshooting section
2. Review the component documentation
3. Check GitHub issues
4. Contact the development team

---

*Last updated: December 2024*
*Version: 0.1.0*