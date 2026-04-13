-- SLA Monitoring & Custom Integrations Framework tables
-- Migration: 007_sla_integrations.sql

-- ── SLA Policies ────────────────────────────────────────────────────

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

-- ── SLA Metrics ──────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sla_metrics (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    metric_type varchar(50) NOT NULL CHECK (metric_type IN ('uptime', 'response_time', 'error_rate', 'throughput')),
    value float NOT NULL,
    labels jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now()
);

-- ── SLA Alerts ───────────────────────────────────────────────────────

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

-- ── Integration Configs ──────────────────────────────────────────────

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

-- ── Integration Events ───────────────────────────────────────────────

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

-- ── Integration Logs ─────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS integration_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    config_id uuid NOT NULL REFERENCES integration_configs(id) ON DELETE CASCADE,
    event_id uuid REFERENCES integration_events(id) ON DELETE SET NULL,
    level varchar(20) NOT NULL DEFAULT 'info' CHECK (level IN ('debug', 'info', 'warning', 'error')),
    message text NOT NULL,
    created_at timestamptz DEFAULT now()
);

-- ── Indexes ──────────────────────────────────────────────────────────

CREATE INDEX IF NOT EXISTS idx_sla_policies_user_id ON sla_policies(user_id);
CREATE INDEX IF NOT EXISTS idx_sla_policies_metric ON sla_policies(user_id, metric);
CREATE INDEX IF NOT EXISTS idx_sla_policies_enabled ON sla_policies(user_id, enabled) WHERE enabled = true;

CREATE INDEX IF NOT EXISTS idx_sla_metrics_user_id ON sla_metrics(user_id);
CREATE INDEX IF NOT EXISTS idx_sla_metrics_type ON sla_metrics(user_id, metric_type);
CREATE INDEX IF NOT EXISTS idx_sla_metrics_created_at ON sla_metrics(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sla_alerts_user_id ON sla_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_sla_alerts_policy_id ON sla_alerts(policy_id);
CREATE INDEX IF NOT EXISTS idx_sla_alerts_acknowledged ON sla_alerts(user_id, acknowledged) WHERE acknowledged = false;
CREATE INDEX IF NOT EXISTS idx_sla_alerts_created_at ON sla_alerts(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_integration_configs_user_id ON integration_configs(user_id);
CREATE INDEX IF NOT EXISTS idx_integration_configs_type ON integration_configs(user_id, type);
CREATE INDEX IF NOT EXISTS idx_integration_configs_provider ON integration_configs(user_id, provider);

CREATE INDEX IF NOT EXISTS idx_integration_events_config_id ON integration_events(config_id);
CREATE INDEX IF NOT EXISTS idx_integration_events_user_id ON integration_events(user_id);
CREATE INDEX IF NOT EXISTS idx_integration_events_status ON integration_events(config_id, status);
CREATE INDEX IF NOT EXISTS idx_integration_events_created_at ON integration_events(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_integration_logs_config_id ON integration_logs(config_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_event_id ON integration_logs(event_id);
CREATE INDEX IF NOT EXISTS idx_integration_logs_created_at ON integration_logs(created_at DESC);

-- ── RLS ──────────────────────────────────────────────────────────────

ALTER TABLE sla_policies ENABLE ROW LEVEL SECURITY;
ALTER TABLE sla_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE sla_alerts ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE integration_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own SLA policies" ON sla_policies FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own SLA policies" ON sla_policies FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own SLA policies" ON sla_policies FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own SLA policies" ON sla_policies FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own SLA metrics" ON sla_metrics FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own SLA metrics" ON sla_metrics FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can view own SLA alerts" ON sla_alerts FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own SLA alerts" ON sla_alerts FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own SLA alerts" ON sla_alerts FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own integration configs" ON integration_configs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own integration configs" ON integration_configs FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own integration configs" ON integration_configs FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own integration configs" ON integration_configs FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own integration events" ON integration_events FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own integration events" ON integration_events FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own integration events" ON integration_events FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own integration logs" ON integration_logs FOR SELECT USING (auth.uid() IN (SELECT user_id FROM integration_configs WHERE id = config_id));
CREATE POLICY "Users can insert own integration logs" ON integration_logs FOR INSERT WITH CHECK (EXISTS (SELECT 1 FROM integration_configs WHERE id = config_id AND user_id = auth.uid()));