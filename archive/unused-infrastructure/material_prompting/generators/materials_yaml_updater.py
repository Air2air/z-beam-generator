#!/usr/bin/env python3
"""
Materials.yaml Update Generator

Intelligent system for updating Materials.yaml with enhanced material properties and machine settings
using the material prompting system for category-aware customization and validation.

This generator provides:
- Automated gap detection in Materials.yaml
- AI-powered property research and generation
- Category-aware validation and enhancement
- Machine settings optimization
- Backup and rollback capabilities
- Incremental update processing
"""

import logging
import yaml
from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)


@dataclass
class MaterialUpdate:
    """Represents an update operation for a single material"""
    material_name: str
    current_data: Dict[str, Any]
    enhanced_properties: Dict[str, Any]
    optimized_settings: Dict[str, Any]
    validation_results: List[str]
    confidence_score: float
    update_timestamp: str


@dataclass
class UpdateResult:
    """Result of Materials.yaml update operation"""
    success: bool
    materials_updated: int
    properties_added: int
    settings_optimized: int
    validation_errors: List[str]
    backup_path: Optional[str]
    update_summary: List[str]


class MaterialsYamlUpdater:
    """
    Materials Research and Population System
    
    KEY PURPOSE: Research and populate Materials.yaml with comprehensive,
    scientifically accurate material data through AI-powered analysis.
    
    MISSION: Ensure every value for each material is fully analyzed, 
    checked and highly accurate.
    
    Research Features:
    - Comprehensive materials database gap analysis
    - AI-powered material property research and validation with multi-source verification
    - Statistical analysis and scientific cross-validation of all property values
    - Scientific literature-informed data population with accuracy classification
    - Category-aware material science validation with confidence scoring
    - Machine settings research based on material characteristics with quality metrics
    - Safe backup and recovery
    """
    
    def __init__(self, materials_yaml_path: str = "data/Materials.yaml"):
        """
        Initialize Materials.yaml updater
        
        Args:
            materials_yaml_path: Path to Materials.yaml file
        """
        self.materials_yaml_path = Path(materials_yaml_path)
        self.backup_dir = Path("backups/materials_yaml_updates")
        
        # Initialize subsystems
        self.property_enhancer = None
        self.settings_optimizer = None
        self.material_generator = None
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Materials.yaml updater initialized for {materials_yaml_path}")
    
    def _initialize_subsystems(self):
        """Lazy initialization of subsystems"""
        try:
            if self.property_enhancer is None:
                from ..properties.enhancer import MaterialPropertiesEnhancer
                self.property_enhancer = MaterialPropertiesEnhancer()
            
            if self.settings_optimizer is None:
                from ..machine_settings.optimizer import MaterialMachineSettingsEnhancer
                self.settings_optimizer = MaterialMachineSettingsEnhancer()
            
            if self.material_generator is None:
                from ..core.material_aware_generator import MaterialAwarePromptGenerator
                self.material_generator = MaterialAwarePromptGenerator()
                
        except ImportError as e:
            logger.error(f"Failed to initialize subsystems: {e}")
            raise
    
    def analyze_materials_gaps(self) -> Dict[str, List[str]]:
        """
        Analyze Materials.yaml for missing properties and optimization opportunities
        
        Returns:
            Dictionary mapping material names to lists of missing/incomplete data
        """
        
        if not self.materials_yaml_path.exists():
            logger.error(f"Materials file not found: {self.materials_yaml_path}")
            return {}
        
        try:
            with open(self.materials_yaml_path, 'r') as f:
                materials_data = yaml.safe_load(f)
            
            gaps = {}
            
            for material_name, material_data in materials_data.items():
                if not isinstance(material_data, dict):
                    continue
                
                material_gaps = []
                
                # Check for missing category
                if 'category' not in material_data:
                    material_gaps.append('missing_category')
                
                # Check for missing properties section
                if 'properties' not in material_data:
                    material_gaps.append('missing_properties_section')
                else:
                    properties = material_data['properties']
                    
                    # Check for critical properties based on category
                    category = material_data.get('category', 'unknown')
                    critical_props = self._get_critical_properties_for_category(category)
                    
                    for prop in critical_props:
                        if prop not in properties:
                            material_gaps.append(f'missing_property_{prop}')
                        else:
                            # Check if property has sufficient data
                            prop_data = properties[prop]
                            if isinstance(prop_data, dict):
                                if 'value' not in prop_data or not prop_data['value']:
                                    material_gaps.append(f'incomplete_property_{prop}')
                            elif not prop_data:
                                material_gaps.append(f'empty_property_{prop}')
                
                # Check for missing machine settings
                if 'machineSettings' not in material_data:
                    material_gaps.append('missing_machine_settings')
                else:
                    settings = material_data['machineSettings']
                    required_settings = ['powerRange', 'wavelength', 'processingSpeed']
                    
                    for setting in required_settings:
                        if setting not in settings:
                            material_gaps.append(f'missing_setting_{setting}')
                
                # Check for missing safety information
                if 'safety' not in material_data:
                    material_gaps.append('missing_safety_info')
                
                if material_gaps:
                    gaps[material_name] = material_gaps
            
            logger.info(f"Gap analysis complete: {len(gaps)} materials need updates")
            return gaps
            
        except Exception as e:
            logger.error(f"Error analyzing materials gaps: {e}")
            return {}
    
    def _get_critical_properties_for_category(self, category: str) -> List[str]:
        """Get list of critical properties for material category"""
        
        critical_properties = {
            'metal': ['density', 'thermalConductivity', 'meltingPoint', 'tensileStrength'],
            'ceramic': ['density', 'thermalConductivity', 'meltingPoint', 'hardness'],
            'wood': ['density', 'thermalConductivity', 'decompositionTemperature', 'hardness'],
            'plastic': ['density', 'thermalConductivity', 'meltingPoint', 'tensileStrength'],
            'composite': ['density', 'thermalConductivity', 'tensileStrength', 'youngsModulus']
        }
        
        return critical_properties.get(category, ['density', 'thermalConductivity'])
    
    def update_materials_yaml(
        self,
        target_materials: Optional[List[str]] = None,
        backup: bool = True,
        validate_only: bool = False
    ) -> UpdateResult:
        """
        Update Materials.yaml with enhanced properties and optimized settings
        
        Args:
            target_materials: Specific materials to update (None = all materials)
            backup: Whether to create backup before updating
            validate_only: Only validate without making changes
            
        Returns:
            UpdateResult with operation details
        """
        
        try:
            # Initialize subsystems
            self._initialize_subsystems()
            
            # Load current materials data
            if not self.materials_yaml_path.exists():
                return UpdateResult(
                    success=False,
                    materials_updated=0,
                    properties_added=0,
                    settings_optimized=0,
                    validation_errors=[f"Materials file not found: {self.materials_yaml_path}"],
                    backup_path=None,
                    update_summary=[]
                )
            
            with open(self.materials_yaml_path, 'r') as f:
                materials_data = yaml.safe_load(f)
            
            # Create backup if requested
            backup_path = None
            if backup and not validate_only:
                backup_path = self._create_backup()
                logger.info(f"Backup created: {backup_path}")
            
            # Process materials
            materials_to_process = target_materials or list(materials_data.keys())
            updates = []
            validation_errors = []
            
            for material_name in materials_to_process:
                if material_name not in materials_data:
                    validation_errors.append(f"Material not found: {material_name}")
                    continue
                
                try:
                    update = self._process_single_material(
                        material_name, 
                        materials_data[material_name]
                    )
                    updates.append(update)
                    
                except Exception as e:
                    validation_errors.append(f"Error processing {material_name}: {e}")
                    logger.error(f"Error processing {material_name}: {e}")
            
            # Apply updates to data
            materials_updated = 0
            properties_added = 0
            settings_optimized = 0
            
            if not validate_only:
                for update in updates:
                    if update.confidence_score >= 0.7:  # Only apply high-confidence updates
                        
                        # Update properties
                        if 'properties' not in materials_data[update.material_name]:
                            materials_data[update.material_name]['properties'] = {}
                        
                        for prop_name, prop_data in update.enhanced_properties.items():
                            materials_data[update.material_name]['properties'][prop_name] = prop_data
                            properties_added += 1
                        
                        # Update machine settings
                        if update.optimized_settings:
                            materials_data[update.material_name]['machineSettings'] = update.optimized_settings
                            settings_optimized += 1
                        
                        materials_updated += 1
                
                # Write updated data back to file
                if materials_updated > 0:
                    with open(self.materials_yaml_path, 'w') as f:
                        yaml.safe_dump(materials_data, f, default_flow_style=False, sort_keys=True)
                    
                    logger.info(f"Updated Materials.yaml: {materials_updated} materials, {properties_added} properties")
            
            # Generate summary
            update_summary = []
            for update in updates:
                summary_line = f"{update.material_name}: +{len(update.enhanced_properties)} properties"
                if update.optimized_settings:
                    summary_line += ", optimized settings"
                summary_line += f" (confidence: {update.confidence_score:.1%})"
                update_summary.append(summary_line)
            
            return UpdateResult(
                success=len(validation_errors) == 0,
                materials_updated=materials_updated,
                properties_added=properties_added,
                settings_optimized=settings_optimized,
                validation_errors=validation_errors,
                backup_path=str(backup_path) if backup_path else None,
                update_summary=update_summary
            )
            
        except Exception as e:
            logger.error(f"Error updating Materials.yaml: {e}")
            return UpdateResult(
                success=False,
                materials_updated=0,
                properties_added=0,
                settings_optimized=0,
                validation_errors=[f"Update failed: {e}"],
                backup_path=None,
                update_summary=[]
            )
    
    def _process_single_material(self, material_name: str, material_data: Dict[str, Any]) -> MaterialUpdate:
        """Process a single material for enhancement"""
        
        category = material_data.get('category', 'unknown')
        current_properties = material_data.get('properties', {})
        
        # Enhance properties
        property_result = self.property_enhancer.enhance_material_properties(
            material_name=material_name,
            material_category=category,
            existing_properties=current_properties,
            material_data=material_data
        )
        
        # Optimize machine settings
        optimized_settings = {}
        if category != 'unknown':
            try:
                settings_result = self.settings_optimizer.optimize_machine_settings(
                    material_name=material_name,
                    material_category=category,
                    material_properties=current_properties
                )
                
                if settings_result.success and settings_result.settings:
                    settings = settings_result.settings
                    optimized_settings = {
                        'powerRange': f"{settings.power_range[0]}-{settings.power_range[1]} W",
                        'wavelength': f"{settings.wavelength} nm",
                        'pulseDuration': settings.pulse_duration,
                        'repetitionRate': f"{settings.repetition_rate[0]}-{settings.repetition_rate[1]} Hz",
                        'fluenceThreshold': f"{settings.fluence_threshold[0]:.1f}-{settings.fluence_threshold[1]:.1f} J/cm²",
                        'spotSize': f"{settings.spot_size[0]}-{settings.spot_size[1]} μm",
                        'processingSpeed': f"{settings.processing_speed[0]}-{settings.processing_speed[1]} mm/min",
                        'safetyLevel': settings.safety_level,
                        'qualityPrediction': settings.quality_prediction
                    }
                    
            except Exception as e:
                logger.warning(f"Could not optimize settings for {material_name}: {e}")
        
        # Convert enhanced properties to YAML format
        enhanced_props = {}
        for prop_name, prop_obj in property_result.enhanced_properties.items():
            enhanced_props[prop_name] = {
                'value': prop_obj.value,
                'unit': prop_obj.unit,
                'description': prop_obj.description,
                'priority': prop_obj.priority.value
            }
            
            if prop_obj.min_range is not None and prop_obj.max_range is not None:
                enhanced_props[prop_name]['range'] = f"{prop_obj.min_range}-{prop_obj.max_range}"
            
            if prop_obj.source:
                enhanced_props[prop_name]['source'] = prop_obj.source
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(property_result, len(current_properties))
        
        return MaterialUpdate(
            material_name=material_name,
            current_data=material_data,
            enhanced_properties=enhanced_props,
            optimized_settings=optimized_settings,
            validation_results=property_result.validation_errors,
            confidence_score=confidence,
            update_timestamp=datetime.now().isoformat()
        )
    
    def _calculate_confidence_score(self, property_result, existing_prop_count: int) -> float:
        """Calculate confidence score for material update"""
        
        base_confidence = 0.8 if property_result.success else 0.3
        
        # Reduce confidence if many validation errors
        error_penalty = min(len(property_result.validation_errors) * 0.1, 0.4)
        
        # Increase confidence if we have existing data to build on
        existing_data_bonus = min(existing_prop_count * 0.05, 0.2)
        
        confidence = base_confidence - error_penalty + existing_data_bonus
        
        return max(0.0, min(1.0, confidence))
    
    def _create_backup(self) -> Path:
        """Create backup of current Materials.yaml"""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"materials_backup_{timestamp}.yaml"
        
        shutil.copy2(self.materials_yaml_path, backup_path)
        
        return backup_path
    
    def restore_from_backup(self, backup_path: str) -> bool:
        """Restore Materials.yaml from backup"""
        
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            shutil.copy2(backup_file, self.materials_yaml_path)
            logger.info(f"Restored Materials.yaml from {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False
    
    def get_update_preview(self, target_materials: Optional[List[str]] = None) -> List[str]:
        """Get preview of what would be updated without making changes"""
        
        result = self.update_materials_yaml(
            target_materials=target_materials,
            backup=False,
            validate_only=True
        )
        
        preview = []
        preview.append(f"Materials to update: {len(result.update_summary)}")
        preview.extend(result.update_summary)
        
        if result.validation_errors:
            preview.append("\nValidation errors:")
            preview.extend(result.validation_errors)
        
        return preview


if __name__ == "__main__":
    # Test Materials.yaml updater
    updater = MaterialsYamlUpdater()
    
    # Analyze gaps
    print("=== MATERIALS.YAML GAP ANALYSIS ===")
    gaps = updater.analyze_materials_gaps()
    for material, gap_list in list(gaps.items())[:3]:  # Show first 3
        print(f"{material}: {len(gap_list)} gaps")
        for gap in gap_list[:3]:  # Show first 3 gaps
            print(f"  - {gap}")
    
    # Preview updates
    print("\n=== UPDATE PREVIEW ===")
    preview = updater.get_update_preview(target_materials=['Aluminum', 'Steel'])
    for line in preview[:10]:  # Show first 10 lines
        print(line)
    
    print(f"\nTotal materials with gaps: {len(gaps)}")
    print("Ready for intelligent Materials.yaml updates!")