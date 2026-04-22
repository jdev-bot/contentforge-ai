-- A/B Testing tables for ContentForge AI
-- Migration 028

-- ============================================================
-- ab_experiments
-- ============================================================
CREATE TABLE IF NOT EXISTS ab_experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  content_id VARCHAR(255),
  variant_a TEXT NOT NULL,
  variant_b TEXT NOT NULL,
  platform VARCHAR(50) NOT NULL DEFAULT 'twitter',
  status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'running', 'paused', 'completed', 'stopped')),
  duration_days INTEGER NOT NULL DEFAULT 7 CHECK (duration_days >= 1 AND duration_days <= 90),
  started_at TIMESTAMPTZ,
  ended_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ab_experiments_user_id ON ab_experiments(user_id);
CREATE INDEX IF NOT EXISTS idx_ab_experiments_status ON ab_experiments(status);

-- ============================================================
-- ab_experiment_results
-- ============================================================
CREATE TABLE IF NOT EXISTS ab_experiment_results (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  experiment_id UUID NOT NULL REFERENCES ab_experiments(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  variant VARCHAR(1) NOT NULL CHECK (variant IN ('a', 'b')),
  impressions INTEGER NOT NULL DEFAULT 0 CHECK (impressions >= 0),
  engagements INTEGER NOT NULL DEFAULT 0 CHECK (engagements >= 0),
  clicks INTEGER NOT NULL DEFAULT 0 CHECK (clicks >= 0),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_ab_experiment_results_experiment_id ON ab_experiment_results(experiment_id);
CREATE INDEX IF NOT EXISTS idx_ab_experiment_results_variant ON ab_experiment_results(variant);

-- ============================================================
-- Row Level Security
-- ============================================================
ALTER TABLE ab_experiments ENABLE ROW LEVEL SECURITY;
ALTER TABLE ab_experiment_results ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own experiments" ON ab_experiments;
CREATE POLICY "Users can view own experiments" ON ab_experiments
  FOR SELECT USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can insert own experiments" ON ab_experiments;
CREATE POLICY "Users can insert own experiments" ON ab_experiments
  FOR INSERT WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can update own experiments" ON ab_experiments;
CREATE POLICY "Users can update own experiments" ON ab_experiments
  FOR UPDATE USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can delete own experiments" ON ab_experiments;
CREATE POLICY "Users can delete own experiments" ON ab_experiments
  FOR DELETE USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can view own experiment results" ON ab_experiment_results;
CREATE POLICY "Users can view own experiment results" ON ab_experiment_results
  FOR SELECT USING (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can insert own experiment results" ON ab_experiment_results;
CREATE POLICY "Users can insert own experiment results" ON ab_experiment_results
  FOR INSERT WITH CHECK (user_id = auth.uid());

DROP POLICY IF EXISTS "Users can delete own experiment results" ON ab_experiment_results;
CREATE POLICY "Users can delete own experiment results" ON ab_experiment_results
  FOR DELETE USING (user_id = auth.uid());