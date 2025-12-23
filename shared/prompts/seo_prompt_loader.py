"""
SEO Prompt Loader

Loads domain-specific SEO prompts from prompts/seo/*.txt files.
Each domain has its own prompt file with specific requirements and examples.

Domain Mapping:
  - materials → prompts/seo/material_page.txt
  - settings → prompts/seo/settings_page.txt
  - contaminants → prompts/seo/contaminant_page.txt
  - compounds → prompts/seo/compound_page.txt
"""

from pathlib import Path
from typing import Optional


class SEOPromptLoader:
    """Load domain-specific SEO generation prompts."""
    
    # Domain to prompt file mapping
    DOMAIN_PROMPTS = {
        'materials': 'material_page.txt',
        'settings': 'settings_page.txt',
        'contaminants': 'contaminant_page.txt',
        'compounds': 'compound_page.txt',
    }
    
    @classmethod
    def load_prompt(cls, domain: str, component_type: str) -> Optional[str]:
        """
        Load SEO prompt template for specified domain and component type.
        
        Args:
            domain: Domain name (materials, settings, contaminants, compounds)
            component_type: Component type (page_title, meta_description)
            
        Returns:
            Prompt template string or None if not found
            
        Raises:
            FileNotFoundError: If prompt file doesn't exist
            ValueError: If domain not supported
        """
        # Only load for SEO component types
        if component_type not in ['page_title', 'meta_description']:
            return None
        
        # Get prompt filename for domain
        if domain not in cls.DOMAIN_PROMPTS:
            raise ValueError(
                f"Unsupported domain: {domain}. "
                f"Available domains: {', '.join(cls.DOMAIN_PROMPTS.keys())}"
            )
        
        prompt_filename = cls.DOMAIN_PROMPTS[domain]
        
        # Path from shared/prompts/ to project root
        project_root = Path(__file__).parent.parent.parent
        prompt_path = project_root / 'prompts' / 'seo' / prompt_filename
        
        # Fail-fast: Prompt file must exist
        if not prompt_path.exists():
            raise FileNotFoundError(
                f"SEO prompt file not found: {prompt_path}. "
                f"Expected: prompts/seo/{prompt_filename}"
            )
        
        # Load prompt
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @classmethod
    def get_available_domains(cls) -> list[str]:
        """Get list of domains with SEO prompts available."""
        return list(cls.DOMAIN_PROMPTS.keys())
