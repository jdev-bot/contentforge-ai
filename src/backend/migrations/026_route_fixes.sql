-- Migration 026: Add missing tables and columns for frontend route compatibility
-- Description: Adds rss_settings table and auto_suggestions.status column
--              needed by the new backend routes for frontend compatibility.
-- Created: 2026-04-20

-- ── rss_settings ─────────────────────────────────────────────
-- Referenced by: rss.py GET/PATCH /rss/settings
CREATE TABLE IF NOT EXISTS rss_settings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    auto_import boolean NOT NULL DEFAULT false,
    default_project_id uuid REFERENCES projects(id) ON DELETE SET NULL,
    notification_enabled boolean NOT NULL DEFAULT true,
    notification_new_entries boolean NOT NULL DEFAULT true,
    notification_import_errors boolean NOT NULL DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_rss_settings_user_id ON rss_settings(user_id);

ALTER TABLE rss_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own RSS settings" ON rss_settings FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own RSS settings" ON rss_settings FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own RSS settings" ON rss_settings FOR UPDATE USING (auth.uid() = user_id);

GRANT SELECT, INSERT, UPDATE ON rss_settings TO authenticated;

COMMENT ON TABLE rss_settings IS 'Stores per-user RSS import settings and notification preferences';

-- ── auto_suggestions.status column ───────────────────────────
-- Referenced by: suggestions.py POST /suggestions/{id}/accept and /dismiss
-- Default is 'pending'; valid values: pending, accepted, dismissed
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'auto_suggestions' AND column_name = 'status'
    ) THEN
        ALTER TABLE auto_suggestions ADD COLUMN status varchar(20) NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending', 'accepted', 'dismissed'));
    END IF;
END
$$;

CREATE INDEX IF NOT EXISTS idx_auto_suggestions_status ON auto_suggestions(user_id, status);

COMMENT ON COLUMN auto_suggestions.status IS 'Suggestion status: pending, accepted, or dismissed';