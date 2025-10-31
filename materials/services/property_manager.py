#!/usr/bin/env python3
"""
Property Manager - Unified Property Lifecycle Management

Consolidates property discovery, research, categorization, and validation into single service.
Replaces PropertyDiscoveryService and PropertyResearchService with unified interface.

Responsibilities:
- Property discovery (gap identification)
- AI research coordination
- Automatic categorization (quantitative/qualitative)
- Validation and normalization
- Machine settings research
- Materials.yaml persistence (AI research writeback)

Follows fail-fast principles:
- No mocks or default values in production
- Explicit error handling with PropertyDiscoveryError
- Validates all inputs immediately

Author: Refactoring - October 17, 2025
Updated: October 20, 2025 - Added Materials.yaml writeback
"""

import logging
import shutil
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Tuple, Callable
from dataclasses import dataclass

from materials.research.property_value_researcher import PropertyValueResearcher
from shared.validation.errors import PropertyDiscoveryError, ConfigurationError
from shared.validation.helpers.unit_converter import UnitConverter

# Qualitative property definitions
from components.frontmatter.qualitative_properties import (
    QUALITATIVE_PROPERTIES,
    is_qualitative_property,
    get_property_definition,
    validate_qualitative_value,
    MATERIAL_CHARACTERISTICS_CATEGORIES
)

logger = logging.getLogger(__name__)


@dataclass
class PropertyResearchResult:
    """Result of complete property research pipeline."""
    quantitative_properties: Dict[str, Dict]
    qualitative_characteristics: Dict[str, Dict]
    machine_settings: Optional[Dict[str, Dict]] = None
    research_metadata: Optional[Dict] = None


class PropertyManager:
    """
    Unified property management service.
    
    Handles complete property lifecycle:
    Discovery → Research → Categorization → Validation → Normalization
    
    Replaces:
    - PropertyDiscoveryService (discovery logic)
    - PropertyResearchService (research coordination)
    - Scattered validation logic
    """
    
    # Essential properties by category
    # NOTE: thermalDestruction is the unified property (replaces meltingPoint, thermalDegradationPoint, etc.)
    # PropertyValueResearcher handles alias resolution automatically
    ESSENTIAL_PROPERTIES = {
        'universal': {'thermalConductivity', 'density', 'hardness', 'laserReflectivity'},  # Changed reflectivity → laserReflectivity
        'metal': {'thermalConductivity', 'density', 'hardness'},  # Removed thermalDestruction (structured property)
        'ceramic': {'thermalConductivity', 'density', 'hardness'},  # Removed thermalDestruction (structured property)
        'plastic': {'thermalConductivity', 'density'},  # Removed thermalDestruction (structured property)
        'composite': {'thermalConductivity', 'density'},  # Removed thermalDestruction (structured property)
        'wood': {'density'},  # Removed thermalDestruction (structured property)
        'stone': {'density', 'hardness'},  # Removed thermalDestruction (structured property)
        'glass': {'thermalConductivity', 'density'},  # Removed thermalDestruction (structured property)
        'semiconductor': {'thermalConductivity', 'density'},  # Removed thermalDestruction (structured property)
        'masonry': {'density', 'hardness'},  # Removed thermalDestruction (structured property)
        'rare-earth': {'thermalConductivity', 'density', 'hardness', 'laserReflectivity'}  # Removed thermalDestruction (structured property)
    }
    
    # Confidence thresholds
    YAML_CONFIDENCE_THRESHOLD = 0.85  # 85%
    
    def __init__(
        self,
        property_researcher: PropertyValueResearcher,
        get_category_ranges_func: Optional[Callable] = None,
        enhance_descriptions_func: Optional[Callable] = None,
        categories_data: Optional[Dict] = None
    ):
        """
        Initialize property manager.
        
        Args:
            property_researcher: PropertyValueResearcher instance for AI research
            get_category_ranges_func: Function to get category ranges for properties
            enhance_descriptions_func: Function to enhance with standardized descriptions
            categories_data: Optional Categories.yaml data for enhanced discovery
            
        Raises:
            PropertyDiscoveryError: If property_researcher is None
        """
        # PropertyValueResearcher can be None in data-only mode (100% complete YAML data)
        if not property_researcher:
            logger.info("PropertyValueResearcher not provided - operating in data-only mode")
        
        self.property_researcher = property_researcher
        self.get_category_ranges = get_category_ranges_func
        self.enhance_descriptions = enhance_descriptions_func
        self.categories_data = categories_data or {}
        self.logger = logger
        self.materials_file = Path("materials/data/Materials.yaml")
    
    # ===== PERSISTENCE METHODS =====
    
    def persist_researched_properties(
        self,
        material_name: str,
        researched_properties: Dict[str, Dict]
    ) -> bool:
        """
        Persist AI-researched properties back to Materials.yaml.
        
        This ensures research results accumulate in the database rather than being
        regenerated on every frontmatter generation.
        
        Args:
            material_name: Name of the material
            researched_properties: Dict of property_name -> property_data
            
        Returns:
            True if successful, False otherwise
            
        Side Effects:
            - Creates timestamped backup of Materials.yaml
            - Updates Materials.yaml with new property values
        """
        if not researched_properties:
            self.logger.debug(f"No researched properties to persist for {material_name}")
            return True
        
        try:
            # Create backup before modification
            if self.materials_file.exists():
                backup_file = self.materials_file.with_suffix(
                    f'.backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.yaml'
                )
                shutil.copy2(self.materials_file, backup_file)
                self.logger.info(f"📦 Backup created: {backup_file.name}")
            
            # Load Materials.yaml
            with open(self.materials_file) as f:
                materials_data = yaml.safe_load(f)
            
            # Find and update material
            if material_name not in materials_data.get('materials', {}):
                self.logger.warning(f"Material '{material_name}' not found in Materials.yaml")
                return False
            
            material_entry = materials_data['materials'][material_name]
            
            # Ensure properties dict exists
            if 'properties' not in material_entry:
                material_entry['properties'] = {}
            
            # Update with researched properties
            updates_count = 0
            for prop_name, prop_data in researched_properties.items():
                # Only persist if not already in YAML or has higher confidence
                existing = material_entry['properties'].get(prop_name)
                
                if existing is None:
                    # New property - add it
                    material_entry['properties'][prop_name] = prop_data
                    updates_count += 1
                    self.logger.debug(f"  ✅ Added {prop_name}: {prop_data.get('value')} {prop_data.get('unit')}")
                elif existing.get('source') != 'ai_research':
                    # Existing property but not from AI - upgrade it
                    material_entry['properties'][prop_name] = prop_data
                    updates_count += 1
                    self.logger.debug(f"  🔄 Updated {prop_name}: {prop_data.get('value')} {prop_data.get('unit')}")
                else:
                    self.logger.debug(f"  ⏭️  Skipped {prop_name} (already has AI research)")
            
            if updates_count > 0:
                # Write updated data back
                with open(self.materials_file, 'w') as f:
                    yaml.dump(materials_data, f, default_flow_style=False, indent=2, sort_keys=False)
                
                self.logger.info(f"💾 Persisted {updates_count} properties to Materials.yaml for {material_name}")
                
                # POST-PROCESSING: Run comprehensive audit after material update
                self._run_post_update_audit(material_name, updates_count)
                
                return True
            else:
                self.logger.debug(f"No new properties to persist for {material_name}")
                return True
                
        except Exception as e:
            self.logger.error(f"❌ Failed to persist properties for {material_name}: {e}")
            return False
    
    # ===== MAIN INTERFACE =====
    
    def discover_and_research_properties(
        self,
        material_name: str,
        material_category: str,
        existing_properties: Dict
    ) -> PropertyResearchResult:
        """
        Complete property discovery and research pipeline.
        
        Pipeline:
        1. Discover which properties need research (gap analysis)
        2. Research missing properties via AI
        3. Categorize properties (quantitative vs qualitative)
        4. Validate and normalize all properties
        5. Return organized result
        
        Args:
            material_name: Name of the material
            material_category: Category (metal, plastic, etc.)
            existing_properties: Properties already present (from YAML)
            
        Returns:
            PropertyResearchResult with categorized properties
            
        Raises:
            PropertyDiscoveryError: If pipeline fails
        """
        try:
            # Step 1: Discovery - identify gaps
            properties_to_research, skip_reasons = self._discover_gaps(
                material_name,
                material_category,
                existing_properties
            )
            
            # Step 2: Research - AI discovery for missing properties
            if properties_to_research:
                self.logger.info(f"🔍 Researching {len(properties_to_research)} missing properties")
                discovered = self.property_researcher.discover_all_material_properties(
                    material_name,
                    material_category
                )
            else:
                self.logger.info("✅ All essential properties present in YAML")
                discovered = {}
            
            # Step 3: Process discovered properties
            quantitative, qualitative = self._process_discovered_properties(
                material_name,
                material_category,
                discovered,
                existing_properties
            )
            
            # Step 3.5: Persist researched properties back to Materials.yaml
            if quantitative:
                self.logger.info(f"💾 Persisting {len(quantitative)} researched properties to Materials.yaml...")
                self.persist_researched_properties(material_name, quantitative)
            
            # Step 4: Validation
            self._validate_essential_coverage(
                material_name,
                material_category,
                {**existing_properties, **quantitative},
                qualitative
            )
            
            # Step 5: Build result
            metadata = {
                'yaml_property_count': len(existing_properties),
                'researched_property_count': len(quantitative),
                'qualitative_count': len(qualitative),
                'skip_reasons': skip_reasons
            }
            
            return PropertyResearchResult(
                quantitative_properties=quantitative,
                qualitative_characteristics=qualitative,
                research_metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Property discovery and research failed for {material_name}: {e}")
            raise PropertyDiscoveryError(
                f"Failed to discover and research properties for {material_name}: {e}"
            )
    
    def research_machine_settings(
        self,
        material_name: str
    ) -> Dict[str, Dict]:
        """
        Research machine settings using AI discovery.
        
        Args:
            material_name: Name of the material
            
        Returns:
            Dict of researched machine settings with complete data structure
            
        Raises:
            PropertyDiscoveryError: If research fails or no settings found
        """
        try:
            # Use comprehensive AI discovery
            discovered_settings = self.property_researcher.discover_all_machine_settings(material_name)
            
            self.logger.info(f"AI discovered {len(discovered_settings)} machine settings for {material_name}")
            
            if not discovered_settings:
                raise PropertyDiscoveryError(
                    f"No machine settings discovered for {material_name}. "
                    "Comprehensive discovery required per fail-fast principles."
                )
            
            # Process and enhance discovered settings
            researched = {}
            for setting_name, setting_data in discovered_settings.items():
                # Build machine setting structure
                machine_setting_data = {
                    'value': setting_data['value'],
                    'unit': setting_data['unit'],
                    'confidence': setting_data['confidence'],
                    'description': setting_data['description'],
                    'min': setting_data.get('min'),
                    'max': setting_data.get('max')
                }
                
                # Enhance with standardized descriptions if available
                if self.enhance_descriptions:
                    machine_setting_data = self.enhance_descriptions(
                        machine_setting_data, setting_name, 'machineSettings'
                    )
                
                researched[setting_name] = machine_setting_data
                self.logger.info(
                    f"🤖 Researched {setting_name}: {setting_data['value']} {setting_data['unit']} "
                    f"(confidence: {setting_data['confidence']}%)"
                )
            
            return researched
            
        except PropertyDiscoveryError:
            raise
        except Exception as e:
            self.logger.error(f"Machine settings research failed for {material_name}: {e}")
            raise PropertyDiscoveryError(
                f"Failed to research machine settings for {material_name}: {e}"
            )
    
    # ===== DISCOVERY METHODS =====
    
    def _discover_gaps(
        self,
        material_name: str,
        material_category: str,
        yaml_properties: Dict
    ) -> Tuple[Set[str], Dict[str, str]]:
        """
        Identify which properties need research (gap analysis).
        
        Args:
            material_name: Material name
            material_category: Material category
            yaml_properties: Existing properties from YAML
            
        Returns:
            Tuple of (properties_to_research, skip_reasons)
        """
        if not material_name:
            raise PropertyDiscoveryError("Material name is required")
        if not material_category:
            raise PropertyDiscoveryError(f"Material category is required for {material_name}")
        
        # Get essential properties for category
        essential = self._get_essential_properties(material_category)
        self.logger.info(f"📋 Category '{material_category}' requires {len(essential)} essential properties")
        
        # Identify high-confidence YAML properties
        yaml_props = self._filter_high_confidence_yaml(yaml_properties)
        self.logger.info(f"✅ Found {len(yaml_props)} high-confidence YAML properties")
        
        # Calculate gaps
        to_research = essential - set(yaml_props.keys())
        
        # Track skip reasons
        skip_reasons = {}
        for prop in essential:
            if prop in yaml_props:
                confidence = yaml_props[prop].get('confidence', 0)
                skip_reasons[prop] = f"High-confidence YAML data (confidence: {confidence})"
        
        self.logger.info(f"🔍 Need to research {len(to_research)} properties")
        
        return to_research, skip_reasons
    
    def _get_essential_properties(self, material_category: str) -> Set[str]:
        """Get essential properties for a material category."""
        category_lower = material_category.lower()
        
        # Start with universal essentials
        essentials = self.ESSENTIAL_PROPERTIES['universal'].copy()
        
        # Add category-specific essentials
        if category_lower in self.ESSENTIAL_PROPERTIES:
            essentials.update(self.ESSENTIAL_PROPERTIES[category_lower])
        else:
            self.logger.warning(
                f"Unknown category '{material_category}' - using universal essentials only"
            )
        
        return essentials
    
    def _filter_high_confidence_yaml(self, yaml_properties: Dict) -> Dict:
        """Filter to only high-confidence YAML properties."""
        high_confidence = {}
        
        for prop_name, prop_data in yaml_properties.items():
            if not isinstance(prop_data, dict):
                continue
            
            confidence = prop_data.get('confidence', 0)
            
            # Normalize confidence to 0-1 scale
            if confidence > 1:
                confidence = confidence / 100.0
            
            if confidence >= self.YAML_CONFIDENCE_THRESHOLD:
                high_confidence[prop_name] = prop_data
        
        return high_confidence
    
    # ===== PROCESSING METHODS =====
    
    def _process_discovered_properties(
        self,
        material_name: str,
        material_category: str,
        discovered: Dict,
        existing_properties: Dict
    ) -> Tuple[Dict[str, Dict], Dict[str, Dict]]:
        """
        Process discovered properties into quantitative and qualitative.
        
        Returns:
            Tuple of (quantitative_properties, qualitative_characteristics)
        """
        from materials.research.property_value_researcher import PropertyValueResearcher
        
        # Start with existing YAML properties - but normalize their units first
        quantitative = {}
        for prop_name, prop_data in existing_properties.items():
            if isinstance(prop_data, dict) and 'value' in prop_data and 'unit' in prop_data:
                # Normalize units for existing YAML properties
                normalized_prop = dict(prop_data)  # Copy
                try:
                    normalized_value, normalized_unit = UnitConverter.normalize(
                        prop_name, prop_data['value'], prop_data['unit']
                    )
                    if normalized_value is not None and normalized_unit is not None:
                        normalized_prop['value'] = normalized_value
                        normalized_prop['unit'] = normalized_unit
                        self.logger.debug(
                            f"Unit normalized (YAML): {prop_name}: {prop_data['value']} {prop_data['unit']} "
                            f"→ {normalized_value} {normalized_unit}"
                        )
                except Exception as e:
                    # Keep original if normalization fails
                    self.logger.debug(f"Unit normalization not applicable for YAML {prop_name}: {e}")
                
                quantitative[prop_name] = normalized_prop
            else:
                # Non-property data, keep as-is
                quantitative[prop_name] = prop_data
        
        qualitative = {}
        
        for prop_name, prop_data in discovered.items():
            # Resolve property aliases (e.g., meltingPoint → thermalDestruction)
            canonical_prop_name = PropertyValueResearcher.resolve_property_alias(prop_name)
            
            if canonical_prop_name != prop_name:
                self.logger.info(
                    f"🔄 Property alias resolved: '{prop_name}' → '{canonical_prop_name}' for {material_name}"
                )
            
            # Skip if already in YAML (YAML takes precedence) - check both names
            if prop_name in existing_properties or canonical_prop_name in existing_properties:
                continue
            
            # Skip redundant thermalDestructionPoint
            if canonical_prop_name == 'thermalDestruction' and 'thermalDestruction' in existing_properties:
                self.logger.debug(f"Skipping redundant {prop_name} (already have thermalDestruction)")
                continue
            
            # Check if qualitative (defined in taxonomy)
            if is_qualitative_property(canonical_prop_name):
                self.logger.debug(f"Property '{canonical_prop_name}' is qualitative - routing to characteristics")
                qualitative[canonical_prop_name] = self._build_qualitative_property(canonical_prop_name, prop_data)
                continue
            
            # Check if value is qualitative (backup check)
            if self._is_qualitative_value(prop_data.get('value')):
                self.logger.warning(
                    f"Property '{canonical_prop_name}' has qualitative value '{prop_data['value']}' "
                    f"but not in QUALITATIVE_PROPERTIES. Consider adding to definitions."
                )
                continue
            
            # Process as quantitative - but skip if no category ranges available
            # Use canonical name for range lookup
            try:
                quantitative[canonical_prop_name] = self._build_quantitative_property(
                    canonical_prop_name,
                    prop_data,
                    material_category,
                    material_name
                )
            except ValueError as e:
                if "missing category ranges" in str(e):
                    self.logger.warning(
                        f"Skipping discovered property '{prop_name}' for {material_category} "
                        f"- no category ranges defined. Property not applicable to this category."
                    )
                else:
                    raise
        
        return quantitative, qualitative
    
    def _build_quantitative_property(
        self,
        prop_name: str,
        prop_data: Dict,
        material_category: str,
        material_name: str
    ) -> Dict:
        """Build quantitative property structure with ranges and normalized units."""
        # Apply unit normalization before building property structure
        value = prop_data['value']
        unit = prop_data['unit']
        
        try:
            normalized_value, normalized_unit = UnitConverter.normalize(prop_name, value, unit)
            if normalized_value is not None and normalized_unit is not None:
                self.logger.debug(
                    f"Unit normalized for {prop_name}: {value} {unit} → {normalized_value} {normalized_unit}"
                )
                value = normalized_value
                unit = normalized_unit
        except Exception as e:
            # If normalization fails, keep original (backward compatible)
            self.logger.debug(f"Unit normalization not applicable for {prop_name}: {e}")
        
        property_data = {
            'value': value,
            'unit': unit,
            'confidence': prop_data['confidence'],
            'description': prop_data['description'],
            'min': None,
            'max': None
        }
        
        # Apply category ranges (REQUIRED for quantitative properties - Zero Null Policy)
        if self.get_category_ranges:
            category_ranges = self.get_category_ranges(material_category, prop_name)
            
            if category_ranges and category_ranges.get('min') is not None:
                property_data['min'] = category_ranges['min']
                property_data['max'] = category_ranges['max']
            else:
                # ❌ FAIL-FAST: Quantitative properties MUST have ranges (Zero Null Policy)
                raise ValueError(
                    f"Quantitative property '{prop_name}' missing category ranges for {material_category}. "
                    f"Zero Null Policy violation - all numerical properties must have non-null min/max ranges."
                )
        
        # Enhance with standardized descriptions
        if self.enhance_descriptions:
            property_data = self.enhance_descriptions(
                property_data, prop_name, 'materialProperties'
            )
        
        self.logger.info(
            f"🤖 Quantitative: {prop_name} = {prop_data['value']} {prop_data['unit']} "
            f"(confidence: {prop_data['confidence']}%)"
        )
        
        return property_data
    
    def _build_qualitative_property(self, prop_name: str, prop_data: Dict) -> Dict:
        """Build qualitative property structure with allowedValues."""
        prop_def = get_property_definition(prop_name)
        
        property_data = {
            'value': prop_data['value'],
            'unit': prop_data.get('unit', prop_def.unit if prop_def else 'type'),
            'confidence': prop_data['confidence'],
            'description': prop_data['description']
            # ✅ NO min/max fields at all - complete omission per Zero Null Policy
        }
        
        # Add allowedValues if defined
        if prop_def:
            property_data['allowedValues'] = prop_def.allowed_values
            
            # Validate value against allowedValues
            if not validate_qualitative_value(prop_name, prop_data['value']):
                self.logger.warning(
                    f"Qualitative property '{prop_name}' value '{prop_data['value']}' "
                    f"not in allowedValues: {prop_def.allowed_values}"
                )
        
        self.logger.info(
            f"🎨 Qualitative: {prop_name} = {prop_data['value']} "
            f"(confidence: {prop_data['confidence']}%)"
        )
        
        return property_data
    
    # ===== VALIDATION METHODS =====
    
    def _validate_essential_coverage(
        self,
        material_name: str,
        material_category: str,
        quantitative_properties: Dict,
        qualitative_characteristics: Dict
    ) -> None:
        """
        Validate that all essential properties are present.
        
        Raises:
            PropertyDiscoveryError: If essential properties missing
        """
        essentials = self._get_essential_properties(material_category)
        all_props = set(quantitative_properties.keys()) | set(qualitative_characteristics.keys())
        missing = essentials - all_props
        
        if missing:
            raise PropertyDiscoveryError(
                f"Missing essential properties for {material_name} ({material_category}): "
                f"{', '.join(sorted(missing))}"
            )
        
        self.logger.info(f"✅ All {len(essentials)} essential properties present for {material_name}")
    
    # ===== UTILITY METHODS =====
    
    @staticmethod
    def _is_qualitative_value(value) -> bool:
        """Check if a value appears to be qualitative (non-numeric string)."""
        if not isinstance(value, str):
            return False
        
        # Try to convert to float - if it works, it's numeric
        try:
            float(value.replace(',', ''))
            return False
        except (ValueError, AttributeError):
            return True
    
    @staticmethod
    def _is_numeric_string(value: str) -> bool:
        """Check if string represents a number."""
        try:
            float(value.replace(',', ''))
            return True
        except (ValueError, AttributeError):
            return False
    
    # ===== AUDITING METHODS =====
    
    def _run_post_update_audit(self, material_name: str, updates_count: int) -> None:
        """
        Run comprehensive audit after material update.
        
        This method ensures the updated material entry complies with all
        system requirements per the comprehensive auditing framework.
        
        Args:
            material_name: Material that was updated
            updates_count: Number of properties that were updated
        """
        try:
            # Import audit functionality (lazy import to avoid circular dependencies)
            from .material_auditor import create_audit_hook
            
            # Create audit hook and run audit
            audit_hook = create_audit_hook()
            audit_result = audit_hook(material_name, auto_fix=True)
            
            # Log audit results based on severity
            if audit_result.overall_status == "PASS":
                self.logger.info(f"✅ Post-update audit PASSED for {material_name} ({updates_count} properties updated)")
            elif audit_result.overall_status == "WARNING":
                self.logger.warning(f"⚠️  Post-update audit has warnings for {material_name}: {audit_result.high_issues} issues")
                # Log top issues
                for issue in audit_result.issues[:3]:  # Show first 3 issues
                    if issue.severity.value in ['HIGH', 'MEDIUM']:
                        self.logger.warning(f"  • {issue.description}")
            else:
                self.logger.error(f"❌ Post-update audit FAILED for {material_name}: {audit_result.critical_issues} critical issues")
                # Log critical issues
                for issue in audit_result.issues:
                    if issue.severity.value == 'CRITICAL':
                        self.logger.error(f"  • CRITICAL: {issue.description}")
                        if issue.remediation:
                            self.logger.error(f"    Fix: {issue.remediation}")
            
            # Store audit metrics for monitoring
            if hasattr(self, 'audit_metrics'):
                self.audit_metrics['total_audits'] = getattr(self.audit_metrics, 'total_audits', 0) + 1
                self.audit_metrics['total_issues'] = getattr(self.audit_metrics, 'total_issues', 0) + audit_result.total_issues
                self.audit_metrics['critical_violations'] = getattr(self.audit_metrics, 'critical_violations', 0) + audit_result.critical_issues
            
        except ImportError as e:
            self.logger.warning(f"⚠️  Audit system not available: {e}")
        except Exception as e:
            self.logger.error(f"❌ Post-update audit failed for {material_name}: {e}")
            # Don't let audit failures break the main update process
    
    def run_comprehensive_audit(
        self, 
        material_name: str, 
        generate_report: bool = False,
        auto_fix: bool = True
    ) -> Dict:
        """
        Run comprehensive audit on demand for a specific material.
        
        This provides a public interface for running detailed audits
        outside of the normal update process.
        
        Args:
            material_name: Material to audit
            generate_report: Whether to generate detailed report
            auto_fix: Whether to apply automatic fixes
            
        Returns:
            Audit result dictionary with compliance status
            
        Raises:
            PropertyDiscoveryError: If audit infrastructure fails
        """
        try:
            from .material_auditor import MaterialAuditor
            
            # Initialize auditor
            auditor = MaterialAuditor()
            
            # Run comprehensive audit
            audit_result = auditor.audit_material(
                material_name=material_name,
                auto_fix=auto_fix,
                skip_frontmatter=not generate_report
            )
            
            # Generate report if requested
            report = None
            if generate_report:
                report = auditor.generate_audit_report(audit_result)
                
                # Save report to file
                report_dir = Path("audit_reports")
                report_dir.mkdir(exist_ok=True)
                report_file = report_dir / f"{material_name}_comprehensive_audit.txt"
                
                with open(report_file, 'w') as f:
                    f.write(report)
                
                self.logger.info(f"📄 Comprehensive audit report saved: {report_file}")
            
            # Return structured result
            return {
                'material_name': material_name,
                'overall_status': audit_result.overall_status,
                'total_issues': audit_result.total_issues,
                'critical_issues': audit_result.critical_issues,
                'high_issues': audit_result.high_issues,
                'property_coverage': audit_result.property_coverage,
                'confidence_score': audit_result.confidence_score,
                'data_storage_compliance': audit_result.data_storage_compliance,
                'architecture_compliance': audit_result.architecture_compliance,
                'schema_compliance': audit_result.schema_compliance,
                'auto_fixes_applied': audit_result.auto_fixes_applied,
                'audit_duration_ms': audit_result.audit_duration_ms,
                'report_file': report_file.name if generate_report else None,
                'report_content': report if generate_report else None
            }
            
        except ImportError as e:
            self.logger.error(f"❌ Audit system not available: {e}")
            raise PropertyDiscoveryError(f"Audit infrastructure missing: {e}")
        except Exception as e:
            self.logger.error(f"❌ Comprehensive audit failed for {material_name}: {e}")
            raise PropertyDiscoveryError(f"Audit execution failed: {e}")
    
    # ===== COMPATIBILITY LAYER FOR OLD SERVICES =====
    # Methods to support migration from PropertyDiscoveryService + PropertyResearchService
    # TODO: Remove after full migration to unified discover_and_research_properties() API
    
    def discover_properties_to_research(
        self,
        material_name: str,
        material_category: str,
        yaml_properties: Dict
    ) -> Tuple[Set[str], Dict[str, str]]:
        """
        Compatibility wrapper for PropertyDiscoveryService.discover_properties_to_research()
        
        Args:
            material_name: Name of material
            material_category: Material category
            yaml_properties: Existing YAML properties
            
        Returns:
            Tuple of (properties_to_research, skip_reasons)
        """
        result = self._discover_gaps(material_name, material_category, yaml_properties)
        return result['to_research'], result['skip_reasons']
    
    def calculate_coverage(
        self,
        material_name: str,
        yaml_properties: Dict,
        category: str
    ) -> Dict:
        """
        Compatibility wrapper for PropertyDiscoveryService.calculate_coverage()
        
        Args:
            material_name: Name of material
            yaml_properties: Existing YAML properties
            category: Material category
            
        Returns:
            Coverage statistics dictionary
        """
        result = self._discover_gaps(material_name, category, yaml_properties)
        essential_props = self._get_essential_properties(category)
        
        return {
            'total_essential': len(essential_props),
            'yaml_provided': len(result['yaml_confidence_properties']),
            'needs_research': len(result['to_research']),
            'coverage_percentage': (len(result['yaml_confidence_properties']) / len(essential_props) * 100) if essential_props else 0,
            'missing_properties': list(result['to_research'])
        }
    
    def validate_property_completeness(
        self,
        category: str,
        researched_properties: Dict
    ) -> None:
        """
        Compatibility wrapper for PropertyDiscoveryService.validate_property_completeness()
        
        Args:
            category: Material category
            researched_properties: Dictionary of researched properties
            
        Raises:
            PropertyDiscoveryError: If essential properties missing
        """
        self._validate_essential_coverage(category, researched_properties)
    
    def add_category_thermal_property(
        self,
        material_name: str,
        properties: Dict,
        category: str
    ) -> bool:
        """
        Compatibility wrapper for PropertyResearchService.add_category_thermal_property()
        
        Args:
            material_name: Name of material
            properties: Properties dictionary to update
            category: Material category
            
        Returns:
            True if thermal property added
        """
        # Check if thermalDestruction already present
        if 'thermalDestruction' in properties:
            return False
        
        # Use category-specific thermal property logic
        essential_props = self._get_essential_properties(category)
        if 'thermalDestruction' in essential_props and 'thermalDestruction' not in properties:
            # This should be handled by research, not manual addition
            self.logger.debug(f"thermalDestruction needed for {material_name} but should be researched")
            return False
        
        return False
    
    def research_material_properties(
        self,
        material_name: str,
        to_research: Set[str],
        category: str
    ) -> Dict[str, Dict]:
        """
        Compatibility wrapper for PropertyResearchService.research_material_properties()
        
        Args:
            material_name: Name of material
            to_research: Set of property names to research
            category: Material category
            
        Returns:
            Dictionary of researched properties
        """
        # Use unified discovery + research method
        result = self.discover_and_research_properties(
            material_name=material_name,
            material_category=category,
            yaml_properties={}  # Will discover from Materials.yaml
        )
        
        # Return only the quantitative properties
        return result.quantitative_properties
