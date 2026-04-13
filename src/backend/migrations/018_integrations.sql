-- Migration: Create integrations and webhook_deliveries tables
-- Author: Backend Engineer (Integrations Ecosystem)
-- Created: 2026-04-13

-- Create integrations table for storing third-party integrations
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

-- Create webhook_deliveries table for tracking webhook deliveries
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

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_integrations_user_id ON integrations(user_id);
CREATE INDEX IF NOT EXISTS idx_integrations_type ON integrations(integration_type);
CREATE INDEX IF NOT EXISTS idx_integrations_user_type ON integrations(user_id, integration_type);
CREATE INDEX IF NOT EXISTS idx_integrations_active ON integrations(is_active);
CREATE INDEX IF NOT EXISTS idx_integrations_created_at ON integrations(created_at);

CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_status ON webhook_deliveries(status);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_event_type ON webhook_deliveries(event_type);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_created_at ON webhook_deliveries(created_at);
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_next_retry ON webhook_deliveries(next_retry_at) WHERE status IN ('pending', 'retrying', 'failed');
CREATE INDEX IF NOT EXISTS idx_webhook_deliveries_webhook_status ON webhook_deliveries(webhook_id, status);

-- Add RLS policies for integrations
ALTER TABLE integrations ENABLE ROW LEVEL SECURITY;

-- Users can only see their own integrations
CREATE POLICY integrations_select_own ON integrations
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own integrations
CREATE POLICY integrations_insert_own ON integrations
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own integrations
CREATE POLICY integrations_update_own ON integrations
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can only delete their own integrations
CREATE POLICY integrations_delete_own ON integrations
    FOR DELETE
    USING (auth.uid() = user_id);

-- Add RLS policies for webhook_deliveries
ALTER TABLE webhook_deliveries ENABLE ROW LEVEL SECURITY;

-- Users can see deliveries for their own webhooks
CREATE POLICY webhook_deliveries_select_own ON webhook_deliveries
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM integrations i
            WHERE i.id = webhook_deliveries.webhook_id
            AND i.user_id = auth.uid()
        )
    );

-- Grant necessary permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON integrations TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON webhook_deliveries TO authenticated;

-- Create trigger function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for integrations table
DROP TRIGGER IF EXISTS update_integrations_updated_at ON integrations;
CREATE TRIGGER update_integrations_updated_at
    BEFORE UPDATE ON integrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comments for documentation
COMMENT ON TABLE integrations IS 'Stores third-party integrations (Zapier, Webhooks, WordPress, etc.)';
COMMENT ON TABLE webhook_deliveries IS 'Tracks webhook delivery attempts and statuses';
COMMENT ON COLUMN integrations.integration_type IS 'Type of integration: zapier, webhook, wordpress, make, n8n';
COMMENT ON COLUMN integrations.config IS 'JSON configuration specific to the integration type';
COMMENT ON COLUMN webhook_deliveries.webhook_id IS 'Reference to the integration that triggered this delivery';
COMMENT ON COLUMN webhook_deliveries.event_type IS 'Type of event that triggered the webhook (content.created, distribution.completed, etc.)';
COMMENT ON COLUMN webhook_deliveries.status IS 'Current status: pending, delivered, failed, retrying';
COMMENT ON COLUMN webhook_deliveries.next_retry_at IS 'When to retry if the delivery failed';
