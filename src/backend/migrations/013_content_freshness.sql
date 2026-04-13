-- Migration: Create content freshness scores table
-- Author: Backend Engineer (Content Freshness Scoring)
-- Created: 2026-04-13

-- Create content_freshness_scores table for tracking content freshness
CREATE TABLE IF NOT EXISTS content_freshness_scores (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid REFERENCES content(id) ON DELETE CASCADE,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    freshness_score int CHECK (freshness_score BETWEEN 0 AND 100),
    age_days int,
    last_analyzed_at timestamptz DEFAULT now(),
    factors jsonb DEFAULT '{}', -- { age_factor: 0.3, engagement_factor: 0.5, trend_factor: 0.2 }
    recommendations jsonb DEFAULT '[]', -- ["Update statistics", "Add recent examples"]
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(content_id, user_id)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_freshness_user_score ON content_freshness_scores(user_id, freshness_score);
CREATE INDEX IF NOT EXISTS idx_freshness_content_id ON content_freshness_scores(content_id);
CREATE INDEX IF NOT EXISTS idx_freshness_user_content ON content_freshness_scores(user_id, content_id);
CREATE INDEX IF NOT EXISTS idx_freshness_last_analyzed ON content_freshness_scores(last_analyzed_at);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_freshness_scores_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS tr_freshness_scores_updated_at ON content_freshness_scores;
CREATE TRIGGER tr_freshness_scores_updated_at
    BEFORE UPDATE ON content_freshness_scores
    FOR EACH ROW
    EXECUTE FUNCTION update_freshness_scores_updated_at();

-- Add RLS policies for content_freshness_scores
ALTER TABLE content_freshness_scores ENABLE ROW LEVEL SECURITY;

-- Users can only see their own freshness scores
CREATE POLICY freshness_scores_select_own ON content_freshness_scores
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own freshness scores
CREATE POLICY freshness_scores_insert_own ON content_freshness_scores
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own freshness scores
CREATE POLICY freshness_scores_update_own ON content_freshness_scores
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can only delete their own freshness scores
CREATE POLICY freshness_scores_delete_own ON content_freshness_scores
    FOR DELETE
    USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON content_freshness_scores TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE content_freshness_scores IS 'Stores content freshness scores and recommendations for content optimization';
COMMENT ON COLUMN content_freshness_scores.freshness_score IS 'Overall freshness score from 0-100';
COMMENT ON COLUMN content_freshness_scores.age_days IS 'Age of content in days';
COMMENT ON COLUMN content_freshness_scores.factors IS 'JSON breakdown of scoring factors';
COMMENT ON COLUMN content_freshness_scores.recommendations IS 'JSON array of improvement recommendations';
COMMENT ON COLUMN content_freshness_scores.last_analyzed_at IS 'When the content was last analyzed';
