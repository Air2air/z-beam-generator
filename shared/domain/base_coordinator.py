"""
Domain Coordinator Base Class

Provides common initialization and generation orchestration for all domains.
Eliminates duplication across materials, compounds, contaminants, settings coordinators.

Architecture:
- Handles API client, Winston, and evaluator initialization
- Loads domain configs (domains/{domain}/config.yaml)
- Orchestrates QualityEvaluatedGenerator pipeline
- Manages data loading through subclass-defined data loaders
- Provides common generation flow with domain-specific customization points

Created: December 24, 2025
Purpose: Consolidate ~400 lines of duplicated coordinator code
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from generation.core.evaluated_generator import QualityEvaluatedGenerator
from postprocessing.evaluation.subjective_evaluator import SubjectiveEvaluator

logger = logging.getLogger(__name__)


class DomainCoordinator(ABC):
    """
    Base class for all domain coordinators (materials, compounds, contaminants, settings).
    
    Provides:
    - Winston client initialization (with graceful degradation)
    - QualityEvaluatedGenerator setup
    - SubjectiveEvaluator setup
    - Domain config loading from domains/{domain}/config.yaml
    - Common generation orchestration flow
    
    Subclasses must implement:
    - domain_name: str property
    - _create_data_loader(): Initialize domain-specific data loader
    - _get_item_data(item_id: str): Get specific item data
    - _save_content(item_id: str, component_type: str, content: str): Save generated content
    """
    
    def __init__(self, api_client=None):
        """
        Initialize coordinator with common components.
        
        Args:
            api_client: API client for content generation (optional for testing/inspection mode)
        """
        # Module-level logger accessible as self.logger for subclasses
        self.logger = logging.getLogger(self.__class__.__module__ + '.' + self.__class__.__name__)

        # Data loader (domain-specific, created by subclass)
        self.data_loader = self._create_data_loader()
        
        # Generation components (only if api_client provided)
        if api_client:
            self.api_client = api_client
            
            # Initialize SubjectiveEvaluator
            self.subjective_evaluator = SubjectiveEvaluator(api_client)
            
            # Initialize Winston client (fail-fast)
            from shared.api.client_factory import APIClientFactory
            self.winston_client = APIClientFactory.create_client(provider="winston")
            logger.info("✅ Winston client initialized")
            
            # Initialize QualityEvaluatedGenerator with domain
            self.generator = QualityEvaluatedGenerator(
                api_client=api_client,
                subjective_evaluator=self.subjective_evaluator,
                winston_client=self.winston_client,
                domain=self.domain_name
            )
            
            logger.info(f"✅ {self.__class__.__name__} initialized with generation pipeline")
        else:
            # Testing/inspection mode - no generation capabilities
            self.api_client = None
            self.generator = None
            self.subjective_evaluator = None
            self.winston_client = None
            logger.info(f"{self.__class__.__name__} initialized in inspection mode (no generation)")
        
        # Load domain config
        self._load_domain_config()
        
    @property
    @abstractmethod
    def domain_name(self) -> str:
        """Return domain name (e.g., 'materials', 'compounds', 'contaminants', 'settings')"""
        pass
    
    @abstractmethod
    def _create_data_loader(self):
        """
        Create and return domain-specific data loader.
        
        Returns:
            Domain-specific data loader instance
        """
        pass
    
    @abstractmethod
    def _get_item_data(self, item_id: str) -> Dict:
        """
        Get data for specific item from domain.
        
        Args:
            item_id: Item identifier (material name, compound id, etc.)
            
        Returns:
            Dict containing item data
            
        Raises:
            ValueError: If item not found
        """
        pass
    
    @abstractmethod
    def _save_content(self, item_id: str, component_type: str, content: str, author_id: Optional[int] = None) -> None:
        """
        Save generated content to domain data file.
        
        Args:
            item_id: Item identifier
            component_type: Type of content (description, micro, faq, etc.)
            content: Generated text content
            author_id: Optional author ID to save
            
        Raises:
            IOError: If save fails
        """
        pass
    
    def _load_domain_config(self) -> None:
        """Load domain configuration from domains/{domain}/config.yaml"""
        # Find project root (where domains/ directory is located)
        # Navigate from shared/domain/ up to project root
        project_root = Path(__file__).parent.parent.parent
        domain_config_path = project_root / "domains" / self.domain_name / "config.yaml"
        
        if not domain_config_path.exists():
            raise FileNotFoundError(
                f"Domain config not found: {domain_config_path}\n"
                f"Expected: domains/{self.domain_name}/config.yaml"
            )
        
        with open(domain_config_path, 'r') as f:
            self.domain_config = yaml.safe_load(f)
        
        logger.debug(f"Loaded config from {domain_config_path}")
    
    def _load_domain_data(self) -> Dict[str, Any]:
        """
        Load domain data from configured data file.
        
        Uses domain config's data_adapter.data_path to locate and load data.
        Provides unified data loading across all domains (eliminates duplicate methods).
        
        Returns:
            Dict containing full domain data from YAML file
        
        Raises:
            FileNotFoundError: If data file doesn't exist
            ValueError: If config missing data_adapter or data_path
        
        Example:
            >>> # MaterialsCoordinator
            >>> data = self._load_domain_data()
            >>> materials = data['materials']
            
            >>> # ContaminantCoordinator  
            >>> data = self._load_domain_data()
            >>> patterns = data['contamination_patterns']
        """
        # Get data path from config (supports both nested and flat structure)
        if 'data_adapter' in self.domain_config:
            data_path = self.domain_config['data_adapter'].get('data_path')
        elif 'data_path' in self.domain_config:
            data_path = self.domain_config['data_path']
        else:
            raise ValueError(
                f"Domain config missing data_adapter.data_path or data_path: {self.domain_name}"
            )
        
        if not data_path:
            raise ValueError(f"Empty data_path in config for domain: {self.domain_name}")
        
        # Resolve path relative to project root
        project_root = Path(__file__).parent.parent.parent
        full_path = project_root / data_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"Domain data file not found: {full_path}")
        
        # Load YAML
        with open(full_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        logger.debug(f"Loaded domain data from {full_path}")
        return data
    
    def generate_content(
        self,
        item_id: str,
        component_type: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate content for specific item and component type.
        
        Universal generation flow:
        1. Validate generator is available
        2. Load item data
        3. Call QualityEvaluatedGenerator.generate() (always regenerates)
        4. Save generated content
        5. Return results
        
        Args:
            item_id: Item identifier (material name, compound id, etc.)
            component_type: Type of content to generate (description, micro, faq, etc.)
            force_regenerate: Legacy compatibility flag (generation always regenerates)
            
        Returns:
            Dict with generation results:
                - success: bool
                - content: str (generated text)
                - component_type: str
                - item_id: str
                - author_id: int
                - quality_scores: dict
                - attempts: int
                
        Raises:
            ValueError: If item not found or component type invalid
            RuntimeError: If generation fails or coordinator not configured for generation
        """
        if not self.generator:
            raise RuntimeError(
                f"{self.__class__.__name__} not configured for generation "
                "(initialized without api_client)"
            )
        
        # Load item data
        try:
            item_data = self._get_item_data(item_id)
        except Exception as e:
            raise ValueError(f"Failed to load {self.domain_name} item '{item_id}': {e}")
        
        # Get author ID from item data
        author_id = item_data.get('author', {}).get('id') if isinstance(item_data.get('author'), dict) else item_data.get('author')
        
        # Generate content using QualityEvaluatedGenerator
        logger.info(f"Generating {component_type} for {self.domain_name} item: {item_id}")
        
        result = self.generator.generate(
            material_name=item_id,  # Note: parameter name is 'material_name' for historical reasons, works for all domains
            component_type=component_type,
            author_id=author_id
        )
        
        if not result.success:
            error_msg = result.error_message or "Unknown error"
            raise RuntimeError(f"Generation failed: {error_msg}")
        
        # Save generated content
        try:
            self._save_content(item_id, component_type, result.content, author_id)
            logger.info(f"✅ Saved {component_type} for {item_id}")
        except Exception as e:
            logger.error(f"Failed to save content: {e}")
            raise
        
        # Return result with additional metadata
        return {
            'success': True,
            'content': result.content,
            'component_type': component_type,
            'item_id': item_id,
            'author_id': author_id,
            'quality_scores': getattr(result, 'quality_scores', None),
            'attempts': getattr(result, 'attempts', 1)
        }
    
    def get_item_list(self) -> list:
        """
        Get list of all items in domain.
        
        Returns:
            List of item identifiers
        """
        return self.data_loader.get_all_items() if hasattr(self.data_loader, 'get_all_items') else []
    
    def validate_component_type(self, component_type: str) -> bool:
        """
        Check if component type is valid for this domain.
        
        Args:
            component_type: Component type to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if prompt template exists
        project_root = Path(__file__).parent.parent.parent
        prompt_dir = project_root / "prompts" / self.domain_name
        prompt_file = prompt_dir / f"{component_type}.txt"
        return prompt_file.exists()

    def list_component_types(self) -> List[str]:
        """
        Discover all component types available for this domain from prompts directory.

        Returns:
            Sorted list of component type names derived from prompts/{domain}/*.txt filenames.
        """
        project_root = Path(__file__).parent.parent.parent
        prompt_dir = project_root / "prompts" / self.domain_name
        if not prompt_dir.exists():
            return []
        return sorted(f.stem for f in prompt_dir.glob("*.txt"))

    def generate_all_components(
        self,
        item_id: str,
        force_regenerate: bool = False
    ) -> Dict[str, Any]:
        """
        Generate all component types for an item using prompt-directory discovery.

        Domain-agnostic: discovers types from prompts/{domain}/*.txt at runtime.
        All domains inherit this; no per-domain override needed.

        Args:
            item_id: Item identifier (material name, compound id, etc.)
            force_regenerate: Whether to regenerate existing content

        Returns:
            Dict mapping component_type -> generation result dict
        """
        component_types = self.list_component_types()
        logger.info(
            f"Generating {len(component_types)} component types for {item_id}: "
            f"{component_types}"
        )
        results = {}
        for component_type in component_types:
            try:
                results[component_type] = self.generate_content(
                    item_id, component_type, force_regenerate
                )
            except Exception as e:
                logger.error(
                    f"Failed to generate {component_type} for {item_id}: {e}"
                )
                results[component_type] = {"success": False, "error": str(e)}
        return results
