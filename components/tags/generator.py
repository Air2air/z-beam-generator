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
        """Generate tags and integrate them directly into frontmatter YAML file"""
        import yaml
        from pathlib import Path
        
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

            # INTEGRATION: Write tags directly into frontmatter YAML file
            material_slug = material_name.lower().replace(' ', '-').replace('_', '-')
            frontmatter_file = Path(f"content/components/frontmatter/{material_slug}-laser-cleaning.yaml")
            
            if not frontmatter_file.exists():
                error_msg = f"Frontmatter file not found: {frontmatter_file}"
                logger.error(error_msg)
                return ComponentResult(
                    component_type="tags",
                    content="",
                    success=False,
                    error_message=error_msg,
                )
            
            # Load existing frontmatter YAML
            with open(frontmatter_file, 'r', encoding='utf-8') as f:
                frontmatter_content = yaml.safe_load(f)
            
            if not frontmatter_content:
                error_msg = f"Could not parse frontmatter YAML: {frontmatter_file}"
                logger.error(error_msg)
                return ComponentResult(
                    component_type="tags",
                    content="",
                    success=False,
                    error_message=error_msg,
                )
            
            # Add tags array to frontmatter
            frontmatter_content['tags'] = final_tags
            
            # Save updated frontmatter with preserved formatting
            with open(frontmatter_file, 'w', encoding='utf-8') as f:
                yaml.dump(frontmatter_content, f, 
                         default_flow_style=False, 
                         sort_keys=False, 
                         allow_unicode=True,
                         width=120)
            
            logger.info(f"Successfully integrated {len(final_tags)} tags into frontmatter: {frontmatter_file}")

            # Return success with tag list for logging
            tag_summary = ", ".join(final_tags)
            return ComponentResult(
                component_type="tags", 
                content=f"Tags integrated into frontmatter: {tag_summary}", 
                success=True
            )

        except Exception as e:
            logger.error(f"Error generating/integrating tags for {material_name}: {e}")
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
        """Generate exactly 11 tags: 1 material + 1 category + 3 industries + 3 processes + 2 characteristics + 1 author"""
        tags = []
        
        try:
            # 1. CORE: Material name (normalized)
            material_slug = material_name.lower().replace(' ', '-').replace('_', '-')
            tags.append(material_slug)
            
            # 2. CORE: Category
            category_raw = template_vars['material_category']
            category = category_raw.lower() if isinstance(category_raw, str) else str(category_raw).lower()
            tags.append(category)
            
            # 3-5. INDUSTRIES: Extract 3 industry tags from applicationTypes
            industry_tags = self._extract_industry_tags(frontmatter_data, category)
            tags.extend(industry_tags[:3])  # Exactly 3 industries
            
            # 6-8. PROCESSES: Extract 3 process tags from applicationTypes
            process_tags = self._extract_process_tags(frontmatter_data, category)
            tags.extend(process_tags[:3])  # Exactly 3 processes
            
            # 9-10. CHARACTERISTICS: Extract 2 material characteristic tags
            characteristic_tags = self._extract_characteristic_tags(frontmatter_data, material_data, category)
            tags.extend(characteristic_tags[:2])  # Exactly 2 characteristics
            
            # 11. AUTHOR: Author name slug
            author_raw = template_vars.get('author_name', '')
            author_slug = author_raw.lower().replace(' ', '-').replace('.', '').replace(',', '') if isinstance(author_raw, str) else str(author_raw).lower().replace(' ', '-')
            tags.append(author_slug)
        except Exception as e:
            logger.error(f"Error generating tags for {material_name}: {e}")
            logger.error(f"template_vars keys: {list(template_vars.keys())}")
            logger.error(f"template_vars: {template_vars}")
            raise
        
        # Validation: Ensure exactly 11 tags (material + category + 3 industries + 3 processes + 2 characteristics + author)
        if len(tags) != 11:
            logger.warning(f"Tag count mismatch for {material_name}: expected 11, got {len(tags)}")
            # Pad or trim to exactly 11
            while len(tags) < 11:
                tags.append('laser-processing')  # Fallback tag
            tags = tags[:11]
        
        return tags
        
        return tags

    def _extract_industry_tags(self, frontmatter_data: Optional[Dict], category: str) -> list:
        """Extract 3 industry tags from applicationTypes"""
        industries = []
        
        if frontmatter_data and 'applicationTypes' in frontmatter_data:
            app_types = frontmatter_data['applicationTypes']
            if isinstance(app_types, list):
                for app_type in app_types:
                    if isinstance(app_type, dict) and 'industries' in app_type:
                        app_industries = app_type['industries']
                        if isinstance(app_industries, list):
                            for industry in app_industries:
                                if isinstance(industry, str):
                                    # Convert to slug: "Cultural Heritage" → "cultural-heritage"
                                    industry_slug = industry.lower().replace(' ', '-').replace('_', '-').replace('&', 'and')
                                    if industry_slug not in industries:
                                        industries.append(industry_slug)
                                    if len(industries) >= 3:
                                        return industries
        
        # Fallback: infer from category if not enough industries found
        fallback_industries = {
            'metal': ['manufacturing', 'aerospace', 'automotive'],
            'metals': ['manufacturing', 'aerospace', 'automotive'],
            'ceramic': ['electronics', 'medical', 'aerospace'],
            'ceramics': ['electronics', 'medical', 'aerospace'],
            'stone': ['cultural-heritage', 'architecture', 'restoration'],
            'composite': ['aerospace', 'automotive', 'marine'],
            'composites': ['aerospace', 'automotive', 'marine'],
            'polymer': ['automotive', 'medical', 'consumer-goods'],
            'polymers': ['automotive', 'medical', 'consumer-goods'],
            'semiconductor': ['electronics', 'computing', 'telecommunications'],
            'glass': ['optics', 'architecture', 'automotive']
        }
        
        category_fallbacks = fallback_industries.get(category, ['manufacturing', 'industrial', 'processing'])
        for fallback in category_fallbacks:
            if fallback not in industries:
                industries.append(fallback)
            if len(industries) >= 3:
                break
        
        # Final padding if still not enough
        generic_industries = ['manufacturing', 'industrial', 'processing', 'maintenance', 'quality-control']
        for generic in generic_industries:
            if len(industries) >= 3:
                break
            if generic not in industries:
                industries.append(generic)
        
        return industries[:3]

    def _extract_process_tags(self, frontmatter_data: Optional[Dict], category: str) -> list:
        """Extract 3 process tags from applicationTypes"""
        processes = []
        
        if frontmatter_data and 'applicationTypes' in frontmatter_data:
            app_types = frontmatter_data['applicationTypes']
            if isinstance(app_types, list):
                for app_type in app_types:
                    if isinstance(app_type, dict) and 'type' in app_type:
                        process_type = app_type['type']
                        if isinstance(process_type, str):
                            # Convert to slug: "Precision Cleaning" → "precision-cleaning"
                            process_slug = process_type.lower().replace(' ', '-').replace('_', '-')
                            if process_slug not in processes:
                                processes.append(process_slug)
                            if len(processes) >= 3:
                                return processes
        
        # Fallback: category-specific processes
        fallback_processes = {
            'metal': ['decoating', 'oxide-removal', 'surface-preparation'],
            'metals': ['decoating', 'oxide-removal', 'surface-preparation'],
            'ceramic': ['precision-cleaning', 'surface-preparation', 'restoration'],
            'ceramics': ['precision-cleaning', 'surface-preparation', 'restoration'],
            'stone': ['restoration-cleaning', 'contamination-removal', 'conservation'],
            'composite': ['surface-preparation', 'adhesion-enhancement', 'coating-removal'],
            'composites': ['surface-preparation', 'adhesion-enhancement', 'coating-removal'],
            'polymer': ['surface-activation', 'contamination-removal', 'preparation'],
            'polymers': ['surface-activation', 'contamination-removal', 'preparation'],
            'semiconductor': ['precision-cleaning', 'particle-removal', 'surface-preparation'],
            'glass': ['precision-cleaning', 'restoration', 'surface-preparation']
        }
        
        category_fallbacks = fallback_processes.get(category, ['surface-preparation', 'contamination-removal', 'maintenance'])
        for fallback in category_fallbacks:
            if fallback not in processes:
                processes.append(fallback)
            if len(processes) >= 3:
                break
        
        # Final padding
        generic_processes = ['laser-ablation', 'surface-treatment', 'cleaning', 'processing', 'decontamination']
        for generic in generic_processes:
            if len(processes) >= 3:
                break
            if generic not in processes:
                processes.append(generic)
        
        return processes[:3]

    def _extract_characteristic_tags(self, frontmatter_data: Optional[Dict], material_data: Dict, category: str) -> list:
        """Extract 2 material characteristic tags from materialProperties"""
        characteristics = []
        
        if frontmatter_data and 'materialProperties' in frontmatter_data:
            props = frontmatter_data['materialProperties']
            
            # Check for porosity
            if 'porosity' in props:
                porosity_val = props['porosity'].get('value', 0) if isinstance(props['porosity'], dict) else props['porosity']
                try:
                    if float(porosity_val) > 5:  # More than 5% porosity
                        characteristics.append('porous-material')
                except (ValueError, TypeError):
                    pass
            
            # Check for thermal sensitivity
            if 'thermalConductivity' in props:
                thermal_val = props['thermalConductivity'].get('value', 0) if isinstance(props['thermalConductivity'], dict) else props['thermalConductivity']
                try:
                    if float(thermal_val) < 10:  # Low thermal conductivity
                        characteristics.append('thermal-sensitive')
                except (ValueError, TypeError):
                    pass
            
            # Check for hardness
            if 'hardness' in props and len(characteristics) < 2:
                hardness_val = props['hardness'].get('value', 0) if isinstance(props['hardness'], dict) else props['hardness']
                try:
                    if float(hardness_val) < 3:  # Mohs < 3
                        characteristics.append('soft-material')
                    elif float(hardness_val) > 7:  # Mohs > 7
                        characteristics.append('hard-material')
                except (ValueError, TypeError):
                    pass
            
            # Check for reflectivity
            if 'reflectivity' in props and len(characteristics) < 2:
                reflectivity_val = props['reflectivity'].get('value', 0) if isinstance(props['reflectivity'], dict) else props['reflectivity']
                try:
                    if float(reflectivity_val) > 0.5:  # High reflectivity
                        characteristics.append('reflective-surface')
                except (ValueError, TypeError):
                    pass
            
            # Check for absorption
            if 'absorptionCoefficient' in props and len(characteristics) < 2:
                characteristics.append('laser-absorptive')
        
        # Fallback: category-specific characteristics
        if len(characteristics) < 2:
            fallback_chars = {
                'metal': ['conductive', 'reflective-surface'],
                'metals': ['conductive', 'reflective-surface'],
                'ceramic': ['thermal-resistant', 'hard-material'],
                'ceramics': ['thermal-resistant', 'hard-material'],
                'stone': ['porous-material', 'weathered-surface'],
                'composite': ['multi-layered', 'anisotropic'],
                'composites': ['multi-layered', 'anisotropic'],
                'polymer': ['thermal-sensitive', 'low-density'],
                'polymers': ['thermal-sensitive', 'low-density'],
                'semiconductor': ['high-purity', 'crystalline'],
                'glass': ['transparent', 'brittle']
            }
            
            category_fallbacks = fallback_chars.get(category, ['industrial-grade', 'processed'])
            for fallback in category_fallbacks:
                if len(characteristics) >= 2:
                    break
                if fallback not in characteristics:
                    characteristics.append(fallback)
        
        # Final padding
        generic_chars = ['engineered', 'processed', 'industrial-grade', 'technical']
        for generic in generic_chars:
            if len(characteristics) >= 2:
                break
            if generic not in characteristics:
                characteristics.append(generic)
        
        return characteristics[:2]

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
            author_obj = frontmatter_data.get("author", {})
            
            # Handle both string and dict author formats
            if isinstance(author_obj, dict):
                author_name = author_obj.get("name", "")
                author_country = author_obj.get("country", "")
                if not author_name or not author_country:
                    raise ValueError(f"Author name or country missing for {material_name} - fail-fast requires complete author data")
            elif isinstance(author_obj, str):
                # Legacy format: author is just a string
                author_name = author_obj
                author_country = "Unknown"
            else:
                raise ValueError(f"Invalid author format for {material_name} - must be dict with name/country or string")
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
