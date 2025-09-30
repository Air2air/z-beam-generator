#!/usr/bin/env python3
"""
Next.js Context-Aware Direct Data Orchestration
Generates frontmatter optimized for Next.js app component usage patterns.
"""

import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add the project root to the Python path
sys.path.insert(0, '/Users/todddunning/Desktop/Z-Beam/z-beam-generator')

class NextJSOptimizedOrchestrator:
    """
    Orchestrates component data with Next.js app context awareness.
    Optimizes for specific component purposes: Caption (microscopic photos), 
    Table (overflow data), Tags (search navigation).
    """
    
    def __init__(self):
        self.api_client = None
        self.component_purposes = {
            "caption": "microscopic_photo_descriptions",
            "table": "short_string_data_overflow", 
            "tags": "clickable_search_navigation",
            "jsonld": "seo_structured_data",
            "metatags": "html_meta_social_seo"
        }
    
    def generate_nextjs_optimized_frontmatter(self, material_name: str) -> Dict[str, Any]:
        """
        Generate frontmatter optimized for Next.js app component usage.
        
        Args:
            material_name: Material to generate frontmatter for
            
        Returns:
            Dict containing Next.js optimized frontmatter structure
        """
        print(f"🎯 Next.js-optimized orchestration for: {material_name}")
        
        # Initialize API client
        try:
            from api.client_factory import create_api_client
            self.api_client = create_api_client()
            print("✅ API client initialized")
        except Exception as e:
            print(f"❌ API client initialization failed: {e}")
            return None
        
        generation_start = datetime.now()
        
        # Step 1: Generate base frontmatter
        print("\\n📄 Step 1: Generating base frontmatter...")
        base_frontmatter = self._generate_base_frontmatter(material_name)
        if not base_frontmatter:
            print("❌ Base frontmatter generation failed")
            return None
        
        # Create material context
        material_context = self._create_material_context(material_name, base_frontmatter)
        
        # Step 2: Next.js component optimization
        print("\\n🎯 Step 2: Next.js component optimization...")
        
        # Initialize componentOutputs with Next.js structure
        base_frontmatter['componentOutputs'] = {
            "content": {},      # Caption, Table - UI content components
            "navigation": {},   # Tags - search navigation
            "metadata": {}      # JSON-LD, Metatags - SEO/social
        }
        
        # 2.1: Generate Caption for microscopic photo descriptions
        caption_data = self._generate_microscopic_caption(material_context)
        if caption_data:
            base_frontmatter['componentOutputs']['content']['caption'] = caption_data
            print("✅ Microscopic caption generated")
        
        # 2.2: Generate Table for overflow data
        table_data = self._generate_overflow_table(material_context, base_frontmatter)
        if table_data:
            base_frontmatter['componentOutputs']['content']['table'] = table_data
            print("✅ Overflow table generated")
        
        # 2.3: Generate Tags for clickable search navigation
        tags_data = self._generate_search_navigation_tags(material_context)
        if tags_data:
            base_frontmatter['componentOutputs']['navigation']['tags'] = tags_data
            print("✅ Search navigation tags generated")
        
        # 2.4: Generate JSON-LD for SEO
        jsonld_data = self._generate_seo_jsonld(material_context)
        if jsonld_data:
            base_frontmatter['componentOutputs']['metadata']['jsonld'] = jsonld_data
            print("✅ SEO JSON-LD generated")
        
        # 2.5: Generate Metatags for social/SEO
        metatags_data = self._generate_social_metatags(material_context)
        if metatags_data:
            base_frontmatter['componentOutputs']['metadata']['metatags'] = metatags_data
            print("✅ Social media metatags generated")
        
        total_time = (datetime.now() - generation_start).total_seconds()
        
        # Add Next.js optimization metadata
        base_frontmatter['nextjs'] = {
            "optimization": "context_aware_generation",
            "timestamp": datetime.now().isoformat(),
            "totalTime": f"{total_time:.2f}s",
            "componentPurposes": self.component_purposes,
            "structure": "content_navigation_metadata"
        }
        
        print(f"\\n🎉 Next.js optimized frontmatter completed!")
        print(f"   ⏱️ Total time: {total_time:.2f}s")
        print(f"   🎯 Structure: Content | Navigation | Metadata")
        print(f"   📊 Total size: {len(str(base_frontmatter)):,} characters")
        
        return base_frontmatter
    
    def _generate_base_frontmatter(self, material_name: str) -> Optional[Dict[str, Any]]:
        """Generate base frontmatter structure."""
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
    
    def _create_material_context(self, material_name: str, frontmatter_data: Dict) -> Dict[str, Any]:
        """Create comprehensive material context for component generation."""
        return {
            "name": material_name,
            "category": frontmatter_data.get("category", ""),
            "subcategory": frontmatter_data.get("subcategory", ""),
            "title": frontmatter_data.get("title", ""),
            "description": frontmatter_data.get("description", ""),
            "materialProperties": frontmatter_data.get("materialProperties", {}),
            "machineSettings": frontmatter_data.get("machineSettings", {}),
            "applications": frontmatter_data.get("applications", []),
            "processes": frontmatter_data.get("processes", []),
            "author": frontmatter_data.get("author", {})
        }
    
    def _generate_microscopic_caption(self, material_context: Dict) -> Optional[Dict[str, Any]]:
        """Generate caption optimized for microscopic photo descriptions."""
        try:
            material_name = material_context.get("name", "")
            category = material_context.get("category", "")
            
            # Create microscopic-focused before text
            before_text = f"Microscopic analysis of {material_name} surface before laser cleaning reveals characteristic contamination patterns typical of {category.lower()} substrates. Surface examination shows accumulated deposits that require precise laser parameter control for effective removal without substrate damage."
            
            # Create microscopic-focused after text  
            after_text = f"Post-cleaning microscopic examination demonstrates successful contaminant removal from {material_name} surface. The cleaned substrate exhibits restored surface characteristics with minimal thermal effects, confirming optimal laser cleaning parameters for {category.lower()} materials."
            
            # Enhanced technical analysis for microscopic context
            technical_analysis = {
                "microscopicObservations": {
                    "beforeCleaning": "Surface contamination visible at microscopic level",
                    "afterCleaning": "Clean substrate with preserved surface integrity",
                    "magnification": "Optimal viewing at 100x-500x magnification"
                },
                "surfaceCharacteristics": {
                    "materialType": category,
                    "cleaningEffectiveness": "High precision contaminant removal",
                    "substratePreservation": "Minimal thermal impact observed"
                },
                "laserInteraction": {
                    "cleaningMechanism": "Selective laser ablation of contaminants",
                    "thermalEffects": "Controlled heat-affected zone",
                    "surfaceQuality": "Preserved substrate microstructure"
                }
            }
            
            # Add material-specific properties if available
            material_props = material_context.get("materialProperties", {})
            if material_props.get("meltingPoint"):
                mp = material_props["meltingPoint"]
                technical_analysis["thermalLimits"] = f"Material melting point: {mp.get('value', 'N/A')} {mp.get('unit', '')}"
            
            return {
                "beforeText": before_text,
                "afterText": after_text,
                "technicalAnalysis": technical_analysis,
                "microscopicContext": {
                    "purpose": "microscopic_photo_descriptions",
                    "optimizedFor": "before_after_analysis",
                    "viewingRecommendations": "100x-500x magnification for optimal detail"
                },
                "generation": {
                    "method": "nextjs_optimized_generation",
                    "timestamp": datetime.now().isoformat(),
                    "purpose": "microscopic_photo_captions"
                }
            }
                
        except Exception as e:
            print(f"❌ Microscopic caption generation exception: {e}")
            return None
    
    def _generate_overflow_table(self, material_context: Dict, frontmatter_data: Dict) -> Optional[Dict[str, Any]]:
        """Generate table data for overflow from materialProperties and machineSettings."""
        try:
            table_data = {
                "purpose": "short_string_data_overflow",
                "sections": {},
                "displayFormat": "responsive_table"
            }
            
            # Check materialProperties for overflow data
            material_props = material_context.get("materialProperties", {})
            overflow_properties = {}
            
            for prop_name, prop_data in material_props.items():
                if isinstance(prop_data, dict):
                    # Look for complex or string values suitable for table display
                    value = prop_data.get('value')
                    if isinstance(value, str) and len(value) > 10:
                        overflow_properties[prop_name] = {
                            "value": value,
                            "unit": prop_data.get('unit', ''),
                            "description": prop_data.get('description', '')[:100] + "..." if len(prop_data.get('description', '')) > 100 else prop_data.get('description', '')
                        }
            
            if overflow_properties:
                table_data["sections"]["materialProperties"] = {
                    "title": "Extended Material Properties",
                    "data": overflow_properties,
                    "columns": ["Property", "Value", "Unit", "Description"]
                }
            
            # Check machineSettings for table display
            machine_settings = material_context.get("machineSettings", {})
            if machine_settings and len(machine_settings) > 5:  # Threshold for table display
                settings_table = {}
                for setting_name, setting_data in machine_settings.items():
                    if isinstance(setting_data, dict):
                        settings_table[setting_name] = {
                            "value": setting_data.get('value', ''),
                            "unit": setting_data.get('unit', ''),
                            "range": f"{setting_data.get('min', '')}-{setting_data.get('max', '')}" if setting_data.get('min') and setting_data.get('max') else ''
                        }
                
                if settings_table:
                    table_data["sections"]["machineSettings"] = {
                        "title": "Laser Machine Settings",
                        "data": settings_table,
                        "columns": ["Setting", "Value", "Unit", "Range"]
                    }
            
            # Check applications and processes for table format
            applications = material_context.get("applications", [])
            if applications and len(applications) > 3:
                app_table = {}
                for i, app in enumerate(applications[:10]):  # Limit to 10 for table display
                    if isinstance(app, str) and ':' in app:
                        parts = app.split(':', 1)
                        app_table[f"Application_{i+1}"] = {
                            "industry": parts[0].strip(),
                            "description": parts[1].strip()
                        }
                    else:
                        app_table[f"Application_{i+1}"] = {
                            "industry": "General",
                            "description": str(app)
                        }
                
                if app_table:
                    table_data["sections"]["applications"] = {
                        "title": "Application Industries",
                        "data": app_table,
                        "columns": ["Industry", "Application Description"]
                    }
            
            # Only return table data if we have sections to display
            if table_data["sections"]:
                table_data["generation"] = {
                    "method": "nextjs_optimized_generation",
                    "timestamp": datetime.now().isoformat(),
                    "purpose": "overflow_data_display",
                    "sections_count": len(table_data["sections"])
                }
                return table_data
            
            return None
                
        except Exception as e:
            print(f"❌ Overflow table generation exception: {e}")
            return None
    
    def _generate_search_navigation_tags(self, material_context: Dict) -> Optional[Dict[str, Any]]:
        """Generate tags optimized for clickable search navigation."""
        try:
            # Create search-optimized tags
            search_tags = []
            
            # Priority 1: Material identification tags
            material_name = material_context.get("name", "")
            category = material_context.get("category", "")
            
            if material_name:
                search_tags.append(material_name.title())
            if category:
                search_tags.append(category)
            
            # Priority 2: Author tag for search filtering
            author = material_context.get("author", {})
            if author.get("name"):
                # Create searchable author tag
                author_tag = author["name"].replace(" ", "-").lower()
                search_tags.append(author_tag)
            
            # Priority 3: Core technology tags for search
            tech_tags = [
                "Laser Cleaning",
                "Surface Treatment", 
                "Industrial Cleaning",
                "Precision Cleaning"
            ]
            search_tags.extend(tech_tags)
            
            # Priority 4: Application-based search tags
            applications = material_context.get("applications", [])
            app_tags = []
            for app in applications[:3]:  # Top 3 applications for search
                if isinstance(app, str):
                    # Extract industry from application string
                    if ':' in app:
                        industry = app.split(':')[0].strip()
                        app_tags.append(industry)
                    else:
                        app_tags.append(app)
            
            search_tags.extend(app_tags)
            
            # Ensure exactly 10 tags for optimal clickable interface
            search_tags = search_tags[:10]
            
            # Fill to 10 if needed with category-specific tags
            if len(search_tags) < 10:
                category_tags = {
                    "Metal": ["Metalworking", "Corrosion Removal"],
                    "Glass": ["Optics", "Transparency Restoration"],
                    "Polymer": ["Plastics", "Coating Removal"],
                    "Ceramic": ["Advanced Materials", "High Temperature"]
                }
                
                if category in category_tags:
                    for tag in category_tags[category]:
                        if len(search_tags) < 10:
                            search_tags.append(tag)
                
                # Final filler tags if still needed
                filler_tags = ["Non-Contact Cleaning", "Contaminant Removal", "Quality Control"]
                for tag in filler_tags:
                    if len(search_tags) < 10:
                        search_tags.append(tag)
            
            return {
                "searchTags": search_tags,
                "searchOptimization": {
                    "totalTags": len(search_tags),
                    "clickableInterface": True,
                    "searchCategories": {
                        "material": search_tags[:2],
                        "technology": search_tags[2:6], 
                        "applications": search_tags[6:]
                    }
                },
                "generation": {
                    "method": "nextjs_optimized_generation",
                    "timestamp": datetime.now().isoformat(),
                    "purpose": "clickable_search_navigation",
                    "interface": "clickable_tags"
                }
            }
                
        except Exception as e:
            print(f"❌ Search navigation tags generation exception: {e}")
            return None
    
    def _generate_seo_jsonld(self, material_context: Dict) -> Optional[Dict[str, Any]]:
        """Generate JSON-LD optimized for SEO structured data."""
        try:
            # Enhanced JSON-LD structure for SEO
            structured_data = {
                "@context": "https://schema.org",
                "@type": ["Article", "TechnicalArticle"],
                "name": material_context.get("title", f"{material_context.get('name', '')} Laser Cleaning"),
                "headline": material_context.get("title", f"{material_context.get('name', '')} Laser Cleaning Guide"),
                "description": material_context.get("description", ""),
                "about": {
                    "@type": "Material",
                    "name": material_context.get("name", ""),
                    "category": material_context.get("category", ""),
                    "description": f"Laser cleaning guide for {material_context.get('name', '')} materials"
                },
                "author": {
                    "@type": "Person", 
                    "name": material_context.get("author", {}).get("name", ""),
                    "description": "Industrial laser cleaning specialist with expertise in material science and precision manufacturing"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "Z-Beam",
                    "url": "https://z-beam.com"
                },
                "dateCreated": datetime.now().isoformat(),
                "applicationCategory": "Laser Cleaning Technology",
                "keywords": [
                    material_context.get("name", ""),
                    material_context.get("category", ""),
                    "laser cleaning",
                    "surface treatment",
                    "industrial cleaning"
                ],
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": f"https://z-beam.com/{material_context.get('name', '').lower().replace(' ', '-')}"
                }
            }
            
            # Add material properties as additionalProperty
            material_props = material_context.get("materialProperties", {})
            if material_props:
                properties = []
                for prop_name, prop_data in list(material_props.items())[:10]:  # Limit for SEO
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
                "seoOptimization": {
                    "schemaTypes": ["Article", "TechnicalArticle"],
                    "keywordDensity": "optimized_for_search",
                    "propertiesIncluded": len(structured_data["about"].get("additionalProperty", []))
                },
                "generation": {
                    "method": "nextjs_optimized_generation", 
                    "timestamp": datetime.now().isoformat(),
                    "purpose": "seo_structured_data",
                    "schema_version": "schema.org"
                }
            }
                
        except Exception as e:
            print(f"❌ SEO JSON-LD generation exception: {e}")
            return None
    
    def _generate_social_metatags(self, material_context: Dict) -> Optional[Dict[str, Any]]:
        """Generate metatags optimized for social media and HTML SEO."""
        try:
            title = material_context.get("title", f"{material_context.get('name', '')} Laser Cleaning")
            description = material_context.get("description", "")
            
            # Create social media optimized description
            social_description = description[:160] if len(description) <= 160 else description[:157] + "..."
            
            # Enhanced keywords for SEO
            keywords = [
                material_context.get("name", ""),
                material_context.get("category", ""),
                "laser cleaning",
                "surface treatment",
                "industrial cleaning",
                "precision cleaning",
                "contaminant removal"
            ]
            keywords_str = ", ".join([k for k in keywords if k])
            
            return {
                "htmlMeta": {
                    "title": title,
                    "description": social_description,
                    "keywords": keywords_str,
                    "robots": "index, follow",
                    "viewport": "width=device-width, initial-scale=1"
                },
                "openGraph": {
                    "og:title": title,
                    "og:description": social_description,
                    "og:type": "article",
                    "og:site_name": "Z-Beam Laser Cleaning",
                    "og:locale": "en_US",
                    "og:image": f"https://z-beam.com/images/{material_context.get('name', '').lower().replace(' ', '-')}-cleaning.jpg"
                },
                "twitterCard": {
                    "twitter:card": "summary_large_image",
                    "twitter:title": title,
                    "twitter:description": social_description[:200],  # Twitter limit
                    "twitter:site": "@ZBeamCleaning",
                    "twitter:image": f"https://z-beam.com/images/{material_context.get('name', '').lower().replace(' ', '-')}-cleaning.jpg"
                },
                "socialOptimization": {
                    "platforms": ["Facebook", "Twitter", "LinkedIn"],
                    "descriptionLength": len(social_description),
                    "keywordCount": len(keywords)
                },
                "generation": {
                    "method": "nextjs_optimized_generation",
                    "timestamp": datetime.now().isoformat(),
                    "purpose": "social_media_seo_metatags"
                }
            }
                
        except Exception as e:
            print(f"❌ Social metatags generation exception: {e}")
            return None

def test_nextjs_optimized_orchestration():
    """Test the Next.js optimized orchestration approach."""
    
    print("🚀 Testing Next.js Optimized Orchestration")
    print("=" * 60)
    print("🎯 Goal: Generate frontmatter optimized for Next.js app component usage")
    print()
    
    # Initialize Next.js optimized orchestrator
    orchestrator = NextJSOptimizedOrchestrator()
    
    # Generate optimized frontmatter for aluminum
    optimized_frontmatter = orchestrator.generate_nextjs_optimized_frontmatter("aluminum")
    
    if optimized_frontmatter:
        # Save the optimized result
        output_path = Path("aluminum-nextjs-optimized.yaml")
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(optimized_frontmatter, f, default_flow_style=False, sort_keys=False, allow_unicode=True, width=120)
        
        file_size = output_path.stat().st_size
        print(f"\\n💾 Saved Next.js optimized frontmatter to: {output_path}")
        print(f"📁 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        # Show Next.js optimized structure
        print(f"\\n📋 Next.js Optimized Structure:")
        print(f"   📄 Base sections: {len([k for k in optimized_frontmatter.keys() if k not in ['componentOutputs', 'nextjs']])}")
        
        component_outputs = optimized_frontmatter.get('componentOutputs', {})
        print(f"   🎯 Component categories: {len(component_outputs)}")
        
        for category_name, category_data in component_outputs.items():
            print(f"      📦 {category_name}: {list(category_data.keys()) if isinstance(category_data, dict) else 'No components'}")
        
        nextjs_info = optimized_frontmatter.get('nextjs', {})
        print(f"   ⚙️ Next.js optimization: {nextjs_info.get('optimization', 'unknown')} - {nextjs_info.get('totalTime', 'N/A')}")
        print(f"   🏗️ Structure: {nextjs_info.get('structure', 'unknown')}")
        
        print("\\n✅ Next.js optimized orchestration successful!")
        return optimized_frontmatter
    else:
        print("\\n❌ Next.js optimized orchestration failed!")
        return None

if __name__ == "__main__":
    result = test_nextjs_optimized_orchestration()
    if result:
        print("\\n🎉 Next.js optimization complete! Components optimized for app usage patterns.")