-- Migration 025: Create all missing Supabase tables
-- Description: Creates 35 tables that are referenced by backend code but missing from the live staging DB.
--              Some of these already have definitions in earlier migration files (006, 007, 009, 013, 014, 016, 018)
--              but were never applied. All use IF NOT EXISTS for idempotency.
-- Created: 2026-04-18

-- ============================================================
-- Order: tables with no FK deps first, then dependent tables
-- ============================================================

-- ── user_profiles ─────────────────────────────────────────────
-- Referenced by: trends.py (select role)
CREATE TABLE IF NOT EXISTS user_profiles (
    id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email varchar(255),
    full_name varchar(255),
    avatar_url text,
    role varchar(50) NOT NULL DEFAULT 'user' CHECK (role IN ('user', 'admin', 'editor')),
    bio text,
    company varchar(255),
    website text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_user_profiles_email ON user_profiles(email);
CREATE INDEX IF NOT EXISTS idx_user_profiles_role ON user_profiles(role);

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);

-- ── assets ─────────────────────────────────────────────────────
-- Referenced by: publishing_queue (asset_id FK)
CREATE TABLE IF NOT EXISTS assets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    project_id uuid REFERENCES projects(id) ON DELETE SET NULL,
    name varchar(255) NOT NULL,
    type varchar(50) NOT NULL DEFAULT 'image' CHECK (type IN ('image', 'video', 'audio', 'document', 'other')),
    url text NOT NULL,
    size bigint DEFAULT 0,
    mime_type varchar(100),
    metadata jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_assets_user_id ON assets(user_id);
CREATE INDEX IF NOT EXISTS idx_assets_project_id ON assets(project_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(user_id, type);

ALTER TABLE assets ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own assets" ON assets FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own assets" ON assets FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own assets" ON assets FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own assets" ON assets FOR DELETE USING (auth.uid() = user_id);

-- ── analytics ─────────────────────────────────────────────────
-- Referenced by: suggestion_service.py (select: content_id, views, likes, shares, comments, engagement_rate, recorded_at)
CREATE TABLE IF NOT EXISTS analytics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content_id uuid REFERENCES content(id) ON DELETE CASCADE,
    views int DEFAULT 0,
    likes int DEFAULT 0,
    shares int DEFAULT 0,
    comments int DEFAULT 0,
    engagement_rate float DEFAULT 0,
    recorded_at timestamptz DEFAULT now(),
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_analytics_user_id ON analytics(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_content_id ON analytics(content_id);
CREATE INDEX IF NOT EXISTS idx_analytics_recorded_at ON analytics(recorded_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_user_content ON analytics(user_id, content_id);

ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own analytics" ON analytics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own analytics" ON analytics FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── saml_providers ─────────────────────────────────────────────
-- Referenced by: saml_service.py (insert) and saml_identities/saml_states FK
CREATE TABLE IF NOT EXISTS saml_providers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name varchar(100) NOT NULL,
    display_name varchar(255) NOT NULL,
    entity_id text NOT NULL,
    sso_url text NOT NULL,
    slo_url text,
    metadata_url text,
    metadata_xml text,
    certificate text,
    attribute_mapping jsonb DEFAULT '{}',
    org_id uuid,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_saml_providers_user_id ON saml_providers(user_id);
CREATE INDEX IF NOT EXISTS idx_saml_providers_name ON saml_providers(name);
CREATE INDEX IF NOT EXISTS idx_saml_providers_entity_id ON saml_providers(entity_id);

ALTER TABLE saml_providers ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own SAML providers" ON saml_providers FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own SAML providers" ON saml_providers FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own SAML providers" ON saml_providers FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own SAML providers" ON saml_providers FOR DELETE USING (auth.uid() = user_id);

-- ── saml_identities ───────────────────────────────────────────
-- Referenced by: saml_service.py (insert: user_id, provider_id, name_id, email, full_name)
CREATE TABLE IF NOT EXISTS saml_identities (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    provider_id uuid NOT NULL REFERENCES saml_providers(id) ON DELETE CASCADE,
    name_id text NOT NULL,
    email varchar(255),
    full_name varchar(255),
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_saml_identities_user_id ON saml_identities(user_id);
CREATE INDEX IF NOT EXISTS idx_saml_identities_provider_id ON saml_identities(provider_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_saml_identities_name_id ON saml_identities(provider_id, name_id);

ALTER TABLE saml_identities ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own SAML identities" ON saml_identities FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own SAML identities" ON saml_identities FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── saml_states ───────────────────────────────────────────────
-- Referenced by: saml_service.py (insert: state, provider_id, relay_state, redirect_uri, saml_request_id, expires_at)
CREATE TABLE IF NOT EXISTS saml_states (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    state varchar(255) NOT NULL UNIQUE,
    provider_id uuid NOT NULL REFERENCES saml_providers(id) ON DELETE CASCADE,
    relay_state text,
    redirect_uri text,
    saml_request_id varchar(255),
    expires_at bigint NOT NULL,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_saml_states_state ON saml_states(state);
CREATE INDEX IF NOT EXISTS idx_saml_states_provider_id ON saml_states(provider_id);
CREATE INDEX IF NOT EXISTS idx_saml_states_expires_at ON saml_states(expires_at);

ALTER TABLE saml_states ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role can manage SAML states" ON saml_states FOR ALL USING (true);

-- ── ai_suggestions ────────────────────────────────────────────
-- Referenced by: ai_suggestions.py (AIImprovementSuggestion model)
CREATE TABLE IF NOT EXISTS ai_suggestions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    suggestion_type varchar(50) NOT NULL,
    original_text text NOT NULL,
    improved_text text NOT NULL,
    explanation text NOT NULL DEFAULT '',
    confidence_score float,
    applied boolean NOT NULL DEFAULT false,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_suggestions_user_id ON ai_suggestions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_content_id ON ai_suggestions(content_id);
CREATE INDEX IF NOT EXISTS idx_ai_suggestions_type ON ai_suggestions(user_id, suggestion_type);

ALTER TABLE ai_suggestions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own AI suggestions" ON ai_suggestions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own AI suggestions" ON ai_suggestions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own AI suggestions" ON ai_suggestions FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own AI suggestions" ON ai_suggestions FOR DELETE USING (auth.uid() = user_id);

-- ── auto_suggestions ──────────────────────────────────────────
-- Referenced by: suggestion_service.py (insert: user_id, suggestion_type, suggestions, metadata)
CREATE TABLE IF NOT EXISTS auto_suggestions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    suggestion_type varchar(50) NOT NULL,
    suggestions jsonb NOT NULL DEFAULT '[]',
    metadata jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_auto_suggestions_user_id ON auto_suggestions(user_id);
CREATE INDEX IF NOT EXISTS idx_auto_suggestions_type ON auto_suggestions(user_id, suggestion_type);
CREATE INDEX IF NOT EXISTS idx_auto_suggestions_created_at ON auto_suggestions(created_at DESC);

ALTER TABLE auto_suggestions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own auto suggestions" ON auto_suggestions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own auto suggestions" ON auto_suggestions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own auto suggestions" ON auto_suggestions FOR DELETE USING (auth.uid() = user_id);

-- ── ai_editor_history ────────────────────────────────────────
-- Referenced by: ai_editor.py (EditorHistoryItem: id, content_id, operation, original_preview, result_preview, tokens_used, created_at)
CREATE TABLE IF NOT EXISTS ai_editor_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content_id uuid REFERENCES content(id) ON DELETE SET NULL,
    operation varchar(50) NOT NULL,
    original_preview text DEFAULT '',
    result_preview text DEFAULT '',
    tokens_used int DEFAULT 0,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ai_editor_history_user_id ON ai_editor_history(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_editor_history_content_id ON ai_editor_history(content_id);
CREATE INDEX IF NOT EXISTS idx_ai_editor_history_operation ON ai_editor_history(user_id, operation);
CREATE INDEX IF NOT EXISTS idx_ai_editor_history_created_at ON ai_editor_history(created_at DESC);

ALTER TABLE ai_editor_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own editor history" ON ai_editor_history FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own editor history" ON ai_editor_history FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── seo_analyses ──────────────────────────────────────────────
-- Referenced by: ai_suggestions.py (SEOAnalysisResult model)
CREATE TABLE IF NOT EXISTS seo_analyses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    seo_score int NOT NULL DEFAULT 0 CHECK (seo_score BETWEEN 0 AND 100),
    keyword_density jsonb NOT NULL DEFAULT '{}',
    readability_score int NOT NULL DEFAULT 0 CHECK (readability_score BETWEEN 0 AND 100),
    suggestions jsonb NOT NULL DEFAULT '[]',
    meta_title_suggestion text,
    meta_description_suggestion text,
    heading_structure_suggestions jsonb DEFAULT '[]',
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_seo_analyses_user_id ON seo_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_seo_analyses_content_id ON seo_analyses(content_id);
CREATE INDEX IF NOT EXISTS idx_seo_analyses_created_at ON seo_analyses(created_at DESC);

ALTER TABLE seo_analyses ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own SEO analyses" ON seo_analyses FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own SEO analyses" ON seo_analyses FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── tone_adjustments ─────────────────────────────────────────
-- Referenced by: ai_suggestions.py (ToneAdjustmentResult model)
CREATE TABLE IF NOT EXISTS tone_adjustments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    original_tone varchar(50) NOT NULL DEFAULT 'neutral',
    target_tone varchar(50) NOT NULL,
    adjusted_text text NOT NULL DEFAULT '',
    tone_characteristics jsonb NOT NULL DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_tone_adjustments_user_id ON tone_adjustments(user_id);
CREATE INDEX IF NOT EXISTS idx_tone_adjustments_content_id ON tone_adjustments(content_id);
CREATE INDEX IF NOT EXISTS idx_tone_adjustments_created_at ON tone_adjustments(created_at DESC);

ALTER TABLE tone_adjustments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own tone adjustments" ON tone_adjustments FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own tone adjustments" ON tone_adjustments FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── quality_scores ────────────────────────────────────────────
-- Referenced by: quality_service.py (insert: content_id, user_id, overall_score, readability, seo, engagement, grammar, brand, suggestions)
CREATE TABLE IF NOT EXISTS quality_scores (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    overall_score float NOT NULL DEFAULT 0,
    readability float NOT NULL DEFAULT 0,
    seo float NOT NULL DEFAULT 0,
    engagement float NOT NULL DEFAULT 0,
    grammar float NOT NULL DEFAULT 0,
    brand float NOT NULL DEFAULT 0,
    suggestions jsonb DEFAULT '[]',
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_quality_scores_user_id ON quality_scores(user_id);
CREATE INDEX IF NOT EXISTS idx_quality_scores_content_id ON quality_scores(content_id);
CREATE INDEX IF NOT EXISTS idx_quality_scores_created_at ON quality_scores(created_at DESC);

ALTER TABLE quality_scores ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own quality scores" ON quality_scores FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own quality scores" ON quality_scores FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── collaboration_edits ──────────────────────────────────────
-- Referenced by: collaboration_service.py (insert: id, content_id, user_id, operation_type, position, length, text, version, created_at)
CREATE TABLE IF NOT EXISTS collaboration_edits (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid NOT NULL,
    user_id uuid NOT NULL,
    operation_type varchar(50) NOT NULL,
    position int DEFAULT 0,
    length int DEFAULT 0,
    text text DEFAULT '',
    version int DEFAULT 0,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_collaboration_edits_content_id ON collaboration_edits(content_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_edits_user_id ON collaboration_edits(user_id);
CREATE INDEX IF NOT EXISTS idx_collaboration_edits_created_at ON collaboration_edits(created_at DESC);

ALTER TABLE collaboration_edits ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view edits for their content" ON collaboration_edits FOR SELECT USING (
    content_id IN (SELECT id FROM content WHERE user_id = auth.uid())
);
CREATE POLICY "Users can insert edits for their content" ON collaboration_edits FOR INSERT WITH CHECK (true);

-- ── presence ──────────────────────────────────────────────────
-- Referenced by: presence_service.py (upsert: room, user_id, user_name, status, last_active, updated_at; on_conflict="room,user_id")
CREATE TABLE IF NOT EXISTS presence (
    room varchar(255) NOT NULL,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    user_name varchar(255) DEFAULT '',
    status varchar(20) NOT NULL DEFAULT 'online' CHECK (status IN ('online', 'away', 'offline')),
    last_active timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    PRIMARY KEY (room, user_id)
);

CREATE INDEX IF NOT EXISTS idx_presence_room ON presence(room);
CREATE INDEX IF NOT EXISTS idx_presence_user_id ON presence(user_id);
CREATE INDEX IF NOT EXISTS idx_presence_status ON presence(room, status);

ALTER TABLE presence ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view presence in rooms" ON presence FOR SELECT USING (true);
CREATE POLICY "Users can insert own presence" ON presence FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own presence" ON presence FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own presence" ON presence FOR DELETE USING (auth.uid() = user_id);

-- ── comment_mentions ──────────────────────────────────────────
-- Referenced by: comments_service.py (insert: comment_id, username)
CREATE TABLE IF NOT EXISTS comment_mentions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id uuid NOT NULL REFERENCES content_comments(id) ON DELETE CASCADE,
    username varchar(255) NOT NULL,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_comment_mentions_comment_id ON comment_mentions(comment_id);
CREATE INDEX IF NOT EXISTS idx_comment_mentions_username ON comment_mentions(username);

ALTER TABLE comment_mentions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view comment mentions" ON comment_mentions FOR SELECT USING (true);
CREATE POLICY "Users can insert comment mentions" ON comment_mentions FOR INSERT WITH CHECK (true);
CREATE POLICY "Users can delete comment mentions" ON comment_mentions FOR DELETE USING (true);

-- ── comment_reactions ─────────────────────────────────────────
-- Referenced by: comments_service.py (insert: comment_id, user_id, emoji)
CREATE TABLE IF NOT EXISTS comment_reactions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    comment_id uuid NOT NULL REFERENCES content_comments(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    emoji varchar(10) NOT NULL,
    created_at timestamptz DEFAULT now(),
    UNIQUE(comment_id, user_id, emoji)
);

CREATE INDEX IF NOT EXISTS idx_comment_reactions_comment_id ON comment_reactions(comment_id);
CREATE INDEX IF NOT EXISTS idx_comment_reactions_user_id ON comment_reactions(user_id);

ALTER TABLE comment_reactions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view comment reactions" ON comment_reactions FOR SELECT USING (true);
CREATE POLICY "Users can insert own reactions" ON comment_reactions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can delete own reactions" ON comment_reactions FOR DELETE USING (auth.uid() = user_id);

-- ── marketplace_installs ──────────────────────────────────────
-- Referenced by: marketplace_service.py (insert: template_id, user_id, installed_at)
CREATE TABLE IF NOT EXISTS marketplace_installs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id uuid NOT NULL REFERENCES marketplace_templates(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    installed_at timestamptz DEFAULT now(),
    UNIQUE(template_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_marketplace_installs_template_id ON marketplace_installs(template_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_installs_user_id ON marketplace_installs(user_id);

ALTER TABLE marketplace_installs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own installs" ON marketplace_installs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own installs" ON marketplace_installs FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── marketplace_ratings ──────────────────────────────────────
-- Referenced by: marketplace_service.py (insert: template_id, user_id, rating, review)
CREATE TABLE IF NOT EXISTS marketplace_ratings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id uuid NOT NULL REFERENCES marketplace_templates(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    rating int NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review text,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(template_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_marketplace_ratings_template_id ON marketplace_ratings(template_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_ratings_user_id ON marketplace_ratings(user_id);

ALTER TABLE marketplace_ratings ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view ratings" ON marketplace_ratings FOR SELECT USING (true);
CREATE POLICY "Users can insert own ratings" ON marketplace_ratings FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own ratings" ON marketplace_ratings FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own ratings" ON marketplace_ratings FOR DELETE USING (auth.uid() = user_id);

-- ── marketplace_template_versions ─────────────────────────────
-- Referenced by: marketplace_service.py (insert: template_id, version, change_summary, author_id)
CREATE TABLE IF NOT EXISTS marketplace_template_versions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id uuid NOT NULL REFERENCES marketplace_templates(id) ON DELETE CASCADE,
    version varchar(50) NOT NULL,
    change_summary text,
    author_id uuid REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_marketplace_template_versions_template_id ON marketplace_template_versions(template_id);
CREATE INDEX IF NOT EXISTS idx_marketplace_template_versions_created_at ON marketplace_template_versions(created_at DESC);

ALTER TABLE marketplace_template_versions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view template versions" ON marketplace_template_versions FOR SELECT USING (true);
CREATE POLICY "Users can insert template versions" ON marketplace_template_versions FOR INSERT WITH CHECK (true);

-- ── automation_logs ───────────────────────────────────────────
-- Referenced by: automation.py (AutomationLogResponse model)
CREATE TABLE IF NOT EXISTS automation_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    rule_id uuid NOT NULL REFERENCES automation_rules(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status varchar(20) NOT NULL DEFAULT 'running' CHECK (status IN ('running', 'completed', 'failed')),
    triggered_by varchar(100) NOT NULL DEFAULT 'manual',
    input_data jsonb DEFAULT '{}',
    output_data jsonb DEFAULT '{}',
    error_message text,
    execution_time_ms int,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_automation_logs_rule_id ON automation_logs(rule_id);
CREATE INDEX IF NOT EXISTS idx_automation_logs_user_id ON automation_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_automation_logs_status ON automation_logs(user_id, status);
CREATE INDEX IF NOT EXISTS idx_automation_logs_created_at ON automation_logs(created_at DESC);

ALTER TABLE automation_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own automation logs" ON automation_logs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own automation logs" ON automation_logs FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own automation logs" ON automation_logs FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own automation logs" ON automation_logs FOR DELETE USING (auth.uid() = user_id);

-- ── publishing_queue ──────────────────────────────────────────
-- Referenced by: automation.py (QueueItemResponse model)
CREATE TABLE IF NOT EXISTS publishing_queue (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    content_id uuid NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    asset_id uuid REFERENCES assets(id) ON DELETE SET NULL,
    platform varchar(50) NOT NULL,
    status varchar(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'scheduled', 'processing', 'published', 'failed')),
    scheduled_for timestamptz,
    published_at timestamptz,
    error_message text,
    retry_count int NOT NULL DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_publishing_queue_user_id ON publishing_queue(user_id);
CREATE INDEX IF NOT EXISTS idx_publishing_queue_content_id ON publishing_queue(content_id);
CREATE INDEX IF NOT EXISTS idx_publishing_queue_status ON publishing_queue(user_id, status);
CREATE INDEX IF NOT EXISTS idx_publishing_queue_scheduled_for ON publishing_queue(scheduled_for);

ALTER TABLE publishing_queue ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own publishing queue" ON publishing_queue FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own publishing queue" ON publishing_queue FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own publishing queue" ON publishing_queue FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own publishing queue" ON publishing_queue FOR DELETE USING (auth.uid() = user_id);

-- ── webhook_endpoints ─────────────────────────────────────────
-- Referenced by: automation.py (WebhookEndpointResponse model)
CREATE TABLE IF NOT EXISTS webhook_endpoints (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name varchar(255) NOT NULL,
    description text,
    project_id uuid REFERENCES projects(id) ON DELETE SET NULL,
    endpoint_url text NOT NULL,
    secret text,
    allowed_ips jsonb DEFAULT '[]',
    is_active boolean NOT NULL DEFAULT true,
    total_calls int NOT NULL DEFAULT 0,
    last_called_at timestamptz,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_webhook_endpoints_user_id ON webhook_endpoints(user_id);
CREATE INDEX IF NOT EXISTS idx_webhook_endpoints_is_active ON webhook_endpoints(is_active);

ALTER TABLE webhook_endpoints ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own webhook endpoints" ON webhook_endpoints FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own webhook endpoints" ON webhook_endpoints FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own webhook endpoints" ON webhook_endpoints FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own webhook endpoints" ON webhook_endpoints FOR DELETE USING (auth.uid() = user_id);

-- ── webhook_logs ──────────────────────────────────────────────
-- Referenced by: webhooks.py (get_webhook_logs: webhook_type, event_source, status, created_at)
-- This table was missing entirely, causing /webhooks/logs 500
CREATE TABLE IF NOT EXISTS webhook_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    webhook_type varchar(50) NOT NULL DEFAULT 'outgoing',
    event_source varchar(100),
    event_type varchar(100),
    payload jsonb DEFAULT '{}',
    status varchar(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'delivered', 'failed', 'retrying')),
    response_status int,
    response_body text,
    error_message text,
    attempts int DEFAULT 0,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_webhook_logs_user_id ON webhook_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_webhook_type ON webhook_logs(user_id, webhook_type);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_status ON webhook_logs(status);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_created_at ON webhook_logs(created_at DESC);

ALTER TABLE webhook_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own webhook logs" ON webhook_logs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own webhook logs" ON webhook_logs FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- Tables from existing migrations (re-declared with IF NOT EXISTS for safety)
-- These migrations exist in the repo but were never applied to staging
-- ============================================================

-- ── funnels (dependency for funnel_events) ────────────────────
CREATE TABLE IF NOT EXISTS funnels (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name varchar(200) NOT NULL,
    description text DEFAULT '',
    steps jsonb NOT NULL DEFAULT '[]',
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_funnels_user_id ON funnels(user_id);
CREATE INDEX IF NOT EXISTS idx_funnels_created_at ON funnels(created_at DESC);

ALTER TABLE funnels ENABLE ROW LEVEL SECURITY;
CREATE POLICY funnels_user_policy ON funnels FOR ALL USING (user_id = auth.uid());

-- ── funnel_events ────────────────────────────────────────────
-- From migration 006_funnel_attribution.sql
CREATE TABLE IF NOT EXISTS funnel_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    funnel_id uuid NOT NULL REFERENCES funnels(id) ON DELETE CASCADE,
    step_id varchar(100) NOT NULL,
    user_id varchar(255) DEFAULT '',
    event_data jsonb DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_funnel_events_funnel_id ON funnel_events(funnel_id);
CREATE INDEX IF NOT EXISTS idx_funnel_events_funnel_step ON funnel_events(funnel_id, step_id);
CREATE INDEX IF NOT EXISTS idx_funnel_events_created_at ON funnel_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_funnel_events_user_id ON funnel_events(user_id) WHERE user_id != '';

ALTER TABLE funnel_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY funnel_events_user_policy ON funnel_events FOR ALL USING (
    funnel_id IN (SELECT id FROM funnels WHERE user_id = auth.uid())
);

-- ── attribution_touchpoints ──────────────────────────────────
-- From migration 006 (dependency-free)
CREATE TABLE IF NOT EXISTS attribution_touchpoints (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid NOT NULL,
    channel varchar(100) NOT NULL,
    source varchar(200) DEFAULT '',
    campaign varchar(200) DEFAULT '',
    event_data jsonb DEFAULT '{}',
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_attribution_touchpoints_content_id ON attribution_touchpoints(content_id);
CREATE INDEX IF NOT EXISTS idx_attribution_touchpoints_channel ON attribution_touchpoints(channel);
CREATE INDEX IF NOT EXISTS idx_attribution_touchpoints_created_at ON attribution_touchpoints(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_attribution_touchpoints_content_channel ON attribution_touchpoints(content_id, channel);

ALTER TABLE attribution_touchpoints ENABLE ROW LEVEL SECURITY;
CREATE POLICY attribution_touchpoints_user_policy ON attribution_touchpoints FOR ALL USING (
    content_id IN (SELECT id FROM content WHERE user_id = auth.uid())
);

-- ── sla_policies (dependency for sla_alerts) ─────────────────
CREATE TABLE IF NOT EXISTS sla_policies (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name varchar(255) NOT NULL,
    metric varchar(50) NOT NULL CHECK (metric IN ('uptime', 'response_time', 'error_rate', 'throughput')),
    threshold float NOT NULL,
    window_minutes int NOT NULL DEFAULT 5 CHECK (window_minutes > 0),
    severity varchar(20) NOT NULL DEFAULT 'warning' CHECK (severity IN ('critical', 'warning', 'info')),
    enabled boolean NOT NULL DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sla_policies_user_id ON sla_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_sla_policies_metric ON sla_policies(user_id, metric);
CREATE INDEX IF NOT EXISTS idx_sla_policies_enabled ON sla_policies(user_id, enabled) WHERE enabled = true;

ALTER TABLE sla_policies ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own SLA policies" ON sla_policies FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own SLA policies" ON sla_policies FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own SLA policies" ON sla_policies FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own SLA policies" ON sla_policies FOR DELETE USING (auth.uid() = user_id);

-- ── sla_metrics ──────────────────────────────────────────────
-- From migration 007
CREATE TABLE IF NOT EXISTS sla_metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_type varchar(50) NOT NULL CHECK (metric_type IN ('uptime', 'response_time', 'error_rate', 'throughput')),
    value float NOT NULL,
    labels jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_sla_metrics_user_id ON sla_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_sla_metrics_type ON sla_metrics(user_id, metric_type);
CREATE INDEX IF NOT EXISTS idx_sla_metrics_created_at ON sla_metrics(created_at DESC);

ALTER TABLE sla_metrics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own SLA metrics" ON sla_metrics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own SLA metrics" ON sla_metrics FOR INSERT WITH CHECK (auth.uid() = user_id);

-- ── sla_alerts ───────────────────────────────────────────────
-- From migration 007
CREATE TABLE IF NOT EXISTS sla_alerts (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    policy_id uuid NOT NULL REFERENCES sla_policies(id) ON DELETE CASCADE,
    metric_type varchar(50) NOT NULL,
    current_value float NOT NULL,
    threshold float NOT NULL,
    severity varchar(20) NOT NULL CHECK (severity IN ('critical', 'warning', 'info')),
    message text,
    created_at timestamptz DEFAULT now(),
    acknowledged boolean NOT NULL DEFAULT false,
    acknowledged_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_sla_alerts_user_id ON sla_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_sla_alerts_policy_id ON sla_alerts(policy_id);
CREATE INDEX IF NOT EXISTS idx_sla_alerts_acknowledged ON sla_alerts(user_id, acknowledged) WHERE acknowledged = false;
CREATE INDEX IF NOT EXISTS idx_sla_alerts_created_at ON sla_alerts(created_at DESC);

ALTER TABLE sla_alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own SLA alerts" ON sla_alerts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own SLA alerts" ON sla_alerts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own SLA alerts" ON sla_alerts FOR UPDATE USING (auth.uid() = user_id);

-- ── integration_configs (dependency for integration_events/logs) ──
-- From migration 007
CREATE TABLE IF NOT EXISTS integration_configs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name varchar(255) NOT NULL,
    type varchar(50) NOT NULL CHECK (type IN ('webhook', 'api', 'polling', 'streaming')),
    provider varchar(255) NOT NULL,
    credentials jsonb DEFAULT '{}'::jsonb,
    settings jsonb DEFAULT '{}'::jsonb,
    enabled boolean NOT NULL DEFAULT true,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_integration_configs_user_id ON integration_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_integration_configs_type ON integration_configs(user_id, type);
CREATE INDEX IF NOT EXISTS idx_integration_configs_provider ON integration_configs(user_id, provider);

ALTER TABLE integration_configs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own integration configs" ON integration_configs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own integration configs" ON integration_configs FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own integration configs" ON integration_configs FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own integration configs" ON integration_configs FOR DELETE USING (auth.uid() = user_id);

-- ── integration_events ───────────────────────────────────────
-- From migration 007
CREATE TABLE IF NOT EXISTS integration_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    config_id uuid NOT NULL REFERENCES integration_configs(id) ON DELETE CASCADE,
    event_type varchar(255) NOT NULL,
    payload jsonb DEFAULT '{}'::jsonb,
    status varchar(50) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    retries int NOT NULL DEFAULT 0,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_integration_events_config_id ON integration_events(config_id);
CREATE INDEX IF NOT EXISTS idx_integration_events_user_id ON integration_events(user_id);
CREATE INDEX IF NOT EXISTS idx_integration_events_status ON integration_events(config_id, status);
CREATE INDEX IF NOT EXISTS idx_integration_events_created_at ON integration_events(created_at DESC);

ALTER TABLE integration_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own integration events" ON integration_events FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own integration events" ON integration_events FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own integration events" ON integration_events FOR UPDATE USING (auth.uid() = user_id);

-- ── integration_logs ──────────────────────────────────────────
-- From migration 007
CREATE TABLE IF NOT EXISTS integration_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id uuid NOT NULL REFERENCES integration_configs(id) ON DELETE CASCADE,
    event_id uuid REFERENCES integration_events(id) ON DELETE SET NULL,
    level varchar(20) NOT NULL DEFAULT 'info' CHECK (level IN ('debug', 'info', 'warning', 'error')),
    message text NOT NULL,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_integration_logs_config_id ON integration_logs(config_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_event_id ON integration_logs(event_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_created_at ON integration_logs(created_at DESC);

ALTER TABLE integration_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own integration logs" ON integration_logs FOR SELECT USING (auth.uid() IN (SELECT user_id FROM integration_configs WHERE id = config_id));
CREATE POLICY "Users can insert own integration logs" ON integration_logs FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM integration_configs WHERE id = config_id AND user_id = auth.uid()));

-- ── trash ────────────────────────────────────────────────────
-- From migration 009
CREATE TABLE IF NOT EXISTS trash (
    id uuid PRIMARY KEY,
    type varchar(50) NOT NULL CHECK (type IN ('content', 'project', 'asset')),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    original_data jsonb NOT NULL,
    deleted_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL,
    restored_at timestamptz,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trash_user_id ON trash(user_id);
CREATE INDEX IF NOT EXISTS idx_trash_type ON trash(type);
CREATE INDEX IF NOT EXISTS idx_trash_deleted_at ON trash(deleted_at);
CREATE INDEX IF NOT EXISTS idx_trash_expires_at ON trash(expires_at);

ALTER TABLE trash ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view their own trash" ON trash FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert into their own trash" ON trash FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update their own trash" ON trash FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete from their own trash" ON trash FOR DELETE USING (auth.uid() = user_id);

-- ── content_freshness_scores ──────────────────────────────────
-- From migration 013 (may already exist but FK might be missing)
CREATE TABLE IF NOT EXISTS content_freshness_scores (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid REFERENCES content(id) ON DELETE CASCADE,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    freshness_score int CHECK (freshness_score BETWEEN 0 AND 100),
    age_days int,
    last_analyzed_at timestamptz DEFAULT now(),
    factors jsonb DEFAULT '{}',
    recommendations jsonb DEFAULT '[]',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(content_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_freshness_user_score ON content_freshness_scores(user_id, freshness_score);
CREATE INDEX IF NOT EXISTS idx_freshness_content_id ON content_freshness_scores(content_id);
CREATE INDEX IF NOT EXISTS idx_freshness_user_content ON content_freshness_scores(user_id, content_id);
CREATE INDEX IF NOT EXISTS idx_freshness_last_analyzed ON content_freshness_scores(last_analyzed_at);

ALTER TABLE content_freshness_scores ENABLE ROW LEVEL SECURITY;
CREATE POLICY freshness_scores_select_own ON content_freshness_scores FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY freshness_scores_insert_own ON content_freshness_scores FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY freshness_scores_update_own ON content_freshness_scores FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY freshness_scores_delete_own ON content_freshness_scores FOR DELETE USING (auth.uid() = user_id);

-- ── trending_topics ──────────────────────────────────────────
-- From migration 014
CREATE TABLE IF NOT EXISTS trending_topics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    topic varchar(255) NOT NULL,
    category varchar(50),
    trend_score float DEFAULT 0,
    mention_count int DEFAULT 0,
    velocity float DEFAULT 0,
    source varchar(50),
    discovered_at timestamptz DEFAULT now(),
    expires_at timestamptz,
    related_keywords jsonb DEFAULT '[]'::jsonb,
    sample_content jsonb DEFAULT '[]'::jsonb,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_trending_topics_category ON trending_topics(category);
CREATE INDEX IF NOT EXISTS idx_trending_topics_discovered_at ON trending_topics(discovered_at DESC);
CREATE INDEX IF NOT EXISTS idx_trending_topics_trend_score ON trending_topics(trend_score DESC);
CREATE INDEX IF NOT EXISTS idx_trending_topics_expires_at ON trending_topics(expires_at);

ALTER TABLE trending_topics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow public read of trending topics" ON trending_topics FOR SELECT USING (expires_at IS NULL OR expires_at > now());
CREATE POLICY "Allow service role insert on trending topics" ON trending_topics FOR INSERT WITH CHECK (true);
CREATE POLICY "Allow service role update on trending topics" ON trending_topics FOR UPDATE USING (true);
CREATE POLICY "Allow service role delete on trending topics" ON trending_topics FOR DELETE USING (true);

-- ── user_topic_interests ─────────────────────────────────────
-- From migration 014
CREATE TABLE IF NOT EXISTS user_topic_interests (
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    topic_id uuid REFERENCES trending_topics(id) ON DELETE CASCADE,
    relevance_score float DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    PRIMARY KEY (user_id, topic_id)
);

CREATE INDEX IF NOT EXISTS idx_user_topic_interests_user_id ON user_topic_interests(user_id);
CREATE INDEX IF NOT EXISTS idx_user_topic_interests_topic_id ON user_topic_interests(topic_id);

ALTER TABLE user_topic_interests ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow users to read own topic interests" ON user_topic_interests FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Allow users to insert own topic interests" ON user_topic_interests FOR INSERT WITH CHECK (user_id = auth.uid());
CREATE POLICY "Allow users to update own topic interests" ON user_topic_interests FOR UPDATE USING (user_id = auth.uid());
CREATE POLICY "Allow users to delete own topic interests" ON user_topic_interests FOR DELETE USING (user_id = auth.uid());

-- ── trend_content_suggestions ────────────────────────────────
-- From migration 014
CREATE TABLE IF NOT EXISTS trend_content_suggestions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_id uuid REFERENCES trending_topics(id) ON DELETE CASCADE,
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    platform varchar(50) NOT NULL,
    suggested_content text NOT NULL,
    tokens_used int DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    used_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_trend_content_suggestions_user_id ON trend_content_suggestions(user_id);
CREATE INDEX IF NOT EXISTS idx_trend_content_suggestions_topic_id ON trend_content_suggestions(topic_id);
CREATE INDEX IF NOT EXISTS idx_trend_content_suggestions_created_at ON trend_content_suggestions(created_at DESC);

ALTER TABLE trend_content_suggestions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow users to read own trend suggestions" ON trend_content_suggestions FOR SELECT USING (user_id = auth.uid());
CREATE POLICY "Allow service role insert on trend suggestions" ON trend_content_suggestions FOR INSERT WITH CHECK (true);

-- ── content_topics ───────────────────────────────────────────
-- From migration 014 (join table)
CREATE TABLE IF NOT EXISTS content_topics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid REFERENCES content(id) ON DELETE CASCADE,
    topic_id uuid REFERENCES trending_topics(id) ON DELETE CASCADE,
    relevance_score float DEFAULT 0,
    created_at timestamptz DEFAULT now(),
    UNIQUE(content_id, topic_id)
);

CREATE INDEX IF NOT EXISTS idx_content_topics_content_id ON content_topics(content_id);
CREATE INDEX IF NOT EXISTS idx_content_topics_topic_id ON content_topics(topic_id);

ALTER TABLE content_topics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Allow users to read content topics" ON content_topics FOR SELECT USING (EXISTS (SELECT 1 FROM content c WHERE c.id = content_topics.content_id AND c.user_id = auth.uid()));
CREATE POLICY "Allow service role insert on content topics" ON content_topics FOR INSERT WITH CHECK (true);

-- ── in_app_notifications ─────────────────────────────────────
-- From migration 016
CREATE TABLE IF NOT EXISTS in_app_notifications (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    alert_id uuid,
    title varchar(255) NOT NULL,
    message text NOT NULL,
    type varchar(50) NOT NULL DEFAULT 'info',
    is_read boolean NOT NULL DEFAULT false,
    created_at timestamptz NOT NULL DEFAULT now(),
    read_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_in_app_notifications_user ON in_app_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_in_app_notifications_user_read ON in_app_notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_in_app_notifications_created ON in_app_notifications(created_at DESC);

ALTER TABLE in_app_notifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY in_app_notifications_user_select ON in_app_notifications FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY in_app_notifications_user_insert ON in_app_notifications FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY in_app_notifications_user_update ON in_app_notifications FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY in_app_notifications_user_delete ON in_app_notifications FOR DELETE USING (auth.uid() = user_id);

-- ── webhook_deliveries (from migration 018) ──────────────────
-- Note: already partially covered by migration 018 but included for IF NOT EXISTS safety
-- The integrations table may already exist; webhook_deliveries references it
CREATE TABLE IF NOT EXISTS integrations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE,
    integration_type varchar(50) NOT NULL CHECK (integration_type IN ('zapier', 'webhook', 'wordpress', 'make', 'n8n')),
    name varchar(255) NOT NULL,
    config jsonb NOT NULL DEFAULT '{}'::jsonb,
    is_active boolean DEFAULT true,
    last_used_at timestamptz,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_integrations_user_id ON integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_integrations_type ON integrations(integration_type);
CREATE INDEX IF NOT EXISTS idx_integrations_user_type ON integrations(user_id, integration_type);
CREATE INDEX IF NOT EXISTS idx_integrations_active ON integrations(is_active);

ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;
CREATE POLICY integrations_select_own ON integrations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY integrations_insert_own ON integrations FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY integrations_update_own ON integrations FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY integrations_delete_own ON integrations FOR DELETE USING (auth.uid() = user_id);

-- webhook_deliveries depends on integrations
CREATE TABLE IF NOT EXISTS webhook_deliveries (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id uuid REFERENCES integrations(id) ON DELETE CASCADE,
    event_type varchar(50) NOT NULL,
    payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    status varchar(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'delivered', 'failed', 'retrying')),
    attempts int DEFAULT 0,
    response_status int,
    response_body text,
    error_message text,
    delivered_at timestamptz,
    next_retry_at timestamptz,
    created_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_status ON webhook_deliveries(status);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_event_type ON webhook_deliveries(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_created_at ON webhook_deliveries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_webhook_status ON webhook_deliveries(webhook_id, status);

ALTER TABLE webhook_deliveries ENABLE ROW LEVEL SECURITY;
CREATE POLICY webhook_deliveries_select_own ON webhook_deliveries FOR SELECT USING (
    EXISTS (SELECT 1 FROM integrations i WHERE i.id = webhook_deliveries.webhook_id AND i.user_id = auth.uid())
);
CREATE POLICY webhook_deliveries_insert_own ON webhook_deliveries FOR INSERT WITH CHECK (true);
CREATE POLICY webhook_deliveries_update_own ON webhook_deliveries FOR UPDATE USING (
    EXISTS (SELECT 1 FROM integrations i WHERE i.id = webhook_deliveries.webhook_id AND i.user_id = auth.uid())
);

-- ============================================================
-- Trigger function for updated_at (idempotent)
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers to tables that need them
DROP TRIGGER IF EXISTS update_integrations_updated_at ON integrations;
CREATE TRIGGER update_integrations_updated_at BEFORE UPDATE ON integrations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_trending_topics_updated_at ON trending_topics;
CREATE TRIGGER update_trending_topics_updated_at BEFORE UPDATE ON trending_topics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_topic_interests_updated_at ON user_topic_interests;
CREATE TRIGGER update_user_topic_interests_updated_at BEFORE UPDATE ON user_topic_interests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS tr_freshness_scores_updated_at ON content_freshness_scores;
CREATE TRIGGER tr_freshness_scores_updated_at BEFORE UPDATE ON content_freshness_scores FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- Grant permissions
-- ============================================================
GRANT SELECT, INSERT, UPDATE, DELETE ON user_profiles TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON assets TO authenticated;
GRANT SELECT, INSERT ON analytics TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON saml_providers TO authenticated;
GRANT SELECT, INSERT ON saml_identities TO authenticated;
GRANT ALL ON saml_states TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ai_suggestions TO authenticated;
GRANT SELECT, INSERT, DELETE ON auto_suggestions TO authenticated;
GRANT SELECT, INSERT ON ai_editor_history TO authenticated;
GRANT SELECT, INSERT ON seo_analyses TO authenticated;
GRANT SELECT, INSERT ON tone_adjustments TO authenticated;
GRANT SELECT, INSERT ON quality_scores TO authenticated;
GRANT SELECT, INSERT ON collaboration_edits TO authenticated;
GRANT ALL ON presence TO authenticated;
GRANT SELECT, INSERT, DELETE ON comment_mentions TO authenticated;
GRANT SELECT, INSERT, DELETE ON comment_reactions TO authenticated;
GRANT SELECT, INSERT ON marketplace_installs TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON marketplace_ratings TO authenticated;
GRANT SELECT, INSERT ON marketplace_template_versions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON automation_logs TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON publishing_queue TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON webhook_endpoints TO authenticated;
GRANT SELECT, INSERT ON webhook_logs TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON funnels TO authenticated;
GRANT SELECT, INSERT ON funnel_events TO authenticated;
GRANT SELECT, INSERT ON attribution_touchpoints TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON sla_policies TO authenticated;
GRANT SELECT, INSERT ON sla_metrics TO authenticated;
GRANT SELECT, INSERT, UPDATE ON sla_alerts TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON integration_configs TO authenticated;
GRANT SELECT, INSERT, UPDATE ON integration_events TO authenticated;
GRANT SELECT, INSERT ON integration_logs TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON trash TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON content_freshness_scores TO authenticated;
GRANT SELECT ON trending_topics TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON user_topic_interests TO authenticated;
GRANT SELECT, INSERT ON trend_content_suggestions TO authenticated;
GRANT SELECT, INSERT ON content_topics TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON in_app_notifications TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON integrations TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON webhook_deliveries TO authenticated;

-- ============================================================
-- Notify PostgREST to reload schema cache
-- This fixes the content_freshness_scores FK issue and picks up all new tables
-- ============================================================
NOTIFY pgrst, 'reload schema';

-- ============================================================
-- Comments
-- ============================================================
COMMENT ON TABLE user_profiles IS 'Extended user profile data with role information';
COMMENT ON TABLE assets IS 'User-uploaded assets (images, videos, documents)';
COMMENT ON TABLE analytics IS 'Content engagement analytics snapshots';
COMMENT ON TABLE saml_providers IS 'SAML IdP provider configurations';
COMMENT ON TABLE saml_identities IS 'SAML identity links (IdP name_id → local user)';
COMMENT ON TABLE saml_states IS 'Transient SAML auth state for SSO flow';
COMMENT ON TABLE ai_suggestions IS 'AI-generated content improvement suggestions';
COMMENT ON TABLE auto_suggestions IS 'Auto-generated suggestions (topics, posting times, improvements)';
COMMENT ON TABLE ai_editor_history IS 'History of AI editor operations (rewrite, expand, condense, optimize)';
COMMENT ON TABLE seo_analyses IS 'SEO analysis results for content';
COMMENT ON TABLE tone_adjustments IS 'Tone adjustment results for content';
COMMENT ON TABLE quality_scores IS 'Content quality scoring results';
COMMENT ON TABLE collaboration_edits IS 'Real-time collaboration edit operations';
COMMENT ON TABLE presence IS 'User presence status in collaboration rooms';
COMMENT ON TABLE comment_mentions IS 'Username mentions within comments';
COMMENT ON TABLE comment_reactions IS 'Emoji reactions on comments';
COMMENT ON TABLE marketplace_installs IS 'Marketplace template install tracking';
COMMENT ON TABLE marketplace_ratings IS 'Marketplace template ratings and reviews';
COMMENT ON TABLE marketplace_template_versions IS 'Marketplace template version history';
COMMENT ON TABLE automation_logs IS 'Automation rule execution logs';
COMMENT ON TABLE publishing_queue IS 'Content publishing queue for scheduled posts';
COMMENT ON TABLE webhook_endpoints IS 'User-defined webhook endpoints';
COMMENT ON TABLE webhook_logs IS 'Webhook event logs (incoming and outgoing)';