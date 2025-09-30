#!/usr/bin/env python3
"""
Single Frontmatter Orchestration Workflow
Generates one unified frontmatter by orchestrating multiple component generators
and embedding their outputs directly into the frontmatter structure.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, '/Users/todddunning/Desktop/Z-Beam/z-beam-generator')

class FrontmatterOrchestrator:
    """
    Orchestrates multiple component generators into a single unified frontmatter output.
    Components generate data that gets embedded directly into frontmatter structure.
    """
    
    def __init__(self):
        self.api_client = None
        self.component_stats = {}
    
    def generate_unified_frontmatter(self, material_name: str) -> Dict[str, Any]:
        """
        Generate a single unified frontmatter by orchestrating component generators.
        
        Args:
            material_name: Material to generate frontmatter for
            
        Returns:
            Dict containing unified frontmatter with embedded component outputs
        """
        print(f"🎯 Orchestrating unified frontmatter for: {material_name}")
        
        # Initialize API client
        try:
            from api.client_factory import create_api_client
            self.api_client = create_api_client()
            print(f"✅ API client initialized")
        except Exception as e:
            print(f"❌ API client initialization failed: {e}")
            return None
        
        generation_start = datetime.now()
        
        # Step 1: Generate base frontmatter structure
        print("\\n📄 Step 1: Generating base frontmatter structure...")
        base_frontmatter = self._generate_base_frontmatter(material_name)
        if not base_frontmatter:
            print("❌ Base frontmatter generation failed")
            return None
        
        # Initialize componentOutputs section
        base_frontmatter['componentOutputs'] = {}
        
        # Step 2: Orchestrate component generations
        print("\\n🔧 Step 2: Orchestrating component generations...")
        
        # 2.1: Generate Tags (essential tags)
        tags_data = self._orchestrate_tags_component(material_name, base_frontmatter)
        if tags_data:
            base_frontmatter['componentOutputs']['tags'] = tags_data
            print("✅ Tags component orchestrated")
        
        # 2.2: Generate JSON-LD (structured data)
        jsonld_data = self._orchestrate_jsonld_component(material_name, base_frontmatter)
        if jsonld_data:
            base_frontmatter['componentOutputs']['jsonld'] = jsonld_data
            print("✅ JSON-LD component orchestrated")
        
        # 2.3: Generate Metatags (SEO and social)
        metatags_data = self._orchestrate_metatags_component(material_name, base_frontmatter)
        if metatags_data:
            base_frontmatter['componentOutputs']['metatags'] = metatags_data
            print("✅ Metatags component orchestrated")
        
        # 2.4: Generate Caption (descriptions)
        caption_data = self._orchestrate_caption_component(material_name, base_frontmatter)
        if caption_data:
            base_frontmatter['componentOutputs']['caption'] = caption_data
            print("✅ Caption component orchestrated")
        
        total_time = (datetime.now() - generation_start).total_seconds()
        
        # Add orchestration metadata
        base_frontmatter['orchestration'] = {
            "method": "unified_generation",
            "timestamp": datetime.now().isoformat(),
            "totalTime": f"{total_time:.2f}s",
            "componentsGenerated": len(base_frontmatter['componentOutputs']),
            "componentsList": list(base_frontmatter['componentOutputs'].keys())
        }
        
        print(f"\\n🎉 Unified frontmatter orchestration completed!")
        print(f"   ⏱️ Total time: {total_time:.2f}s")
        print(f"   🔧 Components: {len(base_frontmatter['componentOutputs'])}")
        print(f"   📊 Total size: {len(str(base_frontmatter)):,} characters")
        
        return base_frontmatter
    
    def _generate_base_frontmatter(self, material_name: str) -> Optional[Dict[str, Any]]:
        """Generate the base frontmatter structure."""
        try:
            from components.frontmatter.core.streamlined_generator import StreamlinedFrontmatterGenerator
            
            generator = StreamlinedFrontmatterGenerator(api_client=self.api_client)
            result = generator.generate(material_name)
            
            if hasattr(result, 'success') and result.success:
                frontmatter_data = yaml.safe_load(result.content)
                print(f"✅ Base frontmatter: {len(str(frontmatter_data)):,} characters")
                return frontmatter_data
            else:
                print(f"❌ Base frontmatter generation failed")
                return None
                
        except Exception as e:
            print(f"❌ Base frontmatter exception: {e}")
            return None
    
    def _orchestrate_tags_component(self, material_name: str, frontmatter_data: Dict) -> Optional[Dict[str, Any]]:
        """Orchestrate tags component to generate essential tags data."""
        try:
            from components.tags.generator import TagsComponentGenerator
            
            generator = TagsComponentGenerator()
            
            # Create complete material data from frontmatter
            material_data = {
                "name": material_name,
                "category": frontmatter_data.get("category", ""),
                "subcategory": frontmatter_data.get("subcategory", ""),
                "formula": frontmatter_data.get("chemicalProperties", {}).get("formula"),
                "symbol": frontmatter_data.get("chemicalProperties", {}).get("symbol")
            }
            
            # Generate tags using frontmatter context
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                frontmatter_data=frontmatter_data,
                author_info=frontmatter_data.get('author', {})
            )
            
            if hasattr(result, 'success') and result.success:
                # Extract essential tags from YAML content (first document only)
                yaml_content = result.content.split('\\n---\\n')[0]
                tags_yaml = yaml.safe_load(yaml_content)
                
                # Return structured tags data for embedding
                return {
                    "essentialTags": tags_yaml.get("essentialTags", []),
                    "generation": {
                        "method": "orchestrated_generation",
                        "timestamp": datetime.now().isoformat(),
                        "totalTags": len(tags_yaml.get("essentialTags", [])),
                        "tagPriority": "essential"
                    }
                }
            else:
                print("❌ Tags generation failed")
                return None
                
        except Exception as e:
            print(f"❌ Tags orchestration exception: {e}")
            return None
    
    def _orchestrate_jsonld_component(self, material_name: str, frontmatter_data: Dict) -> Optional[Dict[str, Any]]:
        """Orchestrate JSON-LD component to generate structured data."""
        try:
            from components.jsonld.generator import JsonldComponentGenerator
            
            generator = JsonldComponentGenerator()
            
            # Generate JSON-LD using API and frontmatter context
            result = generator.generate(
                material_name=material_name,
                material_data={"name": material_name},
                api_client=self.api_client,
                frontmatter_data=frontmatter_data,
                author_info=frontmatter_data.get('author', {})
            )
            
            if hasattr(result, 'success') and result.success:
                # Parse JSON-LD content and extract structured data
                yaml_content = result.content.split('\\n---\\n')[0]
                jsonld_yaml = yaml.safe_load(yaml_content)
                
                # Extract structured data
                structured_data = jsonld_yaml.get("structuredData", {})
                
                # Extract schema types
                schema_types = []
                if "@type" in structured_data:
                    if isinstance(structured_data["@type"], list):
                        schema_types.extend(structured_data["@type"])
                    else:
                        schema_types.append(structured_data["@type"])
                
                return {
                    "structuredData": structured_data,
                    "schemaTypes": schema_types,
                    "generation": {
                        "method": "orchestrated_generation",
                        "timestamp": datetime.now().isoformat(),
                        "schemaVersion": "schema.org",
                        "totalTypes": len(schema_types)
                    }
                }
            else:
                print(f"❌ JSON-LD generation failed")
                return None
                
        except Exception as e:
            print(f"❌ JSON-LD orchestration exception: {e}")
            return None
    
    def _orchestrate_metatags_component(self, material_name: str, frontmatter_data: Dict) -> Optional[Dict[str, Any]]:
        """Orchestrate metatags component to generate SEO and social media tags."""
        try:
            from components.metatags.generator import MetatagsComponentGenerator
            
            generator = MetatagsComponentGenerator()
            
            # Create complete material data from frontmatter
            material_data = {
                "name": material_name,
                "category": frontmatter_data.get("category", ""),
                "subcategory": frontmatter_data.get("subcategory", "")
            }
            
            # Generate metatags using API and frontmatter context
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=self.api_client,
                frontmatter_data=frontmatter_data,
                author_info=frontmatter_data.get('author', {})
            )
            
            if hasattr(result, 'success') and result.success:
                # Parse metatags content - handle multi-document YAML safely
                yaml_content = result.content
                
                # Split on document separators and parse each document
                documents = yaml_content.split('\\n---\\n')
                metatags_yaml = {}
                
                # Try to find the main metatags document
                for doc in documents:
                    doc = doc.strip()
                    if doc and not doc.startswith('---'):
                        try:
                            parsed_doc = yaml.safe_load(doc)
                            if parsed_doc and isinstance(parsed_doc, dict):
                                # Look for metatags-specific fields
                                if any(key in parsed_doc for key in ['title', 'description', 'keywords']):
                                    metatags_yaml = parsed_doc
                                    break
                        except yaml.YAMLError:
                            continue
                
                # Structure metatags data
                return {
                    "htmlMeta": {
                        "title": metatags_yaml.get("title", ""),
                        "description": metatags_yaml.get("description", ""),
                        "keywords": metatags_yaml.get("keywords", "")
                    },
                    "openGraph": {
                        "og:title": metatags_yaml.get("title", ""),
                        "og:description": metatags_yaml.get("description", ""),
                        "og:type": "article"
                    },
                    "twitterCard": {
                        "twitter:card": "summary_large_image",
                        "twitter:title": metatags_yaml.get("title", ""),
                        "twitter:description": metatags_yaml.get("description", "")
                    },
                    "generation": {
                        "method": "orchestrated_generation",
                        "timestamp": datetime.now().isoformat(),
                        "totalTags": 3  # htmlMeta, openGraph, twitterCard
                    }
                }
            else:
                print("❌ Metatags generation failed")
                return None
                
        except Exception as e:
            print(f"❌ Metatags orchestration exception: {e}")
            return None
    
    def _orchestrate_caption_component(self, material_name: str, frontmatter_data: Dict) -> Optional[Dict[str, Any]]:
        """Orchestrate caption component to generate image and content descriptions."""
        try:
            from components.caption.generators.generator import CaptionComponentGenerator
            
            generator = CaptionComponentGenerator()
            
            # Create complete material data from frontmatter
            material_data = {
                "name": material_name,
                "category": frontmatter_data.get("category", ""),
                "subcategory": frontmatter_data.get("subcategory", "")
            }
            
            # Generate caption using API and frontmatter context
            result = generator.generate(
                material_name=material_name,
                material_data=material_data,
                api_client=self.api_client,
                frontmatter_data=frontmatter_data,
                author_info=frontmatter_data.get('author', {})
            )
            
            if hasattr(result, 'success') and result.success:
                # Parse caption content - handle multi-document YAML safely
                yaml_content = result.content
                
                # Split on document separators and parse each document
                documents = yaml_content.split('\\n---\\n')
                caption_yaml = {}
                
                # Try to find the main caption document
                for doc in documents:
                    doc = doc.strip()
                    if doc and not doc.startswith('---'):
                        try:
                            parsed_doc = yaml.safe_load(doc)
                            if parsed_doc and isinstance(parsed_doc, dict):
                                # Look for caption-specific fields
                                if any(key in parsed_doc for key in ['before_text', 'after_text', 'technical_analysis']):
                                    caption_yaml = parsed_doc
                                    break
                        except yaml.YAMLError:
                            continue
                
                # Structure caption data
                return {
                    "beforeText": caption_yaml.get("before_text", ""),
                    "afterText": caption_yaml.get("after_text", ""),
                    "technicalAnalysis": caption_yaml.get("technical_analysis", {}),
                    "generation": {
                        "method": "orchestrated_generation",
                        "timestamp": datetime.now().isoformat(),
                        "sections": 3  # beforeText, afterText, technicalAnalysis
                    }
                }
            else:
                print("❌ Caption generation failed")
                return None
                
        except Exception as e:
            print(f"❌ Caption orchestration exception: {e}")
            return None

def test_single_frontmatter_orchestration():
    """Test the single frontmatter orchestration workflow."""
    
    print("🚀 Testing Single Frontmatter Orchestration Workflow")
    print("=" * 60)
    print("🎯 Goal: Generate ONE unified frontmatter with embedded component data")
    print()
    
    # Initialize orchestrator
    orchestrator = FrontmatterOrchestrator()
    
    # Generate unified frontmatter for aluminum
    unified_frontmatter = orchestrator.generate_unified_frontmatter("aluminum")
    
    if unified_frontmatter:
        # Save the unified result
        output_path = Path("aluminum-unified-orchestrated.yaml")
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(unified_frontmatter, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
        
        file_size = output_path.stat().st_size
        print(f"\\n💾 Saved unified frontmatter to: {output_path}")
        print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Show structure summary
        print(f"\\n📋 Unified Frontmatter Structure:")
        print(f"   📄 Base sections: {len([k for k in unified_frontmatter.keys() if k not in ['componentOutputs', 'orchestration']])}")
        
        component_outputs = unified_frontmatter.get('componentOutputs', {})
        print(f"   🔧 Component outputs: {len(component_outputs)}")
        for comp_name in component_outputs.keys():
            print(f"      • {comp_name}")
        
        orchestration_info = unified_frontmatter.get('orchestration', {})
        print(f"   ⚙️ Orchestration metadata: {orchestration_info.get('totalTime', 'N/A')}")
        
        print(f"\\n✅ Single frontmatter orchestration successful!")
        return unified_frontmatter
    else:
        print(f"\\n❌ Single frontmatter orchestration failed!")
        return None

if __name__ == "__main__":
    result = test_single_frontmatter_orchestration()
    if result:
        print(f"\\n🎉 Orchestration complete! Generated unified frontmatter with embedded components.")