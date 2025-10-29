"""
Author Voice Post-Processor

A discrete, reusable component that enhances text with author voice markers.
Completely decoupled from content generation - operates purely on text + author.

Usage:
    from voice.post_processor import VoicePostProcessor
    
    processor = VoicePostProcessor(api_client)
    
    enhanced_text = processor.enhance(
        text="Original text here",
        author={
            'name': 'Todd Dunning',
            'country': 'United States'
        }
    )
"""

from typing import Dict
import logging
from voice.orchestrator import VoiceOrchestrator

logger = logging.getLogger(__name__)


class VoicePostProcessor:
    """
    Discrete post-processor for enhancing text with author voice markers.
    
    Design Philosophy:
    - Single Responsibility: Only voice enhancement, nothing else
    - Minimal Interface: text + author → enhanced_text
    - No Dependencies: Doesn't know about materials, FAQs, captions, etc.
    - Reusable: Works with any text from any component
    - Configurable: All behavior controlled by caller
    """
    
    def __init__(self, api_client, temperature: float = 0.4):
        """
        Initialize voice post-processor.
        
        Args:
            api_client: API client for text generation (required)
            temperature: Generation temperature (default 0.4 for controlled enhancement)
        """
        if not api_client:
            raise ValueError("API client is required for voice enhancement")
        
        self.api_client = api_client
        self.temperature = temperature
        
    def enhance(
        self,
        text: str,
        author: Dict[str, str],
        min_markers: int = 2,
        max_markers: int = 3,
        preserve_length: bool = True,
        length_tolerance: int = 5,
        voice_intensity: int = 3
    ) -> str:
        """
        Enhance text with author's voice markers.
        
        Args:
            text: Original text to enhance
            author: Author dictionary with 'name' and 'country' keys
            min_markers: Minimum voice markers to inject (default 2)
            max_markers: Maximum voice markers to inject (default 3)
            preserve_length: Whether to maintain similar word count (default True)
            length_tolerance: Word count tolerance in words (default ±5)
            voice_intensity: Author voice intensity level 1-5 (default 3)
                1 = Minimal voice markers, very subtle
                2 = Light voice presence, natural integration
                3 = Moderate voice, balanced authenticity
                4 = Strong voice, distinctive character
                5 = Maximum voice, highly characteristic
            
        Returns:
            Enhanced text with voice markers, or original if enhancement fails
        """
        # Validate inputs
        if not text or not text.strip():
            logger.warning("Empty text provided - returning unchanged")
            return text
            
        if not author or 'country' not in author:
            logger.warning("Invalid author object - returning text unchanged")
            return text
        
        author_name = author.get('name', 'Unknown')
        author_country = author.get('country', 'Unknown')
        
        # Initialize voice orchestrator for this country
        try:
            voice = VoiceOrchestrator(country=author_country)
        except Exception as e:
            logger.error(f"Failed to initialize VoiceOrchestrator for {author_country}: {e}")
            return text
        
        # Get voice indicators for this country
        all_indicators = voice.get_voice_indicators_all_countries()
        # Use the normalized country name from orchestrator (e.g., "usa" -> "united_states" -> "UNITED_STATES")
        country_key = voice.country.upper()
        voice_indicators = all_indicators.get(country_key, [])
        
        if not voice_indicators:
            logger.warning(f"No voice indicators found for {author_country} - returning text unchanged")
            return text
        
        # Check existing voice markers
        text_lower = text.lower()
        found_markers = [ind for ind in voice_indicators if ind in text_lower]
        
        if len(found_markers) >= min_markers:
            logger.info(f"✅ Text already has {len(found_markers)} voice markers - skipping enhancement")
            return text
        
        # Build enhancement prompt
        word_count = len(text.split())
        
        # Define voice intensity guidance
        intensity_guidance = {
            1: "Inject voice markers VERY SUBTLY - barely noticeable, natural integration only",
            2: "Use voice markers LIGHTLY - natural and understated, keep professional tone",
            3: "Apply MODERATE voice presence - balanced authenticity without overwhelming content",
            4: "Apply STRONG voice character - distinctive and recognizable author presence",
            5: "Apply MAXIMUM voice intensity - highly characteristic, unmistakable author signature"
        }
        
        voice_guidance = intensity_guidance.get(voice_intensity, intensity_guidance[3])
        
        prompt = f"""You are {author_name} from {author_country}, enhancing a technical text to better reflect your authentic voice.

ORIGINAL TEXT:
{text}

TASK: Rewrite this text to include {min_markers}-{max_markers} of YOUR characteristic linguistic markers.

YOUR VOICE MARKERS ({author_country}): {', '.join(voice_indicators[:10])}

VOICE INTENSITY LEVEL {voice_intensity}/5:
{voice_guidance}

🚫 CRITICAL REPETITION RULES:
1. **AVOID OVERUSING** any single voice marker - use each marker at most ONCE
2. **VARY YOUR PHRASING** - don't repeat the same phrases or sentence structures
3. **DISTRIBUTE MARKERS** naturally throughout the text, not clustered
4. **LIMIT MARKER FREQUENCY** - if text has 7+ items, a marker appearing in 60%+ is excessive
5. **PRIORITIZE VARIATION** over voice intensity - better to use fewer markers with variety

REQUIREMENTS:
1. {"Maintain similar length (" + str(word_count) + " words ±" + str(length_tolerance) + ")" if preserve_length else "Adjust length as needed"}
2. Naturally incorporate {min_markers}-{max_markers} voice markers from your list (USE EACH ONLY ONCE)
3. **ANSWER IN ENGLISH ONLY** - regardless of your country
4. Maintain the same technical depth and accuracy as the original
5. **VARY your sentence openings and structures** for uniqueness

Write the enhanced text now:"""
        
        system_prompt = f"You are {author_name}, a technical expert from {author_country}. Enhance text to reflect your authentic voice. Always write in English."
        
        try:
            # Calculate max_tokens based on text length
            max_tokens = int(word_count * 2) if preserve_length else int(word_count * 3)
            
            # Make API call
            response = self.api_client.generate_simple(
                prompt,
                system_prompt=system_prompt,
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            
            if not response.success:
                logger.warning(f"Voice enhancement API call failed: {response.error}")
                return text
            
            enhanced = response.content.strip()
            
            # Remove "ENHANCED TEXT" prefix if present (artifact from prompt)
            # Handle various formats: with/without newlines, different spacing
            import re
            enhanced = re.sub(
                r'^ENHANCED TEXT\s*\(incorporating your [^)]+\)\s*:?\s*\n?\s*',
                '',
                enhanced,
                flags=re.IGNORECASE
            ).strip()
            
            # Remove leading slashes and extra line breaks
            enhanced = re.sub(r'^\s*/+\s*', '', enhanced)  # Remove leading slashes
            enhanced = re.sub(r'\n{3,}', '\n\n', enhanced)  # Normalize multiple line breaks to max 2
            enhanced = enhanced.strip()
            
            # Verify enhancement actually added voice markers
            enhanced_lower = enhanced.lower()
            new_markers = [ind for ind in voice_indicators if ind in enhanced_lower]
            
            if len(new_markers) > len(found_markers):
                logger.info(f"✅ Voice enhanced: {len(found_markers)} → {len(new_markers)} markers")
                return enhanced
            else:
                logger.warning("⚠️  Enhancement didn't add markers - keeping original")
                return text
                
        except Exception as e:
            logger.warning(f"Voice enhancement error: {e} - keeping original")
            return text
    
    def get_voice_score(self, text: str, author: Dict[str, str]) -> Dict:
        """
        Analyze text for voice marker presence.
        
        Args:
            text: Text to analyze
            author: Author dictionary with 'country' key
            
        Returns:
            Dictionary with marker analysis:
            {
                'marker_count': int,
                'markers_found': [str],
                'country': str,
                'score': float (0-100)
            }
        """
        if not text or not author or 'country' not in author:
            return {
                'marker_count': 0,
                'markers_found': [],
                'country': 'Unknown',
                'score': 0.0
            }
        
        author_country = author.get('country', 'Unknown')
        
        try:
            voice = VoiceOrchestrator(country=author_country)
            all_indicators = voice.get_voice_indicators_all_countries()
            country_key = author_country.upper()
            voice_indicators = all_indicators.get(country_key, [])
            
            text_lower = text.lower()
            found_markers = [ind for ind in voice_indicators if ind in text_lower]
            
            # Calculate score (0-100)
            # 2+ markers = good (70+), 3+ = excellent (85+), 4+ = outstanding (95+)
            marker_count = len(found_markers)
            if marker_count == 0:
                score = 0.0
            elif marker_count == 1:
                score = 50.0
            elif marker_count == 2:
                score = 75.0
            elif marker_count == 3:
                score = 85.0
            elif marker_count == 4:
                score = 95.0
            else:
                score = 100.0
            
            return {
                'marker_count': marker_count,
                'markers_found': found_markers,
                'country': author_country,
                'score': score
            }
            
        except Exception as e:
            logger.warning(f"Voice score analysis error: {e}")
            return {
                'marker_count': 0,
                'markers_found': [],
                'country': author_country,
                'score': 0.0
            }
    
    def enhance_batch(
        self,
        faq_items: list,
        author: Dict[str, str],
        marker_distribution: str = 'varied',
        preserve_length: bool = True,
        length_tolerance: int = 5,
        voice_intensity: int = 2
    ) -> list:
        """
        Enhance multiple FAQ answers with distributed voice markers.
        
        This method enhances ALL answers in a single API call with global context,
        preventing marker repetition across answers.
        
        Args:
            faq_items: List of FAQ dicts with 'question' and 'answer' keys
            author: Author dictionary with 'name' and 'country' keys
            marker_distribution: Distribution strategy (default 'varied')
                - 'varied': Different markers per answer (recommended)
                - 'balanced': Each marker used approximately once
                - 'sparse': Some answers get no markers (max variation)
            preserve_length: Maintain similar word count per answer
            length_tolerance: Word count tolerance in words (default ±5)
            voice_intensity: Author voice intensity level 1-5 (default 2)
        
        Returns:
            Enhanced FAQ items with distributed voice markers
        """
        # Validate inputs
        if not faq_items:
            logger.warning("Empty FAQ items list - returning unchanged")
            return faq_items
        
        if not author or 'country' not in author:
            logger.warning("Invalid author object - returning FAQ items unchanged")
            return faq_items
        
        author_name = author.get('name', 'Unknown')
        author_country = author.get('country', 'Unknown')
        
        # Initialize voice orchestrator
        try:
            voice = VoiceOrchestrator(country=author_country)
        except Exception as e:
            logger.error(f"Failed to initialize VoiceOrchestrator for {author_country}: {e}")
            return faq_items
        
        # Get voice indicators for this country
        all_indicators = voice.get_voice_indicators_all_countries()
        country_key = voice.country.upper()
        voice_indicators = all_indicators.get(country_key, [])
        
        if not voice_indicators:
            logger.warning(f"No voice indicators found for {author_country} - returning unchanged")
            return faq_items
        
        # Build batch prompt
        num_answers = len(faq_items)
        num_markers = len(voice_indicators[:10])  # Use top 10 markers
        
        # Format FAQ items for prompt
        faq_text = ""
        for i, item in enumerate(faq_items, 1):
            faq_text += f"\n{i}. Q: {item['question']}\n"
            faq_text += f"   A: {item['answer']}\n"
        
        # Define intensity guidance
        intensity_guidance = {
            1: "MINIMAL voice markers - barely noticeable, use sparingly",
            2: "LIGHT voice presence - natural and understated",
            3: "MODERATE voice - balanced authenticity",
            4: "STRONG voice - distinctive character",
            5: "MAXIMUM voice - highly characteristic"
        }
        
        voice_guidance = intensity_guidance.get(voice_intensity, intensity_guidance[2])
        
        prompt = f"""You are {author_name} from {author_country}, enhancing {num_answers} FAQ answers with your voice.

YOUR VOICE MARKERS ({author_country}): {', '.join(voice_indicators[:10])}

VOICE INTENSITY LEVEL {voice_intensity}/5:
{voice_guidance}

🚫 CRITICAL DISTRIBUTION RULES (MUST FOLLOW):
1. **USE EACH MARKER AT MOST ONCE** across all {num_answers} answers
2. **DISTRIBUTE MARKERS** - spread them across different answers, not clustered
3. **VARY YOUR PHRASING** - don't repeat sentence structures
4. **AIM FOR BALANCE** - with {num_answers} answers and {num_markers} markers, use each marker 0-1 times
5. **SOME ANSWERS WITHOUT MARKERS** - it's OK if 2-3 answers have zero markers for variety
6. **AVOID REPETITION** - if a marker appears in 60%+ of answers, that's EXCESSIVE

DISTRIBUTION STRATEGY: {marker_distribution}

REQUIREMENTS:
1. {"Maintain similar length per answer (±" + str(length_tolerance) + " words)" if preserve_length else "Adjust length as needed"}
2. **ANSWER IN ENGLISH ONLY** - regardless of your country
3. Maintain technical depth and accuracy
4. Return answers in the EXACT same order
5. Use JSON format with question/answer pairs

FAQ ANSWERS TO ENHANCE:
{faq_text}

Return enhanced FAQ items as JSON array with this structure:
[
  {{"question": "...", "answer": "enhanced answer here"}},
  {{"question": "...", "answer": "enhanced answer here"}},
  ...
]

Generate the enhanced FAQ array now:"""
        
        try:
            # Single API call for all answers
            logger.info(f"🎭 Batch enhancing {num_answers} FAQ answers with {author_country} voice...")
            response = self.api_client.generate_simple(
                prompt,
                max_tokens=6000,  # Larger for batch
                temperature=self.temperature
            )
            
            if not response.success:
                logger.warning(f"Batch voice enhancement API call failed: {response.error}")
                return faq_items
            
            # Parse response
            import json
            import re
            
            content = response.content.strip()
            
            # Extract JSON array from response
            if '```' in content:
                json_match = re.search(r'```(?:json)?\s*(\[.*?\])\s*```', content, re.DOTALL)
                if json_match:
                    content = json_match.group(1)
            
            enhanced_items = json.loads(content)
            
            # Validate we got the right number of items
            if len(enhanced_items) != len(faq_items):
                logger.warning(f"Batch enhancement returned {len(enhanced_items)} items, expected {len(faq_items)} - using original")
                return faq_items
            
            # Verify enhancement added markers and didn't over-repeat
            all_answers_text = ' '.join([item['answer'].lower() for item in enhanced_items])
            markers_used = [m for m in voice_indicators if m in all_answers_text]
            
            # Check for over-repetition
            excessive_markers = []
            for marker in markers_used:
                marker_count = sum(1 for item in enhanced_items if marker in item['answer'].lower())
                percentage = (marker_count / num_answers) * 100
                if percentage > 60:
                    excessive_markers.append(f"{marker}({percentage:.0f}%)")
            
            if excessive_markers:
                logger.warning(f"⚠️  Excessive marker repetition detected: {', '.join(excessive_markers)}")
            
            logger.info(f"✅ Batch enhanced: {len(markers_used)} unique markers distributed across {num_answers} answers")
            if excessive_markers:
                logger.warning(f"   ⚠️  BUT {len(excessive_markers)} markers exceed 60% threshold")
            
            return enhanced_items
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse batch enhancement JSON: {e}")
            return faq_items
        except Exception as e:
            logger.error(f"Batch voice enhancement error: {e}")
            return faq_items
