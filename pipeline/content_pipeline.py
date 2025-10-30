"""
Universal Content Pipeline

End-to-end orchestration for researching and generating content of ANY type.
Works with any ContentSchema implementation (Material, Product, Service, etc.).

Author: AI Assistant
Date: October 29, 2025
"""

import logging
from typing import Dict, Any, Optional, Type
from pathlib import Path
import yaml
from datetime import datetime

from content.schemas.base import (
    ContentSchema,
    ContentResult,
    ComponentResult,
    ResearchResult,
    FieldResearchSpec
)
from research.factory import ResearcherFactory
from components.universal.text_generator import UniversalTextGenerator
from components.universal.faq_generator import UniversalFAQGenerator
from components.universal.caption_generator import UniversalCaptionGenerator
from components.universal.subtitle_generator import UniversalSubtitleGenerator


class ContentPipeline:
    """
    Universal pipeline for content research → generation → export.
    
    Works with ANY ContentSchema implementation through schema-driven design.
    
    Pipeline Flow:
        1. Initialize content schema (from name or existing data)
        2. Research missing fields (AI-powered discovery)
        3. Generate components (FAQ, caption, subtitle, etc.)
        4. Assemble frontmatter (combine all data)
        5. Export to YAML (save to content file)
    
    Example:
        # Process new material
        pipeline = ContentPipeline(api_client=client)
        result = pipeline.process(
            content_name="Titanium",
            content_schema_class=MaterialContent,
            category="metal"
        )
        
        # Process with existing data
        result = pipeline.process(
            content_name="Steel",
            content_schema_class=MaterialContent,
            existing_data=steel_data
        )
    """
    
    def __init__(
        self,
        api_client: Any,
        categories_file: str = "data/Categories.yaml",
        output_base_dir: str = "content"
    ):
        """
        Initialize universal content pipeline.
        
        Args:
            api_client: API client for AI research/generation
            categories_file: Path to Categories.yaml
            output_base_dir: Base directory for output files
        """
        self.api_client = api_client
        self.logger = logging.getLogger(__name__)
        
        # Load Categories.yaml (shared across all content types)
        self.categories_data = self._load_categories(categories_file)
        
        # Initialize factories and generators
        self.researcher_factory = ResearcherFactory()
        self.text_generator = UniversalTextGenerator(api_client)
        self.faq_generator = UniversalFAQGenerator(api_client)
        self.caption_generator = UniversalCaptionGenerator(api_client)
        self.subtitle_generator = UniversalSubtitleGenerator(api_client)
        
        # Output configuration
        self.output_base = Path(output_base_dir)
        self.output_base.mkdir(parents=True, exist_ok=True)
    
    def _load_categories(self, categories_file: str) -> Dict:
        """Load Categories.yaml"""
        categories_path = Path(categories_file)
        
        if not categories_path.exists():
            raise FileNotFoundError(f"Categories.yaml not found: {categories_file}")
        
        with open(categories_path, 'r') as f:
            data = yaml.safe_load(f)
        
        self.logger.info(f"✅ Loaded {len(data.get('categories', {}))} categories")
        return data
    
    def process(
        self,
        content_name: str,
        content_schema_class: Type[ContentSchema],
        category: Optional[str] = None,
        existing_data: Optional[Dict] = None,
        skip_research: bool = False,
        skip_components: bool = False
    ) -> ContentResult:
        """
        Complete pipeline from name to frontmatter.
        
        Args:
            content_name: Name of content item (e.g., "Steel", "TruLaser 3030")
            content_schema_class: Schema class (MaterialContent, ProductContent, etc.)
            category: Category for new content (required if no existing_data)
            existing_data: Existing content data to update/enhance
            skip_research: Skip research phase (use existing data only)
            skip_components: Skip component generation (research only)
        
        Returns:
            ContentResult with frontmatter and export info
        """
        content_type = content_schema_class.__name__.replace('Content', '').lower()
        
        self.logger.info(f"🚀 Processing {content_name} ({content_type})")
        
        try:
            # Step 1: Initialize content schema
            content = self._initialize_content(
                content_name,
                content_schema_class,
                category,
                existing_data
            )
            
            # Step 2: Research missing fields
            research_results = {}
            if not skip_research and content.needs_research():
                self.logger.info("🔬 Researching missing data...")
                research_results = self._research_missing_fields(content)
                content = self._apply_research(content, research_results)
            
            # Step 3: Generate components
            components = {}
            if not skip_components:
                self.logger.info("🎨 Generating components...")
                components = self._generate_components(content)
                content = self._apply_components(content, components)
            
            # Step 4: Validate completeness
            is_valid, errors = content.validate()
            if not is_valid:
                self.logger.warning(f"⚠️ Validation warnings: {'; '.join(errors)}")
            
            # Step 5: Export to YAML
            self.logger.info("💾 Exporting...")
            export_path = self._export_content(content_name, content)
            
            # Step 6: Generate frontmatter
            self.logger.info("📦 Assembling frontmatter...")
            frontmatter = self._assemble_frontmatter(content)
            
            return ContentResult(
                content_name=content_name,
                content_type=content_type,
                frontmatter=frontmatter,
                export_path=export_path,
                success=True,
                components=components,
                research_results=research_results
            )
        
        except Exception as e:
            self.logger.error(f"❌ Pipeline failed: {e}")
            return ContentResult(
                content_name=content_name,
                content_type=content_type,
                frontmatter={},
                success=False,
                error_message=str(e)
            )
    
    def _initialize_content(
        self,
        content_name: str,
        content_schema_class: Type[ContentSchema],
        category: Optional[str],
        existing_data: Optional[Dict]
    ) -> ContentSchema:
        """Initialize content schema from existing data or create new"""
        
        if existing_data:
            # Load from existing data
            content = content_schema_class.from_dict(existing_data)
            self.logger.info(f"📂 Loaded existing data")
        else:
            # Create new content
            if not category:
                raise ValueError("category required for new content")
            
            content_type = content_schema_class.__name__.replace('Content', '').lower()
            
            content = content_schema_class(
                content_type=content_type,
                name=content_name,
                category=category,
                title=f"{content_name}",
                description="",
                author=self._get_default_author()
            )
            self.logger.info(f"✨ Created new {content_type} content")
        
        return content
    
    def _research_missing_fields(
        self,
        content: ContentSchema
    ) -> Dict[str, ResearchResult]:
        """Research all missing researchable fields"""
        results = {}
        
        # Get fields to research (sorted by priority)
        research_priorities = content.get_research_priorities()
        
        for field_name, field_spec in research_priorities:
            # Check if field needs research
            current_value = getattr(content, field_name, None)
            
            if self._field_needs_research(current_value, field_spec):
                self.logger.info(f"  🔍 Researching {field_name}...")
                
                # Create appropriate researcher
                researcher = self.researcher_factory.create_researcher(
                    field_spec.field_type,
                    self.api_client
                )
                
                # Research the field
                result = researcher.research(
                    content.name,
                    field_spec,
                    context={
                        'category': content.category,
                        'content_type': content.content_type
                    }
                )
                
                results[field_name] = result
                
                if result.success:
                    self.logger.info(f"    ✅ Found {field_name} (confidence: {result.confidence:.2f})")
                else:
                    self.logger.warning(f"    ⚠️ Failed: {result.error_message}")
        
        return results
    
    def _field_needs_research(self, value: Any, spec: FieldResearchSpec) -> bool:
        """Check if field needs research"""
        if value is None or value == "":
            return True
        
        if isinstance(value, (list, dict)) and not value:
            return True
        
        return False
    
    def _apply_research(
        self,
        content: ContentSchema,
        research_results: Dict[str, ResearchResult]
    ) -> ContentSchema:
        """Apply research results to content"""
        for field_name, result in research_results.items():
            if result.success:
                setattr(content, field_name, result.data)
        
        return content
    
    def _generate_components(
        self,
        content: ContentSchema
    ) -> Dict[str, ComponentResult]:
        """Generate all required components"""
        components = {}
        
        required_components = content.get_component_requirements()
        
        for component_type in required_components:
            self.logger.info(f"  🎨 Generating {component_type}...")
            
            generator = self._get_component_generator(component_type)
            result = generator.generate(content, component_type)
            components[component_type] = result
            
            if result.success:
                self.logger.info(f"    ✅ Generated {component_type}")
            else:
                self.logger.warning(f"    ⚠️ Failed: {result.error_message}")
        
        return components
    
    def _get_component_generator(self, component_type: str):
        """Get appropriate component generator"""
        generators = {
            'text': self.text_generator,
            'faq': self.faq_generator,
            'caption': self.caption_generator,
            'subtitle': self.subtitle_generator
        }
        
        generator = generators.get(component_type)
        if not generator:
            raise ValueError(f"Unknown component type: {component_type}")
        
        return generator
    
    def _apply_components(
        self,
        content: ContentSchema,
        components: Dict[str, ComponentResult]
    ) -> ContentSchema:
        """Apply generated components to content"""
        for component_type, result in components.items():
            if result.success and hasattr(content, component_type):
                # Parse YAML content if needed
                if component_type in ['faq', 'caption']:
                    component_data = yaml.safe_load(result.content)
                else:
                    component_data = result.content
                
                setattr(content, component_type, component_data)
        
        return content
    
    def _export_content(self, content_name: str, content: ContentSchema) -> str:
        """Export content to YAML file"""
        # Determine output path
        output_dir = self.output_base / "data"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"{content.content_type}s.yaml"
        
        # Load existing data if file exists
        if output_file.exists():
            with open(output_file, 'r') as f:
                all_data = yaml.safe_load(f) or {}
        else:
            all_data = {f'{content.content_type}s': {}}
        
        # Update with new content
        content_key = f'{content.content_type}s'
        if content_key not in all_data:
            all_data[content_key] = {}
        
        all_data[content_key][content_name] = content.to_dict()
        
        # Write back to file
        with open(output_file, 'w') as f:
            yaml.dump(all_data, f, default_flow_style=False, sort_keys=False)
        
        self.logger.info(f"💾 Saved to {output_file}")
        return str(output_file)
    
    def _assemble_frontmatter(self, content: ContentSchema) -> Dict[str, Any]:
        """Assemble complete frontmatter from content"""
        frontmatter = content.to_dict()
        
        # Add timestamp
        frontmatter['generated_date'] = datetime.now().isoformat()
        
        return frontmatter
    
    def _get_default_author(self) -> Dict[str, Any]:
        """Get default author (for new content)"""
        # TODO: Implement author assignment logic
        return {
            'id': 1,
            'name': 'Dr. Sarah Chen',
            'country': 'Taiwan',
            'expertise': 'Materials Science and Laser Technology'
        }
