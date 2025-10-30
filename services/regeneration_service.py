#!/usr/bin/env python3
"""
Regeneration Service - Modular auto-retry with quality validation

Clean, reusable service for automatic content regeneration on quality failures.
Works with any generator (FAQ, Caption, Subtitle) via callable pattern.

Architecture:
- Modular: Drop-in service like VoicePostProcessor
- Reusable: Works with any content generator
- Observable: Rich terminal logging for iteration tracking
- Configurable: Customizable max attempts and validation rules
"""

import logging
from typing import Callable, Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RegenerationConfig:
    """Configuration for regeneration behavior."""
    max_attempts: int = 3
    retry_on_quality_failure: bool = True
    retry_on_api_failure: bool = False  # Don't retry hard errors
    log_attempts: bool = True


class RegenerationService:
    """
    Modular service for automatic content regeneration on quality failures.
    
    Usage:
        service = RegenerationService(max_attempts=3)
        result = service.generate_with_retry(
            generator_func=lambda: generator.generate_once(...),
            validator_func=lambda content: validator.validate(content),
            context="FAQ for Steel"
        )
    """
    
    def __init__(self, config: Optional[RegenerationConfig] = None):
        """
        Initialize regeneration service.
        
        Args:
            config: Regeneration configuration (optional, uses defaults if None)
        """
        self.config = config or RegenerationConfig()
    
    def generate_with_retry(
        self,
        generator_func: Callable[[], Any],
        validator_func: Optional[Callable[[Any], Dict]] = None,
        context: str = "content",
        material_name: Optional[str] = None,
        author_name: Optional[str] = None
    ) -> Any:
        """
        Generate content with automatic retry on validation failures.
        
        Args:
            generator_func: Callable that generates content (returns result object)
            validator_func: Optional callable that validates content (returns validation dict)
            context: Description for logging (e.g., "FAQ for Steel")
            material_name: Material name for logging
            author_name: Author name for logging
            
        Returns:
            Result from successful generation, or final failed result
        """
        if self.config.log_attempts:
            self._log_start(context, material_name, author_name)
        
        last_result = None
        validation_report = None
        
        for attempt in range(1, self.config.max_attempts + 1):
            # Log attempt start
            if self.config.log_attempts:
                self._log_attempt(attempt, self.config.max_attempts, context)
            
            # Generate content
            result = generator_func()
            last_result = result
            
            # Check for hard errors (don't retry)
            if not result.success and not self._is_quality_error(result):
                if self.config.log_attempts:
                    self._log_hard_error(attempt, result.error_message)
                return result
            
            # Validate if validator provided
            if validator_func and result.success:
                try:
                    validation_report = validator_func(result.content)
                    
                    if validation_report.get('valid', True):
                        # Success!
                        if self.config.log_attempts:
                            self._log_success(
                                attempt, 
                                validation_report.get('quality_score', 100),
                                context
                            )
                        return result
                    else:
                        # Validation failed
                        if self.config.log_attempts:
                            self._log_quality_failure(
                                attempt,
                                self.config.max_attempts,
                                validation_report
                            )
                        
                        # Don't retry on last attempt
                        if attempt == self.config.max_attempts:
                            if self.config.log_attempts:
                                self._log_exhausted(self.config.max_attempts, context)
                            # Mark result as failed
                            result.success = False
                            result.error_message = self._format_validation_error(validation_report)
                            return result
                        
                        continue  # Retry
                
                except Exception as e:
                    logger.warning(f"⚠️  Validation failed with exception: {e}")
                    # Treat as success if validator errors
                    return result
            
            # No validator or generation failed - return as-is
            if result.success:
                if self.config.log_attempts:
                    self._log_success(attempt, None, context)
                return result
        
        # Should not reach here, but handle edge case
        if self.config.log_attempts:
            self._log_exhausted(self.config.max_attempts, context)
        return last_result
    
    def _is_quality_error(self, result) -> bool:
        """Check if error is quality-related (worth retrying)."""
        if not hasattr(result, 'error_message'):
            return False
        
        error_msg = result.error_message or ""
        quality_keywords = [
            "quality validation failed",
            "repetition",
            "variation",
            "word count",
            "too short",
            "too long"
        ]
        return any(keyword in error_msg.lower() for keyword in quality_keywords)
    
    def _format_validation_error(self, validation_report: Dict) -> str:
        """Format validation report into error message."""
        score = validation_report.get('quality_score', 0)
        errors = validation_report.get('errors', [])
        
        if errors:
            return f"Quality validation failed (score: {score}/100)\nErrors: {', '.join(errors[:3])}"
        return f"Quality validation failed (score: {score}/100)"
    
    # ========================================================================
    # TERMINAL LOGGING - Rich, observable output
    # ========================================================================
    
    def _log_start(self, context: str, material_name: Optional[str], author_name: Optional[str]):
        """Log generation start with context."""
        logger.info("")
        logger.info("━" * 70)
        logger.info(f"🔄 REGENERATION SERVICE")
        logger.info("━" * 70)
        logger.info(f"📝 Context: {context}")
        if material_name:
            logger.info(f"🧱 Material: {material_name}")
        if author_name:
            logger.info(f"✍️  Author: {author_name}")
        logger.info(f"⚙️  Max attempts: {self.config.max_attempts}")
        logger.info("━" * 70)
    
    def _log_attempt(self, attempt: int, max_attempts: int, context: str):
        """Log attempt start."""
        if attempt == 1:
            logger.info(f"🎯 Attempt {attempt}/{max_attempts}: Generating {context}...")
        else:
            logger.warning(f"🔄 Attempt {attempt}/{max_attempts}: Retrying generation...")
    
    def _log_success(self, attempt: int, quality_score: Optional[int], context: str):
        """Log successful generation."""
        logger.info("")
        logger.info("━" * 70)
        if quality_score is not None:
            logger.info(f"✅ SUCCESS on attempt {attempt}")
            logger.info(f"📊 Quality Score: {quality_score}/100")
        else:
            logger.info(f"✅ SUCCESS on attempt {attempt}")
        logger.info("━" * 70)
        logger.info("")
    
    def _log_quality_failure(self, attempt: int, max_attempts: int, validation_report: Dict):
        """Log quality validation failure."""
        score = validation_report.get('quality_score', 0)
        errors = validation_report.get('errors', [])
        warnings = validation_report.get('warnings', [])
        
        logger.warning("")
        logger.warning("━" * 70)
        logger.warning(f"⚠️  QUALITY VALIDATION FAILED - Attempt {attempt}/{max_attempts}")
        logger.warning("━" * 70)
        logger.warning(f"📊 Quality Score: {score}/100 (min: 60)")
        
        if errors:
            logger.warning(f"❌ Errors ({len(errors)}):")
            for i, error in enumerate(errors[:3], 1):  # Show first 3
                logger.warning(f"   {i}. {error}")
            if len(errors) > 3:
                logger.warning(f"   ... and {len(errors) - 3} more")
        
        if warnings and len(warnings) > 0:
            logger.warning(f"⚠️  Warnings ({len(warnings)}):")
            for i, warning in enumerate(warnings[:2], 1):  # Show first 2
                logger.warning(f"   {i}. {warning}")
        
        logger.warning("━" * 70)
        
        if attempt < max_attempts:
            logger.warning(f"🔄 Retrying... ({max_attempts - attempt} attempts remaining)")
        logger.warning("")
    
    def _log_hard_error(self, attempt: int, error_message: str):
        """Log hard error (non-retryable)."""
        logger.error("")
        logger.error("━" * 70)
        logger.error(f"❌ HARD ERROR on attempt {attempt} - NOT RETRYING")
        logger.error("━" * 70)
        logger.error(f"Error: {error_message}")
        logger.error("━" * 70)
        logger.error("")
    
    def _log_exhausted(self, max_attempts: int, context: str):
        """Log when all attempts exhausted."""
        logger.error("")
        logger.error("━" * 70)
        logger.error(f"❌ GENERATION FAILED - All {max_attempts} attempts exhausted")
        logger.error("━" * 70)
        logger.error(f"Unable to generate quality {context}")
        logger.error(f"Consider:")
        logger.error(f"  • Adjusting technical intensity")
        logger.error(f"  • Reducing voice intensity")
        logger.error(f"  • Reviewing material-specific constraints")
        logger.error("━" * 70)
        logger.error("")


# ============================================================================
# CONVENIENCE FACTORY
# ============================================================================

def create_regeneration_service(
    max_attempts: int = 3,
    retry_on_quality_failure: bool = True,
    log_attempts: bool = True
) -> RegenerationService:
    """
    Factory function for creating regeneration service.
    
    Args:
        max_attempts: Maximum generation attempts (default: 3)
        retry_on_quality_failure: Retry on quality validation failures (default: True)
        log_attempts: Enable rich terminal logging (default: True)
        
    Returns:
        Configured RegenerationService instance
    """
    config = RegenerationConfig(
        max_attempts=max_attempts,
        retry_on_quality_failure=retry_on_quality_failure,
        log_attempts=log_attempts
    )
    return RegenerationService(config)
