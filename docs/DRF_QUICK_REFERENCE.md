# Django REST Framework - Quick Reference

## 🚨 CRITICAL: DRF Response Patterns

### List Endpoints (Paginated)
```typescript
// ✅ CORRECT
const { data: response } = useQuery<ProductsResponse>({
  queryKey: ['products'],
  queryFn: () => productsApi.getProducts()
})
const products = getResults(response) // or response?.results || []

// ❌ WRONG - Don't access .data
const products = response?.data || []
```

### Detail Endpoints (Single Object)
```typescript
// ✅ CORRECT
const { data: product } = useQuery({
  queryKey: ['product', id],
  queryFn: () => productsApi.getProduct(id)
})
// product is the object directly

// ❌ WRONG - Don't access .results for single objects
const product = response?.results?.[0]
```

## Response Structure

### Paginated Response
```json
{
  "count": 23,
  "next": "http://api.example.com/products/?page=2",
  "previous": null,
  "results": [
    { "id": 1, "name": "Product 1" },
    { "id": 2, "name": "Product 2" }
  ]
}
```

### Single Object Response
```json
{
  "id": 1,
  "name": "Product Name",
  "description": "..."
}
```

## Helper Functions

```typescript
import { getResults } from '@/lib/api'

// Extract results from paginated response
const products = getResults(productsResponse)
const categories = getResults(categoriesResponse)
```

## Pagination Implementation

### Frontend State Management
```typescript
const [currentPage, setCurrentPage] = useState(1)
const [pageSize, setPageSize] = useState(20) // Match backend default PAGE_SIZE

// Calculate offset from current page and page size
const offset = (currentPage - 1) * pageSize

// Reset to first page when filters change
useEffect(() => {
  setCurrentPage(1)
}, [searchTerm, selectedCategory])
```

### API Query with Pagination
```typescript
const { data: response } = useQuery<ProductsResponse>({
  queryKey: ['products', { search: searchTerm, category: selectedCategory, offset, limit: pageSize }],
  queryFn: () => productsApi.getProducts({ 
    ...(searchTerm && { search: searchTerm }),
    ...(selectedCategory !== 'all' && { category: selectedCategory }),
    offset,
    limit: pageSize,
  }),
})

const products = getResults(response)
const totalItems = response?.count || 0
const totalPages = Math.ceil(totalItems / pageSize)
```

### Pagination UI Components
```typescript
import { Pagination, PaginationInfo } from '@/components/ui/pagination'

// Pagination info
<PaginationInfo
  currentPage={currentPage}
  totalPages={totalPages}
  totalItems={totalItems}
  itemsPerPage={pageSize}
/>

// Pagination controls
<Pagination
  currentPage={currentPage}
  totalPages={totalPages}
  onPageChange={setCurrentPage}
/>
```

## TypeScript Types

```typescript
// Use these types for API responses
type ProductsResponse = PaginatedResponse<Product>
type CategoriesResponse = PaginatedResponse<ProductCategory>

// In useQuery
const { data } = useQuery<ProductsResponse>({...})
```

## Common Mistakes to Avoid

1. ❌ `response?.data` for paginated endpoints
2. ❌ `response?.results` for single object endpoints  
3. ❌ Not using proper TypeScript types
4. ❌ Not checking actual API response structure

## Debugging Checklist

1. ✅ Check Network tab for actual response
2. ✅ Verify if endpoint is paginated or single object
3. ✅ Use proper TypeScript types
4. ✅ Use `getResults()` helper for paginated data
5. ✅ Access data directly for single objects

## Pagination Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `offset` | Starting position (0-based) | `offset=20` |
| `limit` | Items per page | `limit=10` |
| `ordering` | Sort order | `ordering=name` |

### Offset Calculation
```typescript
// Convert page number to offset
const offset = (currentPage - 1) * pageSize

// Examples:
// Page 1, 20 items per page → offset = 0
// Page 2, 20 items per page → offset = 20
// Page 3, 20 items per page → offset = 40
```

### Backend Configuration
```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,  # Default limit if not specified
}
```

---

**Remember**: Django REST Framework is opinionated about response structure. Always verify the actual response in browser dev tools!
