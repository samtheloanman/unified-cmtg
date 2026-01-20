"""
AI Content Generator Service

Generates localized content for mortgage program pages using LLMs (Gemini/OpenAI).
"""
import logging
import json
from typing import List, Dict, Optional
from django.conf import settings
import os

logger = logging.getLogger(__name__)

# Try importing Gemini
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Try importing OpenAI
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class AiContentGenerator:
    """
    Service to generate intros and FAQs for local program pages.
    """
    
    def __init__(self, use_openai: bool = False):
        self.use_openai = use_openai
        
        if self.use_openai:
            if not OPENAI_AVAILABLE:
                raise ImportError("openai library not installed. Run 'pip install openai'")
            api_key = getattr(settings, 'OPENAI_API_KEY', None) or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            self.openai_client = OpenAI(api_key=api_key)
        else:
            if not GEMINI_AVAILABLE:
                raise ImportError("google-genai library not installed. Run 'pip install google-genai'")
            api_key = getattr(settings, 'GOOGLE_API_KEY', None) or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            self.gemini_client = genai.Client(api_key=api_key)
            self.gemini_model = 'gemini-2.0-flash'

    def generate_local_intro(self, program_title: str, city_name: str, state: str) -> str:
        """
        Generate a compelling introduction for a local program page.
        """
        prompt = (
            f"Write a compelling, SEO-friendly 200-word introduction for a '{program_title}' "
            f"landing page specifically for borrowers in {city_name}, {state}. "
            f"Mention local real estate market context if generally known, but keep it evergreen. "
            f"Focus on the benefits of this loan program for local residents. "
            f"Do not include headers or markdown formatting, just paragraphs."
        )
        
        return self._generate_text(prompt)

    def generate_local_faqs(self, program_title: str, city_name: str, state: str) -> List[Dict[str, str]]:
        """
        Generate 5 FAQs for a local program page.
        Returns a list of dicts: [{'question': '...', 'answer': '...'}]
        """
        prompt = (
            f"Generate 5 frequently asked questions and answers about '{program_title}' "
            f"specifically for borrowers in {city_name}, {state}. "
            f"Focus on local concerns, loan limits, or state-specific regulations if applicable. "
            f"Return ONLY a valid JSON array of objects with 'question' and 'answer' keys. "
            f"Do not include any explanation or markdown formatting."
        )
        
        response_text = self._generate_text(prompt)
        return self._parse_json(response_text)

    def _generate_text(self, prompt: str) -> str:
        """Internal method to call the LLM."""
        try:
            if self.use_openai:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "You are a mortgage marketing expert copywriter."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            else:
                response = self.gemini_client.models.generate_content(
                    model=self.gemini_model,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        temperature=0.7
                    )
                )
                return response.text.strip()
                
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    def _parse_json(self, text: str) -> List[Dict[str, str]]:
        """Parse JSON from LLM response, handling potential markdown fences."""
        cleaned_text = text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
            
        try:
            data = json.loads(cleaned_text.strip())
            if not isinstance(data, list):
                # Try to extract list if wrapped in object
                if isinstance(data, dict) and 'faqs' in data:
                    return data['faqs']
                raise ValueError("Response is not a list")
            return data
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {text}")
            return []
