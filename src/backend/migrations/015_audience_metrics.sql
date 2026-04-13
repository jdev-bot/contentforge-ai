-- Migration: Create audience metrics and growth snapshots tables
-- Author: Backend Engineer (Audience Growth Metrics)
-- Created: 2026-04-13

-- Create audience_metrics table for tracking social media metrics
CREATE TABLE IF NOT EXISTS audience_metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    platform varchar(50) NOT NULL, -- twitter, linkedin, youtube, instagram, etc.
    metric_type varchar(50) NOT NULL, -- followers, subscribers, views, likes, comments, engagement_rate
    value int NOT NULL DEFAULT 0,
    recorded_at timestamptz DEFAULT now(),
    period varchar(20) DEFAULT 'daily' CHECK (period IN ('daily', 'weekly', 'monthly'))
);

-- Create growth_snapshots table for storing computed growth data
CREATE TABLE IF NOT EXISTS growth_snapshots (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    total_followers int DEFAULT 0,
    new_followers_7d int DEFAULT 0,
    new_followers_30d int DEFAULT 0,
    engagement_rate float DEFAULT 0.0,
    top_performing_content jsonb DEFAULT '[]'::jsonb,
    recorded_at timestamptz DEFAULT now()
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_audience_metrics_user_id ON audience_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_audience_metrics_platform ON audience_metrics(platform);
CREATE INDEX IF NOT EXISTS idx_audience_metrics_metric_type ON audience_metrics(metric_type);
CREATE INDEX IF NOT EXISTS idx_audience_metrics_recorded_at ON audience_metrics(recorded_at);
CREATE INDEX IF NOT EXISTS idx_audience_metrics_user_platform ON audience_metrics(user_id, platform);
CREATE INDEX IF NOT EXISTS idx_audience_metrics_user_period ON audience_metrics(user_id, period, recorded_at);

CREATE INDEX IF NOT EXISTS idx_growth_snapshots_user_id ON growth_snapshots(user_id);
CREATE INDEX IF NOT EXISTS idx_growth_snapshots_recorded_at ON growth_snapshots(recorded_at);

-- Add RLS policies for audience_metrics
ALTER TABLE audience_metrics ENABLE ROW LEVEL SECURITY;

-- Users can only see their own metrics
CREATE POLICY audience_metrics_select_own ON audience_metrics
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own metrics
CREATE POLICY audience_metrics_insert_own ON audience_metrics
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own metrics
CREATE POLICY audience_metrics_update_own ON audience_metrics
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can only delete their own metrics
CREATE POLICY audience_metrics_delete_own ON audience_metrics
    FOR DELETE
    USING (auth.uid() = user_id);

-- Add RLS policies for growth_snapshots
ALTER TABLE growth_snapshots ENABLE ROW LEVEL SECURITY;

-- Users can only see their own snapshots
CREATE POLICY growth_snapshots_select_own ON growth_snapshots
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own snapshots
CREATE POLICY growth_snapshots_insert_own ON growth_snapshots
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own snapshots
CREATE POLICY growth_snapshots_update_own ON growth_snapshots
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can only delete their own snapshots
CREATE POLICY growth_snapshots_delete_own ON growth_snapshots
    FOR DELETE
    USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON audience_metrics TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON growth_snapshots TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE audience_metrics IS 'Stores audience metrics from social media platforms';
COMMENT ON TABLE growth_snapshots IS 'Stores computed growth snapshots for quick dashboard access';
COMMENT ON COLUMN audience_metrics.platform IS 'Social media platform (twitter, linkedin, youtube, instagram, etc.)';
COMMENT ON COLUMN audience_metrics.metric_type IS 'Type of metric (followers, subscribers, views, likes, comments, engagement_rate)';
COMMENT ON COLUMN audience_metrics.period IS 'Time period for the metric (daily, weekly, monthly)';
COMMENT ON COLUMN growth_snapshots.top_performing_content IS 'JSON array of top performing content references';
