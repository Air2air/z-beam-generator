#!/usr/bin/env python3
"""
Unified Frontmatter Generator with Component Orchestration
Generates frontmatter with embedded component outputs by orchestrating 
individual component generators.
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

# Add the project root to the Python path
project_root = Path(__file__).parents[3]
sys.path.insert(0, str(project_root))

# Import component generators
from components.caption.generators.generator import CaptionComponentGenerator
from components.jsonld.generator import JsonldComponentGenerator  
from components.metatags.generator import MetatagsComponentGenerator
from components.tags.generator import TagsComponentGenerator
from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator

logger = logging.getLogger(__name__)

class UnifiedFrontmatterGenerator:
    """
    Enhanced frontmatter generator that orchestrates component generators
    to produce unified frontmatter files with embedded component outputs.
    """
    
    def __init__(self):
        # Initialize component generators
        self.caption_generator = CaptionComponentGenerator()
        self.jsonld_generator = JsonldComponentGenerator()
        self.metatags_generator = MetatagsComponentGenerator()
        self.tags_generator = TagsComponentGenerator()
        self.base_frontmatter_generator = StreamlinedFrontmatterGenerator()
        
        # Define which components to generate by default
        self.default_components = ["caption", "jsonld", "metatags", "tags"]
        
        # Component generation order (some may depend on others)
        self.generation_order = ["caption", "jsonld", "metatags", "tags"]
    
    def generate_unified_frontmatter(self, material_name: str, 
                                   components: Optional[List[str]] = None,
                                   api_client=None,
                                   **kwargs) -> Dict[str, Any]:
        """
        Generate unified frontmatter with embedded component outputs.
        
        Args:
            material_name: Name of the material to generate for
            components: List of components to generate (default: all supported)
            api_client: API client for AI-generated components
            **kwargs: Additional arguments passed to generators
            
        Returns:
            Complete frontmatter data with embedded componentOutputs
        """
        
        # Use default components if none specified
        if components is None:
            components = self.default_components.copy()
        
        logger.info(f"Generating unified frontmatter for {material_name} with components: {components}")
        
        # Step 1: Generate base frontmatter data
        base_frontmatter = self._generate_base_frontmatter(material_name, **kwargs)
        
        if not base_frontmatter:
            logger.error(f"Failed to generate base frontmatter for {material_name}")
            return {}
        
        # Step 2: Initialize componentOutputs section
        base_frontmatter['componentOutputs'] = {}
        
        # Step 3: Generate each component in order
        generation_results = {}
        
        for component_type in self.generation_order:
            if component_type not in components:
                continue
                
            try:
                logger.info(f"Generating {component_type} component for {material_name}")
                
                component_output = self._generate_component_output(
                    component_type, 
                    material_name, 
                    base_frontmatter,
                    api_client=api_client,
                    **kwargs
                )
                
                if component_output:
                    base_frontmatter['componentOutputs'][component_type] = component_output
                    generation_results[component_type] = {
                        "status": "success",
                        "size": len(str(component_output))
                    }
                    logger.info(f"✅ Generated {component_type} component ({generation_results[component_type]['size']} chars)")
                else:
                    generation_results[component_type] = {
                        "status": "failed",
                        "error": "Empty output from generator"
                    }
                    logger.warning(f"❌ Failed to generate {component_type} component - empty output")
                    
            except Exception as e:
                generation_results[component_type] = {
                    "status": "failed", 
                    "error": str(e)
                }
                logger.error(f"❌ Failed to generate {component_type} component: {e}")
        
        # Step 4: Add generation metadata
        base_frontmatter['generationMetadata'] = {
            "generatedAt": datetime.now().isoformat(),
            "method": "unified_orchestration",
            "componentsRequested": components,
            "componentsGenerated": list(base_frontmatter['componentOutputs'].keys()),
            "generationResults": generation_results,
            "totalComponents": len(base_frontmatter['componentOutputs']),
            "unifiedGenerator": "v1.0.0"
        }
        
        logger.info(f"✅ Unified frontmatter generation complete for {material_name}")
        logger.info(f"   📊 Generated {len(base_frontmatter['componentOutputs'])} components")
        logger.info(f"   📏 Total size: {len(str(base_frontmatter)):,} characters")
        
        return base_frontmatter
    
    def _generate_base_frontmatter(self, material_name: str, **kwargs) -> Dict[str, Any]:
        """Generate the base frontmatter data using existing generator."""
        
        try:
            # Use the existing streamlined frontmatter generator
            result = self.base_frontmatter_generator.generate(material_name, {}, **kwargs)
            
            if hasattr(result, 'success') and result.success:
                # Parse the YAML content if it's a string
                if isinstance(result.content, str):
                    return yaml.safe_load(result.content)
                elif isinstance(result.content, dict):
                    return result.content
                else:
                    logger.error(f"Unexpected frontmatter content type: {type(result.content)}")
                    return {}
            else:
                logger.error(f"Base frontmatter generation failed for {material_name}")
                return {}
                
        except Exception as e:
            logger.error(f"Error generating base frontmatter for {material_name}: {e}")
            return {}
    
    def _generate_component_output(self, component_type: str, material_name: str, 
                                 frontmatter_data: Dict[str, Any], 
                                 api_client=None, **kwargs) -> Optional[Dict[str, Any]]:
        """Generate output for a specific component type."""
        
        # Prepare material data from frontmatter
        material_data = {
            "name": material_name,
            "frontmatter": frontmatter_data
        }
        
        try:
            if component_type == "caption":
                return self._generate_caption_output(material_name, material_data, frontmatter_data, api_client)
            
            elif component_type == "jsonld":
                return self._generate_jsonld_output(material_name, material_data, frontmatter_data)
            
            elif component_type == "metatags":
                return self._generate_metatags_output(material_name, material_data, frontmatter_data)
            
            elif component_type == "tags":
                return self._generate_tags_output(material_name, material_data, frontmatter_data)
            
            else:
                logger.warning(f"Unknown component type: {component_type}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating {component_type} output: {e}")
            return None
    
    def _generate_caption_output(self, material_name: str, material_data: Dict[str, Any], 
                               frontmatter_data: Dict[str, Any], api_client) -> Optional[Dict[str, Any]]:
        """Generate caption component output."""
        
        if not api_client:
            logger.warning("No API client provided for caption generation - skipping")
            return None
        
        try:
            result = self.caption_generator.generate(
                material_name, 
                material_data, 
                frontmatter_data=frontmatter_data,
                api_client=api_client
            )
            
            if hasattr(result, 'success') and result.success:
                # Parse the caption content and transform to embedded format
                if isinstance(result.content, str):
                    caption_data = yaml.safe_load(result.content)
                else:
                    caption_data = result.content
                
                # Transform to embedded format
                return {
                    "beforeText": caption_data.get("before_text", ""),
                    "afterText": caption_data.get("after_text", ""),
                    "technicalAnalysis": caption_data.get("technical_analysis", {}),
                    "microscopy": caption_data.get("microscopy", {}),
                    "seo": caption_data.get("seo", {}),
                    "processing": caption_data.get("processing", {}),
                    "generation": {
                        "generated": datetime.now().isoformat(),
                        "componentType": "ai_caption_embedded",
                        "method": "orchestrated_generation"
                    },
                    "author": caption_data.get("author", ""),
                    "materialProperties": caption_data.get("material_properties", {})
                }
            else:
                logger.error("Caption generation failed")
                return None
                
        except Exception as e:
            logger.error(f"Caption generation error: {e}")
            return None
    
    def _generate_jsonld_output(self, material_name: str, material_data: Dict[str, Any], 
                              frontmatter_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate JSON-LD component output."""
        
        try:
            result = self.jsonld_generator.generate(
                material_name,
                material_data,
                frontmatter_data=frontmatter_data
            )
            
            if hasattr(result, 'success') and result.success:
                # Parse JSON-LD content
                if isinstance(result.content, str):
                    try:
                        structured_data = json.loads(result.content)
                    except json.JSONDecodeError:
                        structured_data = {"raw_content": result.content}
                else:
                    structured_data = result.content
                
                # Extract schema types
                schema_types = self._extract_schema_types(structured_data)
                
                return {
                    "structuredData": structured_data,
                    "schemaTypes": schema_types,
                    "generation": {
                        "generated": datetime.now().isoformat(),
                        "method": "orchestrated_generation",
                        "schemaVersion": "https://schema.org"
                    }
                }
            else:
                logger.error("JSON-LD generation failed")
                return None
                
        except Exception as e:
            logger.error(f"JSON-LD generation error: {e}")
            return None
    
    def _generate_metatags_output(self, material_name: str, material_data: Dict[str, Any], 
                                frontmatter_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate metatags component output."""
        
        try:
            result = self.metatags_generator.generate(
                material_name,
                material_data,
                frontmatter_data=frontmatter_data
            )
            
            if hasattr(result, 'success') and result.success:
                # Parse metatags content
                if isinstance(result.content, str):
                    metatags_data = yaml.safe_load(result.content)
                else:
                    metatags_data = result.content
                
                return {
                    "htmlMeta": metatags_data.get("meta", {}),
                    "openGraph": metatags_data.get("og", {}),
                    "twitterCard": metatags_data.get("twitter", {}),
                    "generation": {
                        "generated": datetime.now().isoformat(),
                        "method": "orchestrated_generation"
                    }
                }
            else:
                logger.error("Metatags generation failed")
                return None
                
        except Exception as e:
            logger.error(f"Metatags generation error: {e}")
            return None
    
    def _generate_tags_output(self, material_name: str, material_data: Dict[str, Any], 
                            frontmatter_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate tags component output."""
        
        try:
            result = self.tags_generator.generate(
                material_name,
                material_data,
                frontmatter_data=frontmatter_data
            )
            
            if hasattr(result, 'success') and result.success:
                # Parse tags content
                if isinstance(result.content, str):
                    try:
                        tags_data = yaml.safe_load(result.content)
                    except Exception:
                        # If parsing fails, treat as a simple list
                        tags_data = result.content.split('\n') if result.content else []
                else:
                    tags_data = result.content
                
                # Handle different tag formats
                if isinstance(tags_data, list):
                    content_tags = tags_data
                    seo_tags = []
                    industry_tags = []
                elif isinstance(tags_data, dict):
                    content_tags = tags_data.get("tags", tags_data.get("contentTags", []))
                    seo_tags = tags_data.get("seo_tags", tags_data.get("seoTags", []))
                    industry_tags = tags_data.get("industry_tags", tags_data.get("industryTags", []))
                else:
                    content_tags = []
                    seo_tags = []
                    industry_tags = []
                
                return {
                    "contentTags": content_tags,
                    "seoTags": seo_tags,
                    "industryTags": industry_tags,
                    "materialTags": self._generate_material_tags(frontmatter_data),
                    "processTags": self._generate_process_tags(frontmatter_data),
                    "generation": {
                        "generated": datetime.now().isoformat(),
                        "method": "orchestrated_generation",
                        "totalTags": len(content_tags) + len(seo_tags) + len(industry_tags)
                    }
                }
            else:
                logger.error("Tags generation failed")
                return None
                
        except Exception as e:
            logger.error(f"Tags generation error: {e}")
            return None
    
    def _extract_schema_types(self, structured_data: Dict[str, Any]) -> List[str]:
        """Extract schema.org types from JSON-LD structured data."""
        
        types = []
        
        if isinstance(structured_data, dict):
            if "@type" in structured_data:
                if isinstance(structured_data["@type"], list):
                    types.extend(structured_data["@type"])
                else:
                    types.append(structured_data["@type"])
            
            if "@graph" in structured_data:
                for item in structured_data["@graph"]:
                    if isinstance(item, dict) and "@type" in item:
                        if isinstance(item["@type"], list):
                            types.extend(item["@type"])
                        else:
                            types.append(item["@type"])
        
        return list(set(types))  # Remove duplicates
    
    def _generate_material_tags(self, frontmatter_data: Dict[str, Any]) -> List[str]:
        """Generate material property-based tags from frontmatter."""
        
        tags = []
        
        # Add category-based tags
        if "category" in frontmatter_data:
            tags.append(frontmatter_data["category"].lower())
        
        if "subcategory" in frontmatter_data:
            tags.append(frontmatter_data["subcategory"].lower().replace("_", "-"))
        
        # Add material name tag
        if "name" in frontmatter_data:
            name_tag = frontmatter_data["name"].lower().replace(" ", "-")
            tags.append(name_tag)
        
        return tags
    
    def _generate_process_tags(self, frontmatter_data: Dict[str, Any]) -> List[str]:
        """Generate laser process-related tags from frontmatter."""
        
        tags = ["laser-cleaning", "surface-treatment", "industrial-cleaning"]
        
        # Add wavelength-based tags
        machine_settings = frontmatter_data.get("machineSettings", {})
        if "wavelength" in machine_settings:
            wavelength = machine_settings["wavelength"]
            if isinstance(wavelength, dict) and "value" in wavelength:
                wl_value = wavelength["value"]
                if wl_value == 1064:
                    tags.append("infrared-laser")
                elif wl_value < 400:
                    tags.append("uv-laser")
                elif wl_value < 700:
                    tags.append("visible-laser")
        
        return tags
    
    def save_unified_frontmatter(self, material_name: str, frontmatter_data: Dict[str, Any]) -> bool:
        """Save unified frontmatter to file."""
        
        output_path = Path(f"content/components/frontmatter/{material_name.lower()}-laser-cleaning.yaml")
        
        try:
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with proper YAML formatting
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(frontmatter_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
            
            logger.info(f"✅ Saved unified frontmatter to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save unified frontmatter for {material_name}: {e}")
            return False

def test_unified_generator():
    """Test the unified frontmatter generator."""
    
    from api.client_factory import create_api_client
    
    print("🚀 Testing Unified Frontmatter Generator")
    print("=" * 50)
    
    # Create generator and API client
    generator = UnifiedFrontmatterGenerator()
    
    try:
        api_client = create_api_client('deepseek')
        print("✅ API client created successfully")
    except Exception as e:
        print(f"❌ Failed to create API client: {e}")
        print("⚠️ Proceeding without AI-generated components")
        api_client = None
    
    # Test with aluminum
    material_name = "aluminum"
    components = ["caption", "jsonld", "metatags", "tags"] if api_client else ["jsonld", "metatags", "tags"]
    
    print(f"\n📄 Generating unified frontmatter for {material_name}")
    print(f"🔧 Components: {', '.join(components)}")
    
    unified_data = generator.generate_unified_frontmatter(
        material_name=material_name,
        components=components,
        api_client=api_client
    )
    
    if unified_data:
        print("\n✅ Generation successful!")
        
        # Show results
        component_outputs = unified_data.get('componentOutputs', {})
        print(f"📊 Components generated: {len(component_outputs)}")
        
        for comp_type, comp_data in component_outputs.items():
            size = len(str(comp_data))
            print(f"  • {comp_type}: {size:,} characters")
        
        total_size = len(str(unified_data))
        print(f"📏 Total unified file size: {total_size:,} characters")
        
        # Save the result
        if generator.save_unified_frontmatter(material_name, unified_data):
            print(f"💾 Saved to: content/components/frontmatter/{material_name}-laser-cleaning.yaml")
        
        return unified_data
    else:
        print("❌ Generation failed")
        return None

if __name__ == "__main__":
    test_unified_generator()