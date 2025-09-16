# Backend API Patterns - Django REST Framework

## Overview
This project uses **Django REST Framework (DRF)** as the backend API framework. Understanding DRF patterns is crucial for frontend development.

## Standard Response Patterns

### 1. Paginated List Responses
DRF automatically paginates list endpoints when `DEFAULT_PAGINATION_CLASS` is configured.

**Structure:**
```json
{
  "count": 23,
  "next": "http://api.example.com/products/?page=2",
  "previous": null,
  "results": [
    // Array of actual data objects
  ]
}
```

**Frontend Access Pattern:**
```typescript
const { data: response } = useQuery({
  queryKey: ['products'],
  queryFn: () => productsApi.getProducts()
})

// ✅ CORRECT: Access results array
const products = response?.results || []

// ❌ WRONG: Don't access .data
const products = response?.data || []
```

### 2. Single Object Responses
For detail endpoints (GET /api/products/123/), DRF returns the object directly:

```json
{
  "id": 123,
  "name": "Product Name",
  "description": "...",
  // ... other fields
}
```

**Frontend Access Pattern:**
```typescript
const { data: product } = useQuery({
  queryKey: ['product', id],
  queryFn: () => productsApi.getProduct(id)
})

// ✅ CORRECT: Access data directly
const productName = product?.name

// ❌ WRONG: Don't access .results for single objects
const productName = product?.results?.name
```

### 3. Error Responses
DRF returns structured error responses:

```json
{
  "field_name": ["This field is required."],
  "non_field_errors": ["General error message"]
}
```

**Frontend Error Handling:**
```typescript
try {
  await productsApi.createProduct(data)
} catch (error) {
  if (error.response?.data) {
    // Handle field-specific errors
    const fieldErrors = error.response.data
    // Handle non-field errors
    const generalErrors = error.response.data.non_field_errors
  }
}
```

## API Endpoint Patterns

### List Endpoints (Paginated)
- `GET /api/products/products/` → Returns paginated response
- `GET /api/products/categories/` → Returns paginated response
- `GET /api/users/` → Returns paginated response

### Detail Endpoints (Single Object)
- `GET /api/products/products/123/` → Returns single product object
- `GET /api/products/categories/456/` → Returns single category object
- `GET /api/users/789/` → Returns single user object

### Action Endpoints
- `POST /api/products/products/` → Returns created object
- `PATCH /api/products/products/123/` → Returns updated object
- `DELETE /api/products/products/123/` → Returns 204 No Content

## Frontend API Client Standards

### 1. Consistent Response Handling
All API methods should handle DRF patterns consistently:

```typescript
// For list endpoints (paginated)
getProducts: async (params?: ApiParams) => {
  const response = await api.get('/api/products/products/', { params })
  return response.data // This will be the paginated response
}

// For detail endpoints (single object)
getProduct: async (id: number) => {
  const response = await api.get(`/api/products/products/${id}/`)
  return response.data // This will be the single object
}
```

### 2. TypeScript Interfaces
Define interfaces that match DRF response patterns:

```typescript
// Paginated response wrapper
interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}

// Usage
interface ProductsResponse extends PaginatedResponse<Product> {}
```

### 3. Query Hook Patterns
Use consistent patterns in React Query hooks:

```typescript
// For paginated data
const { data: response } = useQuery({
  queryKey: ['products'],
  queryFn: () => productsApi.getProducts()
})
const products = response?.results || []

// For single object data
const { data: product } = useQuery({
  queryKey: ['product', id],
  queryFn: () => productsApi.getProduct(id)
})
```

## Common DRF Features Used

### 1. Filtering
DRF uses `django-filter` for advanced filtering:
- `?search=term` → Text search
- `?category=123` → Exact match
- `?min_price=100&max_price=500` → Range filters
- `?is_active=true` → Boolean filters

### 2. Ordering
- `?ordering=name` → Ascending
- `?ordering=-created_at` → Descending
- `?ordering=name,-price` → Multiple fields

### 3. Pagination
- `?offset=20` → Starting position (0-based)
- `?limit=50` → Items per page (if allowed)

## Development Guidelines

### 1. Always Check Response Structure
When working with new endpoints:
1. Check the actual API response in browser dev tools
2. Verify if it's paginated (`count`, `results`) or single object
3. Update frontend code accordingly

### 2. Use TypeScript Strictly
Define proper interfaces for all API responses to catch mismatches early.

### 3. Test API Responses
Use browser dev tools or tools like Postman to verify API response structure before implementing frontend code.

### 4. Document Endpoint Patterns
When adding new endpoints, document whether they return:
- Paginated list (`PaginatedResponse<T>`)
- Single object (`T`)
- Custom response structure

## Troubleshooting Checklist

When API data isn't loading:

1. ✅ **Check Network Tab**: Is the request being made?
2. ✅ **Check Response Structure**: Is it `{results: [...]}` or `{data: [...]}`?
3. ✅ **Check Console Logs**: What does the actual response look like?
4. ✅ **Check DRF Pagination**: Is the endpoint paginated?
5. ✅ **Check Frontend Access**: Are we accessing the right field?

## Quick Reference

| Endpoint Type | DRF Response | Frontend Access |
|---------------|--------------|-----------------|
| List (paginated) | `{count, next, previous, results: [...]}` | `response.results` |
| List (unpaginated) | `[...]` | `response` |
| Detail | `{id, name, ...}` | `response` |
| Create/Update | `{id, name, ...}` | `response` |
| Delete | `204 No Content` | No response body |

---

**Remember**: Django REST Framework is opinionated about response structure. When in doubt, check the actual API response in browser dev tools!
