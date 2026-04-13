-- ============================================================================
-- REMOVE TRANSLATION SYSTEM
-- Drops translation tables and related objects
-- ============================================================================

-- Drop translation table
DROP TABLE IF EXISTS public.translations CASCADE;

-- Drop translation cache table if it exists
DROP TABLE IF EXISTS public.translation_cache CASCADE;

-- Drop helper functions
DROP FUNCTION IF EXISTS public.get_user_translation_stats(uuid);
DROP FUNCTION IF EXISTS public.cleanup_old_translations(integer);

-- ============================================================================
-- NOTE: Language support now limited to English (en) and German (de) only.
-- No additional language tables or translation services needed.
-- ============================================================================
