"""
Groq AI service for content generation.
"""
import httpx
from typing import Optional, List, Dict, Any, Tuple
from app.core.config import get_settings

settings = get_settings()

GROQ_API_URL = "https://api.groq.com/openai/v1"


class GroqService:
    """Service for interacting with Groq API."""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.model = settings.GROQ_MODEL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def generate_content(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str:
        """Generate content using Groq API."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{GROQ_API_URL}/chat/completions",
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
        
        # Parse the result into separate posts
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
        
        # Parse the thread
        posts = []
        for line in result.split("\n"):
            line = line.strip()
            if line and (line.startswith(("1/", "2/", "3/", "4/", "5/", "6/", "7/", "8/", "9/", "10/"))):
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
        
        # Estimate tokens used (rough approximation)
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
            focus_instruction = f"\n\nFocus on expanding these areas: {', '.join(focus_areas)}"
        
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
        preserve_instruction = "Ensure all key points and main ideas are preserved." if preserve_key_points else "Condense as needed, prioritizing brevity."
        
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
        
        hashtag_instruction = "Include 3-5 relevant hashtags at the end." if include_hashtags else "Do not include hashtags."
        cta_instruction = "Include a strong call-to-action." if include_cta else "No explicit call-to-action needed."
        
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
        
        # Calculate character count
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


    # ===== TRANSLATION METHODS =====

    async def translate_text(
        self,
        text: str,
        target_language: str,
        preserve_formatting: bool = True,
    ) -> Dict[str, Any]:
        """Translate text to target language using Groq AI.
        
        Args:
            text: The text to translate
            target_language: Target language code (e.g., 'es', 'fr', 'de')
            preserve_formatting: Whether to preserve original formatting
            
        Returns:
            Dictionary with translated_text, source_language, confidence_score, tokens_used
        """
        # Language names for better prompting
        language_names = {
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "zh-cn": "Chinese Simplified",
            "zh-tw": "Chinese Traditional",
            "ja": "Japanese",
            "ko": "Korean",
            "pt": "Portuguese",
            "it": "Italian",
            "ru": "Russian",
            "ar": "Arabic",
            "hi": "Hindi",
            "nl": "Dutch",
            "pl": "Polish",
            "tr": "Turkish",
            "vi": "Vietnamese",
            "th": "Thai",
            "sv": "Swedish",
            "da": "Danish",
            "no": "Norwegian",
            "fi": "Finnish",
            "cs": "Czech",
            "el": "Greek",
            "he": "Hebrew",
        }
        
        target_lang_name = language_names.get(target_language, target_language)
        
        formatting_instruction = """Preserve all formatting including:
- Paragraph breaks
- List structures (bullet points, numbered lists)
- Line breaks
- Markdown formatting if present""" if preserve_formatting else "Translate the content naturally, adjusting formatting as needed."
        
        system_prompt = f"""You are an expert translator. Translate the provided text into {target_lang_name}.

Requirements:
- Provide an accurate, natural-sounding translation
- Maintain the original meaning and tone
- {formatting_instruction}
- If the text appears to already be in the target language, return it as-is
- Detect the source language automatically

Respond in this exact format:
SOURCE_LANGUAGE: [detected language code, e.g., 'en', 'es', 'fr']
CONFIDENCE: [confidence score 0.0-1.0]
TRANSLATION:
[translated text here]"""
        
        prompt = f"""Translate the following text to {target_lang_name}:

{text}"""
        
        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.3,  # Lower temperature for more accurate translation
            max_tokens=4000,
        )
        
        # Parse the response
        source_language = "en"  # Default
        confidence_score = 0.9
        translated_text = result
        
        lines = result.strip().split("\n")
        for i, line in enumerate(lines):
            if line.startswith("SOURCE_LANGUAGE:"):
                source_language = line.split(":", 1)[1].strip().lower() or "en"
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence_score = float(line.split(":", 1)[1].strip())
                    confidence_score = max(0.0, min(1.0, confidence_score))
                except (ValueError, IndexError):
                    confidence_score = 0.9
            elif line.startswith("TRANSLATION:"):
                # Get everything after "TRANSLATION:" line
                translated_text = "\n".join(lines[i+1:]).strip()
                if not translated_text:
                    # Maybe it's on the same line
                    translated_text = line.split(":", 1)[1].strip()
                break
        
        # If we couldn't parse properly, try to use the whole result
        if not translated_text or translated_text == result:
            # Remove metadata lines if present
            translated_text = result
            for prefix in ["SOURCE_LANGUAGE:", "CONFIDENCE:", "TRANSLATION:"]:
                if prefix in translated_text:
                    parts = translated_text.split(prefix, 1)
                    if len(parts) > 1:
                        translated_text = parts[1]
            # Clean up any remaining prefixes
            for line in translated_text.split("\n"):
                if line.strip() and not line.strip().endswith(":"):
                    translated_text = "\n".join(translated_text.split("\n")[translated_text.split("\n").index(line):])
                    break
        
        # Estimate tokens used
        estimated_tokens = len(text.split()) + len(translated_text.split()) if translated_text else 0
        
        return {
            "translated_text": translated_text.strip() if translated_text else text,
            "source_language": source_language,
            "target_language": target_language,
            "confidence_score": confidence_score,
            "tokens_used": estimated_tokens,
        }
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of the given text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with detected language code and confidence
        """
        system_prompt = """You are a language detection expert. Identify the language of the provided text.

Respond in this exact format:
LANGUAGE: [ISO 639-1 language code, e.g., 'en', 'es', 'fr', 'de', 'zh-cn', 'ja', etc.]
CONFIDENCE: [confidence score 0.0-1.0]
LANGUAGE_NAME: [full language name]"""
        
        prompt = f"""Detect the language of this text:

{text[:500]}"""  # Use first 500 chars for detection
        
        result = await self.generate_content(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.2,
            max_tokens=100,
        )
        
        detected_lang = "en"
        confidence = 0.9
        
        for line in result.strip().split("\n"):
            if line.startswith("LANGUAGE:"):
                detected_lang = line.split(":", 1)[1].strip().lower() or "en"
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = float(line.split(":", 1)[1].strip())
                    confidence = max(0.0, min(1.0, confidence))
                except (ValueError, IndexError):
                    confidence = 0.9
        
        return {
            "language": detected_lang,
            "confidence": confidence,
        }


# Singleton instance
groq_service = GroqService()
