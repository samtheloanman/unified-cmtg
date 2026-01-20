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
            f"Return a valid JSON object with a single key 'content' containing the text."
        )
        
        response = self._generate_text(prompt)
        try:
            data = self._parse_json(response)
            return data.get('content', response)
        except Exception:
            return response

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

    def generate_program_content(self, program_title: str, program_type: str) -> Dict:
        """
        Generate full content for a ProgramPage.
        Returns a dict with keys matching ProgramPage fields.
        """
        expert_persona = self._get_expert_persona(program_title)
        
        prompt = (
            f"Act as a {expert_persona}. \n"
            f"Write comprehensive, high-compliance content for a Mortgage Loan Program page titled '{program_title}' "
            f"(Type: {program_type}).\n\n"
            f"Your output must be a valid JSON object with the following keys containing HTML (for RichText) or data:\n"
            f"1. 'mortgage_program_highlights': HTML bullet points of key features.\n"
            f"2. 'what_are': HTML definition of the program.\n"
            f"3. 'details_about_mortgage_loan_program': HTML detailed explanation.\n"
            f"4. 'benefits_of': HTML section on why a borrower would choose this.\n"
            f"5. 'requirements': HTML bulleted list of borrower/property requirements.\n"
            f"6. 'how_to_qualify_for': HTML steps to qualify.\n"
            f"7. 'why_us': HTML pitch for why choose Custom Mortgage/CMRE.\n"
            f"8. 'faqs': List of 6 objects {{'question': '...', 'answer': '...'}}.\n"
            f"9. 'seo_title': Optimized meta title.\n"
            f"10. 'seo_description': Optimized meta description.\n\n"
            f"Tone: Professional, authoritative, encouraging. Use <h2> and <h3> tags for structure in HTML fields. "
            f"Do not use markdown blocks, return raw JSON."
        )
        
        return self._parse_json(self._generate_text(prompt))

    def _get_expert_persona(self, title: str) -> str:
        """Determine the specific expert persona based on the program title."""
        t = title.lower()
        
        # Base pattern: "Senior Mortgage Copywriter with deep expertise in {Topic}"
        
        if 'sba' in t or 'business' in t:
            topic = "SBA Lending and Business Financing"
        elif 'commercial' in t or 'apartment' in t or 'retail' in t or 'industrial' in t or 'office' in t:
            topic = "Commercial Real Estate Financing"
        elif 'hotel' in t or 'gas station' in t:
            topic = "Niche Commercial Property Financing"
        elif 'construction' in t or 'land' in t:
            topic = "Construction and Land Development Loans"
        elif 'hard money' in t or 'fix and flip' in t or 'rehab' in t or 'bridge' in t:
            topic = "Private Money, Bridge, and Rehab Lending"
        elif 'nonqm' in t or 'non-qm' in t or 'dscr' in t or 'statement' in t or 'depletion' in t or 'no income' in t:
            topic = "Non-QM and Self-Employed Borrower Solutions"
        elif 'jumbo' in t:
            topic = "Luxury Home Financing and Jumbo Loans"
        elif 'fha' in t:
            topic = "FHA Lending Guidelines and First-Time Homebuyers"
        elif 'va' in t:
            topic = "VA Mortgages and Military Family Financing"
        elif 'usda' in t:
            topic = "USDA Rural Housing Loans"
        elif 'reverse' in t:
            topic = "Reverse Mortgages and Retirement Financing"
        elif 'physician' in t:
            topic = "Medical Professional Loans"
        else:
            topic = "Residential Mortgage Lending"
            
        return f"Senior Mortgage Copywriter with deep expertise in {topic}"  

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
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                return response.choices[0].message.content.strip()
            else:
                response = self.gemini_client.models.generate_content(
                    model=self.gemini_model,
                    contents=[prompt],
                    config=types.GenerateContentConfig(
                        temperature=0.7,
                        response_mime_type="application/json" 
                    )
                )
                return response.text.strip()
                
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            raise

    def _parse_json(self, text: str) -> Dict:
        """Parse JSON from LLM response."""
        cleaned_text = text.strip()
        # Remove markdown fences if present
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
            
        try:
            return json.loads(cleaned_text.strip())
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON: {text}")
            return {}
