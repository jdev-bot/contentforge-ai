"""
Provider-agnostic LLM service for content generation.

Supports any OpenAI-compatible API provider. Configure via:
  AI_PROVIDER  — google | groq | cerebras | openrouter | custom
  AI_API_KEY   — API key for the chosen provider
  AI_BASE_URL  — Override base URL (auto-set for known providers)
  AI_MODEL     — Model identifier (provider-specific defaults exist)

Legacy GROQ_API_KEY / GROQ_MODEL are still supported as fallbacks.

BYOK: Per-user API keys are resolved via the api_keys table.
When a user has their own key, it overrides the platform default.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Cache decrypted per-user keys in-memory (short TTL)
from functools import lru_cache
import time as _time

_user_key_cache: Dict[str, Tuple[float, Dict]] = {}  # user_id -> (timestamp, {provider: decrypted_key, ...})
_USER_KEY_CACHE_TTL = 300  # 5 minutes

# ---------------------------------------------------------------------------
# Provider presets — known base URLs and default models
# ---------------------------------------------------------------------------
PROVIDER_PRESETS: Dict[str, Dict[str, str]] = {
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
        "default_model": "gemini-2.5-flash",
        "models_url": "https://generativelanguage.googleapis.com/v1beta/models",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "models_url": "https://api.groq.com/openai/v1/models",
    },
    "cerebras": {
        "base_url": "https://api.cerebras.ai/v1",
        "default_model": "llama-3.3-70b",
        "models_url": "https://api.cerebras.ai/v1/models",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "meta-llama/llama-3.3-70b-instruct",
        "models_url": "https://openrouter.ai/api/v1/models",
    },
}


class LLMService:
    """Provider-agnostic LLM service using OpenAI-compatible chat/completions."""

    def __init__(self):
        settings = get_settings()

        # Resolve provider
        self.provider: str = settings.AI_PROVIDER
        preset = PROVIDER_PRESETS.get(self.provider, {})

        # Resolve API key — new env var first, then legacy Groq fallback
        self.api_key: str = settings.AI_API_KEY or ""

        # Resolve base URL — explicit override > preset > error
        self.base_url: str = settings.AI_BASE_URL or preset.get("base_url", "")
        if not self.base_url:
            raise ValueError(
                f"AI_BASE_URL not set and no preset for provider '{self.provider}'. "
                "Set AI_BASE_URL or use a known provider: "
                + ", ".join(PROVIDER_PRESETS.keys())
            )

        # Resolve model — explicit AI_MODEL > legacy GROQ_MODEL (only when provider=groq) > preset default
        groq_model = settings.GROQ_MODEL if self.provider == "groq" else None
        self.model: str = (
            settings.AI_MODEL
            or groq_model
            or preset.get("default_model", "")
        )

        # Models listing URL for health checks (provider-specific)
        self._models_url: str = preset.get("models_url", f"{self.base_url}/models")

        self.headers: Dict[str, str] = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # OpenRouter expects extra headers for app attribution (optional)
        if self.provider == "openrouter":
            self.headers["HTTP-Referer"] = getattr(
                settings, "APP_URL", "https://contentforge-ai.onrender.com"
            )

        logger.info(
            "LLMService initialized: provider=%s, model=%s, base_url=%s",
            self.provider,
            self.model,
            self.base_url,
        )

    # ------------------------------------------------------------------
    # Core generation method
    # ------------------------------------------------------------------

    async def generate_content(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate content using the configured LLM provider."""
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]

    # ------------------------------------------------------------------
    # Health check helper
    # ------------------------------------------------------------------

    async def check_health(self) -> Dict[str, Any]:
        """Check connectivity to the LLM provider's models endpoint.

        Returns a dict with status, response_time_ms, and details.
        """
        import time as _time

        result: Dict[str, Any] = {
            "provider": self.provider,
            "model": self.model,
            "status": "unknown",
        }
        try:
            start = _time.time()
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    self._models_url,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
            elapsed_ms = round((_time.time() - start) * 1000, 2)
            result["response_time_ms"] = elapsed_ms

            if resp.status_code == 200:
                result["status"] = "healthy"
                result["message"] = f"{self.provider} API accessible"
            else:
                result["status"] = "unhealthy"
                result["message"] = (
                    f"{self.provider} API returned status {resp.status_code}"
                )
                result["status_code"] = resp.status_code
        except Exception as exc:
            result["status"] = "unhealthy"
            result["message"] = f"{self.provider} API check failed: {exc}"

        return result

    # ------------------------------------------------------------------
    # Content generation methods (business logic — same as before)
    # ------------------------------------------------------------------

    async def generate_social_posts(
        self,
        content: str,
        platform: str,
        count: int = 3,
    ) -> List[str]:
        """Generate social media posts from content."""
        system_prompt = f"""You are a social media expert. Generate {count} engaging {platform} posts from the provided content.
        Each post should be optimized for {platform}'s format and best practices.
        Make them catchy, use relevant hashtags, and include a call-to-action when appropriate."""

        prompt = f"""Original content:
{content}

Generate {count} different {platform} posts from this content. Each should be unique and engaging."""

        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=1500,
        )

        posts = [post.strip() for post in result.split("\n\n") if post.strip()]
        return posts[:count]

    async def generate_thread(
        self,
        content: str,
        platform: str = "twitter",
    ) -> List[str]:
        """Generate a thread from content."""
        system_prompt = f"""You are an expert at creating viral {platform} threads.
        Break down the content into a compelling thread format.
        Each post should connect to the next.
        Hook readers in the first post, provide value in the middle, and end with a strong CTA.
        Number each post (1/, 2/, etc.)."""

        prompt = f"""Create a viral {platform} thread from this content:

{content}

Make it 5-10 posts long. Each post should be under 280 characters."""

        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=2000,
        )

        posts = []
        for line in result.split("\n"):
            line = line.strip()
            if line and (
                line.startswith(
                    ("1/", "2/", "3/", "4/", "5/", "6/", "7/", "8/", "9/", "10/")
                )
            ):
                posts.append(line[2:].strip())
        return posts

    async def generate_newsletter(
        self,
        content: str,
        subject_line: Optional[str] = None,
    ) -> Dict[str, str]:
        """Generate a newsletter from content."""
        system_prompt = """You are an expert email copywriter. Create a compelling newsletter from the content.
        Include:
        1. An attention-grabbing subject line
        2. A warm, conversational introduction
        3. The main content formatted for easy reading
        4. A clear call-to-action
        5. A friendly sign-off

        Format the output clearly with sections."""

        prompt = f"""Create a newsletter from this content:

{content}

{f'Suggested subject: {subject_line}' if subject_line else ''}

Format with clear sections: Subject, Introduction, Body, CTA, Sign-off."""

        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2500,
        )

        return {"newsletter": result}

    async def generate_short_video_script(
        self,
        content: str,
    ) -> Dict[str, Any]:
        """Generate a short video script (for TikTok/Reels/Shorts)."""
        system_prompt = """You are a viral video script writer. Create a script for a 30-60 second short-form video.
        Include:
        1. A HOOK (first 3 seconds that stop the scroll)
        2. Main content (fast-paced, valuable)
        3. Call-to-action
        4. Suggested visual cues

        Format for easy reading during recording."""

        prompt = f"""Create a viral short video script from this content:

{content}

Script should be 30-60 seconds when read aloud. Include hook, content, CTA, and visual cues."""

        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8,
            max_tokens=1500,
        )

        return {"script": result}

    # ===== SMART CONTENT EDITOR METHODS =====

    async def rewrite_content(
        self,
        content: str,
        tone: str = "professional",
        style: str = "neutral",
    ) -> Tuple[str, int]:
        """Rewrite content with different tone and style."""
        tone_descriptions = {
            "casual": "relaxed, conversational, using everyday language",
            "professional": "business-appropriate, clear, and authoritative",
            "witty": "clever, humorous, with wordplay and light sarcasm",
            "formal": "academic, sophisticated vocabulary, no contractions",
            "friendly": "warm, approachable, supportive tone",
            "authoritative": "confident, expert-driven, decisive statements",
            "enthusiastic": "excited, energetic, passionate delivery",
            "empathetic": "understanding, compassionate, emotionally resonant",
        }

        style_descriptions = {
            "neutral": "balanced and objective, no strong persuasion",
            "persuasive": "convincing, compelling arguments, action-oriented",
            "informative": "educational, factual, detailed explanations",
            "storytelling": "narrative-driven, engaging, with a clear arc",
            "concise": "brief, to-the-point, no fluff",
            "descriptive": "vivid imagery, sensory details, immersive",
        }

        tone_desc = tone_descriptions.get(tone, tone_descriptions["professional"])
        style_desc = style_descriptions.get(style, style_descriptions["neutral"])

        system_prompt = f"""You are an expert content editor. Rewrite the provided content with the following specifications:
- Tone: {tone_desc}
- Style: {style_desc}

Maintain the core meaning and key information while adapting the presentation."""

        prompt = f"""Rewrite the following content:

ORIGINAL CONTENT:
{content}

REQUIREMENTS:
- Tone: {tone} ({tone_desc})
- Style: {style} ({style_desc})
- Preserve all key information
- Ensure natural flow and readability

Provide only the rewritten content without explanations."""

        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=3000,
        )

        estimated_tokens = len(content.split()) + len(result.split())
        return result.strip(), estimated_tokens

    async def expand_content(
        self,
        content: str,
        target_length: int = 2,
        focus_areas: List[str] = None,
    ) -> Tuple[str, int]:
        """Expand content with more detail."""
        focus_areas = focus_areas or []

        focus_instruction = ""
        if focus_areas:
            focus_instruction = (
                f"\n\nFocus on expanding these areas: {', '.join(focus_areas)}"
            )

        system_prompt = f"""You are an expert content expander. Take the provided content and expand it to approximately {target_length}x its original length.
Add depth, detail, examples, and elaboration while maintaining coherence and quality."""

        prompt = f"""Expand the following content to approximately {target_length}x its length:

ORIGINAL CONTENT:
{content}

REQUIREMENTS:
- Expand to roughly {target_length}x the original length
- Add relevant details, examples, and elaboration
- Maintain the original structure where appropriate
- Ensure the expanded content flows naturally{focus_instruction}

Provide only the expanded content without explanations."""

        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=4000,
        )

        estimated_tokens = len(content.split()) + len(result.split())
        return result.strip(), estimated_tokens

    async def condense_content(
        self,
        content: str,
        target_percentage: int = 50,
        preserve_key_points: bool = True,
    ) -> Tuple[str, int]:
        """Condense content to be shorter."""
        preserve_instruction = (
            "Ensure all key points and main ideas are preserved."
            if preserve_key_points
            else "Condense as needed, prioritizing brevity."
        )

        system_prompt = f"""You are an expert content condenser. Summarize and condense the provided content to approximately {target_percentage}% of its original length.
{preserve_instruction} Maintain clarity and coherence."""

        prompt = f"""Condense the following content to approximately {target_percentage}% of its length:

ORIGINAL CONTENT:
{content}

REQUIREMENTS:
- Reduce to roughly {target_percentage}% of original length
- {preserve_instruction}
- Remove redundant information and wordiness
- Keep sentences clear and impactful
- Maintain the original tone and key messages

Provide only the condensed content without explanations."""

        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.6,
            max_tokens=2500,
        )

        estimated_tokens = len(content.split()) + len(result.split())
        return result.strip(), estimated_tokens

    async def optimize_content(
        self,
        content: str,
        platform: str,
        include_hashtags: bool = True,
        include_cta: bool = True,
    ) -> Dict[str, Any]:
        """Optimize content for specific platform."""
        platform_specs = {
            "twitter": {
                "max_length": 280,
                "style": "concise, punchy, hashtag-friendly",
                "best_practices": "Hook immediately, use line breaks for readability, 1-2 hashtags max",
            },
            "linkedin": {
                "max_length": 3000,
                "style": "professional, thought leadership, value-driven",
                "best_practices": "Start with a hook, use short paragraphs, include a clear takeaway",
            },
            "blog": {
                "max_length": 5000,
                "style": "informative, SEO-optimized, structured",
                "best_practices": "Use headers, bullet points, include meta description suggestions",
            },
            "newsletter": {
                "max_length": 2000,
                "style": "personal, conversational, skimmable",
                "best_practices": "Subject line suggestion, scannable sections, clear CTA",
            },
            "instagram": {
                "max_length": 2200,
                "style": "visual-friendly, engaging, community-focused",
                "best_practices": "Engaging caption, relevant hashtags, emoji usage",
            },
            "tiktok": {
                "max_length": 2200,
                "style": "trendy, authentic, quick-hitting",
                "best_practices": "Hook in first 3 seconds, trending sounds reference, punchy text",
            },
        }

        specs = platform_specs.get(platform, platform_specs["blog"])

        hashtag_instruction = (
            "Include 3-5 relevant hashtags at the end."
            if include_hashtags
            else "Do not include hashtags."
        )
        cta_instruction = (
            "Include a strong call-to-action."
            if include_cta
            else "No explicit call-to-action needed."
        )

        system_prompt = f"""You are a {platform} content optimization expert. Adapt the content for {platform}'s format and audience.
Platform style: {specs['style']}
Best practices: {specs['best_practices']}"""

        prompt = f"""Optimize this content for {platform}:

ORIGINAL CONTENT:
{content}

REQUIREMENTS:
- Platform: {platform}
- Maximum length: {specs['max_length']} characters
- Style: {specs['style']}
- Best practices: {specs['best_practices']}
- {hashtag_instruction}
- {cta_instruction}

Provide the optimized content ready to publish on {platform}."""

        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=2000,
        )

        char_count = len(result.strip())
        word_count = len(result.split())
        estimated_tokens = len(content.split()) + word_count

        return {
            "optimized_content": result.strip(),
            "platform": platform,
            "character_count": char_count,
            "word_count": word_count,
            "estimated_tokens": estimated_tokens,
        }


# Singleton instance
llm_service = LLMService()


# ---------------------------------------------------------------------------
# Per-user LLM service factory (BYOK)
# ---------------------------------------------------------------------------

async def get_user_llm_config(user_id: str) -> Optional[Dict[str, str]]:
    """Resolve a user's API key from the api_keys table.

    Returns {provider, api_key, base_url, model} or None if the user has no key.
    Results are cached for 5 minutes.
    """
    now = _time.time()
    cached = _user_key_cache.get(user_id)
    if cached and (now - cached[0]) < _USER_KEY_CACHE_TTL:
        return cached[1]

    try:
        from app.core.supabase import get_supabase_admin_client
        from app.core.encryption import decrypt as _decrypt

        admin = get_supabase_admin_client()
        result = admin.table("api_keys").select(
            "provider, encrypted_key, base_url, model, is_valid"
        ).eq("user_id", user_id).eq("is_valid", True).execute()

        if not result.data:
            _user_key_cache[user_id] = (now, None)
            return None

        # Use the first valid key (one per provider, pick the most recently validated)
        best = result.data[0]
        raw_key = _decrypt(best["encrypted_key"])

        config = {
            "provider": best["provider"],
            "api_key": raw_key,
            "base_url": best.get("base_url"),
            "model": best.get("model"),
        }
        _user_key_cache[user_id] = (now, config)
        return config
    except Exception as exc:
        logger.warning("Failed to resolve user API key for %s: %s", user_id, exc)
        return None


def invalidate_user_key_cache(user_id: str):
    """Clear cached API key for a user (call after key CRUD)."""
    _user_key_cache.pop(user_id, None)


def create_llm_service_for_user(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None,
) -> LLMService:
    """Create an LLMService instance with explicit credentials.

    Used when a user's own API key is available.
    Falls back to platform defaults for any missing parameter.
    """
    settings = get_settings()
    resolved_provider = provider or settings.AI_PROVIDER
    preset = PROVIDER_PRESETS.get(resolved_provider, {})

    resolved_api_key = api_key or settings.AI_API_KEY or ""
    resolved_base_url = base_url or preset.get("base_url", "")

    if not resolved_base_url:
        raise ValueError(
            f"No base_url for provider '{resolved_provider}'. Set AI_BASE_URL or use a known provider."
        )

    # Model: explicit > legacy GROQ_MODEL (groq only) > preset default
    groq_model = settings.GROQ_MODEL if resolved_provider == "groq" else None
    resolved_model = model or groq_model or preset.get("default_model", "")

    models_url = preset.get("models_url", f"{resolved_base_url}/models")

    headers = {
        "Authorization": f"Bearer {resolved_api_key}",
        "Content-Type": "application/json",
    }
    if resolved_provider == "openrouter":
        headers["HTTP-Referer"] = getattr(
            settings, "APP_URL", "https://contentforge-ai.onrender.com"
        )

    svc = LLMService.__new__(LLMService)
    svc.provider = resolved_provider
    svc.api_key = resolved_api_key
    svc.base_url = resolved_base_url
    svc.model = resolved_model
    svc._models_url = models_url
    svc.headers = headers

    logger.info(
        "Per-user LLMService: provider=%s, model=%s",
        resolved_provider,
        resolved_model,
    )
    return svc