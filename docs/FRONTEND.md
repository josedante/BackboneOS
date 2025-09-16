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

## Backend Integration

> **⚠️ Critical for Developers and AI Assistants**: The frontend is tightly coupled with the Django backend. **ALWAYS** reference the backend codebase when implementing frontend features to understand data models, API contracts, and field structures.

### Backend Codebase Reference Guide

**Essential Backend Files to Review:**

1. **Data Models** (Source of Truth):
   - `backend/world/models.py` - Industries, skills, market segments, tags, countries, etc.
   - `backend/products/models.py` - Product models and relationships
   - `backend/entities/models.py` - People, organizations, contacts
   - `backend/interactions/models.py` - Interactions, touchpoints, agents
   - `backend/campaigns/models.py` - Campaign models and hierarchies
   - `backend/offers/models.py` - Offer models and validity

2. **API Serializers** (Response Structure):
   - `backend/*/serializers.py` - Defines exact API response format
   - Pay attention to field names, data types, and nested structures

3. **API Views** (Endpoints and Behavior):
   - `backend/*/views.py` - Available endpoints, parameters, and business logic

### Common Backend-Frontend Integration Issues

| Issue | Backend Model | Frontend Mistake | Correct Approach |
|-------|---------------|------------------|------------------|
| Tag Primary Key | `Tag.slug` (primary key) | Using `tag.id` | Use `tag.slug` |
| UUID Fields | Most models use UUID | Using string/number | Use UUID type |
| Active Filtering | `is_active` boolean | Not filtering | Always filter by `is_active=True` |
| Relationship Fields | Foreign key structure | Wrong field names | Check model relationships |

### Development Checklist

Before implementing any frontend feature:

- [ ] **Review Backend Model**: Check the corresponding model in `backend/*/models.py`
- [ ] **Check Serializer**: Review `backend/*/serializers.py` for response structure
- [ ] **Verify Endpoints**: Check `backend/*/views.py` for available endpoints
- [ ] **Test with Real Data**: Use actual backend data to validate field names
- [ ] **Handle Edge Cases**: Check for nullable fields, default values, and constraints

### Example: Tag Model Integration

```python
# backend/world/models.py
class Tag(models.Model):
    slug = models.SlugField(primary_key=True)  # ← Primary key is slug, not id
    name = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
```

```typescript
// frontend - CORRECT approach
{tags.filter((tag: any) => tag.slug).map((tag: any) => (
  <label key={`tag-${tag.slug}`}>  // ← Use slug as key
    <input 
      checked={formData.tags_ids?.includes(tag.slug)}  // ← Use slug
      onChange={(e) => {
        // Handle slug, not id
      }}
    />
  </label>
))}
```

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

## AI Assistant and Developer Guidance

### For AI Assistants Working on Frontend

When helping with frontend development, **ALWAYS**:

1. **Read Backend Models First**: Before suggesting any frontend implementation, examine the corresponding backend model to understand:
   - Primary key structure (UUID, slug, integer)
   - Field names and data types
   - Required vs optional fields
   - Relationships and foreign keys

2. **Check API Serializers**: Review the serializer to understand the exact response structure and field names.

3. **Validate Field Names**: Use the exact field names from the backend models, not assumptions.

4. **Handle Edge Cases**: Consider nullable fields, default values, and data validation rules from the backend.

### Common AI Assistant Mistakes to Avoid

- ❌ Assuming all models use `id` as primary key (Tag uses `slug`)
- ❌ Using generic field names without checking backend models
- ❌ Not filtering by `is_active` fields when appropriate
- ❌ Incorrect data type handling (UUID vs string vs number)
- ❌ Missing required fields in form submissions

### AI Assistant Workflow

1. **User asks about frontend feature**
2. **AI reads corresponding backend model** (e.g., `backend/world/models.py` for Tag)
3. **AI checks serializer structure** (e.g., `backend/world/serializers.py`)
4. **AI implements frontend with correct field names and types**
5. **AI includes backend model references in response**

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

## Development Roadmap

Based on the comprehensive backend API available, here's the prioritized development plan for the frontend:

### 🎯 **Phase 1: Core Business Features (6-9 weeks)**

#### **Products Management System** (2-3 weeks)
**Backend Endpoints Available:**
- `/api/products/divisions/` - Product divisions
- `/api/products/categories/` - Product categories  
- `/api/products/products/` - Full CRUD for products
- `/api/products/analytics/*` - Comprehensive analytics

**Frontend Implementation:**
- Create `ProductsPage` with full CRUD interface
- Build `ProductsTable` component with advanced filtering
- Implement product creation/editing forms with validation
- Add product analytics dashboard with charts
- Create division and category management interfaces
- Implement product search and bulk operations

#### **Entities Management System** (2-3 weeks)
**Backend Endpoints Available:**
- `/api/entities/people/` - Individual people
- `/api/entities/organizations/` - Organizations
- `/api/entities/contacts/` - Contact details
- `/api/entities/profiles/` - Individual profiles

**Frontend Implementation:**
- Create `EntitiesPage` with tabbed interface (People/Organizations)
- Build `PeopleTable` and `OrganizationsTable` components
- Implement contact management interface
- Add entity relationship visualization
- Create entity search and filtering system
- Implement entity import/export functionality

#### **Interactions Management System** (2-3 weeks)
**Backend Endpoints Available:**
- `/api/interactions/interactions/` - Main interactions
- `/api/interactions/actions/` - Action types
- `/api/interactions/channels/` - Communication channels
- `/api/interactions/agents/` - Interaction agents

**Frontend Implementation:**
- Create `InteractionsPage` with timeline view
- Build interaction tracking interface
- Implement channel and agent management
- Add interaction analytics and reporting
- Create interaction templates and automation
- Implement real-time interaction updates

### 🚀 **Phase 2: Advanced Business Features (6-8 weeks)**

#### **Campaigns Management System** (3-4 weeks)
**Backend Endpoints Available:**
- `/api/campaigns/campaigns/` - Full campaign CRUD
- `/api/campaigns/campaigns/active_now/` - Active campaigns
- `/api/campaigns/campaigns/analytics/` - Campaign analytics

**Frontend Implementation:**
- Create `CampaignsPage` with campaign calendar
- Build campaign creation wizard with templates
- Implement campaign performance tracking
- Add campaign touchpoint management
- Create campaign automation workflows
- Implement campaign A/B testing interface

#### **Offers Management System** (3-4 weeks)
**Backend Endpoints Available:**
- `/api/offers/offerings/` - Product offerings
- `/api/offers/offerings/currently_valid/` - Valid offers
- `/api/offers/offerings/analytics/` - Offer analytics

**Frontend Implementation:**
- Create `OffersPage` with offer management
- Build offer creation with product linking
- Implement offer validity tracking and scheduling
- Add offer performance analytics
- Create offer template system
- Implement offer approval workflows

### 🔧 **Phase 3: System Administration (4-5 weeks)**

#### **World/Reference Data Management** (2-3 weeks)
**Backend Endpoints Available:**
- `/api/world/countries/` - Countries
- `/api/world/industries/` - Industries
- `/api/world/market-segments/` - Market segments
- `/api/world/tags/` - Tags system

**Frontend Implementation:**
- Create `SettingsPage` with reference data management
- Build tag management interface with categorization
- Implement industry/segment management
- Add country/region management
- Create data import/export tools
- Implement data validation and cleanup tools

#### **Enhanced Analytics Dashboard** (2-3 weeks)
**Backend Analytics Available:**
- Product analytics with market segmentation
- Growth analytics and recommendations
- Pricing analytics
- Campaign performance analytics

**Frontend Implementation:**
- Enhance existing analytics page with real data
- Add interactive charts and advanced filtering
- Implement data export functionality
- Create custom dashboard builder
- Add real-time analytics updates
- Implement analytics sharing and scheduling

### 🛠 **Phase 4: Technical Enhancements (3-4 weeks)**

#### **Advanced Search and Filtering** (2 weeks)
**Backend Features Available:**
- Advanced product search
- Semantic search capabilities
- Hierarchical filtering
- Bulk operations

**Frontend Implementation:**
- Implement global search functionality
- Add advanced filter panels with saved filters
- Create saved search functionality
- Build bulk action interfaces
- Implement search suggestions and autocomplete
- Add search analytics and optimization

#### **Performance and UX Improvements** (1-2 weeks)
**Technical Improvements:**
- Implement virtual scrolling for large tables
- Add progressive loading and skeleton screens
- Optimize bundle size and code splitting
- Implement offline support with service workers
- Add keyboard shortcuts and power user features
- Enhance accessibility and screen reader support

### 📋 **Implementation Priority Matrix**

| Feature | Business Impact | Technical Complexity | Backend Support | Priority |
|---------|----------------|---------------------|-----------------|----------|
| Products Management | High | Medium | Complete | 1 |
| Entities Management | High | Medium | Complete | 2 |
| Interactions System | High | High | Complete | 3 |
| Campaigns Management | Medium | High | Complete | 4 |
| Offers Management | Medium | Medium | Complete | 5 |
| Analytics Dashboard | High | Medium | Complete | 6 |
| Reference Data Mgmt | Low | Low | Complete | 7 |
| Advanced Search | Medium | Medium | Complete | 8 |

### 🎯 **Quick Wins (1-2 weeks each)**

1. **Products Page**: Basic CRUD interface with existing backend
2. **Entities Page**: People and organizations management
3. **Enhanced Analytics**: Connect real data to existing charts
4. **Settings Page**: Basic reference data management
5. **Global Search**: Simple search across all entities

### 🚀 **Advanced Features (Future Phases)**

1. **Real-time Updates**: WebSocket integration for live data
2. **PWA Support**: Progressive Web App capabilities
3. **Mobile App**: React Native or PWA mobile version
4. **Advanced Workflows**: Business process automation
5. **AI Integration**: Smart recommendations and insights
6. **Multi-tenancy**: Support for multiple organizations
7. **API Marketplace**: Third-party integrations
8. **Advanced Reporting**: Custom report builder

### 🛠 **Technical Debt and Improvements**

1. **Testing Coverage**: Unit, integration, and E2E tests
2. **Performance Monitoring**: Real-time performance tracking
3. **Error Tracking**: Comprehensive error monitoring
4. **Security Audit**: Security vulnerability assessment
5. **Accessibility**: WCAG 2.1 AA compliance
6. **Internationalization**: Multi-language support
7. **Documentation**: API documentation and user guides
8. **DevOps**: CI/CD pipeline optimization

### 📊 **Success Metrics**

- **User Adoption**: Active users per feature
- **Performance**: Page load times and responsiveness
- **User Experience**: Task completion rates and user satisfaction
- **Code Quality**: Test coverage and maintainability
- **Business Impact**: Feature usage and business value

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