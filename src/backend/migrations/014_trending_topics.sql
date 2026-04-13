-- Migration: Add trending topics and user topic interests tables
-- Description: AI-powered trending topics detection system

-- Create trending_topics table
CREATE TABLE trending_topics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    topic varchar(255) NOT NULL,
    category varchar(50), -- tech, business, entertainment, etc.
    trend_score float DEFAULT 0,
    mention_count int DEFAULT 0,
    velocity float DEFAULT 0, -- rate of growth (mentions/hour)
    source varchar(50), -- twitter, reddit, news, etc.
    discovered_at timestamptz DEFAULT now(),
    expires_at timestamptz, -- when trend becomes stale
    related_keywords jsonb DEFAULT '[]'::jsonb,
    sample_content jsonb DEFAULT '[]'::jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Create user_topic_interests table
CREATE TABLE user_topic_interests (
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id uuid REFERENCES trending_topics(id) ON DELETE CASCADE,
    relevance_score float DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    PRIMARY KEY (user_id, topic_id)
);

-- Create indexes for performance
CREATE INDEX idx_trending_topics_category ON trending_topics(category);
CREATE INDEX idx_trending_topics_discovered_at ON trending_topics(discovered_at DESC);
CREATE INDEX idx_trending_topics_trend_score ON trending_topics(trend_score DESC);
CREATE INDEX idx_trending_topics_expires_at ON trending_topics(expires_at);
CREATE INDEX idx_user_topic_interests_user_id ON user_topic_interests(user_id);
CREATE INDEX idx_user_topic_interests_topic_id ON user_topic_interests(topic_id);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_trending_topics_updated_at
    BEFORE UPDATE ON trending_topics
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_topic_interests_updated_at
    BEFORE UPDATE ON user_topic_interests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable RLS on both tables
ALTER TABLE trending_topics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_topic_interests ENABLE ROW LEVEL SECURITY;

-- Create policies for trending_topics
-- Anyone can read active trending topics
CREATE POLICY "Allow public read of trending topics" 
    ON trending_topics FOR SELECT 
    USING (expires_at IS NULL OR expires_at > now());

-- Only service role can insert/update/delete
CREATE POLICY "Allow service role insert on trending topics" 
    ON trending_topics FOR INSERT 
    WITH CHECK (true);

CREATE POLICY "Allow service role update on trending topics" 
    ON trending_topics FOR UPDATE 
    USING (true);

CREATE POLICY "Allow service role delete on trending topics" 
    ON trending_topics FOR DELETE 
    USING (true);

-- Create policies for user_topic_interests
-- Users can only read their own interests
CREATE POLICY "Allow users to read own topic interests" 
    ON user_topic_interests FOR SELECT 
    USING (user_id = auth.uid());

-- Users can only insert their own interests
CREATE POLICY "Allow users to insert own topic interests" 
    ON user_topic_interests FOR INSERT 
    WITH CHECK (user_id = auth.uid());

-- Users can only update their own interests
CREATE POLICY "Allow users to update own topic interests" 
    ON user_topic_interests FOR UPDATE 
    USING (user_id = auth.uid());

-- Users can only delete their own interests
CREATE POLICY "Allow users to delete own topic interests" 
    ON user_topic_interests FOR DELETE 
    USING (user_id = auth.uid());

-- Create content_topics table to link content with topics
CREATE TABLE content_topics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid REFERENCES content(id) ON DELETE CASCADE,
    topic_id uuid REFERENCES trending_topics(id) ON DELETE CASCADE,
    relevance_score float DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    UNIQUE(content_id, topic_id)
);

-- Create index for content_topics
CREATE INDEX idx_content_topics_content_id ON content_topics(content_id);
CREATE INDEX idx_content_topics_topic_id ON content_topics(topic_id);

-- Enable RLS on content_topics
ALTER TABLE content_topics ENABLE ROW LEVEL SECURITY;

-- Users can read content topics for their own content
CREATE POLICY "Allow users to read content topics" 
    ON content_topics FOR SELECT 
    USING (EXISTS (
        SELECT 1 FROM content c 
        WHERE c.id = content_topics.content_id 
        AND c.user_id = auth.uid()
    ));

CREATE POLICY "Allow service role insert on content topics" 
    ON content_topics FOR INSERT 
    WITH CHECK (true);

-- Create table to store trend content suggestions
CREATE TABLE trend_content_suggestions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id uuid REFERENCES trending_topics(id) ON DELETE CASCADE,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    platform varchar(50) NOT NULL,
    suggested_content text NOT NULL,
    tokens_used int DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    used_at timestamptz
);

-- Create indexes for trend_content_suggestions
CREATE INDEX idx_trend_content_suggestions_user_id ON trend_content_suggestions(user_id);
CREATE INDEX idx_trend_content_suggestions_topic_id ON trend_content_suggestions(topic_id);
CREATE INDEX idx_trend_content_suggestions_created_at ON trend_content_suggestions(created_at DESC);

-- Enable RLS
ALTER TABLE trend_content_suggestions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow users to read own trend suggestions" 
    ON trend_content_suggestions FOR SELECT 
    USING (user_id = auth.uid());

CREATE POLICY "Allow service role insert on trend suggestions" 
    ON trend_content_suggestions FOR INSERT 
    WITH CHECK (true);

-- Add comments for documentation
COMMENT ON TABLE trending_topics IS 'Stores AI-detected trending topics with metrics';
COMMENT ON TABLE user_topic_interests IS 'Tracks user interest in specific trending topics';
COMMENT ON TABLE content_topics IS 'Links user content to trending topics';
COMMENT ON TABLE trend_content_suggestions IS 'Stores AI-generated content suggestions based on trends';
