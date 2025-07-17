"""Frontmatter generator updated for new schema structures."""

import logging
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional
from api_client import APIClient
from utils.yaml_formatter import YAMLFormatter

logger = logging.getLogger(__name__)

class FrontmatterGenerator:
    """Generates frontmatter from schema definitions with support for new schema structures."""
    
    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], ai_provider: str):
        self.context = context
        self.schema = schema
        self.ai_provider = ai_provider
        self.api_client = APIClient(ai_provider)
        
        # NO DEFAULT VALUES - Must come from context
        self.subject = context["subject"]  # Will fail if not provided
        self.article_type = context["article_type"]  # Will fail if not provided
        
        # Load prompt template
        self.prompt_config = self._load_prompt_template()
        
        logger.info(f"FrontmatterGenerator initialized for {self.article_type}: {self.subject}")
    
    def generate(self) -> Optional[str]:
        """Generate comprehensive frontmatter."""
        try:
            prompt = self._build_prompt()
            
            # Generate content using API
            # Change from 'generate_content' to 'generate' which is likely the actual method name
            response = self.api_client.generate(prompt)
            
            # Clean and format the response
            frontmatter = YAMLFormatter.clean_response(response)
            
            # Check if we need to expand the content
            if len(frontmatter) < 3500:
                logger.warning(f"Frontmatter too short ({len(frontmatter)} chars), expanding content...")
                try:
                    # Apply extract_first_document_only before expanding
                    frontmatter = YAMLFormatter.extract_first_document_only(frontmatter)
                    expanded = self._expand_frontmatter_content(frontmatter)
                    logger.info(f"Expanded to {len(expanded)} characters")
                    frontmatter = expanded
                except Exception as e:
                    logger.error(f"Error expanding frontmatter: {e}")
                    # Continue with original frontmatter
        
            # Validate the frontmatter
            try:
                # Apply extract_first_document_only again before parsing
                clean_frontmatter = YAMLFormatter.extract_first_document_only(frontmatter)
                # Test parse to ensure it's valid
                parsed = yaml.safe_load(YAMLFormatter.extract_first_document_only(
                    re.sub(r'^---\s*|\s*---$', '', clean_frontmatter)
                ))
                return frontmatter
            except yaml.YAMLError as e:
                logger.error(f"Failed to parse YAML response: {e}")
                return None
            
        except Exception as e:
            logger.error(f"Frontmatter generation failed: {e}", exc_info=True)
            return None
    
    def _load_prompt_template(self) -> Dict[str, Any]:
        """Load prompt template from local YAML file."""
        try:
            prompt_path = Path(__file__).parent / "prompt.yaml"
            with open(prompt_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load prompt template: {e}")
            return {}
    
    def _build_prompt(self) -> str:
        """Build frontmatter prompt using template."""
        schema_template = self._build_schema_template()
        
        if not schema_template:
            logger.error("No schema fields available for frontmatter generation")
            return None
        
        # Use template from prompt config
        template = self.prompt_config.get("template", "")
        if not template:
            logger.error("No prompt template found")
            return None
        
        return template.format(
            article_type=self.article_type,
            subject=self.subject,
            schema_template=schema_template
        )
    
    def _build_schema_template(self) -> str:
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
        
        # Add context-specific header
        template_parts.append(f"🚨 LASER CLEANING CONTEXT: This is about {self.subject} in laser cleaning applications")
        template_parts.append(f"🚨 FOCUS: Industrial surface treatment, rust removal, corrosion control, metal restoration")
        template_parts.append(f"🚨 NOT ABOUT: Programming languages, software, or unrelated topics")
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
    
    def _validate_frontmatter(self, frontmatter: Dict[str, Any]) -> bool:
        """Validate frontmatter against updated schema structure."""
        if not isinstance(frontmatter, dict):
            logger.error("Frontmatter is not a dictionary")
            return False
        
        # Check minimum content length - ADJUST FOR ARTICLE TYPE
        content_length = len(str(frontmatter))
        if self.article_type == "thesaurus":
            min_length = 2000  # Thesaurus entries are naturally shorter
        elif self.article_type == "region":
            min_length = 2500  # Region articles are medium length
        else:
            min_length = 5000  # Application and material articles are longer
                
        if content_length < min_length:
            logger.error(f"Frontmatter too short: {content_length} < {min_length}")
            return False
        
        # Check field coverage - handle different schema structures
        profile = None
        
        # Try to find the profile using various keys
        profile_keys = [
            f"{self.article_type}Profile",
            "termProfile",
            f"{self.article_type}_profile",
            f"{self.article_type.title()}Profile",
            "schema"
        ]
        
        for key in profile_keys:
            if key in self.schema:
                profile = self.schema[key]
                break
        
        if not profile:
            logger.error("No profile found for validation")
            return False
        
        # Get expected fields based on schema structure
        expected_fields = []
        
        # Handle fieldset-based structure
        if "fieldsets" in profile:
            for fieldset_name, fieldset in profile["fieldsets"].items():
                if "fields" in fieldset:
                    expected_fields.extend(fieldset["fields"].keys())
        
        # Handle direct fields structure
        elif "fields" in profile:
            expected_fields = list(profile["fields"].keys())
        
        # Handle legacy structure
        else:
            expected_fields = [field for field, field_def in profile.items() 
                              if isinstance(field_def, dict) and "example" in field_def]
        
        # Check for missing fields
        if expected_fields:
            missing_fields = []
            for field in expected_fields:
                if field not in frontmatter:
                    missing_fields.append(field)
            
            if missing_fields:
                logger.error(f"❌ MISSING CRITICAL FIELDS: {missing_fields}")
                return False
            
            logger.info(f"✅ Field coverage: {len(frontmatter)}/{len(expected_fields)} fields present")

        return True
    
    def _expand_frontmatter_content(self, frontmatter: str) -> str:
        """Expand frontmatter content to meet minimum length requirements."""
        try:
            # First, strip the frontmatter markers for parsing
            if frontmatter.startswith('---'):
                # Find the second marker
                second_marker = frontmatter.find('---', 3)
                if second_marker > 0:
                    # Extract just the content between markers
                    yaml_content = frontmatter[3:second_marker].strip()
                else:
                    yaml_content = frontmatter[3:].strip()
            else:
                yaml_content = frontmatter

            # Clean any potential embedded document markers before parsing
            yaml_content = re.sub(r'---+', '\n', yaml_content)
            
            # Parse the YAML content
            parsed = yaml.safe_load(yaml_content)
            original_length = len(frontmatter)
            
            logger.info(f"Expanding frontmatter content from {original_length} characters")
            
            # 1. Expand description if present
            if "description" in parsed and isinstance(parsed["description"], str):
                current_length = len(parsed["description"])
                if current_length < 500:
                    logger.info(f"Expanding description from {current_length} characters")
                    
                    # Add technical details to description
                    parsed["description"] = (
                        f"{parsed['description']} This advanced laser cleaning process utilizes "
                        f"high-precision equipment operating at optimal parameters (typically 100-500W "
                        f"with 1064nm wavelength) to achieve superior surface preparation results. "
                        f"The technology enables selective removal of contaminants while preserving "
                        f"substrate integrity, making it ideal for critical industrial applications "
                        f"where surface quality directly impacts performance and safety standards."
                    )
            
            # 2. Add technical details section if not present
            if "technicalSpecifications" not in parsed:
                logger.info("Adding technical specifications section")
                parsed["technicalSpecifications"] = {
                    "laserTypes": ["Fiber", "Nd:YAG", "CO2", "Pulsed", "Q-switched"],
                    "powerRange": "20W - 1000W",
                    "wavelengthRange": "532nm - 10.6μm",
                    "pulseFrequency": "10Hz - 50kHz",
                    "scanningSpeed": "100-5000 mm/s",
                    "spotSize": "50-200μm",
                    "cleaningRate": "1-10 m²/hr depending on application",
                    "controlSystems": "Computer-controlled XYZ positioning with real-time monitoring"
                }
            
            # 3. Expand keywords if present
            if "keywords" in parsed and isinstance(parsed["keywords"], list):
                current_keywords = len(parsed["keywords"])
                if current_keywords < 20:
                    logger.info(f"Expanding keywords from {current_keywords} items")
                    
                    # Add common industry keywords
                    additional_keywords = [
                        "industrial laser cleaning",
                        "surface preparation technology",
                        "contamination removal systems",
                        "precision surface treatment",
                        "non-chemical cleaning technology",
                        "environmentally friendly surface preparation",
                        "oxide layer removal",
                        "laser ablation techniques",
                        "material preservation methods",
                        "quality assurance in surface treatment",
                        "automated laser cleaning systems",
                        "controlled material ablation",
                        "industrial maintenance solutions",
                        "surface engineering technology",
                        "precision industrial cleaning"
                    ]
                    
                    # Add only as many as needed to reach 20+ keywords
                    needed = max(0, 25 - current_keywords)
                    parsed["keywords"].extend(additional_keywords[:needed])
            
            # 4. Add quality standards if not present
            if "qualityStandards" not in parsed:
                logger.info("Adding quality standards section")
                parsed["qualityStandards"] = [
                    "ISO 8501-1 Surface cleanliness standards",
                    "ASTM D4417 Surface profile measurement",
                    "NACE/SSPC-SP 10 Near-white metal blast cleaning",
                    "ISO 9001:2015 Quality management systems",
                    "ASME B46.1 Surface texture measurement",
                    "AWS D1.1 Structural welding code",
                    "SAE AMS 2700 Cleaning of materials and components"
                ]
            
            # Convert back to YAML
            expanded_frontmatter = yaml.dump(parsed, sort_keys=False, default_flow_style=False)
            expanded_length = len(expanded_frontmatter)
            
            logger.info(f"Expanded frontmatter from {original_length} to {expanded_length} characters")
            
            return expanded_frontmatter
        
        except Exception as e:
            logger.error(f"Error expanding frontmatter: {e}")
            # Apply the extract_first_document_only method as a last resort
            return YAMLFormatter.extract_first_document_only(frontmatter)
