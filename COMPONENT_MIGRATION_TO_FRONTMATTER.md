# Component Migration to Frontmatter Strategy

## Overview

This document outlines a comprehensive strategy to migrate all specialized component outputs (caption, jsonld, author, metatags, table, tags, etc.) from separate `.yaml` files into frontmatter files as embedded keys. This approach aligns with the frontmatter-first architecture and creates a true single-source-of-truth system.

## Current State Analysis

### Current Architecture
```
content/components/
├── frontmatter/
│   └── aluminum-laser-cleaning.yaml  # Core material data
├── caption/
│   └── aluminum-laser-cleaning.yaml  # Caption content
├── jsonld/
│   └── aluminum-laser-cleaning.yaml  # JSON-LD structured data
├── author/
│   └── aluminum-laser-cleaning.yaml  # Author information
├── metatags/
│   └── aluminum-laser-cleaning.yaml  # HTML metatags
├── table/
│   └── aluminum-laser-cleaning.yaml  # Properties table
└── tags/
    └── aluminum-laser-cleaning.yaml  # Content tags
```

### Target Architecture
```
content/components/frontmatter/
└── aluminum-laser-cleaning.yaml  # All component data embedded
```

## Migration Strategy

### Phase 1: Schema Enhancement

#### 1.1 Extend Frontmatter Schema
Add new top-level keys to `schemas/frontmatter.json`:

```json
{
  "properties": {
    // Existing frontmatter properties...
    
    "componentOutputs": {
      "type": "object",
      "description": "Embedded component outputs",
      "properties": {
        "caption": {
          "$ref": "#/definitions/CaptionOutput"
        },
        "jsonld": {
          "$ref": "#/definitions/JsonldOutput"
        },
        "author": {
          "$ref": "#/definitions/AuthorOutput"
        },
        "metatags": {
          "$ref": "#/definitions/MetatagsOutput"
        },
        "table": {
          "$ref": "#/definitions/TableOutput"
        },
        "tags": {
          "$ref": "#/definitions/TagsOutput"
        },
        "badgesymbol": {
          "$ref": "#/definitions/BadgeSymbolOutput"
        }
      }
    }
  }
}
```

#### 1.2 Define Component Output Schemas
Create detailed schemas for each component type:

```json
"definitions": {
  "CaptionOutput": {
    "type": "object",
    "properties": {
      "beforeText": {
        "type": "string",
        "description": "Pre-cleaning surface description"
      },
      "afterText": {
        "type": "string", 
        "description": "Post-cleaning surface description"
      },
      "technicalAnalysis": {
        "type": "object",
        "properties": {
          "focus": {"type": "string"},
          "uniqueCharacteristics": {"type": "array", "items": {"type": "string"}},
          "contaminationProfile": {"type": "string"}
        }
      },
      "microscopy": {
        "type": "object",
        "properties": {
          "parameters": {"type": "string"},
          "qualityMetrics": {"type": "string"}
        }
      },
      "seo": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "description": {"type": "string"}
        }
      },
      "generation": {
        "type": "object",
        "properties": {
          "generated": {"type": "string", "format": "date-time"},
          "componentType": {"type": "string"},
          "method": {"type": "string"}
        }
      }
    }
  },
  
  "JsonldOutput": {
    "type": "object",
    "properties": {
      "structuredData": {
        "type": "object",
        "description": "Complete JSON-LD structured data"
      },
      "schemaTypes": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Schema.org types included"
      }
    }
  },
  
  "AuthorOutput": {
    "type": "object", 
    "properties": {
      "authorInfo": {
        "type": "object",
        "properties": {
          "profile": {
            "type": "object",
            "properties": {
              "description": {"type": "string"},
              "expertiseAreas": {"type": "array", "items": {"type": "string"}},
              "contactNote": {"type": "string"}
            }
          }
        }
      },
      "materialContext": {
        "type": "object",
        "properties": {
          "specialization": {"type": "string"}
        }
      }
    }
  },
  
  "MetatagsOutput": {
    "type": "object",
    "properties": {
      "htmlMeta": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "description": {"type": "string"},
          "keywords": {"type": "string"},
          "author": {"type": "string"},
          "robots": {"type": "string"},
          "canonical": {"type": "string"}
        }
      },
      "openGraph": {
        "type": "object",
        "properties": {
          "title": {"type": "string"},
          "description": {"type": "string"},
          "image": {"type": "string"},
          "url": {"type": "string"}
        }
      },
      "twitterCard": {
        "type": "object",
        "properties": {
          "card": {"type": "string"},
          "title": {"type": "string"},
          "description": {"type": "string"}
        }
      }
    }
  },
  
  "TableOutput": {
    "type": "object",
    "properties": {
      "propertiesTable": {
        "type": "object",
        "properties": {
          "headers": {"type": "array", "items": {"type": "string"}},
          "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
          "caption": {"type": "string"},
          "styling": {"type": "object"}
        }
      },
      "machineSettings": {
        "type": "object",
        "properties": {
          "headers": {"type": "array", "items": {"type": "string"}},
          "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}
        }
      }
    }
  },
  
  "TagsOutput": {
    "type": "object",
    "properties": {
      "contentTags": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Generated content tags"
      },
      "seoTags": {
        "type": "array", 
        "items": {"type": "string"},
        "description": "SEO-optimized tags"
      },
      "industryTags": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Industry-specific tags"
      }
    }
  },
  
  "BadgeSymbolOutput": {
    "type": "object",
    "properties": {
      "materialSymbol": {
        "type": "string",
        "description": "Material identifier symbol"
      },
      "categoryBadge": {
        "type": "string", 
        "description": "Category classification badge"
      },
      "industryIcon": {
        "type": "string",
        "description": "Industry application icon"
      }
    }
  }
}
```

### Phase 2: Migration Implementation

#### 2.1 Create Migration Tool
```python
#!/usr/bin/env python3
"""
Component Migration Tool
Migrates existing component outputs into frontmatter files.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, Any

class ComponentMigrator:
    def __init__(self):
        self.frontmatter_dir = Path("content/components/frontmatter")
        self.component_dirs = {
            "caption": Path("content/components/caption"),
            "jsonld": Path("content/components/jsonld"), 
            "author": Path("content/components/author"),
            "metatags": Path("content/components/metatags"),
            "table": Path("content/components/table"),
            "tags": Path("content/components/tags"),
            "badgesymbol": Path("content/components/badgesymbol")
        }
    
    def migrate_material(self, material_name: str) -> bool:
        """Migrate all component outputs for a material into frontmatter."""
        frontmatter_file = self.frontmatter_dir / f"{material_name}-laser-cleaning.yaml"
        
        if not frontmatter_file.exists():
            print(f"❌ No frontmatter file for {material_name}")
            return False
        
        # Load existing frontmatter
        with open(frontmatter_file, 'r') as f:
            frontmatter_data = yaml.safe_load(f)
        
        # Initialize componentOutputs section
        if 'componentOutputs' not in frontmatter_data:
            frontmatter_data['componentOutputs'] = {}
        
        # Migrate each component type
        for component_type, component_dir in self.component_dirs.items():
            component_file = component_dir / f"{material_name}-laser-cleaning.yaml"
            
            if component_file.exists():
                try:
                    with open(component_file, 'r') as f:
                        component_data = yaml.safe_load(f)
                    
                    # Transform component data based on type
                    transformed_data = self._transform_component_data(
                        component_type, component_data
                    )
                    
                    frontmatter_data['componentOutputs'][component_type] = transformed_data
                    print(f"✅ Migrated {component_type} for {material_name}")
                    
                except Exception as e:
                    print(f"❌ Failed to migrate {component_type} for {material_name}: {e}")
        
        # Save updated frontmatter
        try:
            with open(frontmatter_file, 'w') as f:
                yaml.dump(frontmatter_data, f, default_flow_style=False, sort_keys=False)
            print(f"✅ Updated frontmatter for {material_name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save frontmatter for {material_name}: {e}")
            return False
    
    def _transform_component_data(self, component_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Transform component data to fit embedded structure."""
        
        if component_type == "caption":
            return {
                "beforeText": data.get("before_text", ""),
                "afterText": data.get("after_text", ""),
                "technicalAnalysis": data.get("technical_analysis", {}),
                "microscopy": data.get("microscopy", {}),
                "seo": data.get("seo", {}),
                "generation": data.get("generation", {})
            }
        
        elif component_type == "jsonld":
            # Parse JSON-LD content if it's a string
            structured_data = data.get("content", {})
            if isinstance(structured_data, str):
                try:
                    structured_data = json.loads(structured_data)
                except:
                    structured_data = {}
            
            return {
                "structuredData": structured_data,
                "schemaTypes": self._extract_schema_types(structured_data)
            }
        
        elif component_type == "author":
            return {
                "authorInfo": data.get("authorInfo", {}),
                "materialContext": data.get("materialContext", {})
            }
        
        elif component_type == "metatags":
            return {
                "htmlMeta": data.get("meta", {}),
                "openGraph": data.get("og", {}),
                "twitterCard": data.get("twitter", {})
            }
        
        elif component_type == "table":
            return {
                "propertiesTable": data.get("properties_table", {}),
                "machineSettings": data.get("machine_settings", {})
            }
        
        elif component_type == "tags":
            if isinstance(data, list):
                return {"contentTags": data}
            return {
                "contentTags": data.get("content_tags", []),
                "seoTags": data.get("seo_tags", []),
                "industryTags": data.get("industry_tags", [])
            }
        
        elif component_type == "badgesymbol":
            return {
                "materialSymbol": data.get("symbol", ""),
                "categoryBadge": data.get("badge", ""),
                "industryIcon": data.get("icon", "")
            }
        
        return data
    
    def _extract_schema_types(self, structured_data: Dict[str, Any]) -> list:
        """Extract schema.org types from JSON-LD."""
        types = []
        
        if "@type" in structured_data:
            types.append(structured_data["@type"])
        
        if "@graph" in structured_data:
            for item in structured_data["@graph"]:
                if "@type" in item:
                    types.append(item["@type"])
        
        return list(set(types))  # Remove duplicates

def main():
    migrator = ComponentMigrator()
    
    # Get list of materials from frontmatter directory
    materials = []
    for file in migrator.frontmatter_dir.glob("*-laser-cleaning.yaml"):
        material_name = file.stem.replace("-laser-cleaning", "")
        materials.append(material_name)
    
    print(f"Found {len(materials)} materials to migrate")
    
    successful = 0
    failed = 0
    
    for material in materials:
        if migrator.migrate_material(material):
            successful += 1
        else:
            failed += 1
    
    print(f"\n📊 Migration Summary:")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📁 Total: {len(materials)}")

if __name__ == "__main__":
    main()
```

#### 2.2 Update Generator Classes
Modify existing generators to read from and write to frontmatter:

```python
# Example: Enhanced Caption Generator
class CaptionComponentGenerator:
    def generate(self, material_name: str, material_data: dict, **kwargs) -> ComponentResult:
        """Generate caption content and embed in frontmatter."""
        
        # Generate caption content (existing logic)
        caption_data = self._generate_caption_content(material_name, material_data)
        
        # Load existing frontmatter
        frontmatter_path = f"content/components/frontmatter/{material_name.lower()}-laser-cleaning.yaml"
        frontmatter_data = self._load_frontmatter(frontmatter_path)
        
        # Embed caption in frontmatter
        if 'componentOutputs' not in frontmatter_data:
            frontmatter_data['componentOutputs'] = {}
        
        frontmatter_data['componentOutputs']['caption'] = {
            "beforeText": caption_data.get("before_text", ""),
            "afterText": caption_data.get("after_text", ""),
            "technicalAnalysis": caption_data.get("technical_analysis", {}),
            "microscopy": caption_data.get("microscopy", {}),
            "seo": caption_data.get("seo", {}),
            "generation": {
                "generated": datetime.now().isoformat(),
                "componentType": "ai_caption_fail_fast",
                "method": "embedded_frontmatter"
            }
        }
        
        # Save updated frontmatter
        self._save_frontmatter(frontmatter_path, frontmatter_data)
        
        return ComponentResult(
            success=True,
            content=yaml.dump(caption_data),
            file_path=frontmatter_path,
            component_type="caption"
        )
```

### Phase 3: Enhanced Frontmatter Generator

#### 3.1 Unified Generation Interface
```python
class UnifiedFrontmatterGenerator:
    """Enhanced frontmatter generator that manages all component outputs."""
    
    def generate_complete(self, material_name: str, components: list = None) -> UnifiedResult:
        """Generate frontmatter with all requested component outputs embedded."""
        
        # Default to all components if none specified
        if components is None:
            components = ["caption", "jsonld", "author", "metatags", "table", "tags", "badgesymbol"]
        
        # Generate base frontmatter
        frontmatter_data = self._generate_base_frontmatter(material_name)
        
        # Initialize componentOutputs
        frontmatter_data['componentOutputs'] = {}
        
        # Generate each component and embed
        for component_type in components:
            try:
                component_data = self._generate_component(component_type, material_name, frontmatter_data)
                frontmatter_data['componentOutputs'][component_type] = component_data
            except Exception as e:
                print(f"❌ Failed to generate {component_type}: {e}")
        
        # Save unified frontmatter file
        output_path = f"content/components/frontmatter/{material_name.lower()}-laser-cleaning.yaml"
        with open(output_path, 'w') as f:
            yaml.dump(frontmatter_data, f, default_flow_style=False, sort_keys=False)
        
        return UnifiedResult(
            frontmatter=frontmatter_data,
            success=True,
            file_path=output_path,
            components_generated=components
        )
    
    def extract_component(self, material_name: str, component_type: str) -> Dict[str, Any]:
        """Extract specific component data from frontmatter."""
        
        frontmatter_path = f"content/components/frontmatter/{material_name.lower()}-laser-cleaning.yaml"
        
        try:
            with open(frontmatter_path, 'r') as f:
                frontmatter_data = yaml.safe_load(f)
            
            return frontmatter_data.get('componentOutputs', {}).get(component_type, {})
            
        except Exception as e:
            print(f"❌ Failed to extract {component_type} from {material_name}: {e}")
            return {}
```

### Phase 4: Backwards Compatibility

#### 4.1 Legacy Component Support
```python
class LegacyComponentAdapter:
    """Adapter to maintain backwards compatibility during migration."""
    
    def __init__(self):
        self.unified_generator = UnifiedFrontmatterGenerator()
    
    def generate_legacy_file(self, material_name: str, component_type: str) -> bool:
        """Generate legacy component file from frontmatter data."""
        
        # Extract component data from frontmatter
        component_data = self.unified_generator.extract_component(material_name, component_type)
        
        if not component_data:
            return False
        
        # Transform back to legacy format
        legacy_data = self._transform_to_legacy(component_type, component_data)
        
        # Save legacy file
        legacy_path = f"content/components/{component_type}/{material_name.lower()}-laser-cleaning.yaml"
        os.makedirs(os.path.dirname(legacy_path), exist_ok=True)
        
        with open(legacy_path, 'w') as f:
            yaml.dump(legacy_data, f, default_flow_style=False)
        
        return True
```

## Migration Benefits

### Immediate Benefits
1. **Single Source of Truth**: All component data in one authoritative file
2. **Reduced File Clutter**: 121 materials × 7 components = 847 files → 121 files (85% reduction)
3. **Atomic Updates**: Change material data once, all components reflect changes
4. **Simplified Backup**: Single directory to backup vs. 7 component directories

### Development Benefits
1. **Faster Testing**: Read one file vs. multiple files per material
2. **Easier Debugging**: All data in one location for troubleshooting
3. **Simpler Validation**: Validate complete material data in single operation
4. **Reduced I/O**: Single file read vs. multiple file reads

### Maintenance Benefits
1. **Consistency Assurance**: No more out-of-sync component files
2. **Easier Updates**: Bulk operations on single file type
3. **Better Version Control**: Fewer files to track in git
4. **Simplified Deployment**: Single directory structure

## Implementation Timeline

### Week 1: Foundation
- [ ] Extend frontmatter schema with componentOutputs structure
- [ ] Create component migration tool
- [ ] Test migration with 5 sample materials
- [ ] Validate schema compliance

### Week 2: Migration Execution  
- [ ] Run migration tool on all 121 materials
- [ ] Validate migrated data integrity
- [ ] Create backup of original component files
- [ ] Update frontmatter generator for embedded outputs

### Week 3: Generator Updates
- [ ] Modify all component generators to use embedded approach
- [ ] Create legacy adapter for backwards compatibility
- [ ] Update run.py to handle unified frontmatter
- [ ] Comprehensive testing of new architecture

### Week 4: Cleanup and Optimization
- [ ] Archive legacy component directories
- [ ] Update documentation
- [ ] Performance optimization
- [ ] Production deployment

## Success Metrics

### File System Metrics
- **File Count Reduction**: From 847 component files to 121 frontmatter files
- **Directory Simplification**: From 8 component directories to 1 frontmatter directory
- **Storage Efficiency**: Estimated 30-40% reduction in total file size

### Performance Metrics
- **Read Performance**: 70% faster material data loading (1 file vs. 7 files)
- **Write Performance**: 60% faster generation (single file update)
- **Memory Usage**: 50% reduction in memory footprint

### Development Metrics
- **Test Execution**: 80% faster test runs (fewer file operations)
- **Bug Resolution**: 60% faster debugging (single data source)
- **Feature Development**: 70% faster new component development

## Risk Mitigation

### Data Loss Prevention
1. **Complete Backup**: Full backup of existing component directories before migration
2. **Validation Testing**: Extensive validation of migrated data
3. **Rollback Plan**: Ability to restore from legacy files if needed

### Compatibility Assurance
1. **Legacy Adapter**: Maintain ability to generate legacy component files
2. **Gradual Migration**: Phase migration to reduce risk
3. **Dual Mode Operation**: Support both embedded and legacy modes during transition

### Quality Assurance
1. **Schema Validation**: Strict schema validation for embedded components
2. **Content Verification**: Compare migrated content with original files
3. **Integration Testing**: Comprehensive testing of unified system

---

**Next Action**: Begin Phase 1 by extending the frontmatter schema to support embedded component outputs.