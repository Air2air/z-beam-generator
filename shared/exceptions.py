"""
Standardized Exception Classes

Provides consistent error handling across the Z-Beam Generator with:
- Clear error messages
- Actionable fix suggestions
- Documentation links
- Proper exception hierarchy

Usage:
    from shared.exceptions import ConfigurationError, DataError
    
    raise ConfigurationError(
        "Missing API key: GROK_API_KEY",
        fix="Add GROK_API_KEY to your .env file",
        doc_link="docs/01-getting-started/SETUP_GUIDE.md#api-keys"
    )

Created: December 20, 2025
"""

from typing import Optional


class ZBeamError(Exception):
    """
    Base exception for all Z-Beam Generator errors.
    
    Provides enhanced error messages with actionable guidance.
    """
    
    def __init__(
        self,
        message: str,
        fix: Optional[str] = None,
        doc_link: Optional[str] = None,
        context: Optional[dict] = None
    ):
        """
        Initialize error with enhanced context.
        
        Args:
            message: Clear description of what went wrong
            fix: Actionable steps to resolve the error
            doc_link: Path to relevant documentation
            context: Additional context (file paths, values, etc.)
        """
        self.message = message
        self.fix = fix
        self.doc_link = doc_link
        self.context = context or {}
        
        # Build formatted error message
        parts = [f"❌ {message}"]
        
        if fix:
            parts.append(f"\n\n✅ FIX: {fix}")
        
        if doc_link:
            parts.append(f"\n📖 DOCS: {doc_link}")
        
        if context:
            parts.append("\n\n📋 CONTEXT:")
            for key, value in context.items():
                parts.append(f"   {key}: {value}")
        
        super().__init__("".join(parts))


class ConfigurationError(ZBeamError):
    """
    Configuration file or setup error.
    
    Examples:
        - Missing config files
        - Invalid config structure
        - Missing required keys
        - Invalid paths
    """
    pass


class DataError(ZBeamError):
    """
    Data file or content error.
    
    Examples:
        - Missing data files
        - Invalid YAML structure
        - Missing required fields
        - Data validation failures
    """
    pass


class GenerationError(ZBeamError):
    """
    Content generation error.
    
    Examples:
        - API failures
        - Quality gate failures
        - Template errors
        - Parameter issues
    """
    pass


class ValidationError(ZBeamError):
    """
    Data or content validation error.
    
    Examples:
        - Schema validation failures
        - Integrity check failures
        - Link validation failures
        - Format validation failures
    """
    pass


class ExportError(ZBeamError):
    """
    Frontmatter export error.
    
    Examples:
        - Write failures
        - Enrichment failures
        - Generator failures
        - Path issues
    """
    pass


class APIError(ZBeamError):
    """
    External API error.
    
    Examples:
        - Missing API keys
        - Rate limiting
        - Network failures
        - Invalid responses
    """
    pass


# Convenience functions for common error patterns

def config_file_not_found(file_path: str, domain: str = None) -> ConfigurationError:
    """Standard error for missing config files"""
    context = {"file": str(file_path)}
    if domain:
        context["domain"] = domain
    
    return ConfigurationError(
        f"Configuration file not found: {file_path}",
        fix=f"Ensure config file exists at {file_path}",
        doc_link="docs/02-architecture/export-configuration.md",
        context=context
    )


def data_file_not_found(file_path: str, domain: str = None) -> DataError:
    """Standard error for missing data files"""
    context = {"file": str(file_path)}
    if domain:
        context["domain"] = domain
    
    return DataError(
        f"Data file not found: {file_path}",
        fix=f"Ensure data file exists at {file_path}. Run health check: python3 scripts/tools/health_check.py",
        doc_link="docs/05-data/DATA_ARCHITECTURE.md",
        context=context
    )


def api_key_missing(api_name: str, env_var: str) -> APIError:
    """Standard error for missing API keys"""
    return APIError(
        f"Missing API key: {api_name}",
        fix=f"Add {env_var} to your .env file. See setup guide for instructions.",
        doc_link="docs/01-getting-started/SETUP_GUIDE.md#api-keys",
        context={"api": api_name, "env_var": env_var}
    )


def validation_failed(item_name: str, errors: list) -> ValidationError:
    """Standard error for validation failures"""
    error_list = "\n   ".join(f"- {e}" for e in errors)
    
    return ValidationError(
        f"Validation failed for {item_name}",
        fix="Fix the validation errors listed below and try again",
        doc_link="docs/05-data/DATA_VALIDATION_STRATEGY.md",
        context={
            "item": item_name,
            "error_count": len(errors),
            "errors": error_list
        }
    )


def quality_gate_failed(component: str, score: float, threshold: float) -> GenerationError:
    """Standard error for quality gate failures"""
    return GenerationError(
        f"Quality gate failed for {component}",
        fix=f"Content quality ({score:.1f}) below threshold ({threshold:.1f}). Regenerate or adjust quality settings.",
        doc_link="docs/03-components/quality-scoring.md",
        context={
            "component": component,
            "score": score,
            "threshold": threshold
        }
    )
