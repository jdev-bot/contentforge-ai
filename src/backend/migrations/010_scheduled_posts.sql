-- Migration: Create scheduled_posts table for automated content scheduling
-- Author: Backend Engineer (Scheduled Publishing)
-- Created: 2026-04-13

-- Create scheduled_posts table for automated publishing
CREATE TABLE IF NOT EXISTS scheduled_posts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    content_id uuid REFERENCES content(id) ON DELETE CASCADE,
    asset_id uuid REFERENCES generated_assets(id) ON DELETE CASCADE,
    platform varchar(50) NOT NULL CHECK (platform IN ('twitter', 'linkedin', 'instagram', 'facebook', 'blog', 'email', 'tiktok', 'youtube')),
    scheduled_at timestamptz NOT NULL,
    status varchar(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'published', 'failed', 'cancelled')),
    asset_type varchar(50) DEFAULT 'post' CHECK (asset_type IN ('post', 'thread', 'article', 'story', 'reel', 'video')),
    settings jsonb DEFAULT '{}'::jsonb,
    content text, -- Actual content to publish (cached from asset)
    retry_count int DEFAULT 0,
    max_retries int DEFAULT 3,
    timezone varchar(50) DEFAULT 'UTC',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    published_at timestamptz,
    error_message text,
    external_id text, -- Platform-specific ID after publishing
    published_url text -- URL to published content
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_user_time ON scheduled_posts(user_id, scheduled_at);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_status ON scheduled_posts(status);
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_scheduled_at ON scheduled_posts(scheduled_at) WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS idx_scheduled_posts_platform ON scheduled_posts(platform, status);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_scheduled_posts_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
DROP TRIGGER IF EXISTS tr_scheduled_posts_updated_at ON scheduled_posts;
CREATE TRIGGER tr_scheduled_posts_updated_at
    BEFORE UPDATE ON scheduled_posts
    FOR EACH ROW
    EXECUTE FUNCTION update_scheduled_posts_updated_at();

-- Add RLS policies for scheduled_posts
ALTER TABLE scheduled_posts ENABLE ROW LEVEL SECURITY;

-- Users can only see their own scheduled posts
CREATE POLICY scheduled_posts_select_own ON scheduled_posts
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own scheduled posts
CREATE POLICY scheduled_posts_insert_own ON scheduled_posts
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own scheduled posts
CREATE POLICY scheduled_posts_update_own ON scheduled_posts
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can only delete their own scheduled posts
CREATE POLICY scheduled_posts_delete_own ON scheduled_posts
    FOR DELETE
    USING (auth.uid() = user_id);

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON scheduled_posts TO authenticated;
GRANT USAGE ON SEQUENCE scheduled_posts_id_seq TO authenticated;

-- Add comment for documentation
COMMENT ON TABLE scheduled_posts IS 'Stores scheduled content posts with automated publishing capabilities';
COMMENT ON COLUMN scheduled_posts.status IS 'Current status: pending, processing, published, failed, cancelled';
COMMENT ON COLUMN scheduled_posts.settings IS 'Platform-specific settings as JSON';
