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
        """Format tags as structured YAML for Next.js consumption"""
        from datetime import datetime
        
        # Categorize tags
        industry_tags = []
        process_tags = []
        author_tags = []
        other_tags = []
        
        # Known categories for classification
        industries = {'aerospace', 'automotive', 'manufacturing', 'electronics', 'marine', 'medical', 'industrial'}
        processes = {'decoating', 'decontamination', 'restoration', 'polishing', 'texturing', 'etching', 'passivation', 'anodizing'}
        
        for tag in tags_list:
            tag_clean = tag.strip().lower()
            # Since we exclude material names now, this section won't match
            if tag_clean in industries:
                industry_tags.append(tag_clean)
            elif tag_clean in processes:
                process_tags.append(tag_clean)
            elif '-' in tag_clean and len(tag_clean.split('-')) == 2:  # Likely author name
                author_tags.append(tag_clean)
            else:
                other_tags.append(tag_clean)
        
        # Format as proper YAML
        yaml_content = "tags:\n"
        for tag in tags_list:
            yaml_content += f"  - {tag.strip()}\n"
        
        yaml_content += f"material: \"{material_name.lower()}\"\n"
        yaml_content += f"count: {len(tags_list)}\n"
        yaml_content += "categories:\n"
        
        yaml_content += "  industry:\n"
        for tag in industry_tags:
            yaml_content += f"    - {tag}\n"
        
        yaml_content += "  process:\n"
        for tag in process_tags:
            yaml_content += f"    - {tag}\n"
        
        yaml_content += "  author:\n"
        for tag in author_tags:
            yaml_content += f"    - {tag}\n"
        
        yaml_content += "  other:\n"
        for tag in other_tags:
            yaml_content += f"    - {tag}\n"
        
        yaml_content += "metadata:\n"
        yaml_content += f"  generated: \"{datetime.now().isoformat()}\"\n"
        yaml_content += "  format: \"yaml\"\n"
        yaml_content += "  version: \"2.0\""
        
        return yaml_content

    def _generate_tags_from_frontmatter(self, material_name: str, material_data: Dict, frontmatter_data: Optional[Dict], template_vars: Dict) -> list:
        """Generate tags purely from frontmatter data without AI"""
        tags = []
        
        # 1. Always include author slug
        author_slug = template_vars['author_name'].lower().replace(' ', '-')
        tags.append(author_slug)
        
        # 2. Add material category AND subcategory tags
        category = template_vars['material_category'].lower()
        subcategory = template_vars.get('material_subcategory', '').lower()
        
        # Add category-specific tags
        if category in ['metal', 'alloy']:
            tags.extend(['metalworking', 'industrial'])
        elif category in ['ceramic', 'glass']:
            tags.extend(['ceramics', 'precision'])
        elif category in ['polymer', 'plastic', 'composite']:
            tags.extend(['polymer', 'manufacturing'])
        elif category in ['wood', 'organic']:
            tags.extend(['woodworking', 'restoration'])
        elif category in ['stone', 'mineral']:
            tags.extend(['masonry', 'heritage'])
        else:
            tags.append('industrial')
        
        # Add subcategory-specific tags
        if subcategory:
            subcategory_tags = {
                # Metal subcategories
                'precious': ['precious-metals', 'high-value'],
                'ferrous': ['steel-processing', 'heavy-industry'],
                'non-ferrous': ['light-metals', 'corrosion-resistant'],
                'refractory': ['high-temperature', 'aerospace'],
                'reactive': ['specialized-handling', 'aerospace'],
                'specialty': ['advanced-alloys', 'high-performance'],
                
                # Ceramic subcategories  
                'oxide': ['advanced-ceramics', 'high-temperature'],
                'nitride': ['technical-ceramics', 'wear-resistant'],
                'carbide': ['cutting-tools', 'wear-resistant'],
                'traditional': ['architectural', 'decorative'],
                
                # Composite subcategories
                'fiber-reinforced': ['advanced-composites', 'lightweight'],
                'matrix': ['engineered-materials', 'high-performance'],
                'resin': ['thermoset', 'structural'],
                'elastomeric': ['flexible', 'sealing'],
                'structural': ['load-bearing', 'construction'],
                
                # Glass subcategories
                'borosilicate': ['laboratory', 'thermal-shock'],
                'silicate': ['architectural', 'commercial'],
                'crystal': ['decorative', 'optical'],
                'treated': ['safety', 'tempered'],
                
                # Stone subcategories
                'igneous': ['natural-stone', 'construction'],
                'metamorphic': ['decorative', 'architectural'],
                'sedimentary': ['building-materials', 'construction'],
                'soft': ['carving', 'decorative'],
                'mineral': ['crystalline', 'specialty'],
                
                # Wood subcategories
                'hardwood': ['furniture', 'flooring'],
                'softwood': ['construction', 'framing'],
                'engineered': ['manufactured', 'composite'],
                'flexible': ['specialty', 'crafts']
            }
            
            if subcategory in subcategory_tags:
                # Add up to 2 subcategory tags
                for tag in subcategory_tags[subcategory][:2]:
                    if tag not in tags and len(tags) < 6:
                        tags.append(tag)
        
        # 3. Extract industry applications from frontmatter
        if frontmatter_data:
            # Look for applications in various frontmatter fields
            applications = frontmatter_data.get('applications', [])
            if isinstance(applications, list):
                for app in applications[:2]:  # Limit to 2 applications
                    if isinstance(app, str):
                        # Extract just the industry name, not the full description
                        app_clean = app.split(':')[0].lower().replace(' ', '-')
                        if app_clean not in tags and len(app_clean) < 20:  # Avoid long descriptions
                            tags.append(app_clean)
            
            # Look for industries in keywords
            keywords = frontmatter_data.get('keywords', '')
            if isinstance(keywords, str):
                keyword_list = [k.strip().lower() for k in keywords.split(',')]
                industry_keywords = ['aerospace', 'automotive', 'medical', 'electronics', 'marine', 'semiconductor']
                for keyword in keyword_list:
                    if keyword in industry_keywords and keyword not in tags:
                        tags.append(keyword)
                        if len(tags) >= 6:  # Leave room for process tags
                            break
        
        # 4. Add common process tags based on material type
        process_tags = ['decontamination', 'surface-preparation']
        if category in ['metal', 'alloy']:
            process_tags.extend(['passivation', 'decoating'])
        elif category in ['ceramic', 'glass']:
            process_tags.extend(['polishing', 'etching'])
        elif category in ['polymer', 'composite']:
            process_tags.extend(['texturing', 'preparation'])
        elif category in ['wood']:
            process_tags.extend(['restoration', 'refinishing'])
        elif category in ['stone']:
            process_tags.extend(['restoration', 'conservation'])
        
        # Add process tags until we have 8 total
        for process_tag in process_tags:
            if len(tags) >= 8:
                break
            if process_tag not in tags:
                tags.append(process_tag)
        
        # 5. Fail-fast: Must have at least some tags from content - no fallback defaults
        if len(tags) < 2:
            raise ValueError(f"Insufficient tag content extracted from material data - need minimum 2 tags, got {len(tags)}")
        
        # Return available tags up to 8 - no default padding
        
        return tags[:8]  # Always return exactly 8 tags

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
