"""
FrontmatterOrchestrator - Coordinate module execution

Orchestrates all frontmatter modules to generate complete frontmatter YAML.

Architecture:
- Initialize all 9 modules
- Execute in logical order
- Assemble complete frontmatter dict
- Handle errors gracefully
- Log progress clearly
"""

import logging
from typing import Dict, Optional

from .modules.metadata_module import MetadataModule
from .modules.author_module import AuthorModule
from .modules.applications_module import ApplicationsModule
from .modules.properties_module import PropertiesModule
from .modules.settings_module import SettingsModule
from .modules.simple_modules import (
    ComplianceModule,
    ImpactModule,
    MediaModule,
    CharacteristicsModule
)


class FrontmatterOrchestrator:
    """Orchestrate frontmatter generation using modular components"""
    
    def __init__(self, categories_yaml_path: str = "materials/data/Categories.yaml"):
        """
        Initialize orchestrator with all modules
        
        Args:
            categories_yaml_path: Path to Categories.yaml for ranges
        """
        self.logger = logging.getLogger(__name__)
        
        # Initialize modules
        self.metadata_module = MetadataModule()
        self.author_module = AuthorModule()
        self.applications_module = ApplicationsModule()
        self.properties_module = PropertiesModule(categories_yaml_path)
        self.settings_module = SettingsModule(categories_yaml_path)
        self.compliance_module = ComplianceModule()
        self.impact_module = ImpactModule()
        self.media_module = MediaModule()
        self.characteristics_module = CharacteristicsModule()
        
        self.logger.info("✅ Initialized FrontmatterOrchestrator with 9 modules")
    
    def generate(
        self,
        material_name: str,
        material_data: Dict,
        include_faq: bool = True
    ) -> Dict:
        """
        Generate complete frontmatter for material
        
        Args:
            material_name: Name of material
            material_data: Material data from Materials.yaml
            include_faq: Whether to include FAQ section (default: True)
            
        Returns:
            Complete frontmatter dictionary ready for YAML export
            
        Raises:
            ValueError: If generation fails
        """
        self.logger.info(f"🚀 Generating frontmatter for {material_name}")
        
        frontmatter = {}
        
        try:
            # 1. Metadata (name, title, subtitle, description, category, subcategory)
            self.logger.debug("1/9 Generating metadata...")
            metadata = self.metadata_module.generate(material_name, material_data)
            frontmatter.update(metadata)
            
            # 2. Author
            self.logger.debug("2/9 Extracting author...")
            frontmatter['author'] = self.author_module.generate(material_data)
            
            # 3. Applications
            self.logger.debug("3/9 Extracting applications...")
            frontmatter['applications'] = self.applications_module.generate(
                material_name, material_data
            )
            
            # 4. Material Properties (with ranges)
            self.logger.debug("4/9 Generating material properties...")
            frontmatter['materialProperties'] = self.properties_module.generate(
                material_name, material_data
            )
            
            # 5. Machine Settings (with ranges)
            self.logger.debug("5/9 Generating machine settings...")
            frontmatter['machineSettings'] = self.settings_module.generate(
                material_name, material_data
            )
            
            # 6. Compliance (regulatory standards)
            self.logger.debug("6/9 Extracting compliance...")
            frontmatter['regulatoryStandards'] = self.compliance_module.generate(
                material_data
            )
            
            # 7. Impact (environmental, outcomes)
            self.logger.debug("7/9 Extracting impact data...")
            impact_data = self.impact_module.generate(material_data)
            frontmatter['environmentalImpact'] = impact_data['environmentalImpact']
            frontmatter['outcomeMetrics'] = impact_data['outcomeMetrics']
            
            # 8. Media (images, caption)
            self.logger.debug("8/9 Extracting media...")
            media_data = self.media_module.generate(material_data)
            frontmatter['images'] = media_data['images']
            frontmatter['caption'] = media_data['caption']
            
            # 9. Characteristics (qualitative properties)
            self.logger.debug("9/9 Extracting characteristics...")
            frontmatter['materialCharacteristics'] = self.characteristics_module.generate(
                material_data
            )
            
            # Optional: Include FAQ
            if include_faq and 'faq' in material_data:
                frontmatter['faq'] = material_data['faq']
            
            self.logger.info(
                f"✅ Generated complete frontmatter for {material_name} "
                f"({len(frontmatter)} fields)"
            )
            
            return frontmatter
            
        except Exception as e:
            self.logger.error(f"❌ Failed to generate frontmatter: {e}")
            raise ValueError(f"Frontmatter generation failed for {material_name}: {e}")
    
    def generate_batch(
        self,
        materials_data: Dict,
        material_names: Optional[list] = None
    ) -> Dict[str, Dict]:
        """
        Generate frontmatter for multiple materials
        
        Args:
            materials_data: Complete materials data from Materials.yaml
            material_names: List of material names (None = all materials)
            
        Returns:
            Dictionary mapping material_name -> frontmatter_dict
        """
        if material_names is None:
            material_names = list(materials_data['materials'].keys())
        
        self.logger.info(f"🚀 Batch generating {len(material_names)} materials")
        
        results = {}
        errors = []
        
        for material_name in material_names:
            try:
                material_data = materials_data['materials'][material_name]
                frontmatter = self.generate(material_name, material_data)
                results[material_name] = frontmatter
                
            except Exception as e:
                error_msg = f"{material_name}: {e}"
                errors.append(error_msg)
                self.logger.error(f"❌ {error_msg}")
        
        self.logger.info(
            f"✅ Batch complete: {len(results)} successful, {len(errors)} failed"
        )
        
        if errors:
            self.logger.warning(f"Errors: {errors}")
        
        return results
