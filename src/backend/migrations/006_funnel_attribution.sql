-- Migration 006: Funnel Tracking and Attribution Modeling
-- Creates tables for custom funnels, funnel events, and attribution touchpoints

-- ============================================================
-- Funnels
-- ============================================================
CREATE TABLE IF NOT EXISTS funnels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    steps JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for listing funnels by user
CREATE INDEX IF NOT EXISTS idx_funnels_user_id ON funnels(user_id);
CREATE INDEX IF NOT EXISTS idx_funnels_created_at ON funnels(created_at DESC);

-- ============================================================
-- Funnel Events
-- ============================================================
CREATE TABLE IF NOT EXISTS funnel_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    funnel_id UUID NOT NULL REFERENCES funnels(id) ON DELETE CASCADE,
    step_id VARCHAR(100) NOT NULL,
    user_id VARCHAR(255) DEFAULT '',
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for querying events by funnel
CREATE INDEX IF NOT EXISTS idx_funnel_events_funnel_id ON funnel_events(funnel_id);
-- Index for querying events by step within a funnel
CREATE INDEX IF NOT EXISTS idx_funnel_events_funnel_step ON funnel_events(funnel_id, step_id);
-- Index for date-range queries
CREATE INDEX IF NOT EXISTS idx_funnel_events_created_at ON funnel_events(created_at DESC);
-- Index for user-level funnel tracking
CREATE INDEX IF NOT EXISTS idx_funnel_events_user_id ON funnel_events(user_id) WHERE user_id != '';

-- ============================================================
-- Attribution Touchpoints
-- ============================================================
CREATE TABLE IF NOT EXISTS attribution_touchpoints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL,
    channel VARCHAR(100) NOT NULL,
    source VARCHAR(200) DEFAULT '',
    campaign VARCHAR(200) DEFAULT '',
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for querying touchpoints by content
CREATE INDEX IF NOT EXISTS idx_attribution_touchpoints_content_id ON attribution_touchpoints(content_id);
-- Index for querying by channel
CREATE INDEX IF NOT EXISTS idx_attribution_touchpoints_channel ON attribution_touchpoints(channel);
-- Index for date-range queries
CREATE INDEX IF NOT EXISTS idx_attribution_touchpoints_created_at ON attribution_touchpoints(created_at DESC);
-- Composite index for channel + content lookups
CREATE INDEX IF NOT EXISTS idx_attribution_touchpoints_content_channel ON attribution_touchpoints(content_id, channel);

-- ============================================================
-- Row Level Security (RLS)
-- ============================================================
ALTER TABLE funnels ENABLE ROW LEVEL SECURITY;
ALTER TABLE funnel_events ENABLE ROW LEVEL SECURITY;
-- attribution_touchpoints does not have a direct user_id FK,
-- so RLS is applied via content ownership

-- Funnels: users can only see/manage their own funnels
CREATE POLICY funnels_user_policy ON funnels
    FOR ALL USING (user_id = auth.uid());

-- Funnel events: accessible via funnel ownership
CREATE POLICY funnel_events_user_policy ON funnel_events
    FOR ALL USING (
        funnel_id IN (SELECT id FROM funnels WHERE user_id = auth.uid())
    );

-- Attribution touchpoints: accessible via content ownership
CREATE POLICY attribution_touchpoints_user_policy ON attribution_touchpoints
    FOR ALL USING (
        content_id IN (SELECT id FROM content WHERE user_id = auth.uid())
    );