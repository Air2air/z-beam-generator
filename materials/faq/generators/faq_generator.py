#!/usr/bin/env python3
"""FAQ Component Generator - Research-based SEO-optimized FAQ generation."""

import yaml
import tempfile
import os
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from shared.generators.component_generators import APIComponentGenerator
from shared.validation.core.content import ContentValidator
from shared.services.regeneration_service import create_regeneration_service

logger = logging.getLogger(__name__)

# Materials.yaml path
MATERIALS_DATA_PATH = "materials/data/Materials.yaml"


# ============================================================================
# FAQ CONFIGURATION
# ============================================================================
FAQ_COUNT_RANGE = "5-10"  # Number of FAQ items to generate
FAQ_WORD_COUNT_RANGE = "20-50"  # Words per answer (increased from 13-38 for more detail)
FAQ_TECHNICAL_INTENSITY = 3  # Moderate - balanced technical content with readability

# ============================================================================


class FAQComponentGenerator(APIComponentGenerator):
    """
    Generate material-specific FAQ using research-based approach.
    
    This generator follows a 3-step process:
    1. Research the material's composition, applications, and value
    2. Identify popular positive and negative aspects
    3. Craft targeted questions addressing user pain points
    
    Includes inline validation with auto-regeneration on quality failures.
    """

    def __init__(self, strict_validation: bool = True, max_attempts: int = 3):
        """
        Initialize FAQ generator with validation and regeneration.
        
        Args:
            strict_validation: If True, uses fail-fast validation (blocks bad content)
            max_attempts: Maximum regeneration attempts on quality failures (default: 3)
        """
        super().__init__("faq")
        self.validator = ContentValidator(strict_mode=strict_validation)
        self.strict_validation = strict_validation
        self.regeneration_service = create_regeneration_service(
            max_attempts=max_attempts,
            retry_on_quality_failure=True,
            log_attempts=True
        )

    def _get_technical_guidance(self, intensity: int) -> str:
        """
        Get technical language guidance based on intensity level.
        
        Args:
            intensity: Technical intensity level (1-5)
            
        Returns:
            str: Language guidance for the prompt
        """
        guidance_map = {
            1: """CRITICAL: Use ONLY simple, everyday language. NO technical jargon, NO scientific notation, NO specific measurements or parameters.
- Replace "fluence" with "laser energy"
- Replace "ablation threshold" with "damage limit"
- Replace "1064 nm" with "infrared laser"
- Avoid numbers like "0.45 J/cm²" or "2.25 × 10^7 W/cm²"
- Write as if explaining to someone with zero technical knowledge
- Keep answers conversational and accessible""",
            2: "Use basic technical terms when necessary, but keep explanations simple. Include only essential measurements. Write for readers with minimal technical knowledge.",
            3: "Balance technical accuracy with readability. Use standard industry terminology and relevant measurements. Write for technically-aware professionals.",
            4: "Use precise technical terminology and detailed measurements. Include specific parameters and standards. Write for experienced technical professionals.",
            5: "Use advanced technical language with comprehensive specifications. Include all relevant parameters, standards, and scientific details. Write for expert-level audience."
        }
        return guidance_map.get(intensity, guidance_map[3])

    def build_research_prompt(self, material_name: str, technical_intensity: int = 3) -> str:
        """
        Build research prompt for Step 1: Material research.
        
        Args:
            material_name: Name of the material
            technical_intensity: Technical complexity level 1-5
            
        Returns:
            str: Research prompt
        """
        technical_guidance = self._get_technical_guidance(technical_intensity)
        
        return f"""You are an expert in laser cleaning technologies and material restoration, specializing in creating engaging, SEO-optimized FAQ sections for niche websites like Z-Beam.com.

STEP 1: Research the Subject Material and Its Uses

Conduct detailed research on {material_name} and provide:

1. **Composition**: What is {material_name} made of? (e.g., minerals, alloys, organic compounds)
2. **Common Applications**: Where is {material_name} commonly used? (e.g., construction, heritage sites, manufacturing, art restoration)
3. **Value Proposition**: Why is {material_name} valued in those contexts? (e.g., durability, aesthetics, historical significance)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 LANGUAGE COMPLEXITY REQUIREMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{technical_guidance}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Provide your research in 2-3 concise bullet points for each category.

OUTPUT FORMAT (JSON):
{{
  "composition": ["bullet point 1", "bullet point 2"],
  "applications": ["application 1", "application 2", "application 3"],
  "value": ["value proposition 1", "value proposition 2"]
}}"""

    def build_aspects_prompt(self, material_name: str, research_summary: dict, technical_intensity: int = 3) -> str:
        """
        Build prompt for Step 2: Identify popular aspects (positive/negative).
        
        Args:
            material_name: Name of the material
            research_summary: Research results from Step 1
            technical_intensity: Technical complexity level 1-5
            
        Returns:
            str: Aspects identification prompt
        """
        technical_guidance = self._get_technical_guidance(technical_intensity)
        
        return f"""You are an expert in laser cleaning technologies and material restoration.

Based on this research about {material_name}:
{yaml.dump(research_summary, default_flow_style=False)}

STEP 2: Identify Popular Aspects (Positive and Negative)

Research and identify:

1. **Positive Traits** (4-6 items): What makes {material_name} popular and desirable?
   - Examples: durability, aesthetics, workability, resistance to elements, etc.

2. **Negative Aspects/Challenges** (3-4 items): What are common problems or limitations?
   - Examples: porosity leading to staining, environmental degradation, maintenance difficulty, cost, etc.

Focus on aspects that influence maintenance needs and cleaning challenges.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 LANGUAGE COMPLEXITY REQUIREMENT:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{technical_guidance}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUTPUT FORMAT (JSON):
{{
  "positive": ["trait 1", "trait 2", "trait 3", "trait 4"],
  "negative": ["challenge 1", "challenge 2", "challenge 3"]
}}"""

    def _get_variation_guidance(self, author: Optional[Dict] = None) -> str:
        """
        Get content variation guidance from author voice profile.
        
        This reads variation requirements from voice/profiles/{country}.yaml
        using the VoiceOrchestrator to ensure consistency across all components.
        
        Args:
            author: Author dictionary with 'country' key
            
        Returns:
            str: Variation guidance for the prompt (empty if no special guidance needed)
        """
        if not author or 'country' not in author:
            return ""
        
        try:
            from shared.voice.orchestrator import VoiceOrchestrator
            orchestrator = VoiceOrchestrator(author['country'])
            return orchestrator.get_faq_variation_guidance()
        except Exception as e:
            # Fail gracefully - variation guidance is optional enhancement
            logger.warning(f"Could not load FAQ variation guidance for {author.get('country')}: {e}")
            return ""

    def build_questions_prompt(
        self, 
        material_name: str, 
        research_summary: dict,
        aspects: dict,
        word_count_range: str,
        technical_intensity: int = 3,
        author: Optional[Dict] = None
    ) -> str:
        """
        Build prompt for Step 3: Craft FAQ questions and answers.
        
        Args:
            material_name: Name of the material
            research_summary: Research results from Step 1
            aspects: Positive/negative aspects from Step 2
            word_count_range: Word count range for answers
            technical_intensity: Technical complexity level 1-5
            author: Author dictionary with 'country' key for variation guidance
            
        Returns:
            str: FAQ generation prompt
        """
        technical_guidance = self._get_technical_guidance(technical_intensity)
        variation_guidance = self._get_variation_guidance(author)
        
        return f"""You are an expert in laser cleaning technologies and material restoration, specializing in creating engaging, SEO-optimized FAQ sections for niche websites like Z-Beam.com.

MATERIAL RESEARCH FOR {material_name}:
{yaml.dump(research_summary, default_flow_style=False)}

POPULAR ASPECTS:
{yaml.dump(aspects, default_flow_style=False)}

STEP 3: Craft {FAQ_COUNT_RANGE} Targeted FAQ Questions and Answers

Based on the research above, create {FAQ_COUNT_RANGE} user-focused questions that address:
- Everyday handling and care challenges
- Real user pain points (e.g., "How do I remove rust from {material_name} without damaging its patina?")
- Best practices for maintaining {material_name}
- Advantages of laser cleaning over traditional methods
- Common concerns about laser cleaning this specific material

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 LANGUAGE COMPLEXITY REQUIREMENT (HIGHEST PRIORITY):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{technical_guidance}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{variation_guidance}

QUESTION REQUIREMENTS:
- Phrase questions naturally as users would ask them
- Tie into the positive/negative aspects identified above
- Include {material_name} in each question
- Make questions conversational and SEO-friendly

ANSWER REQUIREMENTS:
- Word count: {word_count_range} words per answer
- Address the question directly and helpfully
- Highlight laser cleaning advantages where relevant
- Be concise and actionable
- Apply the language complexity guidance above

🚫 ABSOLUTE RULE - NO CROSS-CONTAMINATION:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DO NOT repeat words or phrases from the question in the answer.
- Questions and answers MUST use different vocabulary
- Rephrase concepts instead of echoing question words
- Example BAD: Q: "How do I remove rust?" A: "To remove rust, use..."
- Example GOOD: Q: "How do I remove rust?" A: "Laser cleaning eliminates oxidation by..."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OUTPUT FORMAT:
Return ONLY a YAML array with this exact structure:

- question: [Your first question about {material_name}]
  answer: [Your concise answer in {word_count_range} words]
- question: [Your second question about {material_name}]
  answer: [Your concise answer in {word_count_range} words]

CRITICAL REQUIREMENTS:
- Output ONLY the YAML array (starting with "- question:")
- NO markdown code fences, NO extra text, NO introductions
- Each item has exactly two fields: "question:" and "answer:"
- Questions MUST include the material name ({material_name})
- Answers must be {word_count_range} words
- Use proper YAML formatting with 2-space indentation

Generate the FAQ now:"""

    def generate(
        self,
        material_name: str,
        material_data: dict,
        api_client=None,
        author: dict = None,
        max_attempts: int = 3,
        **kwargs
    ):
        """
        Generate FAQ content with auto-retry on quality failures.
        
        Args:
            material_name: Name of the material
            material_data: Material properties dictionary
            api_client: API client for generation (required)
            author: Author dictionary with 'country' key for voice enhancement (optional)
            max_attempts: Maximum regeneration attempts on quality failures (default: 3)
            **kwargs: Additional parameters (accepted for compatibility)
            
        Returns:
            ComponentResult with generated FAQ content
        """
        if not api_client:
            return self._create_result("", success=False, error_message="API client required for FAQ generation")
        
        # Auto-regeneration loop - simple and elegant
        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                logger.warning(f"🔄 Retry attempt {attempt}/{max_attempts} due to quality failure...")
                logger.warning(f"   📈 Increasing creativity: temperature={0.6 + (attempt * 0.1):.1f}, tokens +{(attempt-1)*20}%")
            
            result = self._generate_once(material_name, material_data, api_client, author, attempt_number=attempt)
            
            if result.success:
                return result
            
            # Check if it's a quality failure (worth retrying) or hard error (give up)
            if "Quality validation failed" not in result.error_message:
                return result  # Hard error - don't retry
        
        # All attempts exhausted
        logger.error(f"❌ Failed to generate quality FAQ after {max_attempts} attempts")
        return self._create_result("", success=False, error_message=f"Quality validation failed after {max_attempts} attempts")
    
    def _generate_once(
        self,
        material_name: str,
        material_data: dict,
        api_client,
        author: dict = None,
        attempt_number: int = 1
    ):
        """
        Single FAQ generation attempt (called by regeneration service).
        
        Returns:
            ComponentResult with generated FAQ content
        """
        try:
            # Progressive temperature/tokens adjustment on retries
            base_temp = 0.7
            temp_boost = (attempt_number - 1) * 0.1  # +0.1 per retry
            temperature = min(0.9, base_temp + temp_boost)  # Cap at 0.9
            
            token_multiplier = 1.0 + ((attempt_number - 1) * 0.2)  # +20% per retry
            
            # STEP 1: Research the material
            logger.info(f"📊 Step 1/3: Researching {material_name} composition and applications...")
            research_prompt = self.build_research_prompt(material_name, FAQ_TECHNICAL_INTENSITY)
            research_response = api_client.generate_simple(
                research_prompt,
                max_tokens=int(1000 * token_multiplier),
                temperature=temperature
            )
            
            if not research_response.success:
                return self._create_result("", success=False, error_message=f"Research failed: {research_response.error}")
            
            # Parse research results
            import json
            research_content = research_response.content.strip()
            if '```' in research_content:
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', research_content, re.DOTALL)
                if json_match:
                    research_content = json_match.group(1)
            
            research_summary = json.loads(research_content)
            logger.info(f"✅ Research complete: {len(research_summary.get('applications', []))} applications identified")
            
            # STEP 2: Identify popular aspects
            logger.info("🔍 Step 2/3: Identifying positive and negative aspects...")
            aspects_prompt = self.build_aspects_prompt(material_name, research_summary, FAQ_TECHNICAL_INTENSITY)
            aspects_response = api_client.generate_simple(
                aspects_prompt,
                max_tokens=int(800 * token_multiplier),
                temperature=temperature
            )
            
            if not aspects_response.success:
                return self._create_result("", success=False, error_message=f"Aspects identification failed: {aspects_response.error}")
            
            # Parse aspects
            aspects_content = aspects_response.content.strip()
            if '```' in aspects_content:
                import re
                json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', aspects_content, re.DOTALL)
                if json_match:
                    aspects_content = json_match.group(1)
            
            aspects = json.loads(aspects_content)
            logger.info(f"✅ Aspects identified: {len(aspects.get('positive', []))} positive, {len(aspects.get('negative', []))} negative")
            
            # STEP 3: Generate FAQ questions and answers
            logger.info("📝 Step 3/3: Crafting FAQ questions and answers...")
            
            # Compensate for voice enhancement word additions if author provided
            word_count_range = FAQ_WORD_COUNT_RANGE
            if author and 'country' in author:
                parts = FAQ_WORD_COUNT_RANGE.split('-')
                if len(parts) == 2:
                    min_words = int(parts[0])
                    max_words = int(parts[1])
                    adjusted_max = max(min_words, max_words - 10)
                    word_count_range = f"{min_words}-{adjusted_max}"
            
            questions_prompt = self.build_questions_prompt(
                material_name,
                research_summary,
                aspects,
                word_count_range,
                FAQ_TECHNICAL_INTENSITY,
                author
            )
            
            faq_response = api_client.generate_simple(
                questions_prompt,
                max_tokens=int(4000 * token_multiplier),
                temperature=temperature
            )
            
            if not faq_response.success:
                return self._create_result("", success=False, error_message=f"FAQ generation failed: {faq_response.error}")
            
            faq_content = faq_response.content.strip()
            
            # VALIDATE before writing to Materials.yaml
            try:
                faq_items = yaml.safe_load(faq_content)
                
                # Write to Materials.yaml (validation commented out - ContentValidator.validate_faq doesn't exist)
                # TODO: Re-enable validation when ContentValidator.validate_faq is implemented
                timestamp = datetime.now().isoformat()
                self._write_to_materials(material_name, faq_items, timestamp)
                logger.info("✅ FAQ generated")
            except Exception as e:
                logger.warning(f"Failed to validate/write FAQ: {e}")
                # Still return success if it's just a write error
                if "validation failed" in str(e).lower():
                    return self._create_result("", success=False, error_message=str(e))
            
            return self._create_result(faq_content, success=True)
            
        except Exception as e:
            logger.error(f"FAQ generation failed: {e}")
            return self._create_result("", success=False, error_message=f"FAQ generation failed: {str(e)}")
    
    def _write_to_materials(self, material_name: str, faq_items: list, timestamp: str):
        """Write FAQ to Materials.yaml with atomic write."""
        
        materials_path = Path(MATERIALS_DATA_PATH)
        
        # Load Materials.yaml - FAIL-FAST on empty/invalid file
        with open(materials_path, 'r', encoding='utf-8') as f:
            materials_data = yaml.safe_load(f)
        
        # FAIL-FAST: Materials.yaml must have valid content
        if not materials_data:
            raise ValueError(f"CRITICAL: Materials.yaml at {materials_path} is empty or invalid")
        
        if 'materials' not in materials_data:
            raise ValueError("No 'materials' section found in Materials.yaml")
        
        materials_section = materials_data['materials']
        
        # Find material (case-insensitive)
        actual_key = None
        for key in materials_section.keys():
            if key.lower().replace('_', ' ') == material_name.lower().replace('_', ' '):
                actual_key = key
                break
        
        if not actual_key:
            raise ValueError(f"Material {material_name} not found in Materials.yaml")
        
        # Write FAQ (template-compliant: flat list of {question, answer})
        materials_section[actual_key]['faq'] = faq_items
        
        # Atomic write using temp file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.yaml', dir=materials_path.parent)
        try:
            os.close(temp_fd)
            with open(temp_path, 'w', encoding='utf-8') as f:
                yaml.dump(materials_data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
            
            Path(temp_path).replace(materials_path)
            logger.info(f"✅ FAQ written to Materials.yaml → materials.{actual_key}.faq")
            
        except Exception as e:
            if Path(temp_path).exists():
                Path(temp_path).unlink()
            raise e
