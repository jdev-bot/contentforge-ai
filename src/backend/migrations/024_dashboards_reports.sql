-- Custom Dashboards & Report Scheduling tables
-- Migration: 024_dashboards_reports.sql

-- ── Dashboards ────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dashboards (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name varchar(100) NOT NULL,
    description text,
    layout_config jsonb DEFAULT '{}',
    is_default boolean DEFAULT false,
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS dashboard_widgets (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    dashboard_id uuid NOT NULL REFERENCES dashboards(id) ON DELETE CASCADE,
    widget_type varchar(50) NOT NULL CHECK (widget_type IN ('metric_card', 'line_chart', 'bar_chart', 'pie_chart', 'table', 'counter', 'recent_list')),
    title varchar(200) NOT NULL,
    data_source varchar(50) NOT NULL CHECK (data_source IN ('content_count', 'distribution_stats', 'quality_scores', 'sentiment_summary', 'team_activity', 'usage_stats')),
    refresh_interval int NOT NULL DEFAULT 60 CHECK (refresh_interval IN (30, 60, 300, 900, 1800)),
    size jsonb DEFAULT '{"w": 4, "h": 3}',
    position int NOT NULL DEFAULT 0,
    config jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_dashboards_user_id ON dashboards(user_id);
CREATE INDEX IF NOT EXISTS idx_dashboards_is_default ON dashboards(user_id, is_default) WHERE is_default = true;
CREATE INDEX IF NOT EXISTS idx_dashboard_widgets_dashboard_id ON dashboard_widgets(dashboard_id);
CREATE INDEX IF NOT EXISTS idx_dashboard_widgets_position ON dashboard_widgets(dashboard_id, position);

-- RLS
ALTER TABLE dashboards ENABLE ROW LEVEL SECURITY;
ALTER TABLE dashboard_widgets ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own dashboards" ON dashboards FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own dashboards" ON dashboards FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own dashboards" ON dashboards FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own dashboards" ON dashboards FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own dashboard widgets" ON dashboard_widgets FOR SELECT USING (
    dashboard_id IN (SELECT id FROM dashboards WHERE user_id = auth.uid())
);
CREATE POLICY "Users can insert own dashboard widgets" ON dashboard_widgets FOR INSERT WITH CHECK (
    dashboard_id IN (SELECT id FROM dashboards WHERE user_id = auth.uid())
);
CREATE POLICY "Users can update own dashboard widgets" ON dashboard_widgets FOR UPDATE USING (
    dashboard_id IN (SELECT id FROM dashboards WHERE user_id = auth.uid())
);
CREATE POLICY "Users can delete own dashboard widgets" ON dashboard_widgets FOR DELETE USING (
    dashboard_id IN (SELECT id FROM dashboards WHERE user_id = auth.uid())
);

-- ── Scheduled Reports ──────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS scheduled_reports (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    name varchar(200) NOT NULL,
    description text,
    report_type varchar(50) NOT NULL CHECK (report_type IN ('content_summary', 'performance_overview', 'quality_report', 'sentiment_report', 'team_activity')),
    schedule varchar(100) NOT NULL,  -- cron expression
    format varchar(10) NOT NULL DEFAULT 'html' CHECK (format IN ('pdf', 'html', 'csv')),
    recipients jsonb DEFAULT '[]',
    filters jsonb DEFAULT '{}',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS report_runs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    report_id uuid NOT NULL REFERENCES scheduled_reports(id) ON DELETE CASCADE,
    user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    status varchar(50) NOT NULL DEFAULT 'completed',
    format varchar(10) NOT NULL DEFAULT 'html',
    storage_path text,
    file_name varchar(255),
    error_message text,
    generated_at timestamptz DEFAULT now()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_scheduled_reports_user_id ON scheduled_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_report_runs_report_id ON report_runs(report_id);
CREATE INDEX IF NOT EXISTS idx_report_runs_user_id ON report_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_report_runs_generated_at ON report_runs(generated_at DESC);

-- RLS
ALTER TABLE scheduled_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE report_runs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own scheduled reports" ON scheduled_reports FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own scheduled reports" ON scheduled_reports FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own scheduled reports" ON scheduled_reports FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own scheduled reports" ON scheduled_reports FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own report runs" ON report_runs FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own report runs" ON report_runs FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own report runs" ON report_runs FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own report runs" ON report_runs FOR DELETE USING (auth.uid() = user_id);

-- ── Storage bucket for reports ────────────────────────────────────
-- Note: Run this in Supabase SQL editor or via API:
-- INSERT INTO storage.buckets (id, name, public) VALUES ('reports', 'reports', false) ON CONFLICT DO NOTHING;