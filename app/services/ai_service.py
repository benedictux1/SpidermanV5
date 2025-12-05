"""
AI Service
Unified AI analysis service with Gemini (preferred) and OpenAI fallback
"""

import os
import json
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

CATEGORY_DEFINITIONS = """
- Actionable: Immediate tasks, follow-ups, reminders, requests, or discussion topics requiring attention within days or weeks.
- Goals: Clearly defined aspirations and objectives across all life domains, including short-term targets (3-12 months), medium-term goals (1-5 years), and long-term visions (5+ years).
- Relationship_Strategy: Structured approaches to nurturing, deepening, or improving your relationship with specific tactics for connection and support.
- Social: Comprehensive mapping of their social ecosystem including family dynamics, friendship networks, romantic relationships, professional connections, community involvement.
- Professional_Background: Detailed career history and occupational profile including employment timeline, educational credentials, skill inventory, achievement record.
- Financial_Situation: Comprehensive portrait of their economic circumstances, money management approach, and financial outlook.
- Wellbeing: Holistic health status encompassing physical, mental, emotional, and spiritual dimensions.
- Avocation: Comprehensive inventory of non-professional interests, passions, and recreational activities.
- Environment_And_Lifestyle: Detailed portrait of their daily living context and routine patterns.
- Psychology_And_Values: In-depth profile of their mental frameworks, belief systems, and guiding principles.
- Communication_Style: Comprehensive analysis of their interpersonal communication patterns and preferences across all contexts.
- Challenges_And_Development: Nuanced exploration of their struggles, growth areas, and evolution across personal and professional domains.
- Deeper_Insights: Profound observations about their core essence, philosophical outlook, and unique qualities that transcend conventional categorization.
- Admin_matters: Administrative details including important dates, birthdays, anniversaries, and other key information to track.
- Others: Any other important information that doesn't fit into the categories above.
"""


class AIService:
    """AI service for note analysis with Gemini and OpenAI support"""
    
    def __init__(self):
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.gemini_model = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')
        
    def analyze_note(self, content: str, contact_name: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze note and extract structured categories"""
        if self.gemini_api_key:
            try:
                return self._analyze_with_gemini(content, contact_name, context)
            except Exception as e:
                logger.warning(f"Gemini analysis failed: {e}, trying OpenAI fallback")
        
        if self.openai_api_key:
            try:
                return self._analyze_with_openai(content, contact_name, context)
            except Exception as e:
                logger.warning(f"OpenAI analysis failed: {e}, using local fallback")
        
        return self._fallback_analysis(content, contact_name)
    
    def _analyze_with_gemini(self, content: str, contact_name: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze note using Google Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel(self.gemini_model)
            
            context_section = ""
            if context and context != "No relevant history found.":
                context_section = f"""
**Retrieved Relevant History:**
{context}

Use the retrieved history to maintain consistency and build upon existing knowledge.

"""
            
            prompt = f"""Analyze this note about {contact_name} and extract structured information.

{context_section}**New Note to Analyze:**
{content}

Categorize the content into these categories (only include if relevant):

CATEGORY_DEFINITIONS:
{CATEGORY_DEFINITIONS}

Return a JSON response with this structure:
{{
    "categories": {{
        "Actionable": {{"content": "specific factual information extracted", "confidence": 0.85}},
        "Goals": {{"content": "specific factual information extracted", "confidence": 0.80}}
    }}
}}

IMPORTANT:
- Only include categories that have relevant content from the note
- Extract specific, factual information - not interpretations
- Confidence should be between 0.0 and 1.0 based on clarity of information
- Be precise and concise in your extraction
- PRESERVE FORMATTING: Maintain the original structure, bullet points, line breaks, and organization from the input text
- Use markdown formatting (e.g., `- ` for bullet points, `**text**` for bold, line breaks with `\n`) to preserve the visual structure
- If the input has categories, sections, or lists, maintain that hierarchy in the extracted content

NEGATIVE CONSTRAINTS (What NOT to do):
- Do NOT infer feelings, emotions, or internal states not explicitly stated
- Do NOT add information that is not present in the note text
- Do NOT make assumptions about relationships beyond what is stated
- Do NOT extrapolate future plans or intentions unless explicitly mentioned
- Do NOT categorize information into multiple categories if it clearly belongs to one
- Do NOT include generic or vague statements that don't add value
- Do NOT flatten structured content into a single paragraph - preserve lists, sections, and formatting

Return ONLY the JSON response."""
            
            max_retries = 3
            retry_delay = 2
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(prompt)
                    break
                except Exception as e:
                    if "quota" in str(e).lower() or "429" in str(e) or "ResourceExhausted" in str(type(e).__name__):
                        if attempt < max_retries - 1:
                            logger.warning(f"Gemini API rate limit hit, retrying in {retry_delay}s")
                            time.sleep(retry_delay)
                            retry_delay *= 2
                            continue
                        else:
                            raise Exception(f"Gemini API rate limit exceeded")
                    else:
                        raise
            
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.startswith('```'):
                response_text = response_text[3:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            result = json.loads(response_text.strip())
            if 'categories' not in result:
                result = {'categories': result}
            
            logger.info(f"Gemini analysis completed for {contact_name}")
            return result
            
        except Exception as e:
            logger.error(f"Gemini analysis error: {e}")
            raise
    
    def _analyze_with_openai(self, content: str, contact_name: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Analyze note using OpenAI"""
        try:
            import openai
            openai.api_key = self.openai_api_key
            
            context_section = ""
            if context and context != "No relevant history found.":
                context_section = f"**Retrieved Relevant History:**\n{context}\n\nUse the retrieved history to maintain consistency.\n\n"
            
            system_prompt = f"""You are an AI assistant that analyzes personal notes and extracts structured information into specific categories.

Available categories:
{CATEGORY_DEFINITIONS}

Return ONLY a JSON object with this structure:
{{
    "categories": {{
        "category_name": {{"content": "specific factual information", "confidence": 0.85}}
    }}
}}

IMPORTANT FORMATTING RULES:
- PRESERVE FORMATTING: Maintain the original structure, bullet points, line breaks, and organization from the input text
- Use markdown formatting (e.g., `- ` for bullet points, `**text**` for bold, line breaks with `\n`) to preserve the visual structure
- If the input has categories, sections, or lists, maintain that hierarchy in the extracted content
- Do NOT flatten structured content into a single paragraph - preserve lists, sections, and formatting

Only include categories with relevant content. Be factual and precise."""
            
            user_prompt = f"""{context_section}Analyze this note about {contact_name} and extract structured information:

{content}

Return ONLY the JSON response."""
            
            try:
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3
                )
                result_text = response.choices[0].message.content
            except:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3
                )
                result_text = response.choices[0].message.content
            
            result_text = result_text.strip()
            if result_text.startswith('```json'):
                result_text = result_text[7:]
            if result_text.startswith('```'):
                result_text = result_text[3:]
            if result_text.endswith('```'):
                result_text = result_text[:-3]
            
            result = json.loads(result_text.strip())
            if 'categories' not in result:
                result = {'categories': result}
            
            logger.info(f"OpenAI analysis completed for {contact_name}")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            raise
    
    def _fallback_analysis(self, content: str, contact_name: str) -> Dict[str, Any]:
        """Fallback analysis when AI services are unavailable"""
        logger.info("Using fallback analysis - AI services unavailable")
        content_lower = content.lower()
        categories = {}
        
        if any(word in content_lower for word in ['goal', 'want', 'plan', 'aspire', 'hope', 'aim']):
            categories['Goals'] = {'content': content[:200], 'confidence': 0.5}
        
        if any(word in content_lower for word in ['task', 'todo', 'remind', 'follow', 'call', 'meet']):
            categories['Actionable'] = {'content': content[:200], 'confidence': 0.5}
        
        # Check for interests/hobbies (Avocation)
        if any(word in content_lower for word in ['like', 'likes', 'love', 'loves', 'enjoy', 'enjoys', 'hobby', 'interest', 'interested', 'passion', 'favorite', 'favourite']):
            categories['Avocation'] = {'content': content[:200], 'confidence': 0.6}
        
        if not categories:
            categories['Others'] = {'content': content[:200], 'confidence': 0.3}
        
        return {'categories': categories}

