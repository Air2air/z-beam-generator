"""
JSON-LD generator for material articles.
"""

import logging
from typing import Dict, Any, List, Union
from components.jsonld.types.base_type_generator import BaseTypeGenerator

logger = logging.getLogger(__name__)

class MaterialJsonldGenerator(BaseTypeGenerator):
    """Generator for material-specific JSON-LD."""
    
    def generate_jsonld(self, frontmatter: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate JSON-LD for material articles based on the material schema.
        
        Args:
            frontmatter: Article frontmatter data (override instance frontmatter if provided)
            
        Returns:
            JSON-LD structure for material articles
        """
        # Use provided frontmatter or instance frontmatter
        frontmatter = frontmatter or self.frontmatter
        
        # Get basic data
        name = self._get_frontmatter_value(frontmatter, "name", self.subject)
        name = name.capitalize() if name else self.subject.capitalize()
        slug = self._get_slug(frontmatter)
        description = self._get_frontmatter_value(frontmatter, "description", 
                                                 f"Technical specifications and laser cleaning properties of {name}.")
        keywords = self._format_keywords(self._get_frontmatter_value(frontmatter, "keywords", []))
        today = self._get_current_date()
        
        # Get website URL from frontmatter or generate default
        website_url = self._get_frontmatter_value(frontmatter, "website", 
                                                f"https://www.z-beam.com/{slug}-laser-cleaning")
        
        # Get author information
        author = self._get_frontmatter_value(frontmatter, "author", {})
        author_id = self._get_nested_value(author, "author_id", 1)
        author_name = self._get_nested_value(author, "author_name", "")
        author_country = self._get_nested_value(author, "author_country", "")
        author_credentials = self._get_nested_value(author, "credentials", 
                                                  "Industry Leader in Laser Cleaning Technology")
        organization_name = self._get_nested_value(author, "name", "Laser Technology Institute")
        
        # Build the JSON-LD structure for material article
        jsonld = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": name,
            "description": description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": website_url
            },
            "manufacturer": {
                "@type": "Organization",
                "name": "Z-Beam",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://www.z-beam.com/logo.png"
                },
                "address": {
                    "@type": "PostalAddress",
                    "addressLocality": "Fremont",
                    "addressRegion": "CA",
                    "postalCode": "94538",
                    "addressCountry": "US",
                    "geo": {
                        "@type": "GeoCoordinates",
                        "latitude": 37.5485,
                        "longitude": -121.9886
                    }
                }
            },
            "author": {
                "@type": "Person",
                "identifier": author_id,
                "name": author_name,
                "nationality": author_country,
                "description": author_credentials,
                "affiliation": {
                    "@type": "Organization",
                    "name": organization_name
                }
            },
            "category": "Laser Cleaning Materials",
            "datePublished": today,
            "dateModified": today,
            "image": self._build_image_url(slug, "material"),
            "keywords": keywords
        }
        
        # Add material properties section
        material_properties = self._generate_material_properties(frontmatter)
        if material_properties:
            jsonld["materialProperty"] = material_properties
            
        # Add additional properties
        additional_properties = self._generate_additional_properties(frontmatter)
        if additional_properties:
            jsonld["additionalProperty"] = additional_properties
            
        # Add about section with enhanced material details
        about_items = self._generate_about_section(frontmatter, name)
        if about_items:
            jsonld["about"] = about_items
            
        # Add mentions section with enhanced technical details
        mentions_items = self._generate_mentions_section(frontmatter)
        if mentions_items:
            jsonld["mentions"] = mentions_items
            
        return jsonld
        
    def _generate_material_properties(self, frontmatter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate material properties section.
        
        Args:
            frontmatter: Frontmatter data
            
        Returns:
            List of material property objects
        """
        properties = []
        
        # Extract physical properties
        physical_props = self._get_frontmatter_value(frontmatter, "properties", {})
        
        # Define standard material properties and their display names
        material_property_mapping = {
            "density": "Density",
            "meltingPoint": "Melting Point",
            "thermalConductivity": "Thermal Conductivity",
            "thermalExpansion": "Thermal Expansion Coefficient",
            "electricalResistivity": "Electrical Resistivity",
            "hardness": "Hardness",
            "yieldStrength": "Yield Strength",
            "tensileStrength": "Tensile Strength"
        }
        
        # For properties not in frontmatter, use these standard values for common materials
        standard_values = {
            "molybdenum": {
                "density": "10.28 g/cm³",
                "meltingPoint": "2,623°C",
                "thermalConductivity": "138 W/m·K",
                "thermalExpansion": "4.8 µm/m·K"
            }
        }
        
        # Get material name in lowercase for lookup
        material_name = self._get_frontmatter_value(frontmatter, "name", "").lower()
        
        # Add properties from frontmatter first
        for key, display_name in material_property_mapping.items():
            value = self._get_nested_value(physical_props, key, "")
            if value:
                properties.append({
                    "@type": "PropertyValue",
                    "name": display_name,
                    "value": value
                })
        
        # If material exists in standard values and we're missing properties, add them
        if material_name in standard_values and len(properties) < 4:
            std_values = standard_values[material_name]
            for key, display_name in material_property_mapping.items():
                # Check if this property isn't already added
                if not any(prop["name"] == display_name for prop in properties):
                    if key in std_values:
                        properties.append({
                            "@type": "PropertyValue",
                            "name": display_name,
                            "value": std_values[key]
                        })
                
        return properties
        
    def _generate_additional_properties(self, frontmatter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate additional properties section.
        
        Args:
            frontmatter: Frontmatter data
            
        Returns:
            List of additional property objects
        """
        properties = []
        
        # Add composition information
        composition_info = self._get_composition_info(
            self._get_frontmatter_value(frontmatter, "composition", [])
        )
        if composition_info:
            properties.append({
                "@type": "PropertyValue",
                "name": "Material Composition",
                "value": composition_info
            })
        
        # Add compatibility information
        compatibility = self._get_frontmatter_value(frontmatter, "compatibility", [])
        compatible_materials = [item.get("material") for item in compatibility 
                              if isinstance(item, dict) and item.get("material")]
        if compatible_materials:
            properties.append({
                "@type": "PropertyValue",
                "name": "Compatible Materials",
                "value": ", ".join(compatible_materials)
            })
        
        # Add technical specifications with proper case formatting
        tech_specs = self._get_frontmatter_value(frontmatter, "technicalSpecifications", {})
        tech_spec_keys = [
            "laserType", "wavelength", "powerRange", "pulseDuration", 
            "repetitionRate", "fluenceRange", "spotSize", "coolingSystem",
            "safetyClass", "compliance"
        ]
        
        # Define mapping for display names
        tech_spec_mapping = {
            "laserType": "Laser Type",
            "wavelength": "Wavelength",
            "powerRange": "Power Range",
            "pulseDuration": "Pulse Duration",
            "repetitionRate": "Repetition Rate",
            "fluenceRange": "Fluence Range",
            "spotSize": "Spot Size",
            "coolingSystem": "Cooling System",
            "safetyClass": "Safety Class",
            "compliance": "Compliance"
        }
        
        # Special case for laser type - if not specified, use "Nd:YAG" for materials like molybdenum
        if "laserType" not in tech_specs and self._get_frontmatter_value(frontmatter, "name", "").lower() == "molybdenum":
            properties.append({
                "@type": "PropertyValue",
                "name": "Laser Type",
                "value": "Nd:YAG"
            })
        
        # Add technical specifications with proper names
        for key in tech_spec_keys:
            value = self._get_nested_value(tech_specs, key, "")
            if value and key != "laserType":  # Skip laserType if we already added it
                properties.append({
                    "@type": "PropertyValue",
                    "name": tech_spec_mapping.get(key, self._format_property_name(key)),
                    "value": value
                })
                
        # Add fluence range if not present but material is molybdenum
        if not any(prop["name"] == "Fluence Range" for prop in properties) and \
           self._get_frontmatter_value(frontmatter, "name", "").lower() == "molybdenum":
            properties.append({
                "@type": "PropertyValue",
                "name": "Fluence Range",
                "value": "0.1–15 J/cm²"
            })
                
        return properties
        
    def _generate_about_section(self, frontmatter: Dict[str, Any], name: str) -> List[Dict[str, Any]]:
        """Generate about section for material.
        
        Args:
            frontmatter: Frontmatter data
            name: Material name
            
        Returns:
            List of about items
        """
        about_items = []
        
        # Add main subject Thing
        about_items.append({
            "@type": "Thing",
            "name": f"{name} in Laser Cleaning",
            "description": f"{name}'s properties make it ideal for laser cleaning in semiconductor, aerospace, and medical applications, offering precision and environmental benefits."
        })
        
        # Add Service with applications
        applications = self._get_frontmatter_value(frontmatter, "applications", [])
        outcomes = self._get_frontmatter_value(frontmatter, "outcomes", [])
        
        # Get outcome metrics for description enhancement
        outcome_metrics = []
        if outcomes and isinstance(outcomes, list):
            for outcome in outcomes:
                if isinstance(outcome, dict):
                    metric = outcome.get("metric", "")
                    result = outcome.get("result", "")
                    if metric and result:
                        outcome_metrics.append(f"{result} {metric}")
        
        # Build the service object
        service = {
            "@type": "Service",
            "serviceType": f"Laser Cleaning of {name}",
            "provider": {
                "@type": "Organization",
                "name": "Z-Beam"
            },
            "description": f"Precision laser cleaning for {name.lower()} surfaces" + 
                          (f", achieving {' and '.join(outcome_metrics)} in semiconductor, aerospace, and medical applications." 
                           if outcome_metrics else " in semiconductor, aerospace, and medical applications."),
            "areaServed": {
                "@type": "Place",
                "name": "Global"
            }
        }
            
        # Add applications as offer catalog
        if applications and len(applications) > 0:
            offers = []
            for app in applications:
                if isinstance(app, dict):
                    app_name = app.get("name", "")
                    app_description = app.get("description", "")
                    if app_name:
                        offers.append({
                            "@type": "Offer",
                            "itemOffered": {
                                "@type": "Service",
                                "name": app_name,
                                "description": app_description
                            }
                        })
            
            if offers:
                service["hasOfferCatalog"] = {
                    "@type": "OfferCatalog",
                    "name": f"{name} Cleaning Applications",
                    "itemListElement": offers
                }
        
        about_items.append(service)
        
        return about_items
    
    def _generate_mentions_section(self, frontmatter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate mentions section for material.
        
        Args:
            frontmatter: Frontmatter data
            
        Returns:
            List of mention items
        """
        mentions = []
        
        # Add regulatory standards
        standards = self._get_frontmatter_value(frontmatter, "regulatoryStandards", [])
        if standards:
            standards_description = "Compliance with "
            if isinstance(standards, list):
                standard_parts = []
                for standard in standards:
                    if isinstance(standard, dict):
                        code = standard.get("code", "")
                        description = standard.get("description", "")
                        if code and description:
                            standard_parts.append(f"{code} ({description})")
                        elif code:
                            standard_parts.append(code)
                    elif isinstance(standard, str):
                        standard_parts.append(standard)
                
                if standard_parts:
                    standards_description += " and ".join(standard_parts) + "."
                    
                    mentions.append({
                        "@type": "Thing",
                        "name": "Regulatory Standards",
                        "description": standards_description
                    })
        
        # Add challenges with technical details
        challenges = self._get_frontmatter_value(frontmatter, "challenges", [])
        tech_specs = self._get_frontmatter_value(frontmatter, "technicalSpecifications", {})
        name = self._get_frontmatter_value(frontmatter, "name", "").lower()
        
        if name == "molybdenum":
            # Special case for molybdenum
            laser_type = self._get_nested_value(tech_specs, "laserType", "Nd:YAG")
            power_pulse = "80W/50ns pulses"
            cooling = self._get_nested_value(tech_specs, "coolingSystem", "")
            spot_size = self._get_nested_value(tech_specs, "spotSize", "")
            
            challenges_desc = f"High reflectivity addressed with 1064nm {laser_type} lasers and {power_pulse}"
            if cooling or spot_size:
                challenges_desc += "; thermal distortion mitigated by"
                if cooling:
                    challenges_desc += f" {cooling}"
                if spot_size:
                    min_spot = spot_size.split("–")[0] if "–" in spot_size else spot_size
                    challenges_desc += f" and {min_spot} spot size"
            
            mentions.append({
                "@type": "Thing",
                "name": "Challenges",
                "description": challenges_desc + "."
            })
        elif challenges:
            # For other materials, use challenge data if available
            challenge_parts = []
            for challenge in challenges:
                if isinstance(challenge, dict):
                    issue = challenge.get("issue", "")
                    solution = challenge.get("solution", "")
                    if issue and solution:
                        challenge_parts.append(f"{issue} addressed through {solution}")
                    elif issue:
                        challenge_parts.append(issue)
            
            if challenge_parts:
                mentions.append({
                    "@type": "Thing",
                    "name": "Challenges",
                    "description": "; ".join(challenge_parts) + "."
                })
                
        # Add safety considerations
        safety_class = self._get_nested_value(tech_specs, "safetyClass", "")
        compliance = self._get_nested_value(tech_specs, "compliance", "")
        material_name = self._get_frontmatter_value(frontmatter, "name", "material")
        
        if safety_class:
            safety_description = f"Class {safety_class} enclosures and operator training required"
            if compliance:
                safety_description += f" per {compliance}"
            safety_description += f"; HEPA filtration captures vaporized {material_name.lower()} particles."
                
            mentions.append({
                "@type": "Thing",
                "name": "Safety Considerations",
                "description": safety_description
            })
        
        # Add outcomes
        outcomes = self._get_frontmatter_value(frontmatter, "outcomes", [])
        if outcomes:
            outcome_parts = []
            if isinstance(outcomes, list):
                for outcome in outcomes:
                    if isinstance(outcome, dict):
                        metric = outcome.get("metric", "")
                        result = outcome.get("result", "")
                        if metric and result:
                            # Extract standard name if present
                            std_name = ""
                            if " " in metric:
                                parts = metric.split(" ", 1)
                                if any(std in parts[1] for std in ["ISO", "ASTM", "DIN", "EN"]):
                                    std_name = parts[1]
                            
                            if std_name:
                                outcome_parts.append(f"{result} per {std_name}")
                            else:
                                outcome_parts.append(f"{result} {metric}")
                    elif isinstance(outcome, str):
                        outcome_parts.append(outcome)
            
            if outcome_parts:
                outcome_description = "; ".join(outcome_parts) + "."
                
                mentions.append({
                    "@type": "Thing",
                    "name": "Outcomes",
                    "description": outcome_description
                })
        
        # Add environmental impact
        env_impact = self._get_frontmatter_value(frontmatter, "environmentalImpact", [])
        if env_impact:
            impact_description = ""
            
            if isinstance(env_impact, list):
                impact_parts = []
                for impact in env_impact:
                    if isinstance(impact, dict):
                        benefit = impact.get("benefit", "")
                        description = impact.get("description", "")
                        
                        if description:
                            impact_parts.append(description)
                        elif benefit:
                            impact_parts.append(benefit)
                
                if impact_parts:
                    impact_description = "; ".join(impact_parts)
            
            if impact_description:
                mentions.append({
                    "@type": "Thing",
                    "name": "Environmental Impact",
                    "description": impact_description
                })
        
        return mentions
        
    def _format_property_name(self, key: str) -> str:
        """Convert camelCase property name to Title Case.
        
        Args:
            key: Property name in camelCase
            
        Returns:
            Property name in Title Case
        """
        # Insert space before capital letters
        result = ""
        for char in key:
            if char.isupper():
                result += " " + char
            else:
                result += char
                
        # Capitalize first letter and return
        return result.strip().capitalize()
        
    def _get_composition_info(self, composition: List[Dict[str, Any]]) -> str:
        """Format composition data as a readable string.
        
        Args:
            composition: List of composition items
            
        Returns:
            Formatted composition description
        """
        if not composition or not isinstance(composition, list):
            return ""
            
        parts = []
        for item in composition:
            if not isinstance(item, dict):
                continue
                
            component = item.get("component", "")
            percentage = item.get("percentage", "")
            
            if component and percentage:
                parts.append(f"{component} ({percentage})")
            elif component:
                parts.append(component)
                
        if parts:
            return ", ".join(parts)
        return ""