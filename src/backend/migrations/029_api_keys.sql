-- API Keys table for BYOK (Bring Your Own Key) support
-- Migration 029

-- ============================================================
-- api_keys — stores per-user encrypted LLM provider keys
-- ============================================================
CREATE TABLE IF NOT EXISTS api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  provider VARCHAR(50) NOT NULL CHECK (provider IN ('google', 'groq', 'cerebras', 'openrouter', 'custom')),
  encrypted_key TEXT NOT NULL,
  base_url VARCHAR(500),           -- optional override
  model VARCHAR(100),              -- optional model override
  label VARCHAR(100),              -- user-friendly name e.g. "My Google Key"
  is_valid BOOLEAN NOT NULL DEFAULT false,
  last_validated_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- One key per provider per user (can be relaxed later if needed)
CREATE UNIQUE INDEX IF NOT EXISTS idx_api_keys_user_provider ON api_keys(user_id, provider);
CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);

-- ============================================================
-- RLS policies
-- ============================================================
ALTER TABLE api_keys ENABLE ROW LEVEL SECURITY;

-- Users can only see their own keys
CREATE POLICY api_keys_user_policy ON api_keys
  FOR ALL
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

-- ============================================================
-- updated_at trigger
-- ============================================================
CREATE OR REPLACE FUNCTION update_api_keys_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_api_keys_updated_at ON api_keys;
CREATE TRIGGER trigger_api_keys_updated_at
  BEFORE UPDATE ON api_keys
  FOR EACH ROW
  EXECUTE FUNCTION update_api_keys_updated_at();