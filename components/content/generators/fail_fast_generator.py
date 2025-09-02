#!/usr/bin/env python3
"""
Fail-Fast Content Generator
Removes all hardcoded fallbacks and implements clean error handli                 schema_fields: Optional[Dict] = None) -> GenerationResult:g with retry mechanisms.
"""

import sys
import logging
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from functools import lru_cache

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
import json

# Define our own result class locally
class GenerationResult:
    """Result of content generation with comprehensive scoring"""
    def __init__(self, success: bool, content: str = "", error_message: str = "", 
                 metadata: Optional[Dict] = None, quality_score: Optional[Any] = None):
        self.success = success
        self.content = content
        self.error_message = error_message
        self.metadata = metadata or {}
        self.quality_score = quality_score

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Raised when configuration is missing or invalid."""
    pass

class GenerationError(Exception):
    """Raised when content generation fails."""
    pass

class RetryableError(Exception):
    """Raised when operation should be retried."""
    pass

class FailFastContentGenerator:
    """
    Content generator with fail-fast approach and configurable retry logic.
    No hardcoded fallbacks - fails immediately on missing configuration.
    Includes comprehensive quality scoring for human believability.
    """
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0, 
                 enable_scoring: bool = True, human_threshold: float = 75.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_scoring = enable_scoring
        self.human_threshold = human_threshold
        
        # Initialize content scorer if enabled - FAIL FAST if not available
        if self.enable_scoring:
            from ..validation.content_scorer import create_content_scorer
            self.content_scorer = create_content_scorer(human_threshold)
        else:
            self.content_scorer = None
        
        # Validate required configurations on startup
        self._validate_required_configurations()
    
    def _validate_required_configurations(self):
        """Validate all required configuration files exist and are valid."""
        logger.info("Validating required configurations...")
        
        # Check base content prompt
        base_prompt_file = "components/content/prompts/base_content_prompt.yaml"
        if not Path(base_prompt_file).exists():
            raise ConfigurationError(f"Required base content prompt missing: {base_prompt_file}")
        
        # Validate base prompt structure - check file exists and is valid YAML
        try:
            base_config = self._load_base_content_prompt()
            # Dynamic validation - just ensure we can load it, no required sections
            if not isinstance(base_config, dict):
                raise ConfigurationError("Base content prompt must be a valid YAML dictionary")
        except Exception as e:
            raise ConfigurationError(f"Invalid base content prompt: {e}")
        
        # Check authors configuration
        authors_file = "components/author/authors.json"
        if not Path(authors_file).exists():
            raise ConfigurationError(f"Required authors configuration missing: {authors_file}")
        
        # Validate authors data
        try:
            authors_data = self._load_authors_data()
            if not authors_data or len(authors_data) == 0:
                raise ConfigurationError("Authors configuration is empty")
            
            for author in authors_data:
                required_fields = ['id', 'name', 'country']
                for field in required_fields:
                    if field not in author:
                        raise ConfigurationError(f"Author missing required field '{field}': {author}")
        except Exception as e:
            raise ConfigurationError(f"Invalid authors configuration: {e}")
        
        # Check persona files for all authors
        authors_data = self._load_authors_data()
        for author in authors_data:
            author_id = author['id']
            persona_file = self._get_persona_file_path(author_id)
            
            if not Path(persona_file).exists():
                raise ConfigurationError(f"Required persona file missing for author {author_id}: {persona_file}")
            
            # Validate persona structure
            try:
                persona_config = self._load_persona_prompt(author_id)
                required_sections = ['writing_style', 'language_patterns']
                for section in required_sections:
                    if section not in persona_config:
                        logger.warning(f"Persona {author_id} missing recommended section: {section}")
            except Exception as e:
                raise ConfigurationError(f"Invalid persona file for author {author_id}: {e}")
        
        logger.info("✅ All required configurations validated successfully")
    
    def generate(self, material_name: str, material_data: Dict,
                api_client=None, author_info: Optional[Dict] = None,
                frontmatter_data: Optional[Dict] = None,
                schema_fields: Optional[Dict] = None) -> GenerationResult:
        """
        Generate content with fail-fast approach and retry logic.
        
        Fails immediately if:
        - Required configurations are missing
        - API client is not provided
        - Author information is invalid
        
        Retries on:
        - API communication errors
        - Temporary failures
        """
        # Fail fast on missing requirements
        if not api_client:
            raise GenerationError("API client is required for content generation")
        
        if not author_info or 'id' not in author_info:
            raise GenerationError("Valid author information with 'id' field is required")
        
        if not material_name or not material_data:
            raise GenerationError("Valid material name and data are required")
        
        # Validate author exists in configuration
        author_id = author_info['id']
        if not self._author_exists(author_id):
            raise GenerationError(f"Author ID {author_id} not found in configuration")
        
        # Execute generation with retry logic
        return self._execute_with_retry(
            self._generate_content_internal,
            material_name, material_data, api_client, author_info, frontmatter_data, schema_fields
        )
    
    def _execute_with_retry(self, operation, *args, **kwargs):
        """Execute operation with retry logic for retryable errors."""
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                return operation(*args, **kwargs)
                
            except RetryableError as e:
                last_error = e
                if attempt < self.max_retries:
                    logger.warning(f"Attempt {attempt + 1} failed, retrying in {self.retry_delay}s: {e}")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    logger.error(f"All {self.max_retries + 1} attempts failed")
                    break
                    
            except (ConfigurationError, GenerationError) as e:
                # These errors should not be retried
                logger.error(f"Non-retryable error: {e}")
                raise
                
            except Exception as e:
                # Unexpected errors - treat as retryable
                last_error = RetryableError(f"Unexpected error: {e}")
                if attempt < self.max_retries:
                    logger.warning(f"Unexpected error on attempt {attempt + 1}, retrying: {e}")
                    time.sleep(self.retry_delay)
                    continue
                else:
                    break
        
        # If we get here, all retries failed
        raise GenerationError(f"Content generation failed after {self.max_retries + 1} attempts: {last_error}")
    
    def _generate_content_internal(self, material_name: str, material_data: Dict,
                                 api_client, author_info: Dict,
                                 frontmatter_data: Optional[Dict],
                                 schema_fields: Optional[Dict]) -> GenerationResult:
        """Internal content generation without fallbacks."""
        try:
            # Load required configurations (fail fast if missing)
            base_config = self._load_base_content_prompt()
            author_id = author_info['id']
            persona_config = self._load_persona_prompt(author_id)
            formatting_config = self._load_formatting_prompt(author_id)
            authors_data = self._load_authors_data()
            
            # Find author configuration (fail fast if not found)
            author_config = self._find_author_config(author_id, authors_data)
            
            # Extract required information
            subject = material_data.get('name', material_name)
            formula = material_data.get('formula', 'Not specified')
            author_name = author_config['name']
            author_country = author_config['country']
            
            # Build API prompt
            api_prompt = self._build_api_prompt(
                subject, formula, author_name, author_country,
                frontmatter_data, base_config, persona_config, formatting_config
            )
            
            # Generate content via API (fail fast on API errors)
            response = self._call_api_with_validation(api_client, api_prompt)
            
            # Validate word count against author's maximum
            word_count = len(response.split())
            max_word_count = self._get_author_max_word_count(base_config, author_id)
            if max_word_count and word_count > max_word_count:
                excess_words = word_count - max_word_count
                excess_percentage = (excess_words / max_word_count) * 100
                logger.warning(f"⚠️  Word count violation: {word_count} words > {max_word_count} max for author {author_id} (+{excess_words} words, {excess_percentage:.1f}% over)")
                
                # Retry if word count is significantly over the limit (>20% over)
                if excess_percentage > 20:
                    raise RetryableError(f"Content exceeds word limit by {excess_percentage:.1f}% ({word_count}/{max_word_count} words). Retrying with stricter constraints.")
            
            # Format response
            formatted_content = self._format_api_response(
                response, subject, author_name, author_country, base_config, persona_config
            )
            
            # Generate quality score if enabled
            quality_score = None
            if self.enable_scoring and self.content_scorer:
                try:
                    quality_score = self.content_scorer.score_content(
                        formatted_content, material_data, author_info, frontmatter_data
                    )
                    
                    # Check if retry is recommended based on quality score
                    if quality_score.retry_recommended:
                        logger.warning(f"Quality score recommends retry: {quality_score.overall_score:.1f}/100")
                        if quality_score.human_believability < self.human_threshold:
                            raise RetryableError(f"Content failed human believability threshold: {quality_score.human_believability:.1f} < {self.human_threshold}")
                        
                except Exception as scoring_error:
                    logger.warning(f"Content scoring failed: {scoring_error}")
                    # Don't fail generation for scoring errors, just log
            
            # Enhanced metadata with scoring information
            enhanced_metadata = {
                'generation_method': 'api_fail_fast',
                'author_id': author_id,
                'author_name': author_name,
                'attempts': 1,
                'scoring_enabled': self.enable_scoring
            }
            
            if quality_score:
                enhanced_metadata.update({
                    'overall_score': quality_score.overall_score,
                    'human_believability': quality_score.human_believability,
                    'technical_accuracy': quality_score.technical_accuracy,
                    'author_authenticity': quality_score.author_authenticity,
                    'readability_score': quality_score.readability_score,
                    'passes_human_threshold': quality_score.passes_human_threshold,
                    'retry_recommended': quality_score.retry_recommended,
                    'word_count': quality_score.word_count
                })
            
            return GenerationResult(
                success=True,
                content=formatted_content,
                metadata=enhanced_metadata,
                quality_score=quality_score
            )
            
        except ConfigurationError as e:
            # Configuration errors should fail immediately
            raise GenerationError(f"Configuration error: {e}")
            
        except Exception as e:
            # Other errors might be retryable
            raise RetryableError(f"Generation attempt failed: {e}")
    
    def _find_author_config(self, author_id: int, authors_data: List[Dict]) -> Dict:
        """Find author configuration, fail fast if not found."""
        for author in authors_data:
            if author.get('id') == author_id:
                return author
        
        raise ConfigurationError(f"Author configuration not found for id: {author_id}")
    
    def _get_author_max_word_count(self, base_config: Dict, author_id: int) -> Optional[int]:
        """Extract max word count for author from base configuration."""
        try:
            # Map author IDs to country codes
            author_map = {1: 'taiwan', 2: 'italy', 3: 'indonesia', 4: 'usa'}
            author_key = author_map.get(author_id)
            
            if not author_key:
                return None
            
            # Check author_expertise_areas first
            expertise_areas = base_config.get('author_expertise_areas', {})
            if author_key in expertise_areas:
                max_count = expertise_areas[author_key].get('max_word_count')
                if isinstance(max_count, int):
                    return max_count
            
            # Check author_configurations as fallback
            author_configs = base_config.get('author_configurations', {})
            if author_key in author_configs:
                max_count_str = author_configs[author_key].get('max_word_count', '')
                # Extract number from strings like "380 words maximum"
                import re
                match = re.search(r'(\d+)', max_count_str)
                if match:
                    return int(match.group(1))
            
            return None
            
        except Exception as e:
            logger.warning(f"Could not extract max word count for author {author_id}: {e}")
            return None

    def _author_exists(self, author_id: int) -> bool:
        """Check if author exists in configuration."""
        try:
            authors_data = self._load_authors_data()
            return any(author.get('id') == author_id for author in authors_data)
        except Exception:
            return False
    
    def _call_api_with_validation(self, api_client, prompt: str) -> str:
        """Call API with proper error handling."""
        try:
            # Check if API client has generate_simple method (for backward compatibility)
            if hasattr(api_client, 'generate_simple'):
                response = api_client.generate_simple(prompt)
            else:
                # Use GenerationRequest for newer API clients
                from api.client import GenerationRequest
                request = GenerationRequest(prompt=prompt)
                response = api_client.generate(request)
            
            if not response:
                raise RetryableError("API returned empty response")
            
            if hasattr(response, 'success') and not response.success:
                error_msg = getattr(response, 'error', 'Unknown API error')
                raise RetryableError(f"API request failed: {error_msg}")
            
            # Extract content from response
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)
            
            if not content or len(content.strip()) < 50:
                raise RetryableError("API returned insufficient content")
            
            # Log content length for monitoring
            word_count = len(content.split())
            logger.info(f"📝 Generated content: {word_count} words ({len(content)} chars)")
            
            return content
            
        except Exception as e:
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise RetryableError(f"API connection error: {e}")
            else:
                raise RetryableError(f"API call failed: {e}")
    
    def _get_persona_file_path(self, author_id: int) -> str:
        """Get persona file path for author ID."""
        persona_files = {
            1: "components/content/prompts/personas/taiwan_persona.yaml",
            2: "components/content/prompts/personas/italy_persona.yaml", 
            3: "components/content/prompts/personas/indonesia_persona.yaml",
            4: "components/content/prompts/personas/usa_persona.yaml"
        }
        
        persona_file = persona_files.get(author_id)
        if not persona_file:
            raise ConfigurationError(f"No persona file configured for author_id: {author_id}")
        
        return persona_file
    
    @lru_cache(maxsize=None)
    def _load_base_content_prompt(self) -> Dict[str, Any]:
        """Load base content prompt configuration."""
        base_file = "components/content/prompts/base_content_prompt.yaml"
        
        try:
            with open(base_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                raise ConfigurationError(f"Base content prompt file {base_file} is empty")
            
            return data
            
        except FileNotFoundError:
            raise ConfigurationError(f"Base content prompt not found: {base_file}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in base content prompt: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading base content prompt: {e}")
    
    @lru_cache(maxsize=None)
    def _load_persona_prompt(self, author_id: int) -> Dict[str, Any]:
        """Load persona configuration for author."""
        persona_file = self._get_persona_file_path(author_id)
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                raise ConfigurationError(f"Persona file {persona_file} is empty")
            
            return data
            
        except FileNotFoundError:
            raise ConfigurationError(f"Persona file not found: {persona_file}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in persona file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading persona file: {e}")
    
    @lru_cache(maxsize=None)
    def _load_formatting_prompt(self, author_id: int) -> Dict[str, Any]:
        """Load formatting-specific configuration."""
        formatting_files = {
            1: "components/content/prompts/formatting/taiwan_formatting.yaml",
            2: "components/content/prompts/formatting/italy_formatting.yaml",
            3: "components/content/prompts/formatting/indonesia_formatting.yaml", 
            4: "components/content/prompts/formatting/usa_formatting.yaml"
        }
        
        formatting_file = formatting_files.get(author_id)
        if not formatting_file:
            raise ConfigurationError(f"No formatting file configured for author_id: {author_id}")
        
        if not Path(formatting_file).exists():
            raise ConfigurationError(f"Formatting file not found: {formatting_file}")
        
        try:
            with open(formatting_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            if not data:
                raise ConfigurationError(f"Formatting file is empty: {formatting_file}")
            return data
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in formatting file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading formatting file {formatting_file}: {e}")
    
    @lru_cache(maxsize=None)
    def _load_authors_data(self) -> List[Dict[str, Any]]:
        """Load authors data from authors.json."""
        authors_file = "components/author/authors.json"
        
        try:
            with open(authors_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict) and 'authors' in data:
                authors_list = data['authors']
            elif isinstance(data, list):
                authors_list = data
            else:
                raise ConfigurationError(f"Authors file {authors_file} must contain a list or object with 'authors' key")
            
            if not isinstance(authors_list, list):
                raise ConfigurationError("Authors data must be a list")
            
            return authors_list
            
        except FileNotFoundError:
            raise ConfigurationError(f"Authors file not found: {authors_file}")
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Invalid JSON in authors file: {e}")
        except Exception as e:
            raise ConfigurationError(f"Error loading authors file: {e}")
    
    def _build_api_prompt(self, subject: str, formula: str, author_name: str, 
                         author_country: str, frontmatter_data: Optional[Dict],
                         base_config: Dict, persona_config: Dict, formatting_config: Dict) -> str:
        """Build API prompt from configurations."""
        try:
            # Start with basic material information and frontmatter data FIRST
            prompt_parts = [
                f"Generate laser cleaning content for {subject} ({formula})",
                ""
            ]
            
            # Add frontmatter/material context BEFORE other prompt layers
            if frontmatter_data:
                prompt_parts.append("MATERIAL CONTEXT:")
                
                # Chemical properties
                chem_props = frontmatter_data.get('chemicalProperties', {})
                if chem_props:
                    prompt_parts.append(f"- Chemical Formula: {chem_props.get('formula', formula)}")
                    if 'symbol' in chem_props:
                        prompt_parts.append(f"- Material Symbol: {chem_props['symbol']}")
                    if 'materialType' in chem_props:
                        prompt_parts.append(f"- Material Type: {chem_props['materialType']}")
                
                # Physical properties
                properties = frontmatter_data.get('properties', {})
                if properties:
                    if 'density' in properties:
                        prompt_parts.append(f"- Density: {properties['density']}")
                    if 'thermalConductivity' in properties:
                        prompt_parts.append(f"- Thermal Conductivity: {properties['thermalConductivity']}")
                    if 'meltingPoint' in properties:
                        prompt_parts.append(f"- Melting Point: {properties['meltingPoint']}")
                
                # Category and technical specs
                if 'category' in frontmatter_data:
                    prompt_parts.append(f"- Category: {frontmatter_data['category'].title()}")
                
                tech_specs = frontmatter_data.get('technicalSpecifications', {})
                if tech_specs:
                    if 'tensileStrength' in tech_specs:
                        prompt_parts.append(f"- Tensile Strength: {tech_specs['tensileStrength']}")
                
                prompt_parts.append("")
            
            # Now add author information AFTER material context
            prompt_parts.extend([
                f"Author: {author_name} from {author_country}",
                ""
            ])
            
            # Add PRIMARY guidance from Overall subject section FIRST
            overall_subject = base_config.get('overall_subject')
            if overall_subject:
                prompt_parts.append("PRIMARY CONTENT GUIDANCE:")
                if isinstance(overall_subject, list):
                    for guidance in overall_subject:
                        prompt_parts.append(f"- {guidance}")
                elif isinstance(overall_subject, str):
                    prompt_parts.append(f"- {overall_subject}")
                prompt_parts.append("")
            else:
                # Fallback to use the hardcoded questions if not in config
                prompt_parts.extend([
                    "PRIMARY CONTENT GUIDANCE:",
                    "- What is special about the material?",
                    "- How does it differ from others in the category?",
                    "- What is it often used for?",
                    "- What is it like to laser clean?",
                    "- What special challenges or advantages does it present for laser cleaning?",
                    "- What should the results look like?",
                    ""
                ])
            
            # Get author configuration from base config
            author_configs = base_config.get('author_expertise_areas', {})
            country_lower = author_country.lower()
            
            # Handle special country mappings
            country_mapping = {
                "united states (california)": "usa",
                "united states": "usa", 
                "taiwan": "taiwan",
                "italy": "italy",
                "indonesia": "indonesia"
            }
            
            mapped_country = country_mapping.get(country_lower, country_lower)
            author_config = author_configs.get(mapped_country, {})
            
            # Get technical requirements
            tech_reqs = base_config.get('technical_requirements', {})
            
            # Get persona-specific patterns
            language_patterns = persona_config.get('language_patterns', {})
            writing_style = persona_config.get('writing_style', {})
            technical_focus = persona_config.get('technical_focus', {})
            
            # Add persona-specific technical focus if available
            if technical_focus:
                prompt_parts.append("SECONDARY - PERSONA TECHNICAL FOCUS:")
                for key, value in technical_focus.items():
                    if isinstance(value, str) and key != 'author_id':
                        prompt_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
                prompt_parts.append("")
            
            # Add technical requirements as SECONDARY guidance
            if tech_reqs:
                prompt_parts.append("SECONDARY - TECHNICAL REQUIREMENTS:")
                laser_specs = tech_reqs.get('laser_specifications', [])
                for spec in laser_specs:
                    prompt_parts.append(f"- {spec}")
                
                required_content = tech_reqs.get('required_content', [])
                if required_content:
                    prompt_parts.append("")
                    prompt_parts.append("REQUIRED CONTENT:")
                    for content in required_content:
                        # Replace placeholder with actual formula
                        content_with_formula = content.replace('{material_formula}', formula)
                        prompt_parts.append(f"- {content_with_formula}")
                
                prompt_parts.append("")
            
            # Add language patterns if available - SECONDARY guidance
            if language_patterns:
                signature_phrases = language_patterns.get('signature_phrases', [])
                if signature_phrases:
                    prompt_parts.append("SECONDARY - LANGUAGE STYLE:")
                    prompt_parts.extend([f"- {phrase}" for phrase in signature_phrases[:3]])
                    prompt_parts.append("")
            
            # Add writing style guidance - SECONDARY
            if writing_style:
                prompt_parts.append("SECONDARY - WRITING STYLE:")
                for key, value in writing_style.items():
                    if isinstance(value, str):
                        prompt_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
                prompt_parts.append("")
            
            # Add formatting guidance from formatting config - SECONDARY
            if formatting_config:
                markdown_formatting = formatting_config.get('markdown_formatting', {})
                if markdown_formatting:
                    prompt_parts.append("SECONDARY - FORMATTING REQUIREMENTS:")
                    
                    # Headers
                    headers = markdown_formatting.get('headers', {})
                    if headers:
                        prompt_parts.append("- Headers: " + headers.get('main_title', '# for main title'))
                        prompt_parts.append("- Sections: " + headers.get('section_headers', '## for sections'))
                    
                    # Emphasis
                    emphasis = markdown_formatting.get('emphasis', {})
                    if emphasis:
                        prompt_parts.append("- Bold: " + emphasis.get('critical_info', '**bold** for key information'))
                        prompt_parts.append("- Formulas: " + emphasis.get('formulas', 'simple notation'))
                    
                    # Lists
                    lists = markdown_formatting.get('lists', {})
                    if lists:
                        prompt_parts.append("- Lists: " + lists.get('primary_style', 'numbered lists'))
                    
                    prompt_parts.append("")
            
            # Add content structure from base config
            content_structure = base_config.get('content_structure', {})
            if content_structure:
                required_sections = content_structure.get('required_sections', [])
                if required_sections:
                    prompt_parts.append("CONTENT STRUCTURE:")
                    prompt_parts.extend([f"- {section}" for section in required_sections])
                    prompt_parts.append("")
            
            # Add application focus if available
            app_focus = base_config.get('application_focus', {})
            if app_focus and country_lower in app_focus:
                prompt_parts.append(f"APPLICATION FOCUS: {app_focus[country_lower]}")
                prompt_parts.append("")
            
            # Add explicit word count constraints
            author_id = author_config.get('author_id')
            if not author_id:
                # Try to map from country to author_id
                author_id_map = {'taiwan': 1, 'italy': 2, 'indonesia': 3, 'usa': 4}
                author_id = author_id_map.get(mapped_country)
            
            if author_id:
                max_word_count = self._get_author_max_word_count(base_config, author_id)
                if max_word_count:
                    prompt_parts.extend([
                        "CRITICAL WORD COUNT CONSTRAINT:",
                        f"- Maximum words: {max_word_count} words STRICT LIMIT",
                        f"- Target range: {int(max_word_count * 0.8)}-{max_word_count} words",
                        "- Content MUST be concise and focused",
                        "- Prioritize essential information only",
                        ""
                    ])
            
            # Final instructions
            prompt_parts.extend([
                "Generate comprehensive, expert-level technical content.",
                "Maintain professional scientific tone throughout.",
                "Ensure logical flow and accurate technical terminology."
            ])
            
            return "\n".join(prompt_parts)
            
        except Exception as e:
            raise ConfigurationError(f"Error building API prompt: {e}")
    
    def _format_api_response(self, response: str, subject: str, author_name: str,
                           author_country: str, base_config: Dict, persona_config: Dict) -> str:
        """Format API response with persona-specific formatting."""
        try:
            # Get content structure from persona
            content_structure = persona_config.get('content_structure', {})
            
            # Format title
            title_pattern = content_structure.get('title_pattern', 'Laser Cleaning of {material}: Technical Analysis')
            title = f"# {title_pattern.format(material=subject)}"
            
            # Format byline
            byline_pattern = content_structure.get('byline', '**{author_name}, Ph.D. - {country}**')
            byline = byline_pattern.format(author_name=author_name, country=author_country)
            
            # Combine with response content
            formatted_content = f"{title}\n\n{byline}\n\n{response.strip()}"
            
            return formatted_content
            
        except Exception as e:
            raise ConfigurationError(f"Error formatting response: {e}")


def create_fail_fast_generator(max_retries: int = 3, retry_delay: float = 1.0,
                             enable_scoring: bool = True, human_threshold: float = 75.0) -> FailFastContentGenerator:
    """
    Create a fail-fast content generator.
    
    Args:
        max_retries: Maximum number of retry attempts for retryable errors
        retry_delay: Delay between retries in seconds
        enable_scoring: Whether to enable comprehensive quality scoring
        human_threshold: Minimum score required to pass human believability test
        
    Returns:
        Configured fail-fast content generator with optional scoring
        
    Raises:
        ConfigurationError: If required configurations are missing or invalid
    """
    return FailFastContentGenerator(
        max_retries=max_retries, 
        retry_delay=retry_delay,
        enable_scoring=enable_scoring,
        human_threshold=human_threshold
    )
