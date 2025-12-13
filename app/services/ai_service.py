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
- Avocation: Comprehensive inventory of non-professional interests, passions, and recreational activities. This includes hobbies, leisure activities, creative pursuits, sports, games, collections, and any activities done for enjoyment outside of work (e.g., cooking, reading, gardening, music, art, travel, etc.).
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
        # Log which service will be used
        if not self.gemini_api_key and not self.openai_api_key:
            logger.warning("⚠️ No AI API keys configured - using fallback keyword matching")
        elif self.gemini_api_key:
            logger.info("🤖 Using Gemini AI for analysis")
        elif self.openai_api_key:
            logger.info("🤖 Using OpenAI AI for analysis")
        
        if self.gemini_api_key:
            try:
                result = self._analyze_with_gemini(content, contact_name, context)
                logger.info("✅ Gemini analysis successful")
                return result
            except Exception as e:
                logger.warning(f"Gemini analysis failed: {e}, trying OpenAI fallback")
        
        if self.openai_api_key:
            try:
                result = self._analyze_with_openai(content, contact_name, context)
                logger.info("✅ OpenAI analysis successful")
                return result
            except Exception as e:
                logger.warning(f"OpenAI analysis failed: {e}, using local fallback")
        
        logger.warning("⚠️ Using fallback keyword matching (AI services unavailable)")
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

CRITICAL: UNDERSTAND HIERARCHICAL STRUCTURE
- When a header/title is followed by bullet points or a list, ALL items in that list inherit the context of the header
- Example: "Hobbies\n- Cooking\n- Doing work" means BOTH "Cooking" AND "Doing work" are hobbies (Avocation category)
- Example: "Goals\n- Learn Spanish\n- Travel to Japan" means BOTH are goals
- Example: "Interests\n- Reading\n- Music" means BOTH are interests (Avocation)
- Do NOT categorize items under a header separately - they all belong to the same category as the header

EXAMPLES FOR CLARITY:
- "Hobbies\n- Cooking\n- Doing work" → ALL should be "Avocation" (both cooking and doing work are hobbies in this context)
- "Hobbies: Cooking, Reading" → Should be categorized as "Avocation" (not "Others")
- "Likes playing guitar and painting" → Should be categorized as "Avocation"
- "Goals\n- Learn coding\n- Start business" → ALL should be "Goals"
- "Interests\n- Photography\n- Travel" → ALL should be "Avocation"

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
- **CRITICAL: Do NOT include "Others" category if ANY other category is present. "Others" should ONLY be used when the note truly does not fit into any of the main categories above.**

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
            
            # Post-process: Remove "Others" if any other category exists
            result = self._remove_others_if_other_categories_exist(result)
            
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

CRITICAL: UNDERSTAND HIERARCHICAL STRUCTURE
- When a header/title is followed by bullet points or a list, ALL items in that list inherit the context of the header
- Example: "Hobbies\n- Cooking\n- Doing work" means BOTH "Cooking" AND "Doing work" are hobbies (Avocation category)
- Example: "Goals\n- Learn Spanish\n- Travel" means BOTH are goals
- Example: "Interests\n- Reading\n- Music" means BOTH are interests (Avocation)
- Do NOT categorize items under a header separately - they all belong to the same category as the header

CRITICAL CATEGORIZATION RULE:
- **Do NOT include "Others" category if ANY other category is present. "Others" should ONLY be used when the note truly does not fit into any of the main categories above. If you categorize the note into any main category (Actionable, Goals, Social, etc.), you must NOT also include "Others".**

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
            
            # Post-process: Remove "Others" if any other category exists
            result = self._remove_others_if_other_categories_exist(result)
            
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
        
        # Check for hierarchical structure (header followed by bullets)
        lines = content.split('\n')
        header = None
        bullet_items = []
        
        # Look for header pattern (first line, possibly followed by bullets)
        if len(lines) > 0:
            first_line = lines[0].strip()
            # Check if first line looks like a header (short, no bullets, might be a category name)
            if first_line and not first_line.startswith('-') and len(first_line.split()) <= 5:
                header = first_line.lower()
                # Check if subsequent lines are bullets
                for line in lines[1:]:
                    line_stripped = line.strip()
                    if line_stripped.startswith('-') or line_stripped.startswith('•'):
                        bullet_items.append(line_stripped.lstrip('- •').strip())
        
        # If we found a header with bullets, categorize based on header
        if header and bullet_items:
            logger.info(f"Detected hierarchical structure: header='{header}', items={bullet_items}")
            
            # Combine header and all bullet items for categorization
            combined_text = f"{header} {' '.join(bullet_items)}"
            combined_lower = combined_text.lower()
            
            # Check header keywords
            if any(word in header for word in ['hobby', 'hobbies', 'interest', 'interests', 'like', 'likes', 'enjoy', 'passion']):
                # All items under "Hobbies" or "Interests" are Avocation
                all_items = f"{header}\n" + "\n".join([f"- {item}" for item in bullet_items])
                categories['Avocation'] = {'content': all_items, 'confidence': 0.7}
                logger.info(f"Fallback: Detected '{header}' header - categorizing all items as Avocation")
            elif any(word in header for word in ['goal', 'goals', 'want', 'plan', 'aspire', 'hope', 'aim']):
                all_items = f"{header}\n" + "\n".join([f"- {item}" for item in bullet_items])
                categories['Goals'] = {'content': all_items, 'confidence': 0.7}
                logger.info(f"Fallback: Detected '{header}' header - categorizing all items as Goals")
            elif any(word in header for word in ['task', 'todo', 'remind', 'action', 'follow']):
                all_items = f"{header}\n" + "\n".join([f"- {item}" for item in bullet_items])
                categories['Actionable'] = {'content': all_items, 'confidence': 0.7}
                logger.info(f"Fallback: Detected '{header}' header - categorizing all items as Actionable")
            else:
                # Header not recognized, fall through to regular keyword matching
                content_lower = combined_lower
        
        # Regular keyword matching (if no hierarchical structure detected or header not recognized)
        if not categories:
            # Check for goals
            if any(word in content_lower for word in ['goal', 'goals', 'want', 'wants', 'plan', 'plans', 'aspire', 'aspires', 'hope', 'hopes', 'aim', 'aims', 'objective', 'objectives']):
                categories['Goals'] = {'content': content[:200], 'confidence': 0.5}
            
            # Check for actionable items
            if any(word in content_lower for word in ['task', 'tasks', 'todo', 'todos', 'remind', 'reminder', 'follow', 'follow-up', 'call', 'meet', 'meeting', 'schedule']):
                categories['Actionable'] = {'content': content[:200], 'confidence': 0.5}
            
            # Check for interests/hobbies (Avocation) - IMPROVED KEYWORD MATCHING
            avocation_keywords = [
                'hobby', 'hobbies', 'interest', 'interests', 'interested', 'like', 'likes', 'love', 'loves', 
                'enjoy', 'enjoys', 'passion', 'passions', 'favorite', 'favourite', 'favorites', 'favourites',
                'cooking', 'baking', 'reading', 'writing', 'music', 'art', 'painting', 'drawing', 'photography',
                'gardening', 'travel', 'sports', 'fitness', 'exercise', 'gaming', 'games', 'collecting', 'collection',
                'craft', 'crafts', 'sewing', 'knitting', 'woodworking', 'dancing', 'singing', 'playing', 'instrument',
                'recreational', 'leisure', 'pastime', 'pastimes', 'activity', 'activities'
            ]
            if any(word in content_lower for word in avocation_keywords):
                categories['Avocation'] = {'content': content[:200], 'confidence': 0.6}
                logger.info(f"Fallback detected Avocation keywords in: {content[:50]}...")
        
        if not categories:
            categories['Others'] = {'content': content[:200], 'confidence': 0.3}
            logger.info("Fallback: No specific categories detected, using 'Others'")
        
        result = {'categories': categories}
        # Post-process: Remove "Others" if any other category exists
        result = self._remove_others_if_other_categories_exist(result)
        return result
    
    def _remove_others_if_other_categories_exist(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Remove 'Others' category if any other category exists"""
        if 'categories' not in result:
            return result
        
        categories = result['categories']
        
        # Check if "Others" exists and if there are other categories
        if 'Others' in categories:
            other_categories = [k for k in categories.keys() if k != 'Others']
            if other_categories:
                # Remove "Others" since other categories exist
                del categories['Others']
                logger.debug(f"Removed 'Others' category because other categories exist: {other_categories}")
        
        return result

