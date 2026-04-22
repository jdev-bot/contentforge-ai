-- Migration 027: Create engagement_predictions table
-- Description: Stores engagement prediction analysis results for user content.
--              Used by the engagement_prediction router to save and retrieve prediction history.
-- Created: 2026-04-22

CREATE TABLE IF NOT EXISTS engagement_predictions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content_id uuid,
    platform varchar(50) NOT NULL DEFAULT 'twitter',
    score int NOT NULL CHECK (score BETWEEN 0 AND 100),
    content_preview text NOT NULL DEFAULT '',
    factors jsonb NOT NULL DEFAULT '{}',
    predicted_engagement jsonb NOT NULL DEFAULT '{}',
    suggestions jsonb NOT NULL DEFAULT '[]',
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_engagement_predictions_user_id ON engagement_predictions(user_id);
CREATE INDEX IF NOT EXISTS idx_engagement_predictions_platform ON engagement_predictions(user_id, platform);
CREATE INDEX IF NOT EXISTS idx_engagement_predictions_created_at ON engagement_predictions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_engagement_predictions_score ON engagement_predictions(user_id, score);

ALTER TABLE engagement_predictions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Users can view own engagement predictions" ON engagement_predictions;
CREATE POLICY "Users can view own engagement predictions" ON engagement_predictions FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own engagement predictions" ON engagement_predictions;
CREATE POLICY "Users can insert own engagement predictions" ON engagement_predictions FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can delete own engagement predictions" ON engagement_predictions;
CREATE POLICY "Users can delete own engagement predictions" ON engagement_predictions FOR DELETE USING (auth.uid() = user_id);