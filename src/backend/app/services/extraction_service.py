"""
Content extraction service.
"""
import httpx
from typing import Optional
from bs4 import BeautifulSoup
import re


class ContentExtractionService:
    """Service for extracting content from various sources."""
    
    async def extract_from_url(self, url: str) -> Optional[str]:
        """Extract article content from a URL."""
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                }
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
                    script.decompose()
                
                # Try to find the main article content
                # Common article containers
                article = soup.find('article')
                if article:
                    text = article.get_text()
                else:
                    # Try main content areas
                    main = soup.find('main') or soup.find('div', class_=re.compile('content|article|post|entry'))
                    if main:
                        text = main.get_text()
                    else:
                        # Fallback to body
                        text = soup.get_text()
                
                # Clean up the text
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text[:50000]  # Limit to 50k characters
                
        except Exception as e:
            print(f"Error extracting content from URL: {e}")
            return None
    
    async def extract_from_youtube(self, video_id: str) -> Optional[str]:
        """Extract transcript from YouTube video."""
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            
            transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
            transcript = ' '.join([item['text'] for item in transcript_list])
            
            return transcript[:50000]
            
        except Exception as e:
            print(f"Error extracting YouTube transcript: {e}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        
        return text.strip()


# Singleton instance
content_extraction_service = ContentExtractionService()
