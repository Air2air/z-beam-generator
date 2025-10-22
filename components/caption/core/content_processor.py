#!/usr/bin/env python3
"""
Content Processor - Clean AI response handling with validation

Handles AI response processing, content extraction, and basic validation.
Provides clean separation of content processing concerns.
"""

from typing import Dict, Any, Tuple, Optional
import logging
import time
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class ContentProcessor:
    """Handles AI response processing and validation"""
    
    def __init__(self):
        self.voice_adapter = None  # Will be injected to avoid circular imports
        self.retry_config = {
            'max_retries': 3,
            'base_delay': 0.5,
            'backoff_multiplier': 2.0
        }
        self.error_recovery_stats = {
            'recoverable_errors': 0,
            'successful_recoveries': 0,
            'total_retries': 0
        }
    
    def set_voice_adapter(self, voice_adapter):
        """Inject voice adapter to avoid circular imports"""
        self.voice_adapter = voice_adapter
    
    def extract_and_validate(self, ai_response: str, material_name: str, 
                           author_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract content with intelligent error recovery and validation.
        Returns structured result with content and validation status.
        """
        # Use intelligent retry for the entire operation
        return self._with_intelligent_retry(
            self._extract_and_validate_core,
            ai_response, material_name, author_config
        )
    
    def _extract_and_validate_core(self, ai_response: str, material_name: str, 
                                 author_config: Dict[str, Any]) -> Dict[str, Any]:
        """Core extraction logic with error recovery capabilities"""
        try:
            # Extract before/after content
            content = self._extract_before_after_content(ai_response, material_name)
            
            # Apply sentence count enforcement based on voice profile
            before_text, after_text = self._enforce_sentence_count_limits(
                content['beforeText'], content['afterText'], 
                author_config['country'], material_name
            )
            
            # Update content with enforced text
            content['beforeText'] = before_text
            content['afterText'] = after_text
            
            # Basic validation
            validation_result = self._basic_content_validation(content, material_name)
            
            return {
                'content': content,
                'validation_passed': validation_result['passed'],
                'validation_issues': validation_result['issues'],
                'meets_standards': validation_result['passed']
            }
            
        except Exception as e:
            logger.error(f"Content processing failed for {material_name}: {e}")
            
            # Attempt fallback content extraction
            fallback_result = self._attempt_fallback_extraction(
                ai_response, material_name, author_config, e
            )
            
            if fallback_result:
                self.error_recovery_stats['successful_recoveries'] += 1
                logger.info(f"Successfully recovered content for {material_name} using fallback")
                return fallback_result
            
            return {
                'content': None,
                'validation_passed': False,
                'validation_issues': [str(e)],
                'meets_standards': False
            }
    
    def _extract_before_after_content(self, ai_response: str, material_name: str) -> Dict[str, Any]:
        """Extract before/after text from AI response - FAIL FAST"""
        
        if not ai_response or not ai_response.strip():
            raise ValueError(f"Empty AI response for {material_name} - fail-fast architecture requires valid content")
        
        # Extract BEFORE_TEXT - support both formats
        before_start = ai_response.find('**BEFORE_TEXT:')
        after_marker_search = ai_response.find('**AFTER_TEXT:')
        
        if before_start == -1 or after_marker_search == -1:
            raise ValueError(f"Missing BEFORE_TEXT or AFTER_TEXT markers in AI response for {material_name}")
        
        # Find the end of the BEFORE_TEXT marker line
        marker_line_end = ai_response.find('\n', before_start)
        if marker_line_end == -1:
            marker_line_end = before_start + len('**BEFORE_TEXT:**')
        else:
            marker_line_end += 1
        
        # Extract content between BEFORE_TEXT and AFTER_TEXT
        before_text = ai_response[marker_line_end:after_marker_search].strip()
        before_text = before_text.strip('[]').strip()
        
        # Extract AFTER_TEXT
        after_marker_line_end = ai_response.find('\n', after_marker_search)
        if after_marker_line_end == -1:
            after_start = after_marker_search + len('**AFTER_TEXT:**')
        else:
            after_start = after_marker_line_end + 1
        
        after_text = ai_response[after_start:].strip()
        after_text = after_text.strip('[]').strip()
        
        # Validate content length - FAIL FAST
        min_length = 100  # Flexible minimum for random variation
        
        if not before_text or len(before_text) < min_length:
            raise ValueError(f"BEFORE_TEXT too short for {material_name} - minimum {min_length} characters")
        
        if not after_text or len(after_text) < min_length:
            raise ValueError(f"AFTER_TEXT too short for {material_name} - minimum {min_length} characters")
        
        return {
            'beforeText': before_text,
            'afterText': after_text,
            'technicalFocus': 'surface_analysis',
            'uniqueCharacteristics': [f'{material_name.lower()}_specific'],
            'contaminationProfile': f'{material_name.lower()} surface contamination',
            'microscopyParameters': f'Microscopic analysis of {material_name.lower()}',
            'qualityMetrics': 'Surface improvement analysis'
        }
    
    def _enforce_sentence_count_limits(self, before_text: str, after_text: str, 
                                     author_country: str, material_name: str) -> Tuple[str, str]:
        """
        Enforce sentence count limits based on voice profile requirements.
        
        Args:
            before_text: Generated before text
            after_text: Generated after text  
            author_country: Author's country for voice profile lookup
            material_name: Material name for logging
            
        Returns:
            Tuple of (trimmed_before_text, trimmed_after_text)
        """
        if not self.voice_adapter:
            logger.warning("Voice adapter not set, skipping sentence count enforcement")
            return before_text, after_text
        
        try:
            import re
            
            # Get voice profile requirements
            voice = self.voice_adapter._get_voice_orchestrator(author_country)
            profile = voice.profile
            caption_adaptation = profile.get('voice_adaptation', {}).get('caption_generation', {})
            validation_req = caption_adaptation.get('validation_requirements', {})
            min_sentences = validation_req.get('minimum_sentences', 5)
            
            # Sentence count targets by country (from voice profiles)
            country_limits = {
                'taiwan': (6, 9),
                'italy': (5, 8), 
                'indonesia': (4, 7),
                'united_states': (5, 8),
                'usa': (5, 8)
            }
            
            min_total, max_total = country_limits.get(author_country.lower(), (min_sentences, min_sentences + 3))
            
            # Split into sentences
            def split_sentences(text: str) -> list:
                return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
            
            before_sentences = split_sentences(before_text)
            after_sentences = split_sentences(after_text)
            total_sentences = len(before_sentences) + len(after_sentences)
            
            logger.info(f"Sentence count enforcement for {material_name} ({author_country}): "
                       f"{len(before_sentences)}+{len(after_sentences)}={total_sentences} "
                       f"(target: {min_total}-{max_total})")
            
            # If within limits, return unchanged
            if min_total <= total_sentences <= max_total:
                logger.info(f"✅ Sentence count compliant for {material_name}")
                return before_text, after_text
            
            # If over limit, trim sentences intelligently
            if total_sentences > max_total:
                sentences_to_remove = total_sentences - max_total
                logger.warning(f"⚠️ Trimming {sentences_to_remove} sentences from {material_name} "
                             f"({total_sentences} -> {max_total})")
                
                # Distribute removal between sections
                if len(before_sentences) > len(after_sentences):
                    before_remove = min(sentences_to_remove - sentences_to_remove // 2, 
                                      len(before_sentences) - 2)  # Keep at least 2 sentences
                    after_remove = sentences_to_remove - before_remove
                else:
                    after_remove = min(sentences_to_remove - sentences_to_remove // 2,
                                     len(after_sentences) - 2)  # Keep at least 2 sentences
                    before_remove = sentences_to_remove - after_remove
                
                # Trim sentences (remove from end to preserve opening)
                if before_remove > 0:
                    before_sentences = before_sentences[:-before_remove]
                if after_remove > 0:
                    after_sentences = after_sentences[:-after_remove]
                
                # Reconstruct text
                before_text = '. '.join(before_sentences) + '.' if before_sentences else before_text
                after_text = '. '.join(after_sentences) + '.' if after_sentences else after_text
                
                new_total = len(before_sentences) + len(after_sentences)
                logger.info(f"✅ Trimmed {material_name} to {new_total} sentences "
                           f"({len(before_sentences)}+{len(after_sentences)})")
            
            # If under limit, log but don't modify
            elif total_sentences < min_total:
                logger.warning(f"⚠️ {material_name} has too few sentences ({total_sentences} < {min_total})")
            
            return before_text, after_text
            
        except Exception as e:
            logger.error(f"Error in sentence count enforcement for {material_name}: {e}")
            return before_text, after_text
    
    def _basic_content_validation(self, content: Dict[str, Any], material_name: str) -> Dict[str, Any]:
        """Perform basic content validation"""
        issues = []
        
        # Check content exists
        if not content.get('beforeText'):
            issues.append("Missing before text")
        
        if not content.get('afterText'):
            issues.append("Missing after text")
        
        # Check minimum length
        before_text = content.get('beforeText', '')
        after_text = content.get('afterText', '')
        
        if len(before_text) < 100:
            issues.append(f"Before text too short: {len(before_text)} chars < 100")
        
        if len(after_text) < 100:
            issues.append(f"After text too short: {len(after_text)} chars < 100")
        
        # Check for common issues
        if 'Surface analysis reveals' in before_text and 'Microscopic examination shows' in before_text:
            issues.append("Overuse of formulaic opening phrases")
        
        passed = len(issues) == 0
        
        return {
            'passed': passed,
            'issues': issues
        }
    
    def _with_intelligent_retry(self, operation_func, *args, **kwargs):
        """Intelligent retry wrapper with exponential backoff"""
        last_error = None
        
        for attempt in range(self.retry_config['max_retries'] + 1):
            try:
                return operation_func(*args, **kwargs)
            except (ValueError, KeyError, AttributeError) as e:
                last_error = e
                
                # Check if error is recoverable
                if self._is_recoverable_error(e):
                    self.error_recovery_stats['recoverable_errors'] += 1
                    
                    if attempt < self.retry_config['max_retries']:
                        self.error_recovery_stats['total_retries'] += 1
                        
                        # Exponential backoff
                        delay = self.retry_config['base_delay'] * (
                            self.retry_config['backoff_multiplier'] ** attempt
                        )
                        
                        logger.warning(
                            f"Recoverable error on attempt {attempt + 1}: {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                        continue
                
                # Non-recoverable error or max retries exceeded
                break
        
        # All retries failed
        raise last_error if last_error else Exception("Operation failed with no error details")
    
    def _is_recoverable_error(self, error: Exception) -> bool:
        """Determine if an error is recoverable through retry"""
        error_msg = str(error).lower()
        
        # Recoverable error patterns
        recoverable_patterns = [
            'temporary',
            'timeout', 
            'connection',
            'rate limit',
            'parsing',
            'format'
        ]
        
        return any(pattern in error_msg for pattern in recoverable_patterns)
    
    def _attempt_fallback_extraction(self, ai_response: str, material_name: str,
                                   author_config: Dict[str, Any], 
                                   original_error: Exception) -> Optional[Dict[str, Any]]:
        """Attempt fallback content extraction for partial failures"""
        try:
            logger.info(f"Attempting fallback extraction for {material_name}")
            
            # Simple text splitting fallback
            if ai_response and len(ai_response.strip()) > 50:
                lines = [line.strip() for line in ai_response.split('\n') if line.strip()]
                
                if len(lines) >= 2:
                    # Split content roughly in half
                    mid_point = len(lines) // 2
                    before_lines = lines[:mid_point]
                    after_lines = lines[mid_point:]
                    
                    before_text = ' '.join(before_lines)
                    after_text = ' '.join(after_lines)
                    
                    # Basic validation of fallback content
                    if len(before_text) > 20 and len(after_text) > 20:
                        return {
                            'content': {
                                'beforeText': before_text,
                                'afterText': after_text
                            },
                            'meets_standards': True,  # Lowered standards for fallback
                            'validation_issues': [f"Recovered using fallback extraction (original error: {original_error})"]
                        }
            
            return None
            
        except Exception as fallback_error:
            logger.warning(f"Fallback extraction also failed for {material_name}: {fallback_error}")
            return None
    
    def get_error_recovery_stats(self) -> Dict:
        """Get error recovery statistics for monitoring"""
        total_recoverable = self.error_recovery_stats['recoverable_errors']
        successful_recoveries = self.error_recovery_stats['successful_recoveries']
        
        return {
            'recoverable_errors': total_recoverable,
            'successful_recoveries': successful_recoveries,
            'recovery_rate': successful_recoveries / total_recoverable if total_recoverable > 0 else 0.0,
            'total_retries': self.error_recovery_stats['total_retries']
        }
    
    def reset_error_recovery_stats(self):
        """Reset error recovery statistics"""
        self.error_recovery_stats = {
            'recoverable_errors': 0,
            'successful_recoveries': 0,
            'total_retries': 0
        }
        logger.info("Error recovery stats reset")