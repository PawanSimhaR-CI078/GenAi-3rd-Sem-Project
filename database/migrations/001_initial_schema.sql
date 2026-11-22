CREATE TABLE IF NOT EXISTS tolstoy_users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    display_name TEXT,
    phone_number TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'USER' CHECK (role IN ('USER','ADMIN','SUPER_ADMIN')),
    is_active INTEGER NOT NULL DEFAULT 1,
    token_balance INTEGER NOT NULL DEFAULT 5,
    last_token_refill_at TEXT NOT NULL,
    created_by INTEGER REFERENCES tolstoy_users(id),
    created_at TEXT NOT NULL,
    updated_by INTEGER REFERENCES tolstoy_users(id),
    updated_at TEXT NOT NULL,
    reserved_slot_1 TEXT,
    reserved_slot_2 TEXT
);

CREATE TABLE IF NOT EXISTS tolstoy_stories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES tolstoy_users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    character_gender TEXT,
    target_audience TEXT,
    desired_length TEXT,
    language TEXT,
    generated_script TEXT,
    generation_status TEXT NOT NULL DEFAULT 'pending' CHECK (generation_status IN ('pending','processing','succeeded','failed')),
    story_status TEXT NOT NULL DEFAULT 'EDITING' CHECK (story_status IN ('EDITING','COMPLETED')),
    tokens_consumed INTEGER NOT NULL DEFAULT 0,
    gemini_input_tokens INTEGER,
    gemini_output_tokens INTEGER,
    generated_at TEXT,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    created_by INTEGER REFERENCES tolstoy_users(id),
    created_at TEXT NOT NULL,
    updated_by INTEGER REFERENCES tolstoy_users(id),
    updated_at TEXT NOT NULL,
    reserved_slot_1 TEXT,
    reserved_slot_2 TEXT
);

CREATE TABLE IF NOT EXISTS tolstoy_system_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT NOT NULL UNIQUE,
    setting_value TEXT NOT NULL,
    value_type TEXT NOT NULL DEFAULT 'string' CHECK (value_type IN ('string','integer','boolean','json')),
    description TEXT,
    is_secret INTEGER NOT NULL DEFAULT 0,
    created_by INTEGER REFERENCES tolstoy_users(id),
    created_at TEXT NOT NULL,
    updated_by INTEGER REFERENCES tolstoy_users(id),
    updated_at TEXT NOT NULL,
    reserved_slot_1 TEXT,
    reserved_slot_2 TEXT
);

CREATE INDEX IF NOT EXISTS idx_users_role ON tolstoy_users(role);
CREATE INDEX IF NOT EXISTS idx_users_active ON tolstoy_users(is_active);
CREATE INDEX IF NOT EXISTS idx_stories_user ON tolstoy_stories(user_id);
CREATE INDEX IF NOT EXISTS idx_stories_status ON tolstoy_stories(story_status);
CREATE INDEX IF NOT EXISTS idx_stories_gen ON tolstoy_stories(generation_status);