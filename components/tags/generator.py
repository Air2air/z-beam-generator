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
    
    # TAG BLACKLIST: Terms to exclude from all tags
    TAG_BLACKLIST = {
        # Laser-related terms (too generic for laser cleaning content)
        'laser', 'cleaning', 'laser-cleaning', 'non-contact', 'ablation', 
        'beam', 'photon', 'wavelength', 'radiation', 'light', 'optics', 
        'optical', 'photonic',
        
        # Technical measurement units
        'nm', 'micron', 'μm', 'mm', 'cm', 'm', 'energy', 'joule', 'watt', 
        'power', 'frequency', 'hz', 'khz', 'mhz', 'pulse', 'cw', 
        'continuous', 'wave',
        
        # Generic surface treatment terms (keep specific processes like surface-preparation)
        'surface-treatment', 'treatment', 'processing', 'process',
        
        # Overly generic terms
        'expert', 'professional', 'industrial', 'commercial', 'technical',
        'advanced', 'modern', 'standard', 'basic', 'general',
        
        # Single letters and numbers
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        
        # Empty or whitespace
        '', ' ', '-', '_',
    }

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
    
    def _filter_blacklisted_tags(self, tags: list, material_name: str = "") -> list:
        """Filter out blacklisted tags and material name from tag list"""
        filtered = []
        blacklist_lower = {tag.lower() for tag in self.TAG_BLACKLIST}
        
        # Add material name to blacklist (avoid self-referential tags)
        if material_name:
            material_slug = material_name.lower().replace(' ', '-').replace('_', '-')
            blacklist_lower.add(material_slug)
        
        for tag in tags:
            tag_lower = tag.lower().strip()
            
            # Skip if empty or in blacklist
            if not tag_lower or tag_lower in blacklist_lower:
                logger.debug(f"Filtering blacklisted tag: '{tag}'")
                continue
            
            # Skip if it's a substring of the material name
            if material_name and material_name.lower().replace(' ', '').replace('-', '') in tag_lower.replace('-', ''):
                logger.debug(f"Filtering material-related tag: '{tag}'")
                continue
            
            filtered.append(tag)
        
        return filtered

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
        """Generate exactly 10 tags: 1 category + 5 industries + 3 characteristics + 1 author (NO PROCESS TAGS)"""
        tags = []
        
        # FAIL-FAST: Validate required frontmatter data exists (per GROK_INSTRUCTIONS.md - NO FALLBACKS)
        if not frontmatter_data:
            raise ValueError(f"frontmatter_data is None for {material_name} - fail-fast requires explicit frontmatter")
        
        required_fields = ['applications', 'materialProperties', 'category', 'author']
        missing_fields = [field for field in required_fields if field not in frontmatter_data]
        if missing_fields:
            raise ValueError(f"Missing required frontmatter fields for {material_name}: {', '.join(missing_fields)}")
        
        # Validate applications is not empty
        if not frontmatter_data.get('applications') or not isinstance(frontmatter_data['applications'], list):
            raise ValueError(f"applications field must be a non-empty array for {material_name}")
        
        # Validate materialProperties is not empty
        if not frontmatter_data.get('materialProperties') or not isinstance(frontmatter_data['materialProperties'], dict):
            raise ValueError(f"materialProperties field must be a non-empty dict for {material_name}")
        
        try:
            # 1. CORE: Category
            category_raw = template_vars['material_category']
            category = category_raw.lower() if isinstance(category_raw, str) else str(category_raw).lower()
            tags.append(category)
            
            # 2-N. INDUSTRIES: Extract all available industry tags from applications
            industry_tags = self._extract_industry_tags(frontmatter_data, category)
            # Apply blacklist filtering before selecting
            industry_tags = self._filter_blacklisted_tags(industry_tags, material_name)
            tags.extend(industry_tags)  # Add all industries (typically 3-5)
            
            # N+1 to 9. CHARACTERISTICS: Fill remaining slots with characteristics
            characteristic_tags = self._extract_characteristic_tags(frontmatter_data, material_data, category)
            # Apply blacklist filtering before selecting
            characteristic_tags = self._filter_blacklisted_tags(characteristic_tags, material_name)
            
            # Calculate how many characteristic tags we need to reach 10 total (1 category + industries + characteristics + 1 author = 10)
            needed_characteristics = 10 - len(tags) - 1  # -1 for author
            tags.extend(characteristic_tags[:needed_characteristics])
            
            # 10. AUTHOR: Author name slug
            author_raw = template_vars.get('author_name', '')
            author_slug = author_raw.lower().replace(' ', '-').replace('.', '').replace(',', '') if isinstance(author_raw, str) else str(author_raw).lower().replace(' ', '-')
            tags.append(author_slug)
        except Exception as e:
            logger.error(f"Error generating tags for {material_name}: {e}")
            logger.error(f"template_vars keys: {list(template_vars.keys())}")
            logger.error(f"template_vars: {template_vars}")
            raise
        
        # Final validation: no need for additional filtering since we filtered during extraction
        
        # FAIL-FAST: Must have 4-10 tags (NO FALLBACKS per GROK_INSTRUCTIONS.md)
        # Lowered from 5 to 4 to accommodate materials with minimal properties/applications
        if len(tags) < 4 or len(tags) > 10:
            raise ValueError(f"Tag count mismatch for {material_name}: expected 4-10, got {len(tags)}. Insufficient data in frontmatter - needs more applications or materialProperties.")
        
        return tags

    def _extract_industry_tags(self, frontmatter_data: Optional[Dict], category: str) -> list:
        """Extract 3 industry tags from applications field by parsing 'Industry: Description' format"""
        industries = []
        
        # FAIL-FAST: applications field must exist in frontmatter
        if not frontmatter_data or 'applications' not in frontmatter_data:
            raise ValueError("applications field missing from frontmatter - fail-fast requires explicit application data")
        
        applications = frontmatter_data.get('applications', [])
        if not applications:
            raise ValueError("applications array is empty - fail-fast requires at least one application")
        
        # Parse applications to extract industry names (format: "Industry: Description")
        for app in applications:
            if isinstance(app, str) and ':' in app:
                # Extract industry name (text before the colon)
                industry_raw = app.split(':', 1)[0].strip()
                # Convert to slug format (lowercase, hyphenated)
                industry_slug = industry_raw.lower().replace(' ', '-').replace('_', '-')
                if industry_slug and industry_slug not in industries:
                    industries.append(industry_slug)
        
        # If we don't have at least 1 industry, fail-fast
        # Lowered from 2 to 1 to accommodate wood/stone materials with limited applications
        if len(industries) < 1:
            raise ValueError(f"Insufficient industry data in applications - found {len(industries)}, need at least 1")
        
        return industries  # Return all industries, will fill remaining slots with characteristics

    def _extract_process_tags(self, frontmatter_data: Optional[Dict], category: str) -> list:
        """Extract 3 process tags from application descriptions using keyword detection"""
        processes = []
        
        # FAIL-FAST: applications field must exist
        if not frontmatter_data or 'applications' not in frontmatter_data:
            raise ValueError("applications field missing from frontmatter - cannot extract process tags")
        
        applications = frontmatter_data.get('applications', [])
        
        # Process keyword mappings (lowercase for matching)
        process_keywords = {
            'decontamination': 'decontamination',
            'surface cleaning': 'surface-cleaning',
            'surface preparation': 'surface-preparation',
            'contamination removal': 'contamination-removal',
            'sterilization': 'sterilization',
            'cleaning': 'cleaning',
            'restoration': 'restoration',
            'oxide removal': 'oxide-removal',
            'decoating': 'decoating',
            'coating removal': 'coating-removal',
            'paint removal': 'paint-removal',
            'rust removal': 'rust-removal',
            'precision cleaning': 'precision-cleaning',
            'particle removal': 'particle-removal',
            'surface activation': 'surface-activation',
            'texturing': 'texturing',
            'etching': 'etching',
            'polishing': 'polishing',
            'ablation': 'ablation',
            'conservation': 'conservation',
            'maintenance': 'maintenance'
        }
        
        # Parse application descriptions to find process keywords
        for app in applications:
            if isinstance(app, str) and ':' in app:
                # Extract description (text after the colon)
                description = app.split(':', 1)[1].strip().lower()
                
                # Check for process keywords in description
                for keyword, process_tag in process_keywords.items():
                    if keyword in description and process_tag not in processes:
                        processes.append(process_tag)
                        if len(processes) >= 3:
                            break
            
            # Extract more than 3 to have buffer for blacklist filtering
            if len(processes) >= 6:
                break
        
        # If we don't have at least 3 processes, fail-fast
        if len(processes) < 3:
            raise ValueError(f"Insufficient process keywords in applications - found {len(processes)}, need 3")
        
        return processes

    def _extract_characteristic_tags(self, frontmatter_data: Optional[Dict], material_data: Dict, category: str) -> list:
        """Extract 2 material characteristic tags from materialProperties with enhanced property analysis"""
        characteristics = []
        
        # FAIL-FAST: materialProperties must exist
        if not frontmatter_data or 'materialProperties' not in frontmatter_data:
            raise ValueError("materialProperties field missing from frontmatter - fail-fast requires property data")
        
        props = frontmatter_data['materialProperties']
        
        # Priority 1: Reflectivity (critical for laser cleaning)
        if 'reflectivity' in props:
            reflectivity_val = props['reflectivity'].get('value', 0) if isinstance(props['reflectivity'], dict) else props['reflectivity']
            try:
                if float(reflectivity_val) > 70:  # Reflective (>70%)
                    characteristics.append('reflective')
                elif float(reflectivity_val) < 30:  # Absorptive
                    characteristics.append('absorptive')
            except (ValueError, TypeError):
                pass
        
        # Priority 2: Thermal conductivity (affects heat dissipation)
        if 'thermalConductivity' in props:
            thermal_val = props['thermalConductivity'].get('value', 0) if isinstance(props['thermalConductivity'], dict) else props['thermalConductivity']
            try:
                if float(thermal_val) > 100:  # Thermally conductive (>100 W/m·K)
                    characteristics.append('conductive')
                elif float(thermal_val) < 10:  # Thermally insulating
                    characteristics.append('insulating')
            except (ValueError, TypeError):
                pass
        
        # Priority 3: Hardness (material durability)
        if 'hardness' in props:
            hardness_val = props['hardness'].get('value', 0) if isinstance(props['hardness'], dict) else props['hardness']
            unit = props['hardness'].get('unit', '').upper() if isinstance(props['hardness'], dict) else ''
            try:
                # Adjust thresholds based on hardness scale (HV=Vickers, HB=Brinell, Mohs)
                if 'HV' in unit or 'HB' in unit:
                    if float(hardness_val) > 300:  # Very hard (Vickers/Brinell)
                        characteristics.append('durable')
                    elif float(hardness_val) < 50:  # Soft
                        characteristics.append('soft')
                else:  # Assume Mohs scale
                    if float(hardness_val) > 7:  # Hard (Mohs > 7)
                        characteristics.append('durable')
                    elif float(hardness_val) < 3:  # Soft (Mohs < 3)
                        characteristics.append('soft')
            except (ValueError, TypeError):
                pass
        
        # Priority 4: Porosity
        if 'porosity' in props:
            porosity_val = props['porosity'].get('value', 0) if isinstance(props['porosity'], dict) else props['porosity']
            try:
                if float(porosity_val) > 5:  # Porous (>5%)
                    characteristics.append('porous')
            except (ValueError, TypeError):
                pass
        
        # Priority 5: Density (material weight characteristics)
        if 'density' in props:
            density_val = props['density'].get('value', 0) if isinstance(props['density'], dict) else props['density']
            try:
                if float(density_val) > 7:  # Heavy (>7 g/cm³)
                    characteristics.append('dense')
                elif float(density_val) < 2:  # Lightweight (<2 g/cm³)
                    characteristics.append('lightweight')
            except (ValueError, TypeError):
                pass
        
        # Priority 6: Thermal expansion
        if 'thermalExpansion' in props:
            expansion_val = props['thermalExpansion'].get('value', 0) if isinstance(props['thermalExpansion'], dict) else props['thermalExpansion']
            try:
                if float(expansion_val) > 15:  # High thermal expansion
                    characteristics.append('expansive')
                elif float(expansion_val) < 5:  # Low thermal expansion (dimensionally stable)
                    characteristics.append('stable')
            except (ValueError, TypeError):
                pass
        
        # Priority 7: Melting point
        if 'meltingPoint' in props:
            melting_val = props['meltingPoint'].get('value', 0) if isinstance(props['meltingPoint'], dict) else props['meltingPoint']
            try:
                if float(melting_val) > 1500:  # Refractory (>1500°C)
                    characteristics.append('refractory')
                elif float(melting_val) < 500:  # Low melting point
                    characteristics.append('fusible')
            except (ValueError, TypeError):
                pass
        
        # Priority 8: Compressive strength
        if 'compressiveStrength' in props:
            comp_val = props['compressiveStrength'].get('value', 0) if isinstance(props['compressiveStrength'], dict) else props['compressiveStrength']
            try:
                if float(comp_val) > 100:  # Strong (>100 MPa)
                    characteristics.append('strong')
            except (ValueError, TypeError):
                pass
        
        # Priority 9: Tensile strength
        if 'tensileStrength' in props and 'strong' not in characteristics:
            tensile_val = props['tensileStrength'].get('value', 0) if isinstance(props['tensileStrength'], dict) else props['tensileStrength']
            try:
                if float(tensile_val) > 100:  # Strong tensile strength
                    characteristics.append('strong')
                elif float(tensile_val) < 10:  # Weak/brittle
                    characteristics.append('brittle')
            except (ValueError, TypeError):
                pass
        
        # Priority 10: Young's modulus (stiffness)
        if 'youngsModulus' in props:
            youngs_val = props['youngsModulus'].get('value', 0) if isinstance(props['youngsModulus'], dict) else props['youngsModulus']
            try:
                if float(youngs_val) > 100:  # Very stiff (>100 GPa)
                    characteristics.append('rigid')
                elif float(youngs_val) < 10:  # Flexible
                    characteristics.append('flexible')
            except (ValueError, TypeError):
                pass
        
        # Priority 11: Chemical stability
        if 'chemicalStability' in props:
            chem_val = props['chemicalStability'].get('value', 0) if isinstance(props['chemicalStability'], dict) else props['chemicalStability']
            try:
                if float(chem_val) >= 8:  # High stability (scale 1-10)
                    characteristics.append('corrosion-resistant')
            except (ValueError, TypeError):
                pass
        
        # Priority 12: Surface roughness
        if 'surfaceRoughness' in props:
            rough_val = props['surfaceRoughness'].get('value', 0) if isinstance(props['surfaceRoughness'], dict) else props['surfaceRoughness']
            try:
                if float(rough_val) > 10:  # Rough surface (>10 μm Ra)
                    characteristics.append('textured')
                elif float(rough_val) < 1:  # Smooth surface
                    characteristics.append('smooth')
            except (ValueError, TypeError):
                pass
        
        # Priority 13: Water absorption
        if 'waterAbsorption' in props:
            water_val = props['waterAbsorption'].get('value', 0) if isinstance(props['waterAbsorption'], dict) else props['waterAbsorption']
            try:
                if float(water_val) > 5:  # Absorbent (>5%)
                    characteristics.append('absorbent')
                elif float(water_val) < 1:  # Water-resistant
                    characteristics.append('water-resistant')
            except (ValueError, TypeError):
                pass
        
        # Priority 14: Absorption coefficient (laser interaction)
        if 'absorptionCoefficient' in props and 'absorptive' not in characteristics and 'reflective' not in characteristics:
            absorption_val = props['absorptionCoefficient'].get('value', 0) if isinstance(props['absorptionCoefficient'], dict) else props['absorptionCoefficient']
            try:
                if float(absorption_val) > 0.7:  # High absorption
                    characteristics.append('absorptive')
            except (ValueError, TypeError):
                pass
        
        # FAIL-FAST: Must have at least 2 characteristics
        if len(characteristics) < 2:
            raise ValueError(f"Insufficient materialProperties data - found {len(characteristics)} characteristics, need at least 2")
        
        return characteristics  # Return all characteristics, will fill to 10 total tags

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
