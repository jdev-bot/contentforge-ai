-- Migration: Content Performance Alerts System
-- Description: Create tables for content performance alerts and alert rules

-- =====================================================
-- Table: content_alerts
-- Description: Stores triggered content performance alerts
-- =====================================================
CREATE TABLE IF NOT EXISTS content_alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('viral', 'declining', 'milestone', 'error')),
    content_id UUID REFERENCES content(id) ON DELETE CASCADE,
    metric_name VARCHAR(50) NOT NULL CHECK (metric_name IN ('views', 'engagement', 'clicks', 'shares', 'comments', 'likes')),
    threshold_value FLOAT NOT NULL,
    current_value FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'acknowledged', 'resolved')),
    message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMPTZ
);

-- =====================================================
-- Table: alert_rules
-- Description: Stores user-defined alert rules for content metrics
-- =====================================================
CREATE TABLE IF NOT EXISTS alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('viral', 'declining', 'milestone', 'error')),
    metric_name VARCHAR(50) NOT NULL CHECK (metric_name IN ('views', 'engagement', 'clicks', 'shares', 'comments', 'likes')),
    operator VARCHAR(10) NOT NULL CHECK (operator IN ('greater_than', 'less_than', 'equals', 'percentage_change')),
    threshold_value FLOAT NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    notification_channels JSONB NOT NULL DEFAULT '["in_app"]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- Table: alert_metrics_history
-- Description: Stores historical metrics for alert evaluation
-- =====================================================
CREATE TABLE IF NOT EXISTS alert_metrics_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id UUID NOT NULL REFERENCES content(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_name VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- Table: in_app_notifications
-- Description: Stores in-app notification messages
-- =====================================================
CREATE TABLE IF NOT EXISTS in_app_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    alert_id UUID REFERENCES content_alerts(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'info',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    read_at TIMESTAMPTZ
);

-- =====================================================
-- Indexes for performance
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_content_alerts_user_id ON content_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_content_alerts_content_id ON content_alerts(content_id);
CREATE INDEX IF NOT EXISTS idx_content_alerts_status ON content_alerts(status);
CREATE INDEX IF NOT EXISTS idx_content_alerts_created_at ON content_alerts(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_alerts_user_status ON content_alerts(user_id, status);

CREATE INDEX IF NOT EXISTS idx_alert_rules_user_id ON alert_rules(user_id);
CREATE INDEX IF NOT EXISTS idx_alert_rules_enabled ON alert_rules(is_enabled);
CREATE INDEX IF NOT EXISTS idx_alert_rules_user_enabled ON alert_rules(user_id, is_enabled);

CREATE INDEX IF NOT EXISTS idx_alert_metrics_history_content ON alert_metrics_history(content_id);
CREATE INDEX IF NOT EXISTS idx_alert_metrics_history_recorded ON alert_metrics_history(recorded_at);

CREATE INDEX IF NOT EXISTS idx_in_app_notifications_user ON in_app_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_in_app_notifications_user_read ON in_app_notifications(user_id, is_read);
CREATE INDEX IF NOT EXISTS idx_in_app_notifications_created ON in_app_notifications(created_at DESC);

-- =====================================================
-- Row Level Security (RLS) Policies
-- =====================================================
ALTER TABLE content_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_rules ENABLE ROW LEVEL SECURITY;
ALTER TABLE alert_metrics_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE in_app_notifications ENABLE ROW LEVEL SECURITY;

-- content_alerts policies
CREATE POLICY content_alerts_user_select ON content_alerts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY content_alerts_user_insert ON content_alerts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY content_alerts_user_update ON content_alerts
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY content_alerts_user_delete ON content_alerts
    FOR DELETE USING (auth.uid() = user_id);

-- alert_rules policies
CREATE POLICY alert_rules_user_select ON alert_rules
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY alert_rules_user_insert ON alert_rules
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY alert_rules_user_update ON alert_rules
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY alert_rules_user_delete ON alert_rules
    FOR DELETE USING (auth.uid() = user_id);

-- alert_metrics_history policies
CREATE POLICY alert_metrics_history_user_select ON alert_metrics_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY alert_metrics_history_user_insert ON alert_metrics_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- in_app_notifications policies
CREATE POLICY in_app_notifications_user_select ON in_app_notifications
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY in_app_notifications_user_insert ON in_app_notifications
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY in_app_notifications_user_update ON in_app_notifications
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY in_app_notifications_user_delete ON in_app_notifications
    FOR DELETE USING (auth.uid() = user_id);

-- =====================================================
-- Trigger: Update alert_rules.updated_at
-- =====================================================
CREATE OR REPLACE FUNCTION update_alert_rules_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_alert_rules_updated_at
    BEFORE UPDATE ON alert_rules
    FOR EACH ROW
    EXECUTE FUNCTION update_alert_rules_updated_at();

-- =====================================================
-- Comments for documentation
-- =====================================================
COMMENT ON TABLE content_alerts IS 'Stores triggered content performance alerts for users';
COMMENT ON TABLE alert_rules IS 'Stores user-defined alert rules for monitoring content metrics';
COMMENT ON TABLE alert_metrics_history IS 'Historical metrics data for alert evaluation and trending';
COMMENT ON TABLE in_app_notifications IS 'In-app notifications for alert events';

COMMENT ON COLUMN content_alerts.alert_type IS 'Type of alert: viral (spike), declining (drop), milestone (threshold reached), error (processing failure)';
COMMENT ON COLUMN content_alerts.status IS 'Alert status: active, acknowledged, or resolved';
COMMENT ON COLUMN alert_rules.operator IS 'Comparison operator: greater_than, less_than, equals, percentage_change';
COMMENT ON COLUMN alert_rules.notification_channels IS 'JSON array of notification channels: ["in_app", "email", "slack"]';
