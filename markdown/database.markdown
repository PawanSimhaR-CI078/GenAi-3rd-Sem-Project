# TOLSTOY — Database Design

## 1. Overview

- Engine: SQLite.
- File: `database/tolstoy.db`.
- Application tables: **exactly three**, all prefixed `tolstoy_`.
- No migration-tracking table. Migrations are versioned SQL files in `database/migrations/`.

## 2. Approved Tables

1. `tolstoy_users`
2. `tolstoy_stories`
3. `tolstoy_system_settings`

No other application tables are permitted without owner approval.

## 3. Mandatory Metadata Columns (all tables)

| Column | Type | Nullable | Meaning |
|---|---|---|---|
| `created_by` | INTEGER | YES | User ID of the creator (NULL for system/bootstrap rows) |
| `created_at` | TEXT | NO | ISO-8601 UTC timestamp of creation |
| `updated_by` | INTEGER | YES | User ID of last updater |
| `updated_at` | TEXT | NO | ISO-8601 UTC timestamp of last update |
| `reserved_slot_1` | TEXT | YES | Reserved for future expansion |
| `reserved_slot_2` | TEXT | YES | Reserved for future expansion |

Timestamps stored as `YYYY-MM-DDTHH:MM:SSZ` text. Application sets them; DB defaults not relied upon for audit accuracy.

## 4. Table: `tolstoy_users`

**Purpose:** Accounts for both normal users and administrators.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `username` | TEXT | NOT NULL, UNIQUE | Provisional auth identifier (see Owner Confirmation) |
| `display_name` | TEXT | | Optional friendly name |
| `phone_number` | TEXT | UNIQUE (if provided) | Optional; nullable |
| `password_hash` | TEXT | NOT NULL | Never exposed |
| `role` | TEXT | NOT NULL, DEFAULT 'USER', CHECK IN ('USER','ADMIN','SUPER_ADMIN') | |
| `is_active` | INTEGER | NOT NULL, DEFAULT 1 | 0/1 |
| `token_balance` | INTEGER | NOT NULL, DEFAULT 5 | Application tokens |
| `last_token_refill_at` | TEXT | NOT NULL | ISO-8601 UTC; set at registration |
| `created_by` | INTEGER | FK→tolstoy_users(id) | |
| `created_at` | TEXT | NOT NULL | |
| `updated_by` | INTEGER | FK→tolstoy_users(id) | |
| `updated_at` | TEXT | NOT NULL | |
| `reserved_slot_1` | TEXT | | |
| `reserved_slot_2` | TEXT | | |

**Indexes:** `UNIQUE(username)`, `INDEX(role)`, `INDEX(is_active)`.

**Security:** `password_hash` never returned by any API, viewer, log, or template.

## 5. Table: `tolstoy_stories`

**Purpose:** One row per user story plus its generated comic script.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `user_id` | INTEGER | NOT NULL, FK→tolstoy_users(id) ON DELETE CASCADE | Owner |
| `title` | TEXT | NOT NULL | |
| `content` | TEXT | NOT NULL | User story input |
| `character_gender` | TEXT | | Optional |
| `target_audience` | TEXT | | |
| `desired_length` | TEXT | | |
| `language` | TEXT | | |
| `generated_script` | TEXT | | Structured JSON text |
| `generation_status` | TEXT | NOT NULL, DEFAULT 'pending', CHECK IN ('pending','processing','succeeded','failed') | |
| `story_status` | TEXT | NOT NULL, DEFAULT 'EDITING', CHECK IN ('EDITING','COMPLETED') | Lifecycle |
| `tokens_consumed` | INTEGER | NOT NULL, DEFAULT 0 | Application tokens spent |
| `gemini_input_tokens` | INTEGER | | Provider usage |
| `gemini_output_tokens` | INTEGER | | Provider usage |
| `generated_at` | TEXT | | ISO-8601 UTC |
| `is_deleted` | INTEGER | NOT NULL, DEFAULT 0 | Provisional soft-delete |
| `created_by` | INTEGER | FK→tolstoy_users(id) | |
| `created_at` | TEXT | NOT NULL | |
| `updated_by` | INTEGER | FK→tolstoy_users(id) | |
| `updated_at` | TEXT | NOT NULL | |
| `reserved_slot_1` | TEXT | | |
| `reserved_slot_2` | TEXT | | |

**Indexes:** `INDEX(user_id)`, `INDEX(story_status)`, `INDEX(generation_status)`, `INDEX(is_deleted)`.

**Rules:** Do not store username redundantly; JOIN to `tolstoy_users`. `user_id` must match the authenticated owner; enforced in service layer.

## 6. Generated Script JSON (provisional)

Stored in `generated_script` as validated JSON text:

```json
{
  "title": "string",
  "scenes": [
    {
      "scene_number": 1,
      "setting": "string",
      "panels": [
        {
          "panel_number": 1,
          "description": "string",
          "characters": ["string"],
          "dialogue": [{"character": "string", "line": "string"}],
          "narration": "string"
        }
      ]
    }
  ]
}
```

Exact schema is pending owner confirmation. Validate on save; reject malformed output.

## 7. Table: `tolstoy_system_settings`

**Purpose:** Global configuration via validated key/value rows.

| Column | Type | Constraints | Notes |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY AUTOINCREMENT | |
| `setting_key` | TEXT | NOT NULL, UNIQUE | e.g. `maintenance_mode` |
| `setting_value` | TEXT | NOT NULL | Stored as text; converted by `value_type` |
| `value_type` | TEXT | NOT NULL, DEFAULT 'string', CHECK IN ('string','integer','boolean','json') | |
| `description` | TEXT | | |
| `is_secret` | INTEGER | NOT NULL, DEFAULT 0 | Flag only; no secrets stored |
| `created_by` | INTEGER | FK→tolstoy_users(id) | |
| `created_at` | TEXT | NOT NULL | |
| `updated_by` | INTEGER | FK→tolstoy_users(id) | |
| `updated_at` | TEXT | NOT NULL | |
| `reserved_slot_1` | TEXT | | |
| `reserved_slot_2` | TEXT | | |

**Indexes:** `UNIQUE(setting_key)`.

**No secrets** (API keys, passwords, mail credentials) are stored here; they live in `.env`.

## 8. Relationships

- `tolstoy_stories.user_id` → `tolstoy_users.id` (many stories per user).
- `tolstoy_users.created_by/updated_by` → `tolstoy_users.id` (self-reference; nullable).
- `tolstoy_stories.created_by/updated_by` → `tolstoy_users.id`.
- `tolstoy_system_settings.created_by/updated_by` → `tolstoy_users.id`.

## 9. Constraints Summary

- Foreign keys enforced (`PRAGMA foreign_keys = ON`).
- CHECK constraints on role, statuses, value_type.
- UNIQUE on username, phone_number (if not null), setting_key.
- NOT NULL on required fields.

## 10. Initialization Approach (future)

- A Python initializer reads SQL from `database/migrations/001_initial_schema.sql` and executes it.
- No migration-tracking table; versioning by filename prefix (`001_`, `002_`).
- Idempotent: use `CREATE TABLE IF NOT EXISTS`.

## 11. Backup Strategy

- Backups written to `database/backups/` with timestamped filenames (`tolstoy_backup_YYYY_MM_DD.db`).
- Backups excluded from Git.
- Restore = replace DB file after stopping app.

## 12. Example Records (illustrative only)

```sql
INSERT INTO tolstoy_users (username, password_hash, role, token_balance, last_token_refill_at, created_at, updated_at)
VALUES ('alice', '<hash>', 'USER', 5, '2026-11-21T10:00:00Z', '2026-11-21T10:00:00Z', '2026-11-21T10:00:00Z');

INSERT INTO tolstoy_system_settings (setting_key, setting_value, value_type, description, created_at, updated_at)
VALUES ('maintenance_mode', 'false', 'boolean', 'System maintenance flag', '2026-11-21T10:00:00Z', '2026-11-21T10:00:00Z');
```

## 13. Data Integrity

- Owner enforcement in service layer (user can only touch own stories).
- Atomic token updates with concurrency guard (transaction + conditional UPDATE).
- Refund on failed generation.
- Soft-delete flag provisional (pending owner confirmation).

## 14. Owner Confirmation Required

- Auth identifier (username vs phone) — see plan.md.
- Deletion policy (soft vs hard).
- Editing-after-completion content rules.
- Exact story JSON schema.
- Refill accumulation policy.