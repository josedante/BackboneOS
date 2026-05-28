# Patrones de la API REST - Django REST Framework

## Visión general

Este proyecto usa **Django REST Framework (DRF)** para la API REST. La API es la superficie de integración para clientes externos, webhooks de ingestión (p. ej. Meta/Shopify) y scripts de tracking.

> El CRM de operador **no** consume esta API por HTTP. Renderiza plantillas Django y comparte la lógica con DRF a través de la capa `selectors`/`services` (ver [BACKEND.md](BACKEND.md#-capa-de-servicios-y-selectores) y [FRONTEND_API.md](FRONTEND_API.md)). Por eso no hay loopback interno hacia `/api/...`.

Este documento describe la forma de las respuestas y las capacidades de filtrado para quienes integran contra la API.

## Patrones de respuesta

### 1. Listas paginadas

DRF pagina automáticamente las listas cuando `DEFAULT_PAGINATION_CLASS` está configurado.

```json
{
  "count": 23,
  "next": "http://api.example.com/api/products/?page=2",
  "previous": null,
  "results": [
    { "id": 1, "name": "..." }
  ]
}
```

Los datos están en `results`; la metadata de paginación en `count`/`next`/`previous`.

### 2. Objeto único

Los endpoints de detalle (`GET /api/products/123/`) devuelven el objeto directamente:

```json
{ "id": 123, "name": "Product Name", "description": "..." }
```

### 3. Errores

DRF devuelve errores estructurados:

```json
{
  "field_name": ["This field is required."],
  "non_field_errors": ["General error message"]
}
```

## Patrones de endpoints

### Listas (paginadas)

- `GET /api/products/products/`
- `GET /api/products/categories/`
- `GET /api/users/`

### Detalle (objeto único)

- `GET /api/products/products/123/`
- `GET /api/products/categories/456/`
- `GET /api/users/789/`

### Acciones

- `POST /api/products/products/` -> objeto creado
- `PATCH /api/products/products/123/` -> objeto actualizado
- `DELETE /api/products/products/123/` -> `204 No Content`

## Capacidades comunes de DRF

### Filtrado (`django-filter`)

- `?search=term` -> búsqueda de texto
- `?category=123` -> match exacto
- `?min_price=100&max_price=500` -> rangos
- `?is_active=true` -> booleanos

### Ordenación

- `?ordering=name` -> ascendente
- `?ordering=-created_at` -> descendente
- `?ordering=name,-price` -> múltiples campos

### Paginación

- `?page=2` -> página (paginación por página)
- `?offset=20&limit=50` -> si está habilitada la paginación por límite/offset

## Cómo se implementa internamente

Los ViewSets no contienen lógica de lectura/escritura propia: delegan en la capa compartida.

```python
class ProductViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return products_list_queryset()        # selectors.py

    def perform_create(self, serializer):
        create_product(...)                    # services.py
```

- **Lecturas** -> `selectors.py` (querysets, `select_related`/`prefetch_related`, agregados).
- **Escrituras** -> `services.py` (mutaciones, transacciones, `validate_*` compartidas).
- Los serializers **no** llevan lógica de escritura/M2M; las validaciones compartidas se invocan desde el `validate` del serializer y desde el servicio.

Detalle completo de la convención en [BACKEND.md](BACKEND.md#-capa-de-servicios-y-selectores).

## Guía para integradores

1. **Verifica la forma de la respuesta**: ¿paginada (`count`/`results`) u objeto único?
2. **Maneja errores por campo y `non_field_errors`**.
3. **Usa filtros y ordenación** vía query params en lugar de filtrar en cliente.
4. **Catálogo de endpoints**: ver [API.md](API.md).

## Referencia rápida

| Tipo de endpoint | Respuesta DRF | Acceso |
|------------------|---------------|--------|
| Lista (paginada) | `{count, next, previous, results: [...]}` | `results` |
| Lista (sin paginar) | `[...]` | array directo |
| Detalle | `{id, ...}` | objeto directo |
| Create/Update | `{id, ...}` | objeto directo |
| Delete | `204 No Content` | sin cuerpo |

---

> Relacionado: [API.md](API.md) (catálogo), [BACKEND.md](BACKEND.md) (capa selectors/services), [FRONTEND_API.md](FRONTEND_API.md) (consumidores de datos).
