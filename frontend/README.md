# BackboneOS Frontend

A modern Next.js 15 frontend for the BackboneOS CRM system, built with App Router, TypeScript, and Tailwind CSS.

## Features

- ⚡ **Next.js 15**: Latest Next.js with App Router and React Server Components
- 🔷 **TypeScript**: Full type safety and better developer experience
- 🎨 **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- 📊 **React Query**: Powerful data fetching and caching
- 🗃️ **Server Actions**: Server-side mutations with Next.js 15
- 🔐 **Authentication**: JWT-based authentication with automatic token refresh
- 📱 **Responsive**: Mobile-first responsive design
- 🚀 **Performance**: Optimized for Render.com deployment

## Architecture

### Rendering Strategy

- **App Shell (dashboards, records)**: SSR with RSC streaming
- **Cache reads**: `fetch()` on the server with smart revalidation
- **Mutations**: Direct Django API calls via Server Actions as BFF/proxy
- **Authentication**: Centralized auth handling to avoid CORS issues

### Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Data Fetching**: React Query + Server Actions
- **Charts**: Recharts
- **Icons**: Lucide React
- **Forms**: React Hook Form + Zod validation

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- BackboneOS backend running on port 8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create environment file:
```bash
cp .env.example .env.local
```

3. Update the API base URL in `.env.local`:
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

4. Start the development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`.

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## Project Structure

```
src/
├── app/                    # Next.js App Router pages
│   ├── analytics/         # Analytics dashboard
│   ├── users/            # Users management
│   ├── products/         # Products management
│   ├── entities/         # Entities management
│   ├── interactions/     # Interactions management
│   ├── campaigns/        # Campaigns management
│   ├── offers/           # Offers management
│   ├── settings/         # Settings page
│   ├── login/            # Login page
│   ├── layout.tsx        # Root layout
│   ├── page.tsx          # Dashboard home
│   └── providers.tsx     # React Query provider
├── components/           # Reusable UI components
│   ├── analytics/        # Analytics components
│   ├── dashboard/        # Dashboard components
│   ├── layout/           # Layout components
│   └── users/            # User management components
├── lib/                  # Utility functions
│   ├── api.ts           # API client
│   ├── server-actions.ts # Server Actions
│   └── utils.ts         # Utility functions
└── types/               # TypeScript type definitions
    └── index.ts         # Shared types
```

## Backend Integration

> **⚠️ Important for Developers and AI Assistants**: When working with the frontend, you **MUST** reference the backend codebase to understand data models, API endpoints, and field structures. The backend contains the source of truth for all data models and API contracts.

### Backend Codebase Reference

**Key Backend Files to Reference:**
- `backend/world/models.py` - Data models for industries, skills, market segments, tags, etc.
- `backend/products/models.py` - Product-related data models
- `backend/entities/models.py` - Entity and organization models
- `backend/interactions/models.py` - Interaction and touchpoint models
- `backend/campaigns/models.py` - Campaign models
- `backend/offers/models.py` - Offer models
- `backend/*/serializers.py` - API serializers that define response structure
- `backend/*/views.py` - API endpoints and their behavior

**Common Issues When Not Referencing Backend:**
- Using wrong field names (e.g., `id` vs `slug` for Tag model)
- Incorrect data types in form handling
- Missing required fields in API requests
- Incorrect relationship handling

**Example**: The `Tag` model uses `slug` as primary key, not `id`. Always check the backend models to understand the correct field structure.

## API Integration

The frontend integrates with the Django REST API backend through:

### Server Actions (BFF/Proxy)
- `loginAction()` - User authentication
- `logoutAction()` - User logout
- `createUserAction()` - Create new user
- `updateUserAction()` - Update user
- `deleteUserAction()` - Delete user
- `createProductAction()` - Create product
- `updateProductAction()` - Update product
- `deleteProductAction()` - Delete product

### Client-side API
- `authApi` - Authentication endpoints
- `usersApi` - User management
- `productsApi` - Product management
- `entitiesApi` - Entity management
- `interactionsApi` - Interaction management
- `campaignsApi` - Campaign management
- `offersApi` - Offer management

## Authentication

The app uses token-based authentication with automatic token refresh:

1. **Login**: Server Action handles authentication
2. **Token Storage**: Stored in localStorage (production: httpOnly cookies)
3. **API Requests**: Automatic token injection via axios interceptors
4. **Logout**: Server Action handles cleanup and redirect

## Deployment

### Render.com Deployment

The app is configured for Render.com deployment with:

- **Docker**: Multi-stage Docker build for optimization
- **Standalone Output**: Next.js standalone mode for smaller images
- **Environment Variables**: Configured for production
- **Health Checks**: Built-in health check endpoint

### Environment Variables

Set these in your Render.com dashboard:

```bash
NEXT_PUBLIC_API_BASE=https://your-backend-url.onrender.com
NODE_ENV=production
```

### SSL Certificate Handling

The frontend automatically handles SSL certificates based on the environment:

- **Development**: SSL certificate verification is disabled for self-signed certificates (localhost, orb.local)
- **Production**: Full SSL certificate verification is enforced

This is controlled by checking:
- `NODE_ENV` environment variable
- API base URL domain (localhost/orb.local vs production domains)

**Security Note**: The SSL bypass only applies to development environments with self-signed certificates. In production, proper SSL certificates are required and verification cannot be disabled.

### Build Configuration

The app uses:
- **Output**: `standalone` for Docker deployment
- **Compression**: Enabled for better performance
- **Security Headers**: Configured for production
- **Image Optimization**: Next.js Image component

## Performance Optimizations

- **Server Components**: Reduced client-side JavaScript
- **Streaming**: RSC streaming for faster page loads
- **Caching**: Smart revalidation with `fetch()`
- **Bundle Optimization**: Tree shaking and code splitting
- **Image Optimization**: Next.js Image component
- **Font Optimization**: Next.js Font optimization

## Security Features

- **CSRF Protection**: Server Actions provide CSRF protection
- **XSS Prevention**: React's built-in XSS protection
- **Content Security Policy**: Configured headers
- **Secure Headers**: Security headers for production
- **Input Validation**: Zod schema validation

## Development Workflow

### Before Starting Development

1. **Always Reference Backend Models**: Before implementing any frontend feature, examine the corresponding backend models to understand:
   - Field names and types
   - Required vs optional fields
   - Relationships and foreign keys
   - Primary key structure (UUID, slug, etc.)

2. **Check API Serializers**: Review the serializer files to understand the exact API response structure and field names.

3. **Verify API Endpoints**: Check the views.py files to understand available endpoints and their parameters.

### Development Process

1. **Backend-First Approach**: 
   - Start by understanding the backend data model
   - Check existing API endpoints
   - Review serializer structure
   - Then implement frontend accordingly

2. **Common Patterns**:
   - Use `slug` for Tag model (not `id`)
   - Use `UUID` for most other models
   - Check `is_active` fields for filtering
   - Understand relationship field structures

3. **Testing with Real Data**: Always test with actual backend data to catch field mismatches early.

## Contributing

1. Fork the repository
2. **Reference backend models** before implementing features
3. Create a feature branch
4. Make your changes with proper backend integration
5. Run tests and linting
6. Submit a pull request with backend model references

## License

This project is licensed under the MIT License.
