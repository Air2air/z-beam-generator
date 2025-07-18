"""Template building functions for schema-based frontmatter generation."""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SchemaTemplateBuilder:
    """Builds templates from schema definitions for frontmatter generation."""
    
    def __init__(self, schema: Dict[str, Any], article_type: str, subject: str):
        """Initialize the template builder with schema and context information."""
        self.schema = schema
        self.article_type = article_type
        self.subject = subject
    
    def build_schema_template(self) -> str:
        """Build template using updated schema structure."""
        # Updated profile key handling for new schema organization
        profile_keys = [
            f"{self.article_type}Profile",  # Standard: "applicationProfile"
            "termProfile",                  # Thesaurus: "termProfile"
            f"{self.article_type}_profile", # Snake case
            f"{self.article_type.title()}Profile",  # Title case
            "schema"                        # New unified schema key
        ]
        
        profile = None
        for key in profile_keys:
            if key in self.schema:
                profile = self.schema[key]
                logger.info(f"✅ Found profile using key: {key}")
                break
        
        if profile:
            # Check if we have a nested structure with fieldsets
            if "fieldsets" in profile:
                return self._build_template_from_fieldsets(profile["fieldsets"])
            # Check if we have a nested structure with fields
            elif "fields" in profile:
                return self._build_template_from_fields(profile["fields"])
            # Otherwise use the existing profile approach
            else:
                return self._build_schema_template_from_profile(profile)
        else:
            logger.error(f"❌ No profile found. Tried keys: {profile_keys}")
            logger.error(f"❌ Available schema keys: {list(self.schema.keys())}")
            return None  # NO FALLBACK - FAIL FAST
    
    def _build_template_from_fieldsets(self, fieldsets: Dict[str, Any]) -> str:
        """Build template from the new fieldset-based schema structure."""
        template_parts = []
        
        # Get context from schema
        profile = self._get_profile()
        context = profile.get("generatorConfig", {}).get("context", {})
        focus = context.get("focus", "Industrial surface treatment, rust removal, corrosion control")
        exclusions = context.get("exclusions", "Programming languages, software, or unrelated topics")
        
        # Add context-specific header
        template_parts.append(f"🚨 CONTEXT: This is about {self.subject} in {context.get('domain', 'laser cleaning')} applications")
        template_parts.append(f"🚨 FOCUS: {focus}")
        template_parts.append(f"🚨 NOT ABOUT: {exclusions}")
        template_parts.append("=" * 60)
        
        # Count total fields across all fieldsets
        total_fields = 0
        for fieldset_name, fieldset in fieldsets.items():
            if "fields" in fieldset:
                total_fields += len(fieldset["fields"])
        
        template_parts.append(f"🚨 CRITICAL: ALL {total_fields} FIELDS BELOW ARE MANDATORY")
        template_parts.append("=" * 60)
        
        # Process each fieldset
        field_index = 1
        for fieldset_name, fieldset in fieldsets.items():
            template_parts.append(f"\n## FIELDSET: {fieldset_name}")
            template_parts.append("-" * 50)
            
            if "description" in fieldset:
                template_parts.append(f"Purpose: {fieldset['description']}")
                
            if "fields" in fieldset:
                for field_name, field_def in fieldset["fields"].items():
                    template_parts.append(f"\n🚨 MANDATORY FIELD {field_index}/{total_fields}: {field_name}")
                    template_parts.append("=" * 50)
                    template_parts.append(f"🚨 THIS FIELD IS REQUIRED - MUST APPEAR IN OUTPUT")
                    
                    # Add field type and description
                    field_type = field_def.get("type", "unknown")
                    field_description = field_def.get("description", "No description")
                    template_parts.append(f"Type: {field_type}")
                    template_parts.append(f"Description: {field_description}")
                    
                    # Add example with processing instruction
                    if "example" in field_def:
                        example = field_def["example"]
                        if isinstance(example, str):
                            processed_value = self._replace_placeholders(example)
                            template_parts.append(f"Example: {processed_value}")
                            template_parts.append(f"🚨 GENERATE: Comprehensive 300-500 character content for {field_name}")
                        elif isinstance(example, list):
                            processed_items = [self._replace_placeholders(str(item)) for item in example]
                            template_parts.append(f"Examples: {processed_items}")
                            template_parts.append(f"🚨 GENERATE: Expanded array with 5-10 entries for {field_name}")
                    
                    # Always allow these core fields
                    basic_fields = ["name", "description", "author", "tags", "keywords"]  # Hardcoded field list

                    # Special handling for common array fields
                    if field_name == "keywords":  # Hardcoded field name
                        return [
                            f"{self.subject} {self._generate_keyword_suffix()}",
                            f"{self._generate_keyword_prefix()} {self.subject}",
                            f"{self.subject} {self._generate_keyword_suffix()}"
                        ]
                    
                    template_parts.append(f"🚨 FAILURE TO INCLUDE {field_name} WILL RESULT IN REJECTION")
                    template_parts.append("")  # Add spacing
                    field_index += 1
        
        # Add validation footer
        template_parts.append("=" * 60)
        template_parts.append("🚨 FINAL VALIDATION CHECKLIST:")
        template_parts.append("Before submitting, verify ALL required fields are in your YAML:")
        
        # Create a list of all fields across fieldsets for validation
        all_fields = []
        for fieldset_name, fieldset in fieldsets.items():
            if "fields" in fieldset:
                all_fields.extend(fieldset["fields"].keys())
        
        for field in all_fields:
            template_parts.append(f"✓ {field}")
        
        template_parts.append(f"🚨 TOTAL REQUIRED FIELDS: {len(all_fields)}")
        template_parts.append("🚨 ALL FIELDS MUST BE PRESENT OR OUTPUT WILL BE REJECTED")
        template_parts.append("=" * 60)
        
        return '\n'.join(template_parts)
    
    def _build_template_from_fields(self, fields: Dict[str, Any]) -> str:
        """Build template from direct fields structure."""
        template_parts = []
        
        # Add context-specific header
        template_parts.append(f"🚨 LASER CLEANING CONTEXT: This is about {self.subject} in laser cleaning applications")
        template_parts.append(f"🚨 FOCUS: Industrial surface treatment, rust removal, corrosion control, metal restoration")
        template_parts.append(f"🚨 NOT ABOUT: Programming languages, software, or unrelated topics")
        template_parts.append("=" * 60)
        
        # Add header with field count
        field_count = len(fields)
        template_parts.append(f"🚨 CRITICAL: ALL {field_count} FIELDS BELOW ARE MANDATORY")
        template_parts.append("=" * 60)
        template_parts.append("EVERY FIELD MUST BE PROCESSED - NO EXCEPTIONS")
        template_parts.append("=" * 60)
        
        # Process each field
        field_index = 1
        for field_name, field_def in fields.items():
            template_parts.append(f"\n🚨 MANDATORY FIELD {field_index}/{field_count}: {field_name}")
            template_parts.append("=" * 50)
            template_parts.append(f"🚨 THIS FIELD IS REQUIRED - MUST APPEAR IN OUTPUT")
            
            # Add field type and description
            field_type = field_def.get("type", "unknown")
            field_description = field_def.get("description", "No description")
            template_parts.append(f"Type: {field_type}")
            template_parts.append(f"Description: {field_description}")
            
            # Add example with processing instruction
            if "example" in field_def:
                example = field_def["example"]
                if isinstance(example, str):
                    processed_value = self._replace_placeholders(example)
                    template_parts.append(f"Example: {processed_value}")
                    template_parts.append(f"🚨 GENERATE: Comprehensive 300-500 character content for {field_name}")
                elif isinstance(example, list):
                    processed_items = [self._replace_placeholders(str(item)) for item in example]
                    template_parts.append(f"Examples: {processed_items}")
                    template_parts.append(f"🚨 GENERATE: Expanded array with 5-10 entries for {field_name}")
            
            # Always allow these core fields
            basic_fields = ["name", "description", "author", "tags", "keywords"]  # Hardcoded field list

            # Special handling for common array fields
            if field_name == "keywords":  # Hardcoded field name
                return [
                    f"{self.subject} {self._generate_keyword_suffix()}",
                    f"{self._generate_keyword_prefix()} {self.subject}",
                    f"{self.subject} {self._generate_keyword_suffix()}"
                ]
            
            template_parts.append(f"🚨 FAILURE TO INCLUDE {field_name} WILL RESULT IN REJECTION")
            template_parts.append("")  # Add spacing
            field_index += 1
        
        # Add validation footer
        template_parts.append("=" * 60)
        template_parts.append("🚨 FINAL VALIDATION CHECKLIST:")
        template_parts.append("Before submitting, verify ALL fields below are in your YAML:")
        
        for field_name in fields:
            template_parts.append(f"✓ {field_name}")
        
        template_parts.append(f"🚨 TOTAL REQUIRED FIELDS: {field_count}")
        template_parts.append("🚨 ALL FIELDS MUST BE PRESENT OR OUTPUT WILL BE REJECTED")
        template_parts.append("=" * 60)
        
        return '\n'.join(template_parts)
    
    def _build_schema_template_from_profile(self, profile: Dict[str, Any]) -> str:
        """Build dynamic schema template with field-specific instructions (legacy method)."""
        template_parts = []
        
        # Add context-specific header
        template_parts.append(f"🚨 LASER CLEANING CONTEXT: This is about {self.subject} in laser cleaning applications")
        template_parts.append(f"🚨 FOCUS: Industrial surface treatment, rust removal, corrosion control, metal restoration")
        template_parts.append(f"🚨 NOT ABOUT: Programming languages, software, or unrelated topics")
        template_parts.append("=" * 60)
        
        # Add aggressive field header
        field_count = len(profile)
        template_parts.append(f"🚨 CRITICAL: ALL {field_count} FIELDS BELOW ARE MANDATORY")
        template_parts.append("=" * 60)
        template_parts.append("EVERY FIELD MUST BE PROCESSED - NO EXCEPTIONS")
        template_parts.append("=" * 60)
        
        fields_with_examples = []
        field_index = 1
        
        for field_name, field_def in profile.items():
            if isinstance(field_def, dict) and "example" in field_def:
                fields_with_examples.append(field_name)
                
                # Add field header with emphasis
                template_parts.append(f"\n🚨 MANDATORY FIELD {field_index}/{field_count}: {field_name}")
                template_parts.append("=" * 50)
                template_parts.append(f"🚨 THIS FIELD IS REQUIRED - MUST APPEAR IN OUTPUT")
                
                # Add field type and description
                field_type = field_def.get("type", "unknown")
                field_description = field_def.get("description", "No description")
                template_parts.append(f"Type: {field_type}")
                template_parts.append(f"Description: {field_description}")
                
                # Add example with processing instruction
                example = field_def["example"]
                if isinstance(example, str):
                    processed_value = self._replace_placeholders(example)
                    template_parts.append(f"Example: {processed_value}")
                    template_parts.append(f"🚨 GENERATE: Comprehensive 300-500 character content for {field_name}")
                elif isinstance(example, list):
                    processed_items = [self._replace_placeholders(str(item)) for item in example]
                    template_parts.append(f"Examples: {processed_items}")
                    template_parts.append(f"🚨 GENERATE: Expanded array with 5-10 entries for {field_name}")
                
                template_parts.append(f"🚨 FAILURE TO INCLUDE {field_name} WILL RESULT IN REJECTION")
                template_parts.append("")  # Add spacing
                field_index += 1
    
        # Add final validation checklist
        template_parts.append("=" * 60)
        template_parts.append("🚨 FINAL VALIDATION CHECKLIST:")
        template_parts.append("Before submitting, verify ALL fields below are in your YAML:")
        for field in fields_with_examples:
            template_parts.append(f"✓ {field}")
        template_parts.append(f"🚨 TOTAL REQUIRED FIELDS: {len(fields_with_examples)}")
        template_parts.append("🚨 ALL FIELDS MUST BE PRESENT OR OUTPUT WILL BE REJECTED")
        template_parts.append("=" * 60)
        
        return '\n'.join(template_parts)
    
    def _replace_placeholders(self, value: str) -> str:
        """Replace schema placeholders with laser cleaning context."""
        # Enhanced context mapping
        placeholder_map = {
            "materialName": f"{self.subject} (laser cleaning applications)",
            "applicationName": f"{self.subject} removal using laser technology",
            "regionName": f"{self.subject} in industrial laser cleaning",
            "term": f"{self.subject} (laser cleaning terminology)",
            "{{materialName}}": f"{self.subject} (laser cleaning applications)",
            "{{applicationName}}": f"{self.subject} removal using laser technology",
            "{{regionName}}": f"{self.subject} in industrial laser cleaning",
            "{{term}}": f"{self.subject} (laser cleaning terminology)"
        }
        
        for placeholder, replacement in placeholder_map.items():
            value = value.replace(placeholder, replacement)
        
        return value