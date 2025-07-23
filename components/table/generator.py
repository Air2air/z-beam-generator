"""
Module for generating tables from frontmatter data.
"""

import logging
from typing import Dict, Any, List

from components.base import BaseComponent

logger = logging.getLogger(__name__)

class TableGenerator(BaseComponent):
    """Generates tables for articles based on frontmatter data."""
    
    def __init__(self, subject, article_type, component_name, config=None):
        """Initialize the table generator.
        
        Args:
            subject: Subject of the article (e.g., 'quartzite')
            article_type: Type of article (e.g., 'material')
            component_name: Name of the component (e.g., 'table')
            config: Configuration for the component
        """
        # Enhanced logging for initialization parameters
        logger.debug(f"TableGenerator.__init__ called with: subject={type(subject)}, article_type={type(article_type)}, component_name={type(component_name)}, config={type(config)}")
        
        # Fix for when component_name is actually a config dictionary
        if isinstance(component_name, dict) and config is None:
            logger.info(f"TableGenerator detected component_name is a dict, fixing initialization pattern")
            # The correct initialization pattern is:
            # - subject is the actual subject string
            # - article_type is the actual article_type string
            # - config is the component configuration
            config = component_name
            component_name = "table"
        
        # Log pre-super call state
        logger.debug(f"TableGenerator calling super().__init__ with: subject={subject}, article_type={article_type}, component_name={component_name}, config={bool(config)}")
        
        # Call super with the right parameters
        super().__init__(subject, article_type, component_name, config)
        
        # Log post-initialization state
        logger.debug(f"TableGenerator attributes after init: self.subject={type(self.subject)}, self.article_type={type(self.article_type)}")
        
        # Load the prompt configuration during initialization
        try:
            self.prompt_config = self.load_prompt_config()
            logger.debug(f"Loaded table prompt configuration: {self.prompt_config.keys() if hasattr(self.prompt_config, 'keys') else 'None'}")
        except Exception as e:
            logger.error(f"Failed to load prompt configuration: {str(e)}")
            self.prompt_config = {}
        
        logger.info(f"TableGenerator initialized for {self.subject} with component_name: {self.component_type}")
    
    def generate(self) -> str:
        """Generate tables dynamically based on frontmatter structure."""
        try:
            # Get frontmatter data
            logger.debug(f"TableGenerator.generate() called with subject={self.subject}")
            frontmatter_data = self.get_frontmatter_data()
            
            logger.info(f"Table generator received frontmatter: {bool(frontmatter_data)}")
            
            # Dump all frontmatter keys and types for debugging
            if frontmatter_data:
                logger.debug("Frontmatter contents:")
                for key, value in frontmatter_data.items():
                    value_type = type(value).__name__
                    value_info = f"{len(value)} items" if isinstance(value, (list, dict)) else str(value)[:50]
                    logger.debug(f"  {key}: {value_type} - {value_info}")
        
            # Get format settings from prompt configuration
            logger.debug(f"Getting format settings from prompt_config: {self.prompt_config.keys() if hasattr(self.prompt_config, 'keys') else 'None'}")
            format_config = self.prompt_config.get("format", {})
            header_style = format_config.get("header_style", "")
            logger.debug(f"Using header_style: {header_style}")
            
            # Direct table generation from frontmatter
            tables_content = []
            
            # Process applications data if available
            if 'applications' in frontmatter_data and frontmatter_data['applications']:
                apps = frontmatter_data['applications']
                logger.debug(f"Found applications data: {len(apps) if isinstance(apps, list) else type(apps)}")
                
                if isinstance(apps, list) and apps:
                    logger.info(f"Generating applications table with {len(apps)} entries")
                    heading = f"## Applications of Laser Cleaning on {self.subject.title()}"
                    tables_content.append(heading)
                    
                    description = f"\nLaser cleaning offers specific advantages for different {self.subject} applications:\n"
                    tables_content.append(description)
                    
                    # Create table header with optional styling
                    header_prefix = "**" if header_style == "bold" else ""
                    header_suffix = "**" if header_style == "bold" else ""
                    tables_content.append(f"| {header_prefix}Application{header_suffix} | {header_prefix}Description{header_suffix} |")
                    tables_content.append("| --- | --- |")
                    
                    # Add table rows
                    for app in apps:
                        name = app.get('name', '')
                        desc = app.get('description', '')
                        tables_content.append(f"| {name} | {desc} |")
                    
                    tables_content.append("")
            else:
                logger.debug(f"No applications data found in frontmatter")
            
            # Process composition data if available
            if 'composition' in frontmatter_data and frontmatter_data['composition']:
                comp = frontmatter_data['composition']
                logger.debug(f"Found composition data: {len(comp) if isinstance(comp, list) else type(comp)}")
                
                if isinstance(comp, list) and comp:
                    logger.info(f"Generating composition table with {len(comp)} entries")
                    heading = f"## Composition of {self.subject.title()}"
                    tables_content.append(heading)
                    
                    description = f"\n{self.subject.title()}'s composition affects laser cleaning parameters and effectiveness:\n"
                    tables_content.append(description)
                    
                    # Create table header
                    header_prefix = "**" if header_style == "bold" else ""
                    header_suffix = "**" if header_style == "bold" else ""
                    tables_content.append(f"| {header_prefix}Component{header_suffix} | {header_prefix}Type{header_suffix} | {header_prefix}Percentage{header_suffix} |")
                    tables_content.append("| --- | --- | --- |")
                    
                    # Add table rows
                    for c in comp:
                        component = c.get('component', '')
                        type_val = c.get('type', '')
                        percentage = c.get('percentage', '')
                        tables_content.append(f"| {component} | {type_val} | {percentage} |")
                    
                    tables_content.append("")
            else:
                logger.debug(f"No composition data found in frontmatter")
            
            # Process technical specifications if available
            if 'technicalSpecifications' in frontmatter_data and frontmatter_data['technicalSpecifications']:
                specs = frontmatter_data['technicalSpecifications']
                logger.debug(f"Found technicalSpecifications: {len(specs) if isinstance(specs, dict) else type(specs)}")
                
                if isinstance(specs, dict) and specs:
                    logger.info(f"Generating technical specifications table with {len(specs)} entries")
                    heading = f"## Technical Specifications for Laser Cleaning {self.subject.title()}"
                    tables_content.append(heading)
                    
                    description = f"\nOptimal technical parameters for {self.subject} laser cleaning:\n"
                    tables_content.append(description)
                    
                    # Create table header
                    header_prefix = "**" if header_style == "bold" else ""
                    header_suffix = "**" if header_style == "bold" else ""
                    tables_content.append(f"| {header_prefix}Parameter{header_suffix} | {header_prefix}Value{header_suffix} |")
                    tables_content.append("| --- | --- |")
                    
                    # Add table rows
                    for param, value in specs.items():
                        param_name = param.replace("_", " ").title()
                        tables_content.append(f"| {param_name} | {value} |")
                    
                    tables_content.append("")
            else:
                logger.debug(f"No technicalSpecifications found in frontmatter")
            
            # Process compatibility data if available
            if 'compatibility' in frontmatter_data and frontmatter_data['compatibility']:
                compat = frontmatter_data['compatibility']
                logger.debug(f"Found compatibility data: {len(compat) if isinstance(compat, list) else type(compat)}")
                
                if isinstance(compat, list) and compat:
                    logger.info(f"Generating compatibility table with {len(compat)} entries")
                    heading = f"## Material Compatibility Chart"
                    tables_content.append(heading)
                    
                    description = f"\nLaser cleaning parameters used for {self.subject} can be adapted for similar materials:\n"
                    tables_content.append(description)
                    
                    # Create table header
                    header_prefix = "**" if header_style == "bold" else ""
                    header_suffix = "**" if header_style == "bold" else ""
                    tables_content.append(f"| {header_prefix}Application{header_suffix} | {header_prefix}Compatible Material{header_suffix} |")
                    tables_content.append("| --- | --- |")
                    
                    # Add table rows
                    for c in compat:
                        app = c.get('application', '')
                        mat = c.get('material', '')
                        tables_content.append(f"| {app} | {mat} |")
                    
                    tables_content.append("")
            else:
                logger.debug(f"No compatibility data found in frontmatter")
                    
            # Process environmental impact data if available
            if 'environmentalImpact' in frontmatter_data and frontmatter_data['environmentalImpact']:
                env_impact = frontmatter_data['environmentalImpact']
                logger.debug(f"Found environmentalImpact data: {len(env_impact) if isinstance(env_impact, list) else type(env_impact)}")
                
                if isinstance(env_impact, list) and env_impact:
                    logger.info(f"Generating environmental impact table with {len(env_impact)} entries")
                    heading = f"## Environmental Benefits of Laser Cleaning {self.subject.title()}"
                    tables_content.append(heading)
                    
                    description = f"\nLaser cleaning offers significant environmental advantages over traditional {self.subject} cleaning methods:\n"
                    tables_content.append(description)
                    
                    # Create table header
                    header_prefix = "**" if header_style == "bold" else ""
                    header_suffix = "**" if header_style == "bold" else ""
                    tables_content.append(f"| {header_prefix}Benefit{header_suffix} | {header_prefix}Description{header_suffix} |")
                    tables_content.append("| --- | --- |")
                    
                    # Add table rows
                    for impact in env_impact:
                        benefit = impact.get('benefit', '')
                        description = impact.get('description', '')
                        tables_content.append(f"| {benefit} | {description} |")
                    
                    tables_content.append("")
            else:
                logger.debug(f"No environmentalImpact data found in frontmatter")
                    
            # If no tables were generated, log a warning
            if not tables_content:
                logger.warning(f"No suitable data found for tables in frontmatter for {self.subject}")
                return ""
            
            result = "\n".join(tables_content)
            logger.info(f"Generated {len(tables_content)} lines of table content")
            return result
            
        except Exception as e:
            logger.error(f"Error generating tables: {str(e)}", exc_info=True)
            return f"<!-- Error generating tables: {str(e)} -->"