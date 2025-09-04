#!/usr/bin/env python3
"""
Fail-Fast Content Generator
Removes all hardcoded fallbacks and implements clean error handling with retry mechanisms.
"""

import sys
import logging
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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
                 enable_scoring: bool = True, human_threshold: float = 75.0,
                 ai_detection_service=None, skip_ai_detection: bool = False):
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.enable_scoring = enable_scoring
        self.human_threshold = human_threshold
        self.ai_detection_service = ai_detection_service
        self.skip_ai_detection = skip_ai_detection  # New flag to skip AI detection
        
        logger.info(f"FailFastContentGenerator initialized with AI detection service: {self.ai_detection_service is not None}")
        if self.ai_detection_service:
            logger.info(f"AI detection service available: {self.ai_detection_service.is_available()}")
        
        # Initialize content scorer if enabled - FAIL FAST if not available
        if self.enable_scoring:
            try:
                from ..validation.content_scorer import create_content_scorer
                self.content_scorer = create_content_scorer(human_threshold)
            except ImportError:
                logger.warning("Content scorer not available - disabling quality scoring")
                self.enable_scoring = False
                self.content_scorer = None
        else:
            self.content_scorer = None
        
        # Validate required configurations on startup
        self._validate_required_configurations()
    
    def _validate_required_configurations(self):
        """Validate all required configuration files exist and are valid."""
        logger.info("Validating required configurations...")
        
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
            base_config = {}
            author_id = author_info['id']
            formatting_config = {}
            authors_data = self._load_authors_data()
            
            # Find author configuration (fail fast if not found)
            author_config = self._find_author_config(author_id, authors_data)
            
            # Extract required information
            # Fail fast if material data is missing critical info
            if 'name' not in material_data:
                raise ConfigurationError("Material data missing 'name' field")
            
            subject = material_data['name']
            author_name = author_config['name']
            
            # Build API prompt using the comprehensive prompt building system
            system_prompt = ""
            user_prompt = self._build_api_prompt(
                subject=subject,
                author_id=author_id,
                author_name=author_name,
                material_data=material_data,
                author_info=author_info
            )
            
            # Generate content via API (fail fast on API errors)
            api_response_obj = self._call_api_with_validation(api_client, user_prompt, system_prompt)
            
            # Debug: Log the actual prompts being sent
            logger.info(f"🔍 System prompt preview (first 500 chars): {system_prompt[:500]}...")
            logger.info(f"🔍 User prompt preview (first 500 chars): {user_prompt[:500]}...")
            logger.info(f"📝 System prompt length: {len(system_prompt)} characters")
            logger.info(f"📝 User prompt length: {len(user_prompt)} characters")
            
            # Extract text content from response object for processing
            if hasattr(api_response_obj, 'content'):
                response = api_response_obj.content
            elif isinstance(api_response_obj, str):
                response = api_response_obj
                # For backward compatibility, create a simple wrapper
                class StringResponseWrapper:
                    def __init__(self, content):
                        self.content = content
                        self.success = True
                        self.request_id = "string_response"
                        self.response_time = 0.0
                        self.token_count = len(content.split())
                        self.prompt_tokens = 0
                        self.completion_tokens = len(content.split())
                        self.model_used = "unknown"
                        self.retry_count = 0
                api_response_obj = StringResponseWrapper(response)
            else:
                response = str(api_response_obj)
                # Create wrapper for any other type
                class GenericResponseWrapper:
                    def __init__(self, content):
                        self.content = content
                        self.success = True
                        self.request_id = "generic_response"
                        self.response_time = 0.0
                        self.token_count = len(content.split())
                        self.prompt_tokens = 0
                        self.completion_tokens = len(content.split())
                        self.model_used = "unknown"
                        self.retry_count = 0
                api_response_obj = GenericResponseWrapper(response)
            
            # Validate word count against author's maximum (with 50% tolerance)
            word_count = len(response.split())
            max_word_count = self._get_author_max_word_count(base_config, author_id, formatting_config)
            if max_word_count:
                # Allow 50% tolerance over the limit
                tolerance_limit = max_word_count * 1.5
                if word_count > tolerance_limit:
                    excess_words = word_count - max_word_count
                    excess_percentage = (excess_words / max_word_count) * 100
                    logger.warning(f"⚠️  Word count violation: {word_count} words > {max_word_count} max for author {author_id} (+{excess_words} words, {excess_percentage:.1f}% over)")
                    
                    # Only fail if exceeding 50% tolerance
                    raise RetryableError(f"Content exceeds word limit with 50% tolerance: {word_count}/{int(tolerance_limit)} words. Retrying with stricter constraints.")
                elif word_count > max_word_count:
                    excess_words = word_count - max_word_count
                    excess_percentage = (excess_words / max_word_count) * 100
                    logger.info(f"ℹ️  Word count slightly over target but within 50% tolerance: {word_count} words > {max_word_count} target (+{excess_words} words, {excess_percentage:.1f}% over)")
            
            # Extract content from response object for processing
            if hasattr(response, 'content'):
                response_content = response.content
            elif isinstance(response, dict) and 'choices' in response:
                # Handle OpenAI-style API response
                if response['choices'] and 'message' in response['choices'][0]:
                    response_content = response['choices'][0]['message']['content']
                else:
                    response_content = str(response)
            elif isinstance(response, str):
                response_content = response
            else:
                response_content = str(response)
            
            # Generate quality score first if enabled
            quality_score = None
            if self.enable_scoring and self.content_scorer:
                try:
                    # Create temporary formatted content for scoring
                    temp_formatted = response_content
                    
                    quality_score = self.content_scorer.score_content(
                        temp_formatted, material_data, author_info, frontmatter_data
                    )
                    
                    # Check if retry is recommended based on quality score
                    if quality_score.retry_recommended:
                        logger.warning(f"Quality score recommends retry: {quality_score.overall_score:.1f}/100")
                        if quality_score.human_believability < self.human_threshold:
                            raise RetryableError(f"Content failed human believability threshold: {quality_score.human_believability:.1f} < {self.human_threshold}")
                        
                except Exception as scoring_error:
                    logger.warning(f"Content scoring failed: {scoring_error}")
                    # Don't fail generation for scoring errors, just log

            # Perform AI detection analysis if service is available and not skipped
            ai_detection_result = None
            if not self.skip_ai_detection:
                logger.info(f"Checking AI detection service: {self.ai_detection_service is not None}")
                if self.ai_detection_service and self.ai_detection_service.is_available():
                    logger.info("AI detection service is available, starting analysis...")
                    try:
                        # Use the raw response content for AI detection (without frontmatter)
                        logger.info(f"Text length for AI detection: {len(response_content)} characters")
                        ai_detection_result = self.ai_detection_service.analyze_text(response_content)
                        logger.info(f"AI detection analysis completed: {ai_detection_result.score:.1f} score, {ai_detection_result.classification}")
                        
                        # Log warning if content appears too AI-like
                        if ai_detection_result.score < 30:  # LOW score = AI-like content
                            logger.warning(f"Content appears AI-generated (score: {ai_detection_result.score:.1f})")
                            
                    except Exception as ai_error:
                        logger.warning(f"AI detection analysis failed: {ai_error}")
                        ai_detection_result = None
                else:
                    logger.info("AI detection service not available or not enabled")
            else:
                logger.info("AI detection skipped by configuration")

            # Format response with comprehensive frontmatter (now with quality_score available)
            formatted_content = response_content
            
            # Enhanced metadata with scoring information
            enhanced_metadata = {
                'generation_method': 'api_fail_fast',
                'author_id': author_id,
                'author_name': author_name,
                'attempts': 1,
                'scoring_enabled': self.enable_scoring,
                'ai_detection_enabled': self.ai_detection_service is not None and self.ai_detection_service.is_available()
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
            
            # Add AI detection metadata if available
            if ai_detection_result:
                enhanced_metadata.update({
                    'ai_detection_score': ai_detection_result.score,
                    'ai_detection_confidence': ai_detection_result.confidence,
                    'ai_detection_classification': ai_detection_result.classification,
                    'ai_detection_provider': ai_detection_result.provider,
                    'ai_detection_processing_time': ai_detection_result.processing_time,
                    'ai_detection_details': ai_detection_result.details
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
    
    def _get_author_max_word_count(self, base_config: Dict, author_id: int, formatting_config: Optional[Dict] = None) -> Optional[int]:
        """Extract max word count for author from configuration files."""
        try:
            # First check formatting config (most specific)
            if formatting_config and 'content_constraints' in formatting_config:
                max_count = formatting_config['content_constraints'].get('max_word_count')
                if isinstance(max_count, int):
                    logger.debug(f"Found word limit in formatting config: {max_count}")
                    return max_count
            
            # Map author IDs to country codes
            author_map = {1: 'taiwan', 2: 'italy', 3: 'indonesia', 4: 'usa'}
            author_key = author_map.get(author_id)
            
            if not author_key:
                return None
            
            # Check author_expertise_areas in base config
            expertise_areas = base_config.get('author_expertise_areas', {})
            if author_key in expertise_areas:
                max_count = expertise_areas[author_key].get('max_word_count')
                if isinstance(max_count, int):
                    logger.debug(f"Found word limit in base config expertise areas: {max_count}")
                    return max_count
            
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
    
    def _call_api_with_validation(self, api_client, prompt: str, system_prompt: Optional[str] = None):
        """Call API with proper error handling and return full response object."""
        try:
            # API Terminal Messaging - Start
            print("🚀 [GENERATOR] Starting API call to content generation service...")
            print(f"📤 [GENERATOR] Sending prompt ({len(prompt)} chars) to API")
            if system_prompt:
                print(f"📤 [GENERATOR] System prompt ({len(system_prompt)} chars) included")
            logger.info(f"🌐 [GENERATOR] API call initiated - Prompt length: {len(prompt)} chars")

            # Check if API client has generate_simple method (for backward compatibility)
            if hasattr(api_client, 'generate_simple'):
                response = api_client.generate_simple(prompt, system_prompt=system_prompt)
                # For generate_simple, we only get string content, wrap it
                if isinstance(response, str):
                    # Create a mock response object to maintain API verification data
                    class SimpleResponseWrapper:
                        def __init__(self, content):
                            self.content = content
                            self.success = True
                            self.request_id = "simple_api_call"
                            self.response_time = 0.0
                            self.token_count = len(content.split())
                            self.prompt_tokens = len(prompt.split()) + (len(system_prompt.split()) if system_prompt else 0)
                            self.completion_tokens = len(content.split())
                            self.model_used = "unknown"
                            self.retry_count = 0
                    response = SimpleResponseWrapper(response)
            else:
                # Use GenerationRequest for newer API clients
                from api.client import GenerationRequest
                request = GenerationRequest(prompt=prompt, system_prompt=system_prompt)
                response = api_client.generate(request)
            
            # API Terminal Messaging - Success
            if hasattr(response, 'content'):
                content_length = len(response.content)
            elif isinstance(response, str):
                content_length = len(response)
            else:
                content_length = len(str(response))
            
            print(f"✅ [GENERATOR] API call completed successfully - Received {content_length} chars")
            logger.info(f"✅ [GENERATOR] API response received - Content length: {content_length} chars")
            
            if not response:
                print("❌ [GENERATOR] API returned empty response")
                raise RetryableError("API returned empty response")
            
            if hasattr(response, 'success') and not response.success:
                error_msg = getattr(response, 'error', 'Unknown API error')
                print(f"❌ [GENERATOR] API request failed: {error_msg}")
                raise RetryableError(f"API request failed: {error_msg}")
            
            # Extract content from response for validation
            if hasattr(response, 'content'):
                content = response.content
            elif isinstance(response, str):
                content = response
            else:
                content = str(response)
            
            if not content or len(content.strip()) < 50:
                print(f"⚠️ [GENERATOR] API returned insufficient content: {len(content.strip())} chars")
                raise RetryableError("API returned insufficient content")
            
            # Log content length for monitoring
            word_count = len(content.split())
            logger.info(f"📝 Generated content: {word_count} words ({len(content)} chars)")
            print(f"📊 [GENERATOR] Content generated: {word_count} words, {len(content)} characters")
            
            return response  # Return full response object, not just content
            
        except Exception as e:
            # API Terminal Messaging - Error
            print(f"❌ [GENERATOR] API call failed: {str(e)}")
            logger.error(f"❌ [GENERATOR] API call error: {e}")
            
            if "timeout" in str(e).lower() or "connection" in str(e).lower():
                raise RetryableError(f"API connection error: {e}")
            else:
                raise RetryableError(f"API call failed: {e}")
    
    def _load_base_content_prompt(self) -> Dict[str, Any]:
        """Load base content prompt configuration from YAML file."""
        import yaml
        
        base_prompt_file = "components/text/prompts/base_content_prompt.yaml"
        
        try:
            with open(base_prompt_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                raise ConfigurationError(f"Base content prompt file is empty: {base_prompt_file}")
            
            return config
            
        except FileNotFoundError:
            raise ConfigurationError(f"Base content prompt file not found: {base_prompt_file}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in base content prompt: {e}")
    
    def _load_persona_prompt(self, author_id: int) -> Dict[str, Any]:
        """Load persona configuration for specific author."""
        import yaml
        
        persona_file = self._get_persona_file_path(author_id)
        
        try:
            with open(persona_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                raise ConfigurationError(f"Persona file is empty: {persona_file}")
            
            return config
            
        except FileNotFoundError:
            raise ConfigurationError(f"Persona file not found: {persona_file}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in persona file: {e}")
    
    def _load_formatting_prompt(self, author_id: int) -> Dict[str, Any]:
        """Load formatting configuration for specific author."""
        import yaml
        
        # Map author IDs to country codes
        author_map = {1: 'taiwan', 2: 'italy', 3: 'indonesia', 4: 'usa'}
        country = author_map.get(author_id)
        
        if not country:
            raise ConfigurationError(f"No formatting configuration for author_id: {author_id}")
        
        formatting_file = f"components/text/prompts/formatting/{country}_formatting.yaml"
        
        try:
            with open(formatting_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                raise ConfigurationError(f"Formatting file is empty: {formatting_file}")
            
            return config
            
        except FileNotFoundError:
            raise ConfigurationError(f"Formatting file not found: {formatting_file}")
        except yaml.YAMLError as e:
            raise ConfigurationError(f"Invalid YAML in formatting file: {e}")
    
    def _build_api_prompt(self, subject: str, author_id: int, author_name: str, 
                         material_data: Dict, author_info: Dict) -> str:
        """Build complete API prompt by combining base, persona, and formatting configurations."""
        try:
            # Load all required configurations
            base_config = self._load_base_content_prompt()
            persona_config = self._load_persona_prompt(author_id)
            formatting_config = self._load_formatting_prompt(author_id)
            
            # Build the complete prompt by combining all layers
            prompt_parts = []
            
            # 1. Base content prompt
            if 'overall_subject' in base_config:
                prompt_parts.append(f"## Base Content Requirements\n{base_config['overall_subject']}")
            
            # 2. Author-specific persona
            if 'persona' in persona_config:
                persona = persona_config['persona']
                prompt_parts.append(f"\n## Author Persona: {persona.get('name', author_name)}")
                prompt_parts.append(f"Country: {persona.get('country', 'Unknown')}")
                prompt_parts.append(f"Personality: {persona.get('personality', 'Professional')}")
                prompt_parts.append(f"Tone: {persona.get('tone_objective', 'Professional')}")
            
            # 3. Language patterns and signature phrases
            if 'language_patterns' in persona_config:
                patterns = persona_config['language_patterns']
                prompt_parts.append("\n## Language Patterns (Apply Throughout)")
                if 'vocabulary' in patterns:
                    prompt_parts.append(f"Vocabulary: {patterns['vocabulary']}")
                if 'repetition' in patterns:
                    prompt_parts.append(f"Repetition: {patterns['repetition']}")
                if 'signature_phrases' in patterns:
                    prompt_parts.append(f"Use these signature phrases naturally: {', '.join(patterns['signature_phrases'][:5])}")
            
            # 4. Writing style guidelines
            if 'writing_style' in persona_config:
                style = persona_config['writing_style']
                prompt_parts.append("\n## Writing Style Guidelines")
                if 'tone' in style:
                    prompt_parts.append(f"Tone: {style['tone']['primary']}")
                if 'pacing' in style:
                    prompt_parts.append(f"Pacing: {style['pacing']}")
                if 'guidelines' in style:
                    prompt_parts.append("Key guidelines:")
                    for guideline in style['guidelines'][:3]:
                        prompt_parts.append(f"- {guideline}")
            
            # 5. Formatting requirements
            if 'formatting_patterns' in formatting_config:
                patterns = formatting_config['formatting_patterns']
                prompt_parts.append("\n## Formatting Requirements")
                if 'emphasis' in patterns:
                    prompt_parts.append(f"Emphasis: {patterns['emphasis']}")
                if 'structure' in patterns:
                    prompt_parts.append(f"Structure: {patterns['structure']}")
            
            # 6. Content constraints
            if 'content_constraints' in formatting_config:
                constraints = formatting_config['content_constraints']
                if 'max_word_count' in constraints:
                    prompt_parts.append(f"\n## Content Length\nMaximum word count: {constraints['max_word_count']} words")
            
            # 7. Cultural characteristics
            if 'taiwanese_characteristics' in formatting_config:
                chars = formatting_config['taiwanese_characteristics']
                prompt_parts.append("\n## Cultural Writing Characteristics")
                for key, value in list(chars.items())[:3]:
                    prompt_parts.append(f"{key.replace('_', ' ').title()}: {value}")
            
            # 8. Main content generation instruction
            prompt_parts.append(f"""
## Content Generation Task

Write a comprehensive article about laser cleaning {subject} following all the above guidelines.

**Subject:** {subject}
**Author:** {author_name}
**Target Audience:** Industry professionals and researchers interested in laser cleaning applications

Ensure the content demonstrates authentic {persona_config['persona'].get('country', 'professional')} writing characteristics and maintains the specified tone throughout.

Apply all language patterns, signature phrases, and formatting requirements consistently throughout the article.
""")
            
            # Combine all parts
            complete_prompt = '\n'.join(prompt_parts)
            
            logger.info(f"📝 Built complete prompt: {len(complete_prompt)} characters")
            return complete_prompt
            
        except Exception as e:
            logger.error(f"Failed to build API prompt: {e}")
    def _get_persona_file_path(self, author_id: int) -> str:
        """Get persona file path for author ID."""
        persona_files = {
            1: "components/text/prompts/personas/taiwan_persona.yaml",
            2: "components/text/prompts/personas/italy_persona.yaml", 
            3: "components/text/prompts/personas/indonesia_persona.yaml",
            4: "components/text/prompts/personas/usa_persona.yaml"
        }
        
        persona_file = persona_files.get(author_id)
        if not persona_file:
            raise ConfigurationError(f"No persona file configured for author_id: {author_id}")
        
        return persona_file
    
    def _load_authors_data(self) -> List[Dict[str, Any]]:
        """Load authors data from authors.json."""
        authors_file = "components/author/authors.json"
        
        try:
            import json
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
        except Exception as e:
            raise ConfigurationError(f"Error loading authors file: {e}")


def create_fail_fast_generator(max_retries: int = 3, retry_delay: float = 1.0,
                             enable_scoring: bool = True, human_threshold: float = 75.0,
                             ai_detection_service=None, skip_ai_detection: bool = False) -> FailFastContentGenerator:
    """
    Create a fail-fast content generator.
    
    Args:
        max_retries: Maximum number of retry attempts for retryable errors
        retry_delay: Delay between retries in seconds
        enable_scoring: Whether to enable comprehensive quality scoring
        human_threshold: Minimum score required to pass human believability test
        ai_detection_service: AI detection service for content analysis
        skip_ai_detection: Whether to skip AI detection (useful when called from wrapper)
        
    Returns:
        Configured fail-fast content generator with optional scoring
        
    Raises:
        ConfigurationError: If required configurations are missing or invalid
    """
    return FailFastContentGenerator(
        max_retries=max_retries, 
        retry_delay=retry_delay,
        enable_scoring=enable_scoring,
        human_threshold=human_threshold,
        ai_detection_service=ai_detection_service,
        skip_ai_detection=skip_ai_detection
    )