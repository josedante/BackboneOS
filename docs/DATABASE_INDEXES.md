# Política de índices de base de datos (backend Django)

Este documento registra la política de índices para modelos Django y un resumen de la auditoría de índices redundantes. Al añadir o cambiar índices, sigue las reglas siguientes y actualiza el resumen de auditoría si aplica.

Apps con índices documentados históricamente en `world` y `entities`: la referencia canónica es este archivo (los antiguos `INDEX_OPTIMIZATION.md` por app se consolidaron aquí).

## Policy

1. **Do not add redundant indexes**
   - **ForeignKey**: Django creates an index on every `ForeignKey` column. Do not add a single-column `Meta.indexes` or `db_index=True` on the same field.
   - **Unique**: `unique=True` and `unique_together` create unique indexes. Do not add a separate index on the same column(s).
   - Use one representation per index: either `db_index=True` on the field or an entry in `Meta.indexes`, not both for the same column.

2. **Prefer composite indexes for real query patterns**
   - Add composite indexes (e.g. `(website, started_at)`, `(touchpoint, occurred_at)`) when filters or ordering consistently use those column combinations. Single-column indexes on the same columns are redundant if the leftmost column is already indexed (e.g. by FK).

3. **Do not index low-cardinality fields standalone**
   - Boolean fields (`is_active`, `is_primary`, `verified`) and small enums (< ~15 distinct values) have too little selectivity for standalone indexes — the planner will choose a sequential scan. Use them only as the right-hand column in a composite index with a high-cardinality left column (e.g. `(representative, stage)`, `(person, is_active)`).

4. **Limit indexes on small reference tables**
   - For lookup/reference tables (e.g. world app, Medium, Channel, ActionType) that are typically small (hundreds to low thousands of rows), add no explicit indexes at all — sequential scans on small tables are always faster than index lookups.

5. **When reverting a removal**
   - If a removed index is re-added after observing slow queries, document the revert here (model, index, reason, migration name).

## Audit summary (index cleanup)

The following changes were applied in two rounds (initial FK/unique audit + second-pass boolean/cardinality audit). Migration names are listed per app.

### interactions — migration `0005_remove_redundant_indexes`
- **Agent**: Removed `['is_active']` (boolean). Kept `['agent_type']`, `['identifier']`.
- **Medium, Channel, ActionType, Action, TouchpointType**: Removed ALL explicit indexes. `name` and `code` are `unique=True` (auto-indexed); remaining fields are low-cardinality on tiny lookup tables.
- **Touchpoint**: Kept composite indexes for three-dimensional analysis: `['channel','medium']`, `['medium','touchpoint_type']`, `['channel','touchpoint_type']`. Also kept `['is_active']`, `['touchpoint_type']`, `['code']`, `['url']`, `['name']`.
- **Interaction**: Kept composites for analytics — `['is_active']`, `['occurred_at']`, `['is_active','occurred_at']`, `['touchpoint','is_active']`, `['session_id']`, `['touchpoint','occurred_at']`, `['agent','occurred_at']`.

### websites
- **WebSession**: Removed `db_index=True` from `session_id` (`unique=True` already creates an index). Removed `Index(fields=['session_id'])` from Meta. Kept composite indexes.
- **WebInteraction**: Removed duplicate `Index(fields=['session_id'])` and `Index(fields=['visitor_cookie'])` (fields have `db_index=True`). Kept composite indexes.

### world — migration `0003_remove_redundant_indexes`
- Removed single-column indexes on FK columns (`parent`, `country`, `family`) and on `unique=True` columns (`name`, `code`). Small reference tables pruned to zero or one index.

### entities — migration `0003_remove_redundant_indexes`
- **Person**: Removed `['id_type','id_number']` (redundant with `unique_together`), `['is_active']`, all standalone birthday-related indexes, gender/marital_status composites, `['is_active','country_of_nationality']`, `['is_active','gender']`, `['is_active','created_at']`. Kept `['first_name','last_name']`, `['created_at']`, `['updated_at']`.
- **ContactDetail**: Removed `['is_primary']`, `['verified']`, `['is_active']`, `['is_active','is_primary']`, `['is_active','verified']`, `['person','verified']`, `['organization','verified']`. Kept `['email']`, `['phone']`, `['person','is_primary']`, `['organization','is_primary']`, `['person','is_active']`, `['organization','is_active']`, `['email','verified']`, `['phone','verified']`, `['email','is_active']`, `['phone','is_active']`.
- **IndividualProfile**: Removed all `['is_active',X]` composites (two booleans — too low selectivity). Added standalone `['academic_degree']`. Kept `['allows_marketing']`, `['accepts_privacy_policy']`, `['preferred_contact_medium']`, `['person','is_active']`.
- **Organization**: Removed `['id_type','id_number']` (redundant with `unique_together`), `['is_active']`, `['org_type','industry']`, `['country','industry']`. Kept `['name']`, `['legal_name']`, `['is_active','org_type']`, `['is_active','industry']`, `['is_active','country']`.
- **PhysicalAddress**: Removed `['is_primary']`, `['use_for_billing']`, `['is_active','is_primary']`, `['is_active','use_for_billing']`. Kept owner indexes, geographic indexes, owner+is_primary/is_active composites.

### users — migration `0004_remove_redundant_indexes`
- **StaffProfile**: Removed `['is_active']`, `['verified']` (boolean). `indexes = []`.
- **UserTag**: Removed `['tag_type']` (9-value enum), `['is_active']` (boolean). `indexes = []`.
- **UserPreference**: Removed `['preferred_contact_medium']` (6-value enum), `['notifications_enabled']`, `['is_active']` (booleans). `indexes = []`.
- **UserSession**: Kept `['user','login_time']`, `['login_time']`.
- **CriticalUserEvent**: Kept `['user','timestamp']`, `['event_type','timestamp']`.

### products
- **ProductCategory**: Removed single-column index on `parent` (FK). Kept `division`+`is_active` composite and others.
- **Product**: Removed single-column indexes on `name`, `code` (unique). Removed single-column index on `category` (FK). Kept `category`+`is_active`, `base_price`, `is_active`.

### sales — migration `0002_update_indexes`
- **ProductAcquisition**: Removed `['payment_modality']` (3-value enum). Kept `['price_paid']`.
- **SalesOpportunity**: Added `['is_active','stage']`, `['product','stage']`, `['representative','stage']`, `['expected_closing_date']` — missing indexes for real query patterns (pipeline views, rep dashboards, due-date filtering).

### campaigns
- **Campaign**: Removed single-column indexes on `division`, `team` (FKs). Kept composite and other indexes.

### connectors
- No model changes. `FailedEvent` uses `db_index=True` and Meta composite indexes; both are kept.

## When adding indexes

- **Check**: Is this column a ForeignKey or part of a unique constraint? If yes, do not add an extra single-column index.
- **Check**: Is this a small lookup/reference table? Prefer at most 1–2 indexes (e.g. `is_active` and one composite for the common list ordering).
- **Check**: Are you duplicating the same column in both `db_index=True` and `Meta.indexes`? Use only one.
- When adding an index for a specific query or view, add one line to this audit summary (e.g. "Model X: Index(fields=['a','b']) for reporting view Y.").
