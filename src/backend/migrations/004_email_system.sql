-- Email notification system migration
-- Add email preferences and tracking tables

-- Add email_preferences column to profiles
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS email_preferences JSONB DEFAULT '{
  "marketing_emails": true,
  "usage_alerts": true,
  "weekly_digest": true,
  "feature_announcements": true,
  "invoice_receipts": true,
  "digest_frequency": "weekly"
}'::jsonb;

-- Add welcome email tracking to profiles
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS welcome_email_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS welcome_email_sent_at TIMESTAMPTZ;

-- Add unsubscribed tracking
ALTER TABLE profiles
ADD COLUMN IF NOT EXISTS unsubscribed_at TIMESTAMPTZ;

-- Create email tracking table
CREATE TABLE IF NOT EXISTS email_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES profiles(id) ON DELETE CASCADE,
    to_email TEXT NOT NULL,
    template_type TEXT NOT NULL,
    template_data JSONB DEFAULT '{}'::jsonb,
    status TEXT NOT NULL CHECK (status IN ('pending', 'sent', 'failed', 'skipped')),
    email_id TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for email tracking
CREATE INDEX IF NOT EXISTS idx_email_tracking_user_id ON email_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_email_tracking_status ON email_tracking(status);
CREATE INDEX IF NOT EXISTS idx_email_tracking_template ON email_tracking(template_type);
CREATE INDEX IF NOT EXISTS idx_email_tracking_sent_at ON email_tracking(sent_at);
CREATE INDEX IF NOT EXISTS idx_email_tracking_created_at ON email_tracking(created_at);

-- Create partial index for failed emails (for retry queries)
CREATE INDEX IF NOT EXISTS idx_email_tracking_failed_retry 
ON email_tracking(id, retry_count) 
WHERE status = 'failed' AND retry_count < 3;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for email tracking
DROP TRIGGER IF EXISTS update_email_tracking_updated_at ON email_tracking;
CREATE TRIGGER update_email_tracking_updated_at
    BEFORE UPDATE ON email_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comment for documentation
COMMENT ON TABLE email_tracking IS 'Tracks all email sends with status, retries, and delivery information';
COMMENT ON COLUMN profiles.email_preferences IS 'JSON containing user email notification preferences';
