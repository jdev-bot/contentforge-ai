-- ============================================================================
-- TRANSLATIONS TABLE
-- Stores cached translations for content items
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.translations (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    content_id uuid REFERENCES public.content(id) ON DELETE CASCADE NOT NULL,
    target_language varchar(10) NOT NULL,
    translated_text text NOT NULL,
    source_language varchar(10) DEFAULT 'en',
    confidence_score float CHECK (confidence_score >= 0 AND confidence_score <= 1),
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz DEFAULT now(),
    UNIQUE(content_id, target_language)
);

-- Enable RLS on translations
ALTER TABLE public.translations ENABLE ROW LEVEL SECURITY;

-- Translations RLS policies
-- Users can view translations for content they own
CREATE POLICY "Users can view own translations"
    ON public.translations FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.content
            WHERE content.id = translations.content_id
            AND content.user_id = auth.uid()
        )
    );

-- Users can create translations for content they own
CREATE POLICY "Users can create translations for own content"
    ON public.translations FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.content
            WHERE content.id = translations.content_id
            AND content.user_id = auth.uid()
        )
    );

-- Users can update translations for content they own
CREATE POLICY "Users can update own translations"
    ON public.translations FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.content
            WHERE content.id = translations.content_id
            AND content.user_id = auth.uid()
        )
    );

-- Users can delete translations for content they own
CREATE POLICY "Users can delete own translations"
    ON public.translations FOR DELETE
    USING (
        EXISTS (
            SELECT 1 FROM public.content
            WHERE content.id = translations.content_id
            AND content.user_id = auth.uid()
        )
    );

-- Create indexes for translations
CREATE INDEX IF NOT EXISTS idx_translations_content_id ON public.translations(content_id);
CREATE INDEX IF NOT EXISTS idx_translations_target_language ON public.translations(target_language);
CREATE INDEX IF NOT EXISTS idx_translations_created_at ON public.translations(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_translations_content_language ON public.translations(content_id, target_language);

-- Trigger for updated_at
CREATE TRIGGER handle_translations_updated_at
    BEFORE UPDATE ON public.translations
    FOR EACH ROW EXECUTE FUNCTION public.handle_updated_at();

-- ============================================================================
-- TRANSLATION USAGE TRACKING
-- Add translation action to usage_logs if not exists
-- ============================================================================

-- Note: The usage_logs table already exists and tracks various actions.
-- Translation actions will be tracked with action = 'translation'.

-- ============================================================================
-- TRANSLATION RATE LIMITING SUPPORT
-- ============================================================================

-- Add translation-specific columns to rate limiting if needed
-- (The existing rate limiting system already supports this)

-- ============================================================================
-- HELPER FUNCTION: Get translation stats for a user
-- ============================================================================

CREATE OR REPLACE FUNCTION public.get_user_translation_stats(user_uuid uuid)
RETURNS TABLE (
    total_translations bigint,
    unique_languages bigint,
    cached_translations bigint,
    recent_translations bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::bigint as total_translations,
        COUNT(DISTINCT t.target_language)::bigint as unique_languages,
        COUNT(*) FILTER (WHERE t.created_at < NOW() - INTERVAL '1 hour')::bigint as cached_translations,
        COUNT(*) FILTER (WHERE t.created_at > NOW() - INTERVAL '24 hours')::bigint as recent_translations
    FROM public.translations t
    JOIN public.content c ON c.id = t.content_id
    WHERE c.user_id = user_uuid;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- CLEANUP FUNCTION: Remove old translations
-- ============================================================================

CREATE OR REPLACE FUNCTION public.cleanup_old_translations(older_than_days integer DEFAULT 90)
RETURNS integer AS $$
DECLARE
    deleted_count integer;
BEGIN
    DELETE FROM public.translations
    WHERE created_at < NOW() - (older_than_days || ' days')::interval;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
