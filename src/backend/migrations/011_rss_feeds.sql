-- Migration: Create RSS feeds and entries tables for automated content import
-- Author: Backend Engineer (RSS Feed Import)
-- Created: 2026-04-13

-- Create rss_feeds table for storing RSS feed configurations
CREATE TABLE IF NOT EXISTS rss_feeds (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    name varchar(255),
    url text NOT NULL,
    last_fetched_at timestamptz,
    fetch_frequency varchar(20) DEFAULT 'hourly' CHECK (fetch_frequency IN ('hourly', 'daily')),
    auto_create_content boolean DEFAULT false,
    status varchar(20) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'error')),
    error_message text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Create rss_entries table for storing individual RSS entries
CREATE TABLE IF NOT EXISTS rss_entries (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    feed_id uuid REFERENCES rss_feeds(id) ON DELETE CASCADE,
    external_id varchar(255), -- guid from RSS
    title text,
    link text,
    content text,
    published_at timestamptz,
    processed boolean DEFAULT false,
    content_id uuid REFERENCES content(id) ON DELETE SET NULL,
    created_at timestamptz DEFAULT now(),
    UNIQUE(feed_id, external_id)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_rss_feeds_user_id ON rss_feeds(user_id);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_status ON rss_feeds(status);
CREATE INDEX IF NOT EXISTS idx_rss_feeds_fetch_frequency ON rss_feeds(fetch_frequency) WHERE status = 'active';

CREATE INDEX IF NOT EXISTS idx_rss_entries_feed_id ON rss_entries(feed_id);
CREATE INDEX IF NOT EXISTS idx_rss_entries_processed ON rss_entries(processed);
CREATE INDEX IF NOT EXISTS idx_rss_entries_published_at ON rss_entries(published_at);
CREATE INDEX IF NOT EXISTS idx_rss_entries_feed_processed ON rss_entries(feed_id, processed) WHERE processed = false;

-- Create function to update updated_at timestamp on rss_feeds
CREATE OR REPLACE FUNCTION update_rss_feeds_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at on rss_feeds
DROP TRIGGER IF EXISTS tr_rss_feeds_updated_at ON rss_feeds;
CREATE TRIGGER tr_rss_feeds_updated_at
    BEFORE UPDATE ON rss_feeds
    FOR EACH ROW
    EXECUTE FUNCTION update_rss_feeds_updated_at();

-- Add RLS policies for rss_feeds
ALTER TABLE rss_feeds ENABLE ROW LEVEL SECURITY;

-- Users can only see their own RSS feeds
CREATE POLICY rss_feeds_select_own ON rss_feeds
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own RSS feeds
CREATE POLICY rss_feeds_insert_own ON rss_feeds
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own RSS feeds
CREATE POLICY rss_feeds_update_own ON rss_feeds
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can only delete their own RSS feeds
CREATE POLICY rss_feeds_delete_own ON rss_feeds
    FOR DELETE
    USING (auth.uid() = user_id);

-- Add RLS policies for rss_entries (cascade through feed)
ALTER TABLE rss_entries ENABLE ROW LEVEL SECURITY;

-- Users can see entries for their feeds
CREATE POLICY rss_entries_select_own ON rss_entries
    FOR SELECT
    USING (EXISTS (
        SELECT 1 FROM rss_feeds WHERE rss_feeds.id = rss_entries.feed_id AND rss_feeds.user_id = auth.uid()
    ));

-- Users can only insert/update/delete entries for their feeds
CREATE POLICY rss_entries_insert_own ON rss_entries
    FOR INSERT
    WITH CHECK (EXISTS (
        SELECT 1 FROM rss_feeds WHERE rss_feeds.id = rss_entries.feed_id AND rss_feeds.user_id = auth.uid()
    ));

CREATE POLICY rss_entries_update_own ON rss_entries
    FOR UPDATE
    USING (EXISTS (
        SELECT 1 FROM rss_feeds WHERE rss_feeds.id = rss_entries.feed_id AND rss_feeds.user_id = auth.uid()
    ));

CREATE POLICY rss_entries_delete_own ON rss_entries
    FOR DELETE
    USING (EXISTS (
        SELECT 1 FROM rss_feeds WHERE rss_feeds.id = rss_entries.feed_id AND rss_feeds.user_id = auth.uid()
    ));

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON rss_feeds TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON rss_entries TO authenticated;

-- Add comments for documentation
COMMENT ON TABLE rss_feeds IS 'Stores RSS feed configurations for automated content import';
COMMENT ON TABLE rss_entries IS 'Stores individual RSS feed entries';
COMMENT ON COLUMN rss_feeds.fetch_frequency IS 'How often to fetch: hourly or daily';
COMMENT ON COLUMN rss_feeds.auto_create_content IS 'Whether to automatically create content items from RSS entries';
COMMENT ON COLUMN rss_feeds.status IS 'Current status: active, paused, or error';
COMMENT ON COLUMN rss_entries.external_id IS 'Original GUID from the RSS feed';
COMMENT ON COLUMN rss_entries.processed IS 'Whether this entry has been processed/imported';
COMMENT ON COLUMN rss_entries.content_id IS 'Reference to created content item if imported';
