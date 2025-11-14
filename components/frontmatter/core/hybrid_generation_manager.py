#!/usr/bin/env python3
"""
Hybrid Frontmatter Generation Manager

Separates frontmatter generation into:
1. Data-only mode: Refresh non-text data without AI calls (fast)
2. Text-only mode: Update text fields with optimized AI (Grok)
3. Hybrid mode: Mix data from Materials.yaml with AI text generation
4. Full mode: Generate everything (existing behavior)

This enables efficient generation patterns based on your requirements:
- Frequent data refreshes from Materials.yaml (no API cost)
- Optimized text generation with Grok for quality content
- DeepSeek for complex/comprehensive generation tasks
"""

from typing import Dict, Optional, Any
import logging
from enum import Enum
from pathlib import Path
import yaml

from .text_field_classifier import TextFieldClassifier, FieldType
from materials.data.materials import get_material_by_name_cached

class GenerationMode(Enum):
    """Frontmatter generation modes"""
    DATA_ONLY = "data_only"     # Refresh data from Materials.yaml only (no AI)
    TEXT_ONLY = "text_only"     # Update text fields with AI only (Grok)
    HYBRID = "hybrid"           # Data from YAML + AI text (recommended)
    FULL = "full"               # Complete AI generation (existing behavior)

class HybridFrontmatterManager:
    """Manages hybrid text/non-text frontmatter generation"""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.classifier = TextFieldClassifier()
        
    def generate_frontmatter(
        self,
        material_name: str,
        mode: GenerationMode = GenerationMode.HYBRID,
        text_api_client=None,  # Grok client for text generation
        full_api_client=None,  # DeepSeek client for full generation
        existing_frontmatter: Optional[Dict] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Generate frontmatter using specified mode
        
        Args:
            material_name: Name of material
            mode: Generation mode (data_only, text_only, hybrid, full)
            text_api_client: API client for text generation (Grok)
            full_api_client: API client for full generation (DeepSeek)
            existing_frontmatter: Existing frontmatter to update (optional)
            force_refresh: Force regeneration of existing fields
            
        Returns:
            Generated frontmatter dictionary
        """
        self.logger.info(f"Generating frontmatter for {material_name} in {mode.value} mode")
        
        if mode == GenerationMode.DATA_ONLY:
            return self._generate_data_only(material_name, existing_frontmatter)
            
        elif mode == GenerationMode.TEXT_ONLY:
            if not text_api_client:
                raise ValueError("text_api_client (Grok) required for text_only mode")
            return self._generate_text_only(
                material_name, text_api_client, existing_frontmatter, force_refresh
            )
            
        elif mode == GenerationMode.HYBRID:
            if not text_api_client:
                raise ValueError("text_api_client (Grok) required for hybrid mode")
            return self._generate_hybrid(
                material_name, text_api_client, existing_frontmatter, force_refresh
            )
            
        elif mode == GenerationMode.FULL:
            if not full_api_client:
                raise ValueError("full_api_client (DeepSeek) required for full mode")
            return self._generate_full(material_name, full_api_client)
            
        else:
            raise ValueError(f"Unknown generation mode: {mode}")

    def _generate_data_only(
        self, 
        material_name: str, 
        existing_frontmatter: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate frontmatter using only Materials.yaml data (no AI calls)
        Fast refresh for data updates without text regeneration
        """
        self.logger.info(f"📊 Data-only generation for {material_name} (no AI calls)")
        
        # Load material data from Materials.yaml
        material_data = get_material_by_name_cached(material_name)
        if not material_data:
            raise ValueError(f"Material {material_name} not found in Materials.yaml")
        
        # Start with existing frontmatter or empty dict
        frontmatter = existing_frontmatter.copy() if existing_frontmatter else {}
        
        # Populate data fields from Materials.yaml
        self._populate_data_fields(frontmatter, material_name, material_data)
        
        # Data-only mode complete - no metadata tracking needed
        
        self.logger.info(f"✅ Data-only generation complete - {len(frontmatter)} fields populated")
        return frontmatter

    def _generate_text_only(
        self,
        material_name: str,
        text_api_client,
        existing_frontmatter: Optional[Dict] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Update only text fields using AI (Grok) - preserves existing data
        Optimized for text quality improvements without data refresh
        """
        self.logger.info(f"📝 Text-only generation for {material_name} (Grok API)")
        
        if not existing_frontmatter:
            # Need existing frontmatter for text-only mode
            existing_path = self._get_frontmatter_path(material_name)
            if existing_path.exists():
                with open(existing_path) as f:
                    existing_frontmatter = yaml.safe_load(f)
            else:
                raise ValueError(f"No existing frontmatter found for {material_name} - use hybrid or full mode")
        
        frontmatter = existing_frontmatter.copy()
        
        # Get material data for text generation context
        material_data = get_material_by_name_cached(material_name)
        
        # Identify and generate text fields
        text_fields = self._identify_text_fields(frontmatter)
        generated_fields = []
        
        for field_path in text_fields:
            if not force_refresh and self._field_has_quality_content(frontmatter, field_path):
                self.logger.debug(f"Skipping {field_path} - already has quality content")
                continue
                
            try:
                new_value = self._generate_text_field(
                    field_path, material_name, material_data, text_api_client, frontmatter
                )
                self._set_nested_field(frontmatter, field_path, new_value)
                generated_fields.append(field_path)
                self.logger.info(f"✅ Generated text for {field_path}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to generate {field_path}: {e}")
        
        # Text-only mode complete
        
        self.logger.info(f"✅ Text-only generation complete - {len(generated_fields)} fields updated")
        return frontmatter

    def _generate_hybrid(
        self,
        material_name: str,
        text_api_client,
        existing_frontmatter: Optional[Dict] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Hybrid generation: Data from Materials.yaml + AI text from Grok
        Recommended mode for most use cases
        """
        self.logger.info(f"🔄 Hybrid generation for {material_name} (Materials.yaml + Grok)")
        
        # Step 1: Generate data-only foundation
        frontmatter = self._generate_data_only(material_name, existing_frontmatter)
        
        # Step 2: Enhance with AI text generation
        material_data = get_material_by_name_cached(material_name)
        text_fields = self._identify_text_fields(frontmatter)
        generated_fields = []
        
        for field_path in text_fields:
            if not force_refresh and self._field_has_quality_content(frontmatter, field_path):
                self.logger.debug(f"Skipping {field_path} - already has quality content")
                continue
                
            try:
                new_value = self._generate_text_field(
                    field_path, material_name, material_data, text_api_client, frontmatter
                )
                self._set_nested_field(frontmatter, field_path, new_value)
                generated_fields.append(field_path)
                self.logger.info(f"✅ Generated text for {field_path}")
                
            except Exception as e:
                self.logger.error(f"❌ Failed to generate {field_path}: {e}")
        
        # Hybrid mode complete
        
        self.logger.info(f"✅ Hybrid generation complete - data + {len(generated_fields)} AI text fields")
        return frontmatter

    def _generate_full(self, material_name: str, full_api_client) -> Dict[str, Any]:
        """
        Full AI generation using DeepSeek (existing behavior)
        Most comprehensive but slowest and most expensive
        """
        self.logger.info(f"🤖 Full AI generation for {material_name} (DeepSeek)")
        
        # This would integrate with existing StreamlinedFrontmatterGenerator
        # For now, return a placeholder indicating full generation
        frontmatter = {

            'ai_provider': 'deepseek',
            'note': 'Full AI generation - integrate with existing StreamlinedFrontmatterGenerator'
        }
        
        return frontmatter

    def _populate_data_fields(self, frontmatter: Dict, material_name: str, material_data: Dict) -> None:
        """Populate data fields from Materials.yaml"""
        
        # Basic material information
        frontmatter['name'] = material_name
        frontmatter['title'] = material_data.get('title', f"{material_name} Laser Cleaning")
        frontmatter['category'] = material_data.get('category', 'materials').title()
        frontmatter['subcategory'] = material_data.get('subcategory', material_name.lower())
        
        # Copy materialProperties structure directly (flat structure per frontmatter_template.yaml)
        mat_props = material_data.get('materialProperties', {})
        if mat_props:
            # Copy the entire materialProperties structure to frontmatter
            frontmatter['materialProperties'] = mat_props
        
        # Applications from industryTags
        if 'material_metadata' in material_data:
            metadata = material_data['material_metadata']
            if 'industryTags' in metadata:
                industry_tags = metadata['industryTags']
                if isinstance(industry_tags, list):
                    frontmatter['applications'] = industry_tags
                elif isinstance(industry_tags, dict):
                    apps = []
                    if 'primary_industries' in industry_tags:
                        apps.extend(industry_tags['primary_industries'])
                    if 'secondary_industries' in industry_tags:
                        apps.extend(industry_tags['secondary_industries'])
                    if apps:
                        frontmatter['applications'] = apps
        
        # Default applications if none found
        if 'applications' not in frontmatter:
            frontmatter['applications'] = []

    def _identify_text_fields(self, frontmatter: Dict) -> list:
        """Identify text fields that need AI generation"""
        classifications = self.classifier.classify_frontmatter_structure(frontmatter)
        text_fields = [
            field_path for field_path, field_type in classifications.items()
            if field_type == FieldType.TEXT
        ]
        return text_fields

    def _field_has_quality_content(self, frontmatter: Dict, field_path: str) -> bool:
        """Check if field already has quality content"""
        try:
            value = self._get_nested_field(frontmatter, field_path)
            if not value or not isinstance(value, str):
                return False
            
            # Simple quality checks
            if len(value.strip()) < 10:  # Too short
                return False
            if value.lower().startswith('todo') or 'placeholder' in value.lower():
                return False
            if value.count(' ') < 3:  # Not enough words
                return False
                
            return True
        except Exception:
            return False

    def _generate_text_field(
        self,
        field_path: str,
        material_name: str,
        material_data: Dict,
        api_client,
        context_frontmatter: Dict
    ) -> str:
        """Generate content for a specific text field using AI with enhanced prompting"""
        
        # Import the universal text enhancer
        try:
            from .universal_text_enhancer import EnhancedTextFieldManager
            enhancer = EnhancedTextFieldManager()
        except ImportError:
            self.logger.warning("Universal text enhancer not available, using basic prompts")
            enhancer = None
        
        # Build context-aware prompt for the specific field
        field_name = field_path.split('.')[-1]
        
        # Get base prompt
        if field_name == 'subtitle':
            # DEPRECATED: Use shared.prompts.text_prompt_builder.TextPromptBuilder instead
            base_prompt = self._build_subtitle_prompt_legacy(material_name, material_data, context_frontmatter)
        elif field_name == 'description':
            base_prompt = self._build_description_prompt(material_name, material_data, context_frontmatter)
        elif field_name in ['notes', 'explanation', 'methodology']:
            base_prompt = self._build_notes_prompt(field_path, material_name, material_data, context_frontmatter)
        else:
            base_prompt = self._build_generic_text_prompt(field_path, material_name, material_data, context_frontmatter)
        
        # Enhance prompt with universal text enhancer if available
        if enhancer:
            try:
                enhanced_prompt = enhancer.enhance_field_generation(
                    field_name=field_name,
                    base_prompt=base_prompt,
                    material_name=material_name,
                    material_data=material_data,
                    context_frontmatter=context_frontmatter
                )
                prompt = enhanced_prompt
                self.logger.debug(f"Enhanced prompt for {field_name} with author voice")
            except Exception as e:
                self.logger.warning(f"Failed to enhance prompt for {field_name}: {e}")
                prompt = base_prompt
        else:
            prompt = base_prompt
        
        # Generate with API client (Grok)
        try:
            response = api_client.generate_content(prompt, max_tokens=200, temperature=0.3)
            return response.strip()
        except Exception as e:
            self.logger.error(f"API generation failed for {field_path}: {e}")
            return f"Generated content for {field_name}"  # Fallback

    def _build_subtitle_prompt_legacy(self, material_name: str, material_data: Dict, context: Dict) -> str:
        """
        DEPRECATED: Legacy subtitle prompt builder.
        Use shared.prompts.text_prompt_builder.TextPromptBuilder instead.
        """
        category = material_data.get('category', 'material')
        return f"""Generate a concise, professional subtitle for laser cleaning {material_name} ({category}).

Context:
- Material: {material_name}
- Category: {category}
- Applications: {context.get('applications', [])}

Requirements:
- 8-15 words maximum
- Focus on laser cleaning parameters/specifications
- Professional tone
- No marketing language

Generate only the subtitle text, no quotes or explanations."""

    def _build_description_prompt(self, material_name: str, material_data: Dict, context: Dict) -> str:
        """Build prompt for description generation"""
        category = material_data.get('category', 'material')
        
        # Extract properties from materialProperties (flat structure)
        mat_props = material_data.get('materialProperties', {})
        properties = {}
        metadata_keys = {'label', 'description', 'percentage'}
        for cat in ['material_characteristics', 'laser_material_interaction']:
            cat_data = mat_props.get(cat, {})
            if isinstance(cat_data, dict):
                properties.update({k: v for k, v in cat_data.items() if k not in metadata_keys})
        
        return f"""Generate a professional description for laser cleaning {material_name}.

Context:
- Material: {material_name}
- Category: {category}
- Applications: {context.get('applications', [])}
- Properties: {properties}

Requirements:
- 20-40 words
- Technical but accessible
- Focus on laser cleaning benefits
- Mention key applications
- Professional tone

Generate only the description text, no quotes or explanations."""

    def _build_notes_prompt(self, field_path: str, material_name: str, material_data: Dict, context: Dict) -> str:
        """Build prompt for notes/explanation fields"""
        field_name = field_path.split('.')[-1]
        return f"""Generate technical {field_name} for laser cleaning {material_name}.

Context:
- Material: {material_name}
- Field: {field_name}
- Category: {material_data.get('category', 'material')}

Requirements:
- Technical accuracy
- 15-30 words
- Practical guidance
- Professional tone

Generate only the {field_name} text, no quotes or explanations."""

    def _build_generic_text_prompt(self, field_path: str, material_name: str, material_data: Dict, context: Dict) -> str:
        """Build generic prompt for text fields"""
        field_name = field_path.split('.')[-1]
        return f"""Generate content for {field_name} related to laser cleaning {material_name}.

Requirements:
- Technical accuracy
- 10-25 words
- Professional tone
- Relevant to laser cleaning

Generate only the text content, no quotes or explanations."""

    def _get_nested_field(self, data: Dict, field_path: str) -> Any:
        """Get value from nested field path"""
        keys = field_path.split('.')
        value = data
        for key in keys:
            if '[' in key:  # Handle array indices
                base_key = key.split('[')[0]
                index = int(key.split('[')[1].rstrip(']'))
                value = value[base_key][index]
            else:
                value = value[key]
        return value

    def _set_nested_field(self, data: Dict, field_path: str, value: Any) -> None:
        """Set value in nested field path"""
        keys = field_path.split('.')
        current = data
        
        # Navigate to parent
        for key in keys[:-1]:
            if '[' in key:  # Handle array indices
                base_key = key.split('[')[0]
                index = int(key.split('[')[1].rstrip(']'))
                current = current[base_key][index]
            else:
                if key not in current:
                    current[key] = {}
                current = current[key]
        
        # Set final value
        final_key = keys[-1]
        if '[' in final_key:  # Handle array indices
            base_key = final_key.split('[')[0]
            index = int(final_key.split('[')[1].rstrip(']'))
            current[base_key][index] = value
        else:
            current[final_key] = value

    def _get_frontmatter_path(self, material_name: str) -> Path:
        """Get path to frontmatter file"""
        safe_name = material_name.lower().replace(' ', '-').replace('_', '-')
        return Path(f"content/components/frontmatter/{safe_name}-laser-cleaning.yaml")

    def get_generation_recommendations(self, material_name: str) -> Dict[str, str]:
        """
        Get recommendations for which generation mode to use
        
        Returns:
            Dictionary with mode recommendations and reasons
        """
        recommendations = {}
        
        # Check if frontmatter exists
        frontmatter_path = self._get_frontmatter_path(material_name)
        has_frontmatter = frontmatter_path.exists()
        
        # Check if material data exists
        material_data = get_material_by_name_cached(material_name)
        has_material_data = material_data is not None
        
        if not has_material_data:
            recommendations['recommended'] = 'full'
            recommendations['reason'] = 'Material not found in Materials.yaml - requires full AI generation'
            
        elif not has_frontmatter:
            recommendations['recommended'] = 'hybrid'
            recommendations['reason'] = 'No existing frontmatter - hybrid mode provides best balance of speed and quality'
            
        else:
            # Analyze existing frontmatter
            try:
                with open(frontmatter_path) as f:
                    existing_fm = yaml.safe_load(f)
                
                text_fields = self._identify_text_fields(existing_fm)
                quality_text_fields = [
                    field for field in text_fields 
                    if self._field_has_quality_content(existing_fm, field)
                ]
                
                if len(quality_text_fields) < len(text_fields) * 0.5:
                    recommendations['recommended'] = 'text_only'
                    recommendations['reason'] = f'Existing frontmatter has poor text quality ({len(quality_text_fields)}/{len(text_fields)} fields)'
                else:
                    recommendations['recommended'] = 'data_only'
                    recommendations['reason'] = 'Existing frontmatter has good text - data refresh only needed'
                    
            except Exception as e:
                recommendations['recommended'] = 'hybrid'
                recommendations['reason'] = f'Error analyzing existing frontmatter: {e}'
        
        return recommendations


# Example usage
if __name__ == "__main__":
    import logging
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Create hybrid manager
    manager = HybridFrontmatterManager(logger)
    
    # Test recommendations
    material_name = "Aluminum"
    
    print("🎯 GENERATION RECOMMENDATIONS")
    print("=" * 50)
    
    recommendations = manager.get_generation_recommendations(material_name)
    for key, value in recommendations.items():
        print(f"{key:12s}: {value}")
    
    print("\n📊 GENERATION MODES COMPARISON")
    print("=" * 50)
    
    modes = [
        ("data_only", "📊 Fast data refresh from Materials.yaml (no AI cost)"),
        ("text_only", "📝 Update text fields with Grok AI (medium cost)"),
        ("hybrid", "🔄 Data + AI text generation (recommended balance)"),
        ("full", "🤖 Complete AI generation with DeepSeek (highest cost)")
    ]
    
    for mode, description in modes:
        print(f"{mode:10s}: {description}")