-- Migration: Competitor Analysis System
-- Description: Tables for tracking competitors and analyzing content gaps
-- Created: 2026-04-13

-- Competitors table: Track competitors across different platforms
CREATE TABLE IF NOT EXISTS competitors (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    name varchar(255) NOT NULL,
    platform varchar(50) NOT NULL CHECK (platform IN ('twitter', 'linkedin', 'instagram', 'youtube', 'tiktok', 'facebook', 'blog', 'newsletter', 'other')),
    handle varchar(255) NOT NULL,
    follower_count int DEFAULT 0,
    description text,
    profile_url text,
    avatar_url text,
    is_active boolean DEFAULT true,
    last_synced_at timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    
    -- Unique constraint: one handle per platform per user
    CONSTRAINT unique_competitor_per_user UNIQUE (user_id, platform, handle)
);

-- Competitor content table: Store competitor posts/content
CREATE TABLE IF NOT EXISTS competitor_content (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_id uuid REFERENCES competitors(id) ON DELETE CASCADE,
    external_id varchar(255) NOT NULL,
    content text NOT NULL,
    content_type varchar(50) DEFAULT 'post' CHECK (content_type IN ('post', 'article', 'video', 'story', 'reel', 'thread')),
    published_at timestamptz NOT NULL,
    url text,
    media_urls text[] DEFAULT '{}',
    
    -- Engagement metrics
    likes int DEFAULT 0,
    shares int DEFAULT 0,
    comments int DEFAULT 0,
    views int DEFAULT 0,
    engagement_score int DEFAULT 0,
    
    -- Content analysis
    sentiment varchar(20) CHECK (sentiment IN ('positive', 'negative', 'neutral')),
    topics text[] DEFAULT '{}',
    keywords text[] DEFAULT '{}',
    
    analyzed_at timestamptz,
    created_at timestamptz DEFAULT now(),
    
    -- Unique constraint: one external_id per competitor
    CONSTRAINT unique_content_per_competitor UNIQUE (competitor_id, external_id)
);

-- Content gaps table: Identify opportunities
CREATE TABLE IF NOT EXISTS content_gaps (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    topic varchar(255) NOT NULL,
    category varchar(100),
    
    -- Gap analysis
    competitor_count int DEFAULT 0,
    user_has_content boolean DEFAULT false,
    user_content_count int DEFAULT 0,
    opportunity_score int DEFAULT 0 CHECK (opportunity_score >= 0 AND opportunity_score <= 100),
    
    -- Suggestions
    suggested_action text,
    content_ideas text[] DEFAULT '{}',
    priority varchar(20) DEFAULT 'medium' CHECK (priority IN ('high', 'medium', 'low')),
    
    -- Status tracking
    is_addressed boolean DEFAULT false,
    addressed_at timestamptz,
    
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    
    -- Unique constraint: one topic per user
    CONSTRAINT unique_gap_per_user UNIQUE (user_id, topic)
);

-- Competitor performance snapshot table: Track historical performance
CREATE TABLE IF NOT EXISTS competitor_performance_snapshots (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    competitor_id uuid REFERENCES competitors(id) ON DELETE CASCADE,
    snapshot_date date NOT NULL DEFAULT CURRENT_DATE,
    
    -- Metrics at snapshot time
    follower_count int,
    total_posts int,
    total_likes int,
    total_shares int,
    total_comments int,
    avg_engagement_rate decimal(5,2),
    
    -- Calculated metrics
    posts_last_7_days int DEFAULT 0,
    posts_last_30_days int DEFAULT 0,
    engagement_last_7_days int DEFAULT 0,
    engagement_last_30_days int DEFAULT 0,
    
    created_at timestamptz DEFAULT now(),
    
    -- One snapshot per competitor per day
    CONSTRAINT unique_daily_snapshot UNIQUE (competitor_id, snapshot_date)
);

-- User competitor comparisons table: Store user's performance vs competitors
CREATE TABLE IF NOT EXISTS user_competitor_comparison (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    comparison_date date NOT NULL DEFAULT CURRENT_DATE,
    
    -- User metrics
    user_follower_count int DEFAULT 0,
    user_total_content int DEFAULT 0,
    user_avg_engagement decimal(5,2) DEFAULT 0,
    
    -- Aggregated competitor metrics
    competitor_count int DEFAULT 0,
    avg_competitor_followers int DEFAULT 0,
    avg_competitor_engagement decimal(5,2) DEFAULT 0,
    
    -- Comparison results
    follower_gap int DEFAULT 0,  -- negative means user has fewer
    engagement_gap_percent decimal(5,2) DEFAULT 0,
    
    created_at timestamptz DEFAULT now(),
    
    -- One comparison per user per day
    CONSTRAINT unique_daily_comparison UNIQUE (user_id, comparison_date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_competitors_user_id ON competitors(user_id);
CREATE INDEX IF NOT EXISTS idx_competitors_platform ON competitors(platform);
CREATE INDEX IF NOT EXISTS idx_competitor_content_competitor_id ON competitor_content(competitor_id);
CREATE INDEX IF NOT EXISTS idx_competitor_content_published_at ON competitor_content(published_at);
CREATE INDEX IF NOT EXISTS idx_competitor_content_engagement ON competitor_content(engagement_score DESC);
CREATE INDEX IF NOT EXISTS idx_competitor_content_topics ON competitor_content USING gin(topics);
CREATE INDEX IF NOT EXISTS idx_content_gaps_user_id ON content_gaps(user_id);
CREATE INDEX IF NOT EXISTS idx_content_gaps_opportunity ON content_gaps(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_content_gaps_priority ON content_gaps(priority);
CREATE INDEX IF NOT EXISTS idx_performance_snapshots_competitor_id ON competitor_performance_snapshots(competitor_id);
CREATE INDEX IF NOT EXISTS idx_performance_snapshots_date ON competitor_performance_snapshots(snapshot_date);

-- Row Level Security (RLS) policies
ALTER TABLE competitors ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_content ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_gaps ENABLE ROW LEVEL SECURITY;
ALTER TABLE competitor_performance_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_competitor_comparison ENABLE ROW LEVEL SECURITY;

-- Competitors: Users can only see their own competitors
CREATE POLICY competitors_user_isolation ON competitors
    FOR ALL
    USING (user_id = auth.uid());

-- Competitor content: Users can see content for their competitors
CREATE POLICY competitor_content_user_isolation ON competitor_content
    FOR ALL
    USING (EXISTS (
        SELECT 1 FROM competitors c 
        WHERE c.id = competitor_content.competitor_id 
        AND c.user_id = auth.uid()
    ));

-- Content gaps: Users can only see their own gaps
CREATE POLICY content_gaps_user_isolation ON content_gaps
    FOR ALL
    USING (user_id = auth.uid());

-- Performance snapshots: Users can see snapshots for their competitors
CREATE POLICY performance_snapshots_user_isolation ON competitor_performance_snapshots
    FOR ALL
    USING (EXISTS (
        SELECT 1 FROM competitors c 
        WHERE c.id = competitor_performance_snapshots.competitor_id 
        AND c.user_id = auth.uid()
    ));

-- User comparisons: Users can only see their own comparisons
CREATE POLICY user_comparison_isolation ON user_competitor_comparison
    FOR ALL
    USING (user_id = auth.uid());

-- Update triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_competitors_updated_at
    BEFORE UPDATE ON competitors
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_content_gaps_updated_at
    BEFORE UPDATE ON content_gaps
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Comments
COMMENT ON TABLE competitors IS 'Tracks competitor profiles across social platforms';
COMMENT ON TABLE competitor_content IS 'Stores competitor posts and engagement metrics';
COMMENT ON TABLE content_gaps IS 'Identifies content opportunities based on competitor analysis';
COMMENT ON TABLE competitor_performance_snapshots IS 'Historical performance data for trend analysis';
COMMENT ON TABLE user_competitor_comparison IS 'Daily comparison of user vs competitor performance';