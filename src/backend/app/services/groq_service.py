"""
Groq AI service for content generation.
"""
import httpx
from typing import Optional, List, Dict, Any
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


# Singleton instance
groq_service = GroqService()
