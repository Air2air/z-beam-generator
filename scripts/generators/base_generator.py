"""
Base Generator for Source Data Population

Abstract base class for all generators that populate computed fields
in source YAML files (Materials.yaml, Contaminants.yaml, etc.).

Unlike enrichers (which run during export), generators run independently
and modify source data directly, creating a single source of truth.

Architecture:
- External prompts (prompts/*.txt files, never in code)
- Dependency ordering (coordinators handle dependencies)
- Atomic writes (backup → generate → verify → save)
- Incremental updates (only process changed items)

Usage:
    class SlugGenerator(BaseGenerator):
        def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
            for item_id, item_data in data.items():
                if 'slug' not in item_data:
                    item_data['slug'] = item_id
            return data
        
        def get_generated_fields(self) -> List[str]:
            return ['slug']
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import logging

logger = logging.getLogger(__name__)


class BaseGenerator(ABC):
    """
    Abstract base for all source data generators.
    
    Generators populate computed fields in source YAML files.
    All generators must:
    1. Use external prompt files (never inline text)
    2. Declare generated fields
    3. Validate dependencies
    4. Handle incremental updates
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize generator with configuration.
        
        Args:
            config: Configuration dict with keys:
                - domain: Domain name (materials, contaminants, etc.)
                - project_root: Path to project root (optional)
                - dry_run: If True, don't modify data (optional)
        """
        self.config = config
        self.domain = config.get('domain', '')
        self.project_root = Path(config.get('project_root', Path.cwd()))
        self.dry_run = config.get('dry_run', False)
        
        # Prompt directory (if generator uses prompts)
        self.prompts_dir = self.project_root / 'scripts' / 'generators' / 'prompts'
        
        logger.debug(f"Initialized {self.__class__.__name__} for domain: {self.domain}")
    
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate and populate fields in source data.
        
        Args:
            data: Domain data dict (e.g., all materials)
        
        Returns:
            Updated data dict with generated fields
        """
        pass
    
    @abstractmethod
    def get_generated_fields(self) -> List[str]:
        """
        Return list of field names this generator populates.
        
        Used for validation and documentation.
        
        Returns:
            List of field names (e.g., ['slug', 'url'])
        """
        pass
    
    def validate_dependencies(self, data: Dict[str, Any]) -> bool:
        """
        Check if required fields exist for generation.
        
        Override if generator has dependencies.
        
        Args:
            data: Domain data dict
        
        Returns:
            True if all dependencies satisfied
        """
        return True
    
    def get_dependencies(self) -> List[str]:
        """
        Return list of field names this generator depends on.
        
        Override if generator has dependencies (e.g., URL needs slug).
        
        Returns:
            List of field names (e.g., ['slug'])
        """
        return []
    
    def needs_update(self, item_data: Dict[str, Any]) -> bool:
        """
        Check if item needs fields generated/updated.
        
        Used for incremental updates.
        
        Args:
            item_data: Single item data dict
        
        Returns:
            True if item is missing generated fields
        """
        generated_fields = self.get_generated_fields()
        return any(field not in item_data for field in generated_fields)
    
    def _load_prompt(self, prompt_name: str) -> str:
        """
        Load prompt from external .txt file.
        
        ALL prompts must be external files, never inline in code.
        
        Args:
            prompt_name: Prompt filename (without .txt extension)
        
        Returns:
            Prompt template string
        
        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_file = self.prompts_dir / f"{prompt_name}.txt"
        
        if not prompt_file.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {prompt_file}\n"
                f"All prompts must be external .txt files in {self.prompts_dir}"
            )
        
        with open(prompt_file, 'r') as f:
            return f.read()
    
    def _log_progress(self, message: str, item_count: int = None):
        """
        Log generation progress.
        
        Args:
            message: Progress message
            item_count: Number of items processed (optional)
        """
        if item_count is not None:
            logger.info(f"{self.__class__.__name__}: {message} ({item_count} items)")
        else:
            logger.info(f"{self.__class__.__name__}: {message}")
        
        if not self.dry_run:
            print(f"  • {message}")


class GeneratorError(Exception):
    """Raised when generator encounters an error"""
    pass


class DependencyError(GeneratorError):
    """Raised when generator dependencies not satisfied"""
    pass


class PromptError(GeneratorError):
    """Raised when prompt file is missing or invalid"""
    pass
