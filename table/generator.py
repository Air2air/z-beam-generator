"""Enhanced table generator for new schema structures."""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class TableGenerator:
    """Generates markdown tables for technical articles from schema-driven frontmatter."""

    def __init__(self, context: Dict[str, Any], schema: Dict[str, Any], frontmatter: Dict[str, Any]):
        self.context = context
        self.schema = schema
        self.frontmatter = frontmatter
        
        # Critical context values
        self.article_type = context.get("article_type", "material")
        self.subject = context.get("subject", "")
        
        # Load prompt template
        self.prompt_config = self._load_prompt_template()

    def _load_prompt_template(self) -> Dict[str, Any]:
        """Load prompt template from local YAML file."""
        try:
            prompt_path = Path(__file__).parent / "prompt.yaml"
            with open(prompt_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load table prompt template: {e}")
            return {}

    def generate(self) -> Optional[str]:
        """Generate markdown tables appropriate for the article type."""
        try:
            # Select appropriate table generator based on article type and available data
            if self.article_type == "material":
                return self._generate_material_tables()
            elif self.article_type == "application":
                return self._generate_application_tables()
            elif self.article_type == "thesaurus":
                return self._generate_thesaurus_tables()
            elif self.article_type == "region":
                return self._generate_region_tables()
            else:
                logger.warning(f"Unknown article type: {self.article_type}, falling back to generic table")
                return self._generate_generic_table()
                
        except Exception as e:
            logger.error(f"Table generation failed: {e}", exc_info=True)
            return None

    def _generate_material_tables(self) -> str:
        """Generate tables for material articles."""
        tables = []
        
        # Technical specifications table
        tech_specs = self._generate_technical_specifications_table()
        if tech_specs:
            tables.append(tech_specs)
        
        # Applications table
        applications_table = self._generate_applications_table()
        if applications_table:
            tables.append(applications_table)
        
        # Manufacturing centers table
        centers_table = self._generate_manufacturing_centers_table()
        if centers_table:
            tables.append(centers_table)
        
        # Join tables with spacing
        return "\n\n".join(tables)
    
    def _generate_application_tables(self) -> str:
        """Generate tables for application articles."""
        tables = []
        
        # Parameters table
        parameters_table = self._generate_parameters_table()
        if parameters_table:
            tables.append(parameters_table)
        
        # Benefits and challenges table
        benefits_table = self._generate_benefits_challenges_table()
        if benefits_table:
            tables.append(benefits_table)
        
        # Equipment requirements table
        equipment_table = self._generate_equipment_requirements_table()
        if equipment_table:
            tables.append(equipment_table)
            
        # Join tables with spacing
        return "\n\n".join(tables)
    
    def _generate_thesaurus_tables(self) -> str:
        """Generate tables for thesaurus entries."""
        tables = []
        
        # Related terms table
        related_terms_table = self._generate_related_terms_table()
        if related_terms_table:
            tables.append(related_terms_table)
        
        # Industry standards table
        standards_table = self._generate_industry_standards_table()
        if standards_table:
            tables.append(standards_table)
        
        # Facilities table (using regionalImplementation if available)
        facilities_table = self._generate_facilities_table()
        if facilities_table:
            tables.append(facilities_table)
            
        # Join tables with spacing
        return "\n\n".join(tables)
    
    def _generate_region_tables(self) -> str:
        """Generate tables for region articles."""
        tables = []
        
        # Facilities table
        facilities_table = self._generate_facilities_table()
        if facilities_table:
            tables.append(facilities_table)
        
        # Regional regulations table
        regulations_table = self._generate_regulations_table()
        if regulations_table:
            tables.append(regulations_table)
            
        # Join tables with spacing
        return "\n\n".join(tables)
    
    def _generate_generic_table(self) -> str:
        """Generate a generic table based on available frontmatter data."""
        # Try to find relevant data to tabulate
        for field in ["technicalSpecifications", "applications", "manufacturingCenters", 
                      "equipment", "regionalImplementation", "relatedTerms"]:
            if field in self.frontmatter and self.frontmatter[field]:
                if field == "technicalSpecifications":
                    return self._generate_technical_specifications_table()
                elif field == "applications":
                    return self._generate_applications_table()
                elif field == "manufacturingCenters":
                    return self._generate_manufacturing_centers_table()
                elif field == "equipment":
                    return self._generate_equipment_requirements_table()
                elif field == "regionalImplementation":
                    return self._generate_facilities_table()
                elif field == "relatedTerms":
                    return self._generate_related_terms_table()
        
        # If no suitable data found, return empty string
        logger.warning("No suitable data found for table generation")
        return ""

    def _generate_technical_specifications_table(self) -> str:
        """Generate a table of technical specifications."""
        tech_specs = self.frontmatter.get("technicalSpecifications", {})
        if not tech_specs or not isinstance(tech_specs, dict):
            return ""
        
        # Table header
        table = "## Technical Specifications\n\n"
        table += "| Parameter | Value |\n"
        table += "|-----------|-------|\n"
        
        # Table rows
        for param, value in tech_specs.items():
            # Format parameter name for better readability
            formatted_param = param.replace("_", " ").replace(".", " ").title()
            table += f"| {formatted_param} | {value} |\n"
        
        return table

    def _generate_applications_table(self) -> str:
        """Generate a table of applications."""
        applications = self.frontmatter.get("applications", [])
        if not applications or not isinstance(applications, list):
            return ""
        
        # Table header
        table = "## Applications\n\n"
        table += "| Application | Description | Benefits |\n"
        table += "|-------------|-------------|----------|\n"
        
        # Table rows
        for app in applications:
            if isinstance(app, dict):
                name = app.get("name", "")
                description = app.get("description", "")
                benefits = app.get("benefits", "")
                table += f"| {name} | {description} | {benefits} |\n"
            elif isinstance(app, str):
                table += f"| {app} | | |\n"
        
        return table

    def _generate_manufacturing_centers_table(self) -> str:
        """Generate a table of manufacturing centers."""
        # Try both manufacturingCenters and facilities keys
        centers = self.frontmatter.get("manufacturingCenters", [])
        if not centers:
            centers = self.frontmatter.get("facilities", [])
            
        if not centers or not isinstance(centers, list):
            return ""
        
        # Table header
        table = "## Manufacturing Centers\n\n"
        table += "| Facility Name | Usage | Address |\n"
        table += "|--------------|-------|----------|\n"
        
        # Table rows
        for center in centers:
            if isinstance(center, dict):
                name = center.get("name", "")
                usage = center.get("laserCleaningUsage", center.get("description", ""))
                address = center.get("address", center.get("location", ""))
                table += f"| {name} | {usage} | {address} |\n"
            elif isinstance(center, str):
                table += f"| {center} | | |\n"
        
        return table

    def _generate_parameters_table(self) -> str:
        """Generate a table of process parameters."""
        parameters = self.frontmatter.get("processParameters", {})
        if not parameters or not isinstance(parameters, dict):
            # Try technicalSpecifications as fallback
            parameters = self.frontmatter.get("technicalSpecifications", {})
            if not parameters or not isinstance(parameters, dict):
                return ""
        
        # Table header
        table = "## Process Parameters\n\n"
        table += "| Parameter | Typical Value | Range | Unit |\n"
        table += "|-----------|---------------|-------|------|\n"
        
        # Table rows
        for param, value in parameters.items():
            # Try to parse complex values
            if isinstance(value, dict):
                typical = value.get("typical", "")
                range_val = value.get("range", "")
                unit = value.get("unit", "")
                table += f"| {param} | {typical} | {range_val} | {unit} |\n"
            else:
                # For simple values, just use the value directly
                formatted_param = param.replace("_", " ").replace(".", " ").title()
                table += f"| {formatted_param} | {value} | | |\n"
        
        return table

    def _generate_benefits_challenges_table(self) -> str:
        """Generate a table of benefits and challenges."""
        benefits = self.frontmatter.get("benefits", [])
        challenges = self.frontmatter.get("challenges", [])
        
        if not benefits and not challenges:
            return ""
        
        # Table header
        table = "## Benefits & Challenges\n\n"
        table += "| Type | Description | Mitigation |\n"
        table += "|------|-------------|------------|\n"
        
        # Benefits rows
        for benefit in benefits:
            if isinstance(benefit, dict):
                description = benefit.get("description", "")
                impact = benefit.get("impact", "")
                table += f"| Benefit | {description} | {impact} |\n"
            elif isinstance(benefit, str):
                table += f"| Benefit | {benefit} | |\n"
        
        # Challenges rows
        for challenge in challenges:
            if isinstance(challenge, dict):
                description = challenge.get("description", "")
                mitigation = challenge.get("mitigation", "")
                table += f"| Challenge | {description} | {mitigation} |\n"
            elif isinstance(challenge, str):
                table += f"| Challenge | {challenge} | |\n"
        
        return table

    def _generate_equipment_requirements_table(self) -> str:
        """Generate a table of equipment requirements."""
        equipment = self.frontmatter.get("equipment", [])
        if not equipment or not isinstance(equipment, list):
            return ""
        
        # Table header
        table = "## Equipment Requirements\n\n"
        table += "| Equipment Type | Specifications | Purpose |\n"
        table += "|---------------|----------------|--------|\n"
        
        # Table rows
        for item in equipment:
            if isinstance(item, dict):
                type_name = item.get("type", "")
                specs = item.get("specifications", "")
                purpose = item.get("purpose", "")
                table += f"| {type_name} | {specs} | {purpose} |\n"
            elif isinstance(item, str):
                table += f"| {item} | | |\n"
        
        return table

    def _generate_related_terms_table(self) -> str:
        """Generate a table of related terms for thesaurus entries."""
        related_terms = self.frontmatter.get("relatedTerms", [])
        if not related_terms or not isinstance(related_terms, list):
            return ""
        
        # Table header
        table = "## Related Terms\n\n"
        table += "| Term | Relationship | Description |\n"
        table += "|------|--------------|-------------|\n"
        
        # Table rows
        for term in related_terms:
            if isinstance(term, dict):
                name = term.get("term", "")
                relationship = term.get("relationship", "")
                description = term.get("description", "")
                table += f"| {name} | {relationship} | {description} |\n"
            elif isinstance(term, str):
                table += f"| {term} | Related | |\n"
        
        return table

    def _generate_industry_standards_table(self) -> str:
        """Generate a table of industry standards."""
        standards = self.frontmatter.get("industryStandards", [])
        if not standards:
            standards = self.frontmatter.get("regulatoryStandards", [])
            
        if not standards or not isinstance(standards, list):
            return ""
        
        # Table header
        table = "## Industry Standards\n\n"
        table += "| Standard | Description | Requirements |\n"
        table += "|----------|-------------|-------------|\n"
        
        # Table rows
        for standard in standards:
            if isinstance(standard, dict):
                name = standard.get("name", "")
                description = standard.get("description", "")
                requirements = standard.get("requirements", "")
                table += f"| {name} | {description} | {requirements} |\n"
            elif isinstance(standard, str):
                table += f"| {standard} | | |\n"
        
        return table

    def _generate_facilities_table(self) -> str:
        """Generate a table of facilities from regionalImplementation data."""
        regional = self.frontmatter.get("regionalImplementation", {})
        
        # Check for facility or facilities
        facility = regional.get("facility", "")
        
        if facility:
            # Single facility case
            table = "## Facility Information\n\n"
            table += "| Facility Name | Usage | Address |\n"
            table += "|--------------|-------|----------|\n"
            
            facility_name = regional.get("facility", "")
            description = regional.get("facilityDescription", "")
            location = regional.get("location", "")
            
            table += f"| {facility_name} | {description} | {location} |\n"
            
            return table
            
        # Try facilities array
        facilities = regional.get("facilities", [])
        if not facilities or not isinstance(facilities, list):
            # Check direct facilities in frontmatter
            facilities = self.frontmatter.get("facilities", [])
            if not facilities or not isinstance(facilities, list):
                return ""
        
        # Table header
        table = "## Regional Facilities\n\n"
        table += "| Facility Name | Usage | Address |\n"
        table += "|--------------|-------|----------|\n"
        
        # Table rows
        for facility in facilities:
            if isinstance(facility, dict):
                name = facility.get("name", "")
                usage = facility.get("description", "")
                address = facility.get("address", facility.get("location", ""))
                table += f"| {name} | {usage} | {address} |\n"
            elif isinstance(facility, str):
                table += f"| {facility} | | |\n"
        
        return table

    def _generate_regulations_table(self) -> str:
        """Generate a table of regional regulations."""
        regulations = self.frontmatter.get("regulations", [])
        if not regulations or not isinstance(regulations, list):
            # Try regulatory standards as fallback
            regulations = self.frontmatter.get("regulatoryStandards", [])
            if not regulations or not isinstance(regulations, list):
                return ""
        
        # Table header
        table = "## Regional Regulations\n\n"
        table += "| Regulation | Description | Compliance Requirements |\n"
        table += "|------------|-------------|------------------------|\n"
        
        # Table rows
        for reg in regulations:
            if isinstance(reg, dict):
                name = reg.get("name", "")
                description = reg.get("description", "")
                requirements = reg.get("requirements", reg.get("compliance", ""))
                table += f"| {name} | {description} | {requirements} |\n"
            elif isinstance(reg, str):
                table += f"| {reg} | | |\n"
        
        return table