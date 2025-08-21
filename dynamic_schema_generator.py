#!/usr/bin/env python3
"""
Dynamic Schema Generator - Makes schemas fully dynamic and validates against component examples

FEATURES:
1. Dynamically loads all schema configurations
2. Uses fieldContentMapping for content generation
3. Validates schema requirements against actual component outputs
4. Provides schema-driven validation instead of hardcoded fields
"""

import yaml
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class SchemaValidationResult:
    """Result of schema validation against component output."""
    is_valid: bool
    missing_fields: List[str]
    extra_fields: List[str]
    field_type_errors: List[str]
    schema_name: str


@dataclass
class ComponentExample:
    """Parsed component example for validation."""
    component_type: str
    content: str
    parsed_frontmatter: Optional[Dict] = None
    file_path: str = ""


class DynamicSchemaValidator:
    """Fully dynamic schema validator that uses schema configurations."""
    
    def __init__(self, schemas_dir: str = "schemas"):
        self.schemas_dir = Path(schemas_dir)
        self.schemas = {}
        self.load_all_schemas()
    
    def load_all_schemas(self):
        """Load all schemas and their configurations."""
        logger.info(f"Loading schemas from {self.schemas_dir}")
        
        for schema_file in self.schemas_dir.glob("*.json"):
            try:
                with open(schema_file) as f:
                    schema_data = json.load(f)
                    self.schemas[schema_file.stem] = schema_data
                    logger.info(f"✅ Loaded schema: {schema_file.stem}")
            except Exception as e:
                logger.error(f"❌ Failed to load {schema_file}: {e}")
        
        logger.info(f"Loaded {len(self.schemas)} schemas")
    
    def get_schema_for_component(self, component_type: str, material_category: str = None) -> Optional[Dict]:
        """Get the appropriate schema for a component type."""
        # Priority mapping for component types to schemas
        component_schema_map = {
            'frontmatter': 'material',  # Use material schema for frontmatter
            'content': 'base',
            'jsonld': 'base',
            'metatags': 'base',
            'table': 'base',
            'tags': 'base',
            'bullets': 'base',
            'caption': 'base',
            'propertiestable': 'material'
        }
        
        schema_name = component_schema_map.get(component_type, 'base')
        return self.schemas.get(schema_name)
    
    def get_required_fields_from_schema(self, schema: Dict, component_type: str = 'frontmatter') -> List[str]:
        """Extract required fields dynamically from schema."""
        required_fields = []
        
        # Look for validation section first
        if 'validation' in schema:
            validation = schema['validation']
            if component_type in validation:
                required_fields = validation[component_type].get('requiredFields', [])
            elif 'frontmatter' in validation:
                required_fields = validation['frontmatter'].get('requiredFields', [])
        
        # If no validation section, extract from profile structure
        if not required_fields:
            for profile_key, profile_data in schema.items():
                if 'profile' in profile_data and isinstance(profile_data['profile'], dict):
                    for field_name, field_config in profile_data['profile'].items():
                        if isinstance(field_config, dict) and field_config.get('required', False):
                            required_fields.append(field_name)
        
        return required_fields
    
    def get_field_content_mapping(self, schema: Dict) -> Dict[str, str]:
        """Extract fieldContentMapping from schema for dynamic content generation."""
        for profile_key, profile_data in schema.items():
            if 'generatorConfig' in profile_data:
                config = profile_data['generatorConfig']
                if 'contentGeneration' in config:
                    return config['contentGeneration'].get('fieldContentMapping', {})
        return {}
    
    def validate_frontmatter_against_schema(self, frontmatter: Dict, schema: Dict) -> SchemaValidationResult:
        """Validate frontmatter against schema dynamically."""
        schema_name = "unknown"
        for key in schema.keys():
            if 'Profile' in key or 'profile' in key.lower():
                schema_name = key
                break
        
        # Get required fields dynamically
        required_fields = self.get_required_fields_from_schema(schema, 'frontmatter')
        
        # Check for missing required fields
        missing_fields = []
        for field in required_fields:
            if field not in frontmatter:
                missing_fields.append(field)
        
        # Get schema profile structure for type validation
        profile = {}
        for profile_key, profile_data in schema.items():
            if 'profile' in profile_data:
                profile = profile_data['profile']
                break
        
        # Check field types
        field_type_errors = []
        extra_fields = []
        
        for field_name, field_value in frontmatter.items():
            if field_name in profile:
                expected_type = profile[field_name].get('type', 'string')
                if not self._validate_field_type(field_value, expected_type, field_name):
                    field_type_errors.append(f"{field_name}: expected {expected_type}")
            else:
                # Check if this is an extra field not in schema
                if field_name not in ['subject', 'article_type']:  # Allow template fields
                    extra_fields.append(field_name)
        
        is_valid = len(missing_fields) == 0 and len(field_type_errors) == 0
        
        return SchemaValidationResult(
            is_valid=is_valid,
            missing_fields=missing_fields,
            extra_fields=extra_fields,
            field_type_errors=field_type_errors,
            schema_name=schema_name
        )
    
    def _validate_field_type(self, value: Any, expected_type: str, field_name: str) -> bool:
        """Validate field type against schema expectation."""
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'array':
            return isinstance(value, list)
        elif expected_type == 'object':
            return isinstance(value, dict)
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        else:
            return True  # Unknown type, assume valid


class ComponentExampleAnalyzer:
    """Analyzes component examples to understand expected structure."""
    
    def __init__(self, content_dir: str = "content/components"):
        self.content_dir = Path(content_dir)
    
    def load_component_examples(self, component_type: str, limit: int = 5) -> List[ComponentExample]:
        """Load example files for a component type."""
        examples = []
        component_dir = self.content_dir / component_type
        
        if not component_dir.exists():
            logger.warning(f"Component directory not found: {component_dir}")
            return examples
        
        md_files = list(component_dir.glob("*.md"))[:limit]
        
        for file_path in md_files:
            try:
                with open(file_path) as f:
                    content = f.read()
                
                example = ComponentExample(
                    component_type=component_type,
                    content=content,
                    file_path=str(file_path)
                )
                
                # Parse frontmatter if it's a frontmatter component
                if component_type == 'frontmatter' and content.strip().startswith('---'):
                    example.parsed_frontmatter = self._parse_frontmatter(content)
                
                examples.append(example)
                
            except Exception as e:
                logger.error(f"Failed to load example {file_path}: {e}")
        
        logger.info(f"Loaded {len(examples)} examples for {component_type}")
        return examples
    
    def _parse_frontmatter(self, content: str) -> Optional[Dict]:
        """Parse YAML frontmatter from markdown content."""
        try:
            if not content.strip().startswith('---'):
                return None
            
            # Find the end of frontmatter
            lines = content.split('\n')
            yaml_lines = []
            in_frontmatter = False
            
            for line in lines:
                if line.strip() == '---':
                    if in_frontmatter:
                        break  # End of frontmatter
                    else:
                        in_frontmatter = True  # Start of frontmatter
                        continue
                
                if in_frontmatter:
                    yaml_lines.append(line)
            
            if yaml_lines:
                yaml_content = '\n'.join(yaml_lines)
                return yaml.safe_load(yaml_content)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to parse frontmatter: {e}")
            return None


class SchemaComponentMatcher:
    """Matches schemas against component examples to identify mismatches."""
    
    def __init__(self):
        self.validator = DynamicSchemaValidator()
        self.analyzer = ComponentExampleAnalyzer()
    
    def validate_all_components_against_schemas(self) -> Dict[str, List[SchemaValidationResult]]:
        """Validate all component types against their schemas."""
        results = {}
        
        # Focus on frontmatter components since they have structured data
        component_type = 'frontmatter'
        logger.info(f"Validating {component_type} components")
        
        # Load examples
        examples = self.analyzer.load_component_examples(component_type, limit=5)
        
        if not examples:
            logger.warning(f"No examples found for {component_type}")
            return results
        
        component_results = []
        
        for example in examples:
            logger.info(f"Processing example: {Path(example.file_path).name}")
            
            if example.parsed_frontmatter:
                logger.info(f"Found frontmatter with {len(example.parsed_frontmatter)} fields")
                
                # Get appropriate schema
                schema = self.validator.get_schema_for_component(component_type)
                
                if schema:
                    result = self.validator.validate_frontmatter_against_schema(
                        example.parsed_frontmatter, schema
                    )
                    result.schema_name = f"{component_type} -> material schema"
                    component_results.append(result)
                    
                    logger.info(f"Validation result: Valid={result.is_valid}, Missing={len(result.missing_fields)}, Extra={len(result.extra_fields)}")
                else:
                    logger.warning(f"No schema found for {component_type}")
            else:
                logger.warning(f"No frontmatter parsed for {Path(example.file_path).name}")
        
        if component_results:
            results[component_type] = component_results
        
        return results
    
    def generate_schema_validation_report(self) -> str:
        """Generate a comprehensive validation report."""
        results = self.validate_all_components_against_schemas()
        
        report = ["# Schema Validation Report", ""]
        
        for component_type, validation_results in results.items():
            report.append(f"## {component_type.title()} Component")
            report.append("")
            
            for i, result in enumerate(validation_results, 1):
                report.append(f"### Example {i}")
                report.append(f"**Schema:** {result.schema_name}")
                report.append(f"**Valid:** {'✅ Yes' if result.is_valid else '❌ No'}")
                report.append("")
                
                if result.missing_fields:
                    report.append("**Missing Required Fields:**")
                    for field in result.missing_fields:
                        report.append(f"- {field}")
                    report.append("")
                
                if result.extra_fields:
                    report.append("**Extra Fields (not in schema):**")
                    for field in result.extra_fields:
                        report.append(f"- {field}")
                    report.append("")
                
                if result.field_type_errors:
                    report.append("**Type Errors:**")
                    for error in result.field_type_errors:
                        report.append(f"- {error}")
                    report.append("")
        
        return "\n".join(report)


def main():
    """Run schema validation analysis."""
    logger.info("Starting dynamic schema validation analysis")
    
    matcher = SchemaComponentMatcher()
    report = matcher.generate_schema_validation_report()
    
    # Save report
    report_file = Path("schema_validation_report.md")
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"✅ Schema validation report saved to {report_file}")
    
    # Print summary to console
    print("\n" + "="*60)
    print("SCHEMA VALIDATION SUMMARY")
    print("="*60)
    print(report)


if __name__ == "__main__":
    main()
