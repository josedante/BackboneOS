# Database index policy (Django backend)

This document records the index policy for Django models and a summary of the index audit performed to remove redundant indexes. When adding or changing model indexes, follow the rules below and update the audit summary if needed.

## Policy

1. **Do not add redundant indexes**
   - **ForeignKey**: Django creates an index on every `ForeignKey` column. Do not add a single-column `Meta.indexes` or `db_index=True` on the same field.
   - **Unique**: `unique=True` and `unique_together` create unique indexes. Do not add a separate index on the same column(s).
   - Use one representation per index: either `db_index=True` on the field or an entry in `Meta.indexes`, not both for the same column.

2. **Prefer composite indexes for real query patterns**
   - Add composite indexes (e.g. `(website, started_at)`, `(touchpoint, occurred_at)`) when filters or ordering consistently use those column combinations. Single-column indexes on the same columns are redundant if the leftmost column is already indexed (e.g. by FK).

3. **Limit indexes on small reference tables**
   - For lookup/reference tables (e.g. world app, Medium, Channel, ActionType) that are typically small (hundreds to low thousands of rows), keep at most one or two indexes (e.g. `is_active` and one composite for common list ordering). Avoid indexing every filter column.

4. **When reverting a removal**
   - If a removed index is re-added after observing slow queries, document the revert here (model, index, reason, migration name).

## Audit summary (index cleanup)

The following changes were applied to remove redundant or over-defensive indexes. Indexes listed as "Removed" were redundant with FK/unique or trimmed on small tables.

### interactions
- **Agent**: Removed single-column indexes on FK fields `operated_by`, `represents_person`, `represents_organization`. Kept `agent_type`, `identifier`, `is_active`.
- **Touchpoint**: Removed single-column indexes on FK fields `channel`, `medium`. Kept composite indexes and indexes on `code`, `url`, `name`, `touchpoint_type`, `is_active`.
- **Interaction**: Removed single-column indexes on FK fields `person`, `organization`, `touchpoint`, `action`, `agent`, `representative`. Removed single-column indexes on `ip_address`, `duration_seconds`, `source`. Kept composite indexes for analytics (`touchpoint`+`occurred_at`, `agent`+`occurred_at`, `is_active`+`occurred_at`, etc.) and `session_id`, `occurred_at`, `is_active`.

### websites
- **WebSession**: Removed `db_index=True` from `session_id` (column has `unique=True`, which creates an index). Removed `Index(fields=['session_id'])` from Meta. Kept composite indexes.
- **WebInteraction**: Removed duplicate `Index(fields=['session_id'])` and `Index(fields=['visitor_cookie'])` from Meta (fields already have `db_index=True`). Kept composite indexes.

### world
- Removed single-column indexes on FK columns (`parent`, `country`, `family`) and on columns that are `unique=True` or part of `unique_together` (e.g. `name`, `code` where unique). Trimmed small reference tables to fewer indexes (e.g. kept `is_active` and one ordering composite per model). See migrations `world/migrations/0003_remove_redundant_indexes.py` for the full list.

### entities
- **Person**: Removed single-column indexes on FK fields `gender`, `marital_status`, `country_of_nationality`, `id_type`. Kept composites and non-FK indexes.
- **ContactDetail**: Removed single-column indexes on `person`, `organization` (FKs). Kept composites and other indexes.
- **IndividualProfile**: Removed single-column indexes on `person`, `academic_degree` (FK/OneToOne). Kept composites and other indexes.
- **Organization**: Removed single-column indexes on `org_type`, `industry`, `country`, `id_type` (FKs). Kept composites and other indexes.

### users
- **StaffProfile**: Removed single-column indexes on `division`, `position`, `manager` (FKs). Kept `is_active`, `verified`.
- **UserTag**: Removed single-column index on `representative` (FK). Kept `tag_type`, `is_active`.
- **UserPreference**: Removed single-column index on `user` (OneToOne). Kept other indexes.

### products
- **ProductCategory**: Removed single-column index on `parent` (FK). Kept `division`+`is_active` composite and others.
- **Product**: Removed single-column indexes on `name`, `code` (unique). Removed single-column index on `category` (FK). Kept `category`+`is_active`, `base_price`, `is_active`.

### sales
- **ProductAcquisition**: Removed single-column index on `offering` (FK). Kept `price_paid`, `payment_modality`. (Note: sales app was commented out in INSTALLED_APPS at audit time; when enabled, run `makemigrations sales` to generate the migration.)

### campaigns
- **Campaign**: Removed single-column indexes on `division`, `team` (FKs). Kept composite and other indexes.

### connectors
- No model changes. FailedEvent uses `db_index=True` and Meta composite indexes; both are kept. TouchpointMappingRule has no FK in its index list.

## When adding indexes

- **Check**: Is this column a ForeignKey or part of a unique constraint? If yes, do not add an extra single-column index.
- **Check**: Is this a small lookup/reference table? Prefer at most 1–2 indexes (e.g. `is_active` and one composite for the common list ordering).
- **Check**: Are you duplicating the same column in both `db_index=True` and `Meta.indexes`? Use only one.
- When adding an index for a specific query or view, add one line to this audit summary (e.g. "Model X: Index(fields=['a','b']) for reporting view Y.").
