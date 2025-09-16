# Frontend API Integration Documentation

## Overview

The BackboneOS frontend integrates with the Django REST API backend through a dual-layer approach: Server Actions for mutations and a client-side API client for data fetching. This architecture provides security, performance, and maintainability benefits.

## Architecture

### API Integration Layers

1. **Server Actions (BFF Layer)**: Handles mutations and form submissions
2. **Client-side API**: Handles data fetching and real-time updates
3. **Authentication Layer**: JWT token management and automatic refresh

### Data Flow

```
Frontend Component → Server Action → Django API → Database
Frontend Component → React Query → API Client → Django API → Database
```

## Server Actions (BFF Pattern)

### Location
`src/lib/server-actions.ts`

### Purpose
Server Actions act as a Backend-for-Frontend (BFF) layer, providing:
- CSRF protection
- Server-side validation
- Centralized error handling
- Automatic revalidation

### Authentication Actions

#### loginAction

**Function**: `loginAction(formData: FormData)`

**Purpose**: Authenticate user and return JWT token.

**Parameters**:
```typescript
formData: FormData {
  username: string
  password: string
}
```

**Returns**:
```typescript
{
  success: boolean
  token?: string
  user?: User
  error?: string
}
```

**Usage**:
```tsx
const formData = new FormData()
formData.append('username', 'john_doe')
formData.append('password', 'password123')

const result = await loginAction(formData)
if (result.success) {
  localStorage.setItem('auth_token', result.token)
  router.push('/')
}
```

#### logoutAction

**Function**: `logoutAction()`

**Purpose**: Logout user and redirect to login page.

**Returns**: Redirects to `/login`

**Usage**:
```tsx
await logoutAction()
```

### User Management Actions

#### createUserAction

**Function**: `createUserAction(formData: FormData)`

**Purpose**: Create a new user.

**Parameters**:
```typescript
formData: FormData {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
}
```

**Returns**:
```typescript
{
  success: boolean
  user?: User
  error?: string
}
```

**Usage**:
```tsx
const formData = new FormData()
formData.append('username', 'new_user')
formData.append('email', 'user@example.com')
formData.append('first_name', 'John')
formData.append('last_name', 'Doe')
formData.append('password', 'secure_password')

const result = await createUserAction(formData)
```

#### updateUserAction

**Function**: `updateUserAction(id: number, formData: FormData)`

**Purpose**: Update an existing user.

**Parameters**:
- `id: number` - User ID
- `formData: FormData` - Updated user data

**Returns**:
```typescript
{
  success: boolean
  user?: User
  error?: string
}
```

#### deleteUserAction

**Function**: `deleteUserAction(id: number)`

**Purpose**: Delete a user.

**Parameters**:
- `id: number` - User ID

**Returns**:
```typescript
{
  success: boolean
  error?: string
}
```

### Product Management Actions

#### createProductAction

**Function**: `createProductAction(formData: FormData)`

**Purpose**: Create a new product.

**Parameters**:
```typescript
formData: FormData {
  name: string
  description: string
  price: number
  category: string
}
```

#### updateProductAction

**Function**: `updateProductAction(id: number, formData: FormData)`

**Purpose**: Update an existing product.

#### deleteProductAction

**Function**: `deleteProductAction(id: number)`

**Purpose**: Delete a product.

## Client-side API

### Location
`src/lib/api.ts`

### API Client Configuration

```typescript
export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  ...(httpsAgent && { httpsAgent }),
})
```

### Authentication Interceptors

#### Request Interceptor
```typescript
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})
```

#### Response Interceptor
```typescript
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)
```

### SSL Configuration

The API client automatically handles SSL certificates based on environment:

```typescript
const isDevelopment = process.env.NODE_ENV === 'development' || 
                     process.env['NEXT_PUBLIC_NODE_ENV'] === 'development' ||
                     API_BASE.includes('localhost') ||
                     API_BASE.includes('orb.local')

const httpsAgent = isDevelopment ? new https.Agent({
  rejectUnauthorized: false
}) : undefined
```

**Development**: SSL verification disabled for self-signed certificates
**Production**: Full SSL verification enforced

## API Modules

### Authentication API

**Module**: `authApi`

#### login
```typescript
authApi.login(username: string, password: string)
```

**Endpoint**: `POST /users/jwt/login/`

**Request**:
```json
{
  "username": "john_doe",
  "password": "password123"
}
```

**Response**:
```json
{
  "access": "jwt_token_here",
  "refresh": "refresh_token_here",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

#### getCurrentUser
```typescript
authApi.getCurrentUser()
```

**Endpoint**: `GET /users/user/`

**Response**:
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_active": true,
  "date_joined": "2024-01-01T00:00:00Z"
}
```

#### logout
```typescript
authApi.logout()
```

**Endpoint**: `POST /users/jwt/logout/`

### Users API

**Module**: `usersApi`

#### getUsers
```typescript
usersApi.getUsers(params?: ApiParams)
```

**Endpoint**: `GET /api/users/`

**Parameters**:
```typescript
interface ApiParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  [key: string]: unknown
}
```

**Response**:
```json
{
  "count": 100,
  "next": "http://api.example.com/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true,
      "date_joined": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### getUser
```typescript
usersApi.getUser(id: number)
```

**Endpoint**: `GET /api/users/{id}/`

#### createUser
```typescript
usersApi.createUser(userData: UserCreateData)
```

**Endpoint**: `POST /api/users/`

**Request**:
```json
{
  "username": "new_user",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "password": "secure_password"
}
```

#### updateUser
```typescript
usersApi.updateUser(id: number, userData: UserUpdateData)
```

**Endpoint**: `PATCH /api/users/{id}/`

#### deleteUser
```typescript
usersApi.deleteUser(id: number)
```

**Endpoint**: `DELETE /api/users/{id}/`

### Products API

**Module**: `productsApi`

#### getProducts
```typescript
productsApi.getProducts(params?: ApiParams)
```

**Endpoint**: `GET /api/products/`

#### getProduct
```typescript
productsApi.getProduct(id: number)
```

**Endpoint**: `GET /api/products/{id}/`

#### getAnalytics
```typescript
productsApi.getAnalytics(type: string)
```

**Endpoint**: `GET /api/products/analytics/{type}/`

**Types**: `revenue`, `sales`, `performance`

### Entities API

**Module**: `entitiesApi`

#### getEntities
```typescript
entitiesApi.getEntities(params?: ApiParams)
```

**Endpoint**: `GET /api/entities/`

#### getEntity
```typescript
entitiesApi.getEntity(id: number)
```

**Endpoint**: `GET /api/entities/{id}/`

### Interactions API

**Module**: `interactionsApi`

#### getInteractions
```typescript
interactionsApi.getInteractions(params?: ApiParams)
```

**Endpoint**: `GET /api/interactions/`

#### getInteraction
```typescript
interactionsApi.getInteraction(id: number)
```

**Endpoint**: `GET /api/interactions/{id}/`

### Campaigns API

**Module**: `campaignsApi`

#### getCampaigns
```typescript
campaignsApi.getCampaigns(params?: ApiParams)
```

**Endpoint**: `GET /api/campaigns/`

#### getCampaign
```typescript
campaignsApi.getCampaign(id: number)
```

**Endpoint**: `GET /api/campaigns/{id}/`

### Offers API

**Module**: `offersApi`

#### getOffers
```typescript
offersApi.getOffers(params?: ApiParams)
```

**Endpoint**: `GET /api/offers/`

#### getOffer
```typescript
offersApi.getOffer(id: number)
```

**Endpoint**: `GET /api/offers/{id}/`

## Type Definitions

### Core Types

```typescript
export interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  date_joined: string
}

export interface UserCreateData {
  username: string
  email: string
  first_name: string
  last_name: string
  password: string
}

export interface UserUpdateData {
  username?: string
  email?: string
  first_name?: string
  last_name?: string
}

export interface Product {
  id: number
  name: string
  description: string
  price: number
  category: string
  created_at: string
  updated_at: string
}

export interface Entity {
  id: number
  name: string
  type: string
  created_at: string
  updated_at: string
}

export interface Interaction {
  id: number
  entity: number
  action_type: string
  channel: string
  medium: string
  created_at: string
}

export interface Campaign {
  id: number
  name: string
  description: string
  start_date: string
  end_date: string
  status: string
}

export interface Offer {
  id: number
  name: string
  description: string
  discount_percentage: number
  valid_from: string
  valid_to: string
}
```

### API Response Types

```typescript
export interface ApiParams {
  page?: number
  page_size?: number
  search?: string
  ordering?: string
  [key: string]: unknown
}

export interface ApiResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
```

## Error Handling

### Server Action Error Handling

```typescript
interface ApiError {
  response?: {
    data?: {
      error?: string
      [key: string]: unknown
    }
  }
  message?: string
}

// Error handling in Server Actions
try {
  const response = await api.post('/api/users/', userData)
  return { success: true, user: response.data }
} catch (error: unknown) {
  const apiError = error as ApiError
  return {
    success: false,
    error: apiError.response?.data?.error || apiError.message || 'Failed to create user',
  }
}
```

### Client-side Error Handling

```typescript
// React Query error handling
const { data, error, isLoading } = useQuery({
  queryKey: ['users'],
  queryFn: () => usersApi.getUsers(),
  onError: (error) => {
    console.error('Failed to fetch users:', error)
    toast.error('Failed to load users')
  }
})

if (error) {
  return (
    <div className="bg-red-50 border border-red-200 rounded-md p-4">
      <div className="text-red-700">
        Error loading users: {error instanceof Error ? error.message : 'Unknown error'}
      </div>
    </div>
  )
}
```

## React Query Integration

### Query Configuration

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

### Usage Examples

#### Basic Query
```typescript
const { data: users, isLoading, error } = useQuery({
  queryKey: ['users'],
  queryFn: () => usersApi.getUsers(),
})
```

#### Query with Parameters
```typescript
const { data: users } = useQuery({
  queryKey: ['users', currentPage, pageSize, searchTerm],
  queryFn: () => usersApi.getUsers({
    page: currentPage,
    page_size: pageSize,
    search: searchTerm,
  }),
})
```

#### Mutation with Invalidation
```typescript
const mutation = useMutation({
  mutationFn: (userData) => usersApi.createUser(userData),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['users'] })
    toast.success('User created successfully')
  },
  onError: (error) => {
    toast.error('Failed to create user')
  },
})
```

## Security Considerations

### Authentication Security

1. **Token Storage**: 
   - Development: localStorage
   - Production: httpOnly cookies (recommended)

2. **Token Refresh**: Automatic refresh handling for expired tokens

3. **CSRF Protection**: Server Actions provide built-in CSRF protection

### Request Security

1. **HTTPS Only**: All API requests use HTTPS in production

2. **Content Security Policy**: Configured headers prevent XSS attacks

3. **Input Validation**: Server-side validation for all inputs

4. **Error Information**: Limited error details exposed to client

## Performance Optimizations

### Caching Strategy

1. **Server-side Caching**: Smart revalidation with `fetch()`
2. **Client-side Caching**: React Query with stale-while-revalidate
3. **Request Deduplication**: Automatic request deduplication

### Request Optimization

1. **Pagination**: Efficient data loading for large datasets
2. **Search Debouncing**: Reduced API calls for search functionality
3. **Lazy Loading**: Load data only when needed

## Testing

### API Testing Strategy

1. **Unit Tests**: Individual API function testing
2. **Integration Tests**: End-to-end API workflow testing
3. **Mock Testing**: Mock API responses for development

### Test Examples

```typescript
// Mock API response
jest.mock('@/lib/api', () => ({
  usersApi: {
    getUsers: jest.fn().mockResolvedValue({
      count: 1,
      results: [{ id: 1, username: 'test_user' }]
    })
  }
}))

// Test component with API call
test('loads users on mount', async () => {
  render(<UsersTable />)
  await waitFor(() => {
    expect(screen.getByText('test_user')).toBeInTheDocument()
  })
})
```

## Environment Configuration

### Development
```bash
NEXT_PUBLIC_API_BASE=http://localhost:8000
NODE_ENV=development
```

### Production
```bash
NEXT_PUBLIC_API_BASE=https://your-backend-url.onrender.com
NODE_ENV=production
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure backend CORS configuration allows frontend domain
2. **SSL Certificate Errors**: Check SSL configuration for development
3. **Authentication Failures**: Verify token storage and refresh logic
4. **API Timeout**: Check network connectivity and backend availability

### Debug Mode

Enable detailed logging:
```typescript
// Request logging (development only)
api.interceptors.request.use((config) => {
  console.log('Making API request:', {
    method: config.method,
    url: config.url,
    baseURL: config.baseURL,
    fullURL: `${config.baseURL}${config.url}`,
    data: config.data
  })
  return config
})
```

---

*Last updated: December 2024*
*Version: 0.1.0*
