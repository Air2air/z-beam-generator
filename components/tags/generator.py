#!/usr/bin/env python3
"""
Tags Generator - API-based tags generation for laser cleaning materials.
"""

import logging
from typing import Dict, Optional, Any

from generators.component_generators import APIComponentGenerator, ComponentResult
from utils.core.material_name_resolver import get_material_name_resolver

logger = logging.getLogger(__name__)


class TagsComponentGenerator(APIComponentGenerator):
    """API-based generator for tags components"""

    def __init__(self):
        super().__init__("tags")

    def get_component_info(self) -> Dict[str, Any]:
        """Get component information"""
        return {
            "name": "tags",
            "description": "Navigation tags generation for laser cleaning articles",
            "version": "2.0.0",
            "requires_api": True,
            "type": "dynamic",
        }

    def generate(
        self,
        material_name: str,
        material_data: Dict,
        api_client=None,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> ComponentResult:
        """Generate tags using frontmatter data only (no AI)"""
        try:
            # Pre-validate frontmatter data if available
            if frontmatter_data:
                frontmatter_data = self._sanitize_frontmatter_data(frontmatter_data)
            
            # Create template variables
            template_vars = self._create_template_vars(
                material_name,
                material_data,
                author_info,
                frontmatter_data,
                schema_fields,
            )

            # Generate tags from frontmatter data
            final_tags = self._generate_tags_from_frontmatter(material_name, material_data, frontmatter_data, template_vars)

            # Create structured YAML output
            yaml_content = self._format_as_yaml(material_name, final_tags, template_vars)
            
            # Validate YAML syntax
            try:
                import yaml
                yaml.safe_load(yaml_content)
            except yaml.YAMLError as yaml_err:
                logger.warning(f"Generated YAML has syntax issues for {material_name}: {yaml_err}")
                # Attempt to fix common issues
                yaml_content = self._fix_yaml_syntax(yaml_content)
            
            # Add version info
            from datetime import datetime
            version_info = f"""---
Material: "{material_name.lower()}"
Component: tags
Generated: {datetime.now().isoformat()}
Generator: Z-Beam v1.0.0 (Frontmatter-Based)
Format: YAML v2.0
---"""
            
            final_content = f"{yaml_content}\n\n{version_info}"

            return ComponentResult(
                component_type="tags", content=final_content, success=True
            )

        except Exception as e:
            logger.error(f"Error generating tags for {material_name}: {e}")
            return ComponentResult(
                component_type="tags",
                content="",
                success=False,
                error_message=str(e),
            )

    def _format_as_yaml(self, material_name: str, tags_list: list, template_vars: Dict) -> str:
        """Format tags as YAML for frontmatter embedding"""
        from datetime import datetime
        
        # Simple essential tags format for frontmatter
        yaml_content = "essentialTags:\n"
        for tag in tags_list:
            yaml_content += f"  - {tag.strip()}\n"
        
        yaml_content += "generation:\n"
        yaml_content += f"  generated: \"{datetime.now().isoformat()}\"\n"
        yaml_content += "  method: \"frontmatter_essential\"\n"
        yaml_content += f"  totalTags: {len(tags_list)}\n"
        yaml_content += "  tagPriority: \"essential\"\n"
        
        return yaml_content

    def _generate_tags_from_frontmatter(self, material_name: str, material_data: Dict, frontmatter_data: Optional[Dict], template_vars: Dict) -> list:
        """Generate exactly 10 essential tags for frontmatter"""
        tags = []
        
        # Priority 1: Core identifiers (4 tags)
        # 1. Material name (normalized)
        material_slug = material_name.lower().replace(' ', '-').replace('_', '-')
        tags.append(material_slug)
        
        # 2. Category
        category = template_vars['material_category'].lower()
        tags.append(category)
        
        # 3. Author name (normalized) 
        author_slug = template_vars['author_name'].lower().replace(' ', '-').replace('.', '')
        tags.append(author_slug)
        
        # 4. Core process
        tags.append('laser-cleaning')
        
        # Priority 2: Material classification (2-3 tags)
        subcategory = template_vars.get('material_subcategory', '').lower()
        if subcategory and subcategory != category:
            subcategory_slug = subcategory.replace('_', '-').replace(' ', '-')
            tags.append(subcategory_slug)
        
        # Material type refinement
        if category == 'metals':
            if subcategory in ['light_metals', 'non_ferrous']:
                tags.append('lightweight')
            elif subcategory in ['ferrous', 'steel']:
                tags.append('ferrous')
            elif subcategory in ['precious', 'noble']:
                tags.append('precious')
            else:
                tags.append('alloy')
        elif category == 'ceramics':
            tags.append('ceramic')
        elif category == 'composites':
            tags.append('composite')
        elif category == 'polymers':
            tags.append('polymer')
        else:
            tags.append('industrial')
        
        # Priority 3: Application context (2-3 tags)
        # Extract primary industry from frontmatter if available
        primary_industry = None
        if frontmatter_data:
            # Look for industry keywords in description or applications
            description = frontmatter_data.get('description', '').lower()
            applications = frontmatter_data.get('applications', [])
            
            industry_keywords = {
                'aerospace': 'aerospace',
                'automotive': 'automotive', 
                'medical': 'medical',
                'electronics': 'electronics',
                'marine': 'marine',
                'construction': 'construction',
                'manufacturing': 'manufacturing'
            }
            
            # Check description first
            for keyword, industry in industry_keywords.items():
                if keyword in description:
                    primary_industry = industry
                    break
            
            # Check applications if no industry found in description
            if not primary_industry and isinstance(applications, list):
                for app in applications:
                    if isinstance(app, str):
                        app_lower = app.lower()
                        for keyword, industry in industry_keywords.items():
                            if keyword in app_lower:
                                primary_industry = industry
                                break
                        if primary_industry:
                            break
        
        if primary_industry:
            tags.append(primary_industry)
        else:
            tags.append('industrial')
        
        # Add surface treatment indicator
        tags.append('surface-treatment')
        
        # Priority 4: Fill remaining slots with process-specific tags
        additional_tags = []
        
        # Process-specific tags based on material type
        if category == 'metals':
            additional_tags = ['decoating', 'oxide-removal', 'passivation']
        elif category == 'ceramics':
            additional_tags = ['precision-cleaning', 'surface-prep', 'restoration']
        elif category == 'composites':
            additional_tags = ['preparation', 'texturing', 'maintenance']
        elif category == 'polymers':
            additional_tags = ['preparation', 'modification', 'cleaning']
        else:
            additional_tags = ['maintenance', 'preparation', 'decontamination']
        
        # Add additional tags up to 10 total
        for tag in additional_tags:
            if len(tags) >= 10:
                break
            if tag not in tags:
                tags.append(tag)
        
        # Ensure we have exactly 10 tags (pad if necessary)
        while len(tags) < 10:
            fallback_tags = ['processing', 'industrial', 'precision', 'automated', 'quality']
            for fallback in fallback_tags:
                if fallback not in tags:
                    tags.append(fallback)
                    break
            else:
                # If all fallbacks are used, break to avoid infinite loop
                break
        
        # Validation: Must have core essentials
        required_elements = [material_slug, category, author_slug, 'laser-cleaning']
        missing_required = [req for req in required_elements if req not in tags]
        if missing_required:
            raise ValueError(f"Missing required tags in frontmatter: {missing_required}")
        
        return tags[:10]  # Ensure exactly 10 tags maximum
        return tags[:10]  # Ensure exactly 10 tags maximum

    def _sanitize_frontmatter_data(self, frontmatter_data: Dict) -> Dict:
        """Sanitize frontmatter data to prevent YAML parsing issues"""
        if not frontmatter_data:
            return frontmatter_data
        
        sanitized = {}
        for key, value in frontmatter_data.items():
            if isinstance(value, str):
                # Quote values that might cause YAML issues
                if any(char in value for char in ['(', ')', ':', '"', '\n']) and not (value.startswith('"') and value.endswith('"')):
                    value = f'"{value.replace('"', '""')}"'  # Escape quotes and wrap
                sanitized[key] = value
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_frontmatter_data(value)
            else:
                sanitized[key] = value
        
        return sanitized

    def _fix_yaml_syntax(self, yaml_content: str) -> str:
        """Fix common YAML syntax issues in generated content"""
        lines = yaml_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            # Quote values with special characters
            if ':' in line and not line.strip().startswith('#'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key_part = parts[0]
                    value_part = parts[1].strip()
                    
                    # Quote values that need it
                    if value_part and not (value_part.startswith('"') and value_part.endswith('"')):
                        if any(char in value_part for char in ['(', ')', '-', 'µ', '°']):
                            value_part = f'"{value_part}"'
                    
                    line = f"{key_part}: {value_part}"
            
            fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)

    def _create_template_vars(
        self,
        material_name: str,
        material_data: Dict,
        author_info: Optional[Dict] = None,
        frontmatter_data: Optional[Dict] = None,
        schema_fields: Optional[Dict] = None,
    ) -> Dict:
        """Create template variables for tags generation"""
        # FAIL-FAST: Category must be present and researched
        if not material_data.get("category"):
            raise ValueError(f"Category missing for {material_name} - fail-fast requires explicit categorization")
        category = material_data["category"]
        
        # FAIL-FAST: Chemical identifiers must be researched
        formula = material_data.get("formula")
        symbol = material_data.get("symbol")
        
        # If not provided in material_data, try frontmatter
        if not formula and frontmatter_data:
            chem_props = frontmatter_data.get("chemicalProperties", {})
            formula = chem_props.get("formula")
        if not symbol and frontmatter_data:
            chem_props = frontmatter_data.get("chemicalProperties", {})
            symbol = chem_props.get("symbol")
            
        # If still not found, try to get from Materials.yaml via resolver
        if not formula or not symbol:
            resolver = get_material_name_resolver()
            # Get the materials data structure which contains full material info
            all_materials_data = resolver.materials_data
            materials_section = all_materials_data.get('materials', {})
            
            # Find the specific material in the category-organized structure
            canonical_name = resolver.resolve_canonical_name(material_name)
            if canonical_name:
                # Search through all categories for this material
                for category_data in materials_section.values():
                    if isinstance(category_data, dict) and 'items' in category_data:
                        for item in category_data['items']:
                            if item.get('name') == canonical_name:
                                # Found the material, extract formula and symbol
                                if not formula:
                                    formula = item.get('formula')
                                if not symbol:
                                    symbol = item.get('symbol')
                                break
                        if formula and symbol:
                            break
        
        # Formula and symbol are optional for tags generation - not fail-fast requirements
        # Tags can be generated based on material name, category, and other available data
        
        # FAIL-FAST: Author info must be present
        if not author_info or not author_info.get("name"):
            if not frontmatter_data or not frontmatter_data.get("author"):
                raise ValueError(f"Author information missing for {material_name} - fail-fast requires explicit author data")
            author_name = frontmatter_data["author"]
            author_obj = frontmatter_data.get("author", {})
            if not isinstance(author_obj, dict) or not author_obj.get("country"):
                raise ValueError(f"Author country missing for {material_name} - fail-fast requires complete author data")
            author_country = author_obj["country"]
        else:
            author_name = author_info["name"]
            if not author_info.get("country"):
                raise ValueError(f"Author country missing for {material_name} - fail-fast requires complete author data")
            author_country = author_info["country"]

        return {
            "material_name": material_name,
            "material_category": category,
            "material_subcategory": material_data.get("subcategory", "general"),
            "material_formula": formula,
            "material_symbol": symbol,
            "author_name": author_name,
            "author_country": author_country,
        }

    def _build_api_prompt(self, template_vars: Dict, frontmatter_data: Optional[Dict] = None) -> str:
        """Build API prompt for tags generation"""
        material_name = template_vars["material_name"]
        material_formula = template_vars["material_formula"]
        
        prompt = f"""Generate navigation tags for {material_name} surface treatment.

Output EXACTLY 12 tags as a comma-separated list like this example:
aerospace, automotive, manufacturing, electronics, anodizing, passivation, decoating, restoration, polishing, texturing, metal, industrial

REQUIREMENTS:
- Output exactly 12 tags (we will filter to final 8)
- Use single words or hyphenated terms only"""
        
        # Add formula if available
        if material_formula:
            prompt += f"\n- Include chemical formula or symbol ({material_formula.lower()})"
        
        # Build exclusion list
        exclusions = [
            "laser", "cleaning", "non-contact", "ablation", "beam", "photon", "wavelength", 
            "nm", "micron", "µm", "mm", "energy", "joule", "watt", "power", "frequency", 
            "hz", "khz", "mhz", "pulse", "cw", "continuous", "wave", "radiation", "light", 
            "optics", "optical", "surface-treatment", "expert", material_name.lower()
        ]
        
        # Add chemical formula to exclusions if present
        if material_formula:
            exclusions.append(material_formula.lower())
        
        exclusion_text = ", ".join(exclusions)
        
        prompt += f"""
- Include 2-3 industry applications (aerospace, automotive, manufacturing, electronics, marine, medical, etc.)
- Include relevant process terms (decoating, decontamination, restoration, etching, passivation, polishing, texturing, etc.)
- Include material category terms (metal, polymer, ceramic, composite, etc.) if relevant
- Include 1 author slug: {template_vars['author_name'].lower().replace(' ', '-')}
- Make tags specific and valuable for {material_name} applications
- Use lowercase throughout
- DO NOT INCLUDE any of these terms: {exclusion_text}
- DO NOT use the material name '{material_name.lower()}' as a tag
- Focus on applications, processes, and industries, NOT the material itself
- Output ONLY the comma-separated list, no other text"""

        return prompt
