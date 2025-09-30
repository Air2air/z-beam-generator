#!/usr/bin/env python3
"""
Direct Data Orchestration for Component Integration
Bypasses YAML generation entirely - extracts data structures directly from components.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List

# Add the project root to the Python path
sys.path.insert(0, '/Users/todddunning/Desktop/Z-Beam/z-beam-generator')

class DirectDataOrchestrator:
    """
    Orchestrates component data directly without YAML intermediaries.
    Calls component logic and extracts structured data for frontmatter embedding.
    """
    
    def __init__(self):
        self.api_client = None
        self.generation_stats = {}
    
    def generate_unified_frontmatter(self, material_name: str) -> Dict[str, Any]:
        """
        Generate unified frontmatter by calling component data generation directly.
        
        Args:
            material_name: Material to generate frontmatter for
            
        Returns:
            Dict containing unified frontmatter with embedded component data
        """
        print(f"🎯 Direct data orchestration for: {material_name}")
        
        # Initialize API client
        try:
            from api.client_factory import create_api_client
            self.api_client = create_api_client()
            print("✅ API client initialized")
        except Exception as e:
            print(f"❌ API client initialization failed: {e}")
            return None
        
        generation_start = datetime.now()
        
        # Step 1: Generate base frontmatter structure
        print("\\n📄 Step 1: Generating base frontmatter...")
        base_frontmatter = self._generate_base_frontmatter(material_name)
        if not base_frontmatter:
            print("❌ Base frontmatter generation failed")
            return None
        
        # Create material context for components
        material_context = {
            "name": material_name,
            "category": base_frontmatter.get("category", ""),
            "subcategory": base_frontmatter.get("subcategory", ""),
            "title": base_frontmatter.get("title", ""),
            "description": base_frontmatter.get("description", ""),
            "chemicalProperties": base_frontmatter.get("chemicalProperties", {}),
            "materialProperties": base_frontmatter.get("materialProperties", {}),
            "author": base_frontmatter.get("author", {})
        }
        
        # Initialize componentOutputs section
        base_frontmatter['componentOutputs'] = {}
        
        # Step 2: Direct component data generation
        print("\\n🔧 Step 2: Direct component data generation...")
        
        # 2.1: Generate Tags data directly
        tags_data = self._generate_tags_data_directly(material_context)
        if tags_data:
            base_frontmatter['componentOutputs']['tags'] = tags_data
            print("✅ Tags data generated directly")
        
        # 2.2: Generate JSON-LD data directly
        jsonld_data = self._generate_jsonld_data_directly(material_context)
        if jsonld_data:
            base_frontmatter['componentOutputs']['jsonld'] = jsonld_data
            print("✅ JSON-LD data generated directly")
        
        # 2.3: Generate Metatags data directly
        metatags_data = self._generate_metatags_data_directly(material_context)
        if metatags_data:
            base_frontmatter['componentOutputs']['metatags'] = metatags_data
            print("✅ Metatags data generated directly")
        
        # 2.4: Generate Caption data directly
        caption_data = self._generate_caption_data_directly(material_context)
        if caption_data:
            base_frontmatter['componentOutputs']['caption'] = caption_data
            print("✅ Caption data generated directly")
        
        total_time = (datetime.now() - generation_start).total_seconds()
        
        # Add orchestration metadata
        base_frontmatter['orchestration'] = {
            "method": "direct_data_generation",
            "timestamp": datetime.now().isoformat(),
            "totalTime": f"{total_time:.2f}s",
            "componentsGenerated": len(base_frontmatter['componentOutputs']),
            "componentsList": list(base_frontmatter['componentOutputs'].keys()),
            "bypass": "yaml_generation_skipped"
        }
        
        print(f"\\n🎉 Direct data orchestration completed!")
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
                print("❌ Base frontmatter generation failed")
                return None
                
        except Exception as e:
            print(f"❌ Base frontmatter exception: {e}")
            return None
    
    def _generate_tags_data_directly(self, material_context: Dict) -> Optional[Dict[str, Any]]:
        """Generate tags data directly without YAML processing."""
        try:
            # Direct essential tags generation
            essential_tags = self._create_essential_tags(material_context)
            
            return {
                "essentialTags": essential_tags,
                "generation": {
                    "method": "direct_data_generation",
                    "timestamp": datetime.now().isoformat(),
                    "totalTags": len(essential_tags),
                    "tagPriority": "essential",
                    "bypass": "yaml_skipped"
                }
            }
                
        except Exception as e:
            print(f"❌ Tags direct generation exception: {e}")
            return None
    
    def _create_essential_tags(self, material_context: Dict) -> List[str]:
        """Create the 10 essential tags directly."""
        tags = []
        
        # 1. Material category
        if material_context.get("category"):
            tags.append(material_context["category"])
        
        # 2. Material name
        if material_context.get("name"):
            tags.append(material_context["name"])
        
        # 3. Author name
        author = material_context.get("author", {})
        if author.get("name"):
            tags.append(author["name"])
        
        # 4. Subcategory if available
        if material_context.get("subcategory"):
            tags.append(material_context["subcategory"])
        
        # 5-10. Core laser cleaning tags
        core_tags = [
            "Laser Cleaning",
            "Surface Treatment",
            "Industrial Cleaning",
            "Contaminant Removal",
            "Precision Cleaning",
            "Non-Contact Cleaning"
        ]
        
        # Add core tags until we have 10 total
        for tag in core_tags:
            if len(tags) >= 10:
                break
            if tag not in tags:
                tags.append(tag)
        
        return tags[:10]  # Ensure exactly 10 tags
    
    def _generate_jsonld_data_directly(self, material_context: Dict) -> Optional[Dict[str, Any]]:
        """Generate JSON-LD structured data directly."""
        try:
            # Create structured data object directly
            structured_data = {
                "@context": "https://schema.org",
                "@type": ["Article", "TechnicalArticle"],
                "name": material_context.get("title", f"{material_context.get('name', '')} Laser Cleaning"),
                "description": material_context.get("description", ""),
                "about": {
                    "@type": "Material",
                    "name": material_context.get("name", ""),
                    "category": material_context.get("category", "")
                },
                "author": {
                    "@type": "Person",
                    "name": material_context.get("author", {}).get("name", "")
                },
                "dateCreated": datetime.now().isoformat(),
                "applicationCategory": "Laser Cleaning Technology",
                "keywords": [
                    material_context.get("name", ""),
                    material_context.get("category", ""),
                    "laser cleaning",
                    "surface treatment"
                ]
            }
            
            # Add material properties if available
            material_props = material_context.get("materialProperties", {})
            if material_props:
                properties = []
                for prop_name, prop_data in material_props.items():
                    if isinstance(prop_data, dict) and prop_data.get("value"):
                        properties.append({
                            "@type": "PropertyValue",
                            "name": prop_name,
                            "value": prop_data.get("value"),
                            "unitText": prop_data.get("unit", "")
                        })
                
                if properties:
                    structured_data["about"]["additionalProperty"] = properties
            
            return {
                "structuredData": structured_data,
                "schemaTypes": ["Article", "TechnicalArticle"],
                "generation": {
                    "method": "direct_data_generation",
                    "timestamp": datetime.now().isoformat(),
                    "schemaVersion": "schema.org",
                    "totalTypes": 2,
                    "bypass": "yaml_skipped"
                }
            }
                
        except Exception as e:
            print(f"❌ JSON-LD direct generation exception: {e}")
            return None
    
    def _generate_metatags_data_directly(self, material_context: Dict) -> Optional[Dict[str, Any]]:
        """Generate metatags data directly."""
        try:
            # Generate meta content directly
            title = material_context.get("title", f"{material_context.get('name', '')} Laser Cleaning")
            description = material_context.get("description", "")
            
            # Create keywords from material context
            keywords = [
                material_context.get("name", ""),
                material_context.get("category", ""),
                "laser cleaning",
                "surface treatment",
                "industrial cleaning"
            ]
            keywords_str = ", ".join([k for k in keywords if k])
            
            return {
                "htmlMeta": {
                    "title": title,
                    "description": description[:160],  # Meta description limit
                    "keywords": keywords_str
                },
                "openGraph": {
                    "og:title": title,
                    "og:description": description[:300],  # OG description limit
                    "og:type": "article",
                    "og:site_name": "Z-Beam Laser Cleaning"
                },
                "twitterCard": {
                    "twitter:card": "summary_large_image",
                    "twitter:title": title,
                    "twitter:description": description[:200]  # Twitter description limit
                },
                "generation": {
                    "method": "direct_data_generation",
                    "timestamp": datetime.now().isoformat(),
                    "totalTags": 3,
                    "bypass": "yaml_skipped"
                }
            }
                
        except Exception as e:
            print(f"❌ Metatags direct generation exception: {e}")
            return None
    
    def _generate_caption_data_directly(self, material_context: Dict) -> Optional[Dict[str, Any]]:
        """Generate caption data directly."""
        try:
            material_name = material_context.get("name", "")
            category = material_context.get("category", "")
            
            # Generate caption content directly
            before_text = f"Laser cleaning of {material_name} requires precise parameter control to achieve optimal contaminant removal while preserving the underlying {category.lower()} substrate."
            
            after_text = f"Post-cleaning analysis shows effective removal of surface contaminants from {material_name}, demonstrating the precision and effectiveness of laser cleaning technology for {category.lower()} materials."
            
            # Create technical analysis from material properties
            technical_analysis = {
                "materialType": category,
                "cleaningApproach": "Selective laser ablation",
                "keyConsiderations": [
                    f"{material_name} thermal sensitivity",
                    "Optimal wavelength selection",
                    "Pulse duration optimization"
                ]
            }
            
            # Add material properties if available
            material_props = material_context.get("materialProperties", {})
            if material_props.get("meltingPoint"):
                mp = material_props["meltingPoint"]
                technical_analysis["thermalLimits"] = f"Melting point: {mp.get('value', 'N/A')} {mp.get('unit', '')}"
            
            return {
                "beforeText": before_text,
                "afterText": after_text,
                "technicalAnalysis": technical_analysis,
                "generation": {
                    "method": "direct_data_generation",
                    "timestamp": datetime.now().isoformat(),
                    "sections": 3,
                    "bypass": "yaml_skipped"
                }
            }
                
        except Exception as e:
            print(f"❌ Caption direct generation exception: {e}")
            return None

def test_direct_data_orchestration():
    """Test the direct data orchestration approach."""
    
    print("🚀 Testing Direct Data Orchestration (No YAML)")
    print("=" * 60)
    print("🎯 Goal: Generate unified frontmatter by calling component logic directly")
    print()
    
    # Initialize direct orchestrator
    orchestrator = DirectDataOrchestrator()
    
    # Generate unified frontmatter for aluminum
    unified_frontmatter = orchestrator.generate_unified_frontmatter("aluminum")
    
    if unified_frontmatter:
        # Save the unified result
        output_path = Path("aluminum-direct-orchestrated.yaml")
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(unified_frontmatter, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
        
        file_size = output_path.stat().st_size
        print(f"\\n💾 Saved direct orchestrated frontmatter to: {output_path}")
        print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Show structure summary
        print(f"\\n📋 Direct Orchestrated Frontmatter Structure:")
        print(f"   📄 Base sections: {len([k for k in unified_frontmatter.keys() if k not in ['componentOutputs', 'orchestration']])}")
        
        component_outputs = unified_frontmatter.get('componentOutputs', {})
        print(f"   🔧 Component outputs: {len(component_outputs)}")
        for comp_name, comp_data in component_outputs.items():
            generation_method = comp_data.get('generation', {}).get('method', 'unknown')
            bypass_info = comp_data.get('generation', {}).get('bypass', 'none')
            print(f"      • {comp_name}: {generation_method} ({bypass_info})")
        
        orchestration_info = unified_frontmatter.get('orchestration', {})
        print(f"   ⚙️ Orchestration: {orchestration_info.get('method', 'unknown')} - {orchestration_info.get('totalTime', 'N/A')}")
        print(f"   🚀 Bypass method: {orchestration_info.get('bypass', 'none')}")
        
        print("\\n✅ Direct data orchestration successful!")
        return unified_frontmatter
    else:
        print("\\n❌ Direct data orchestration failed!")
        return None

if __name__ == "__main__":
    result = test_direct_data_orchestration()
    if result:
        print("\\n🎉 Direct orchestration complete! No YAML intermediaries used.")