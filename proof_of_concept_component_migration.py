#!/usr/bin/env python3
"""
Component Migration Tool - Proof of Concept
Demonstrates migrating component outputs into frontmatter files.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class ComponentMigrationPOC:
    """Proof of concept for migrating components into frontmatter."""
    
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.component_dirs = {
            "caption": Path("content/components/caption"),
            "jsonld": Path("content/components/jsonld"),
            "author": Path("content/components/author"),
            "metatags": Path("content/components/metatags"),
            "table": Path("content/components/table"),
            "tags": Path("content/components/tags")
        }
    
    def demo_migration(self, material_name: str = "aluminum") -> Dict[str, Any]:
        """Demonstrate migration process for a single material."""
        
        print(f"🔄 Demonstrating component migration for {material_name}")
        
        # Load existing frontmatter
        frontmatter_file = self.frontmatter_dir / f"{material_name}-laser-cleaning.yaml"
        
        if not frontmatter_file.exists():
            print(f"❌ No frontmatter file found: {frontmatter_file}")
            return {}
        
        print(f"📄 Loading frontmatter from: {frontmatter_file}")
        with open(frontmatter_file, 'r') as f:
            frontmatter_data = yaml.safe_load(f)
        
        # Initialize componentOutputs section
        if 'componentOutputs' not in frontmatter_data:
            frontmatter_data['componentOutputs'] = {}
            print("✨ Created componentOutputs section")
        
        # Collect existing component files
        found_components = []
        migration_results = {}
        
        for component_type, component_dir in self.component_dirs.items():
            component_file = component_dir / f"{material_name}-laser-cleaning.yaml"
            
            if component_file.exists():
                found_components.append(component_type)
                print(f"📁 Found {component_type} component: {component_file}")
                
                try:
                    with open(component_file, 'r') as f:
                        component_data = yaml.safe_load(f)
                    
                    # Transform and embed component data
                    transformed_data = self._transform_component_data(component_type, component_data)
                    frontmatter_data['componentOutputs'][component_type] = transformed_data
                    
                    migration_results[component_type] = {
                        "status": "success",
                        "original_size": len(str(component_data)),
                        "embedded_size": len(str(transformed_data)),
                        "file_path": str(component_file)
                    }
                    
                    print(f"✅ Migrated {component_type} ({migration_results[component_type]['original_size']} → {migration_results[component_type]['embedded_size']} chars)")
                    
                except Exception as e:
                    migration_results[component_type] = {
                        "status": "failed", 
                        "error": str(e)
                    }
                    print(f"❌ Failed to migrate {component_type}: {e}")
            else:
                print(f"⚠️ No {component_type} component found")
        
        # Add migration metadata
        frontmatter_data['migrationMetadata'] = {
            "migratedAt": datetime.now().isoformat(),
            "migratedComponents": found_components,
            "migrationResults": migration_results,
            "originalComponentFiles": len(found_components),
            "method": "proof_of_concept"
        }
        
        return frontmatter_data
    
    def _transform_component_data(self, component_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform component data for embedding in frontmatter."""
        
        if component_type == "caption":
            return {
                "beforeText": data.get("before_text", ""),
                "afterText": data.get("after_text", ""),
                "technicalAnalysis": data.get("technical_analysis", {}),
                "microscopy": data.get("microscopy", {}),
                "seo": data.get("seo", {}),
                "processing": data.get("processing", {}),
                "generation": data.get("generation", {}),
                "author": data.get("author", ""),
                "materialProperties": data.get("material_properties", {})
            }
        
        elif component_type == "jsonld":
            # Handle JSON-LD content
            content = data.get("content", {})
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except Exception:
                    content = {"raw": content}
            
            return {
                "structuredData": content,
                "schemaTypes": self._extract_schema_types(content),
                "generation": data.get("generation", {})
            }
        
        elif component_type == "author":
            return {
                "authorInfo": data.get("authorInfo", {}),
                "materialContext": data.get("materialContext", {}),
                "generation": data.get("generation", {})
            }
        
        elif component_type == "metatags":
            return {
                "htmlMeta": data.get("meta", {}),
                "openGraph": data.get("og", {}),
                "twitterCard": data.get("twitter", {}),
                "generation": data.get("generation", {})
            }
        
        elif component_type == "table":
            return {
                "propertiesTable": data.get("properties_table", {}),
                "machineSettings": data.get("machine_settings", {}),
                "generation": data.get("generation", {})
            }
        
        elif component_type == "tags":
            if isinstance(data, list):
                return {"contentTags": data, "generation": {}}
            return {
                "contentTags": data.get("tags", []),
                "seoTags": data.get("seo_tags", []),
                "industryTags": data.get("industry_tags", []),
                "generation": data.get("generation", {})
            }
        
        # Fallback for other component types
        return data
    
    def _extract_schema_types(self, structured_data: Dict[str, Any]) -> list:
        """Extract schema.org types from JSON-LD."""
        types = []
        
        if isinstance(structured_data, dict):
            if "@type" in structured_data:
                types.append(structured_data["@type"])
            
            if "@graph" in structured_data:
                for item in structured_data["@graph"]:
                    if isinstance(item, dict) and "@type" in item:
                        types.append(item["@type"])
        
        return list(set(types))  # Remove duplicates
    
    def analyze_migration_benefits(self, migrated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the benefits of the migration."""
        
        migration_meta = migrated_data.get('migrationMetadata', {})
        component_outputs = migrated_data.get('componentOutputs', {})
        
        original_files = migration_meta.get('originalComponentFiles', 0)
        migrated_files = 1  # Single frontmatter file
        
        total_original_size = 0
        total_embedded_size = 0
        
        for component, result in migration_meta.get('migrationResults', {}).items():
            if result.get('status') == 'success':
                total_original_size += result.get('original_size', 0)
                total_embedded_size += result.get('embedded_size', 0)
        
        analysis = {
            "fileReduction": {
                "before": original_files,
                "after": migrated_files,
                "reduction": original_files - migrated_files,
                "reductionPercentage": ((original_files - migrated_files) / original_files * 100) if original_files > 0 else 0
            },
            "contentSizes": {
                "originalTotal": total_original_size,
                "embeddedTotal": total_embedded_size,
                "sizeDifference": total_embedded_size - total_original_size,
                "efficiencyGain": ((total_original_size - total_embedded_size) / total_original_size * 100) if total_original_size > 0 else 0
            },
            "componentBreakdown": len(component_outputs),
            "migrationSuccess": len([r for r in migration_meta.get('migrationResults', {}).values() if r.get('status') == 'success']),
            "migrationFailures": len([r for r in migration_meta.get('migrationResults', {}).values() if r.get('status') == 'failed'])
        }
        
        return analysis

def demonstrate_unified_access(migrated_data: Dict[str, Any], material_name: str):
    """Demonstrate how to access embedded component data."""
    
    print(f"\n🔍 Demonstrating unified access for {material_name}")
    
    component_outputs = migrated_data.get('componentOutputs', {})
    
    for component_type, component_data in component_outputs.items():
        print(f"\n📊 {component_type.upper()} Component:")
        
        if component_type == "caption":
            before_text = component_data.get('beforeText', '')[:100] + "..." if len(component_data.get('beforeText', '')) > 100 else component_data.get('beforeText', '')
            print(f"  Before: {before_text}")
            
        elif component_type == "jsonld":
            schema_types = component_data.get('schemaTypes', [])
            print(f"  Schema Types: {', '.join(schema_types)}")
            
        elif component_type == "author":
            author_info = component_data.get('authorInfo', {})
            if 'profile' in author_info:
                expertise = author_info['profile'].get('expertiseAreas', [])
                print(f"  Expertise: {', '.join(expertise[:2])}")
            
        elif component_type == "tags":
            content_tags = component_data.get('contentTags', [])
            print(f"  Tags: {', '.join(content_tags[:5])}")
        
        print(f"  Data Size: {len(str(component_data))} characters")

def main():
    """Demonstrate the component migration approach."""
    
    print("🚀 Component Migration to Frontmatter - Proof of Concept")
    print("=" * 60)
    
    migrator = ComponentMigrationPOC()
    
    # Demo migration for aluminum
    migrated_data = migrator.demo_migration("aluminum")
    
    if migrated_data:
        print("\n📈 Migration Analysis:")
        analysis = migrator.analyze_migration_benefits(migrated_data)
        
        print(f"  File Reduction: {analysis['fileReduction']['before']} → {analysis['fileReduction']['after']} files")
        print(f"  Reduction: {analysis['fileReduction']['reduction']} files ({analysis['fileReduction']['reductionPercentage']:.1f}%)")
        print(f"  Components Migrated: {analysis['migrationSuccess']}")
        print(f"  Migration Failures: {analysis['migrationFailures']}")
        print(f"  Content Efficiency: {analysis['contentSizes']['efficiencyGain']:.1f}% size optimization")
        
        # Show unified structure
        print("\n🏗️ Unified Frontmatter Structure:")
        print(f"  Core Material Data: {len([k for k in migrated_data.keys() if k not in ['componentOutputs', 'migrationMetadata']])} fields")
        print(f"  Component Outputs: {len(migrated_data.get('componentOutputs', {}))} components")
        print(f"  Total File Size: {len(str(migrated_data)):,} characters")
        
        # Demonstrate access patterns
        demonstrate_unified_access(migrated_data, "aluminum")
        
        # Save demo output
        demo_output_path = "aluminum-unified-frontmatter-demo.yaml"
        with open(demo_output_path, 'w') as f:
            yaml.dump(migrated_data, f, default_flow_style=False, sort_keys=False)
        
        print(f"\n💾 Demo output saved to: {demo_output_path}")
        print("📊 Migration completed successfully!")
        
        # Show key benefits
        print("\n🎯 Key Benefits Demonstrated:")
        print("  ✅ Single source of truth for all material data")
        print(f"  ✅ {analysis['fileReduction']['reduction']} fewer files to manage") 
        print("  ✅ Unified access pattern for all components")
        print("  ✅ Atomic updates - change once, affects all components")
        print("  ✅ Simplified backup and version control")
        
    else:
        print("❌ Migration demonstration failed")

if __name__ == "__main__":
    main()