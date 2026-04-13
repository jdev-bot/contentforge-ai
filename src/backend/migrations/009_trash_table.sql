-- Migration: Add trash table for soft delete functionality
-- Created: 2026-04-13

-- Create trash table
CREATE TABLE IF NOT EXISTS trash (
    id UUID PRIMARY KEY,
    type VARCHAR(50) NOT NULL CHECK (type IN ('content', 'project', 'asset')),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    original_data JSONB NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    restored_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_trash_user_id ON trash(user_id);
CREATE INDEX idx_trash_type ON trash(type);
CREATE INDEX idx_trash_deleted_at ON trash(deleted_at);
CREATE INDEX idx_trash_expires_at ON trash(expires_at);
CREATE INDEX idx_trash_restored_at ON trash(restored_at) WHERE restored_at IS NULL;

-- Create unique index to prevent duplicates
CREATE UNIQUE INDEX idx_trash_item ON trash(id, user_id) WHERE restored_at IS NULL;

-- Enable RLS
ALTER TABLE trash ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
CREATE POLICY "Users can view their own trash"
    ON trash FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert into their own trash"
    ON trash FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own trash"
    ON trash FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete from their own trash"
    ON trash FOR DELETE
    USING (auth.uid() = user_id);

-- Add deleted_at columns to content and projects tables if not exists
DO $$
BEGIN
    -- Add deleted_at to content table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'content' AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE content ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
        CREATE INDEX idx_content_deleted_at ON content(deleted_at) WHERE deleted_at IS NULL;
    END IF;

    -- Add deleted_at to projects table
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'projects' AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE projects ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE;
        CREATE INDEX idx_projects_deleted_at ON projects(deleted_at) WHERE deleted_at IS NULL;
    END IF;
END $$;

-- Create function to clean up expired trash
CREATE OR REPLACE FUNCTION cleanup_expired_trash()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER := 0;
BEGIN
    -- Delete expired items from trash
    WITH deleted AS (
        DELETE FROM trash
        WHERE expires_at < NOW()
        AND restored_at IS NULL
        RETURNING id
    )
    SELECT COUNT(*) INTO deleted_count FROM deleted;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Add comment
COMMENT ON TABLE trash IS 'Soft-deleted items with automatic expiration';
COMMENT ON COLUMN trash.original_data IS 'Complete JSON snapshot of the item before deletion';
COMMENT ON COLUMN trash.expires_at IS 'When the item will be permanently deleted (30 days after deletion)';
COMMENT ON COLUMN trash.restored_at IS 'When the item was restored from trash (NULL if not restored)';
