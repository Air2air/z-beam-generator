#!/usr/bin/env python3
"""
Unified Z-Beam Generator Pipeline

Consolidates all scattered functionality into a single, robust pipeline architecture:
- Material auditing and validation
- Data research and completion
- Content generation and deployment
- System management and optimization

Follows GROK fail-fast architecture with zero tolerance for mocks/fallbacks.
"""

import logging
import sys
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime

# Core imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from validation.schema_validator import SchemaValidator
from data.materials import load_materials_cached as load_materials
from api.client_factory import create_api_client
from generators.dynamic_generator import DynamicGenerator

# Service imports
from scripts.pipeline_integration import (
    get_pre_generation_service,
    get_research_service,
    get_quality_service
)

# Component imports
from components.frontmatter.services.material_auditor import MaterialAuditor
from components.frontmatter.services.property_manager import PropertyManager

logger = logging.getLogger(__name__)


class PipelineMode(Enum):
    """Unified pipeline execution modes"""
    # Core generation modes
    MATERIAL_GENERATION = "material"      # Generate content for specific material
    BATCH_GENERATION = "batch"           # Generate content for multiple materials
    FULL_GENERATION = "all"              # Generate all materials
    
    # Data integrity modes
    AUDIT_SINGLE = "audit"               # Audit single material
    AUDIT_BATCH = "audit_batch"          # Audit multiple materials
    AUDIT_ALL = "audit_all"              # Audit all materials
    
    # Research modes
    RESEARCH_PROPERTIES = "research"     # Research missing properties
    DATA_VERIFICATION = "verify"         # Verify existing data
    DATA_COMPLETION = "complete"         # Complete missing data
    
    # System modes
    VALIDATION = "validate"              # System validation
    DEPLOYMENT = "deploy"                # Deploy to production
    TESTING = "test"                     # Testing mode
    SYSTEM_INFO = "info"                 # System information


@dataclass
class PipelineRequest:
    """Unified request structure for all pipeline operations"""
    mode: PipelineMode
    materials: Optional[List[str]] = None
    components: Optional[List[str]] = None
    properties: Optional[List[str]] = None
    
    # Execution options
    auto_fix: bool = False
    quick_mode: bool = False
    generate_report: bool = False
    batch_size: int = 10
    confidence_threshold: int = 70
    
    # Output options
    output_path: Optional[str] = None
    verbose: bool = False
    dry_run: bool = False


@dataclass
class PipelineResult:
    """Unified result structure for all pipeline operations"""
    success: bool
    mode: PipelineMode
    materials_processed: List[str]
    
    # Execution metrics
    duration_seconds: float
    operations_completed: int
    operations_failed: int
    
    # Results data
    results: Dict[str, Any]
    errors: List[str]
    warnings: List[str]
    
    # Audit-specific results
    audit_results: Optional[Dict[str, Any]] = None
    fixes_applied: Optional[Dict[str, Any]] = None
    
    # Research-specific results
    properties_researched: Optional[Dict[str, Any]] = None
    data_gaps_found: Optional[Dict[str, Any]] = None


class UnifiedPipeline:
    """
    Single entry point for all Z-Beam Generator operations.
    
    Consolidates scattered functionality from run.py into a cohesive,
    robust pipeline with comprehensive error handling and validation.
    """
    
    def __init__(self):
        """Initialize the unified pipeline with all required services"""
        self.logger = logging.getLogger(self.__class__.__name__)
        self._initialize_services()
        self._validate_system_integrity()
    
    def _initialize_services(self):
        """Initialize all required services with fail-fast validation"""
        try:
            # Core services
            self.pre_gen_service = get_pre_generation_service()
            self.research_service = get_research_service()
            self.quality_service = get_quality_service()
            
            # Specialized services
            self.material_auditor = MaterialAuditor()
            
            # Initialize PropertyManager with required PropertyValueResearcher
            from components.frontmatter.research.property_value_researcher import PropertyValueResearcher
            from api.client_factory import create_api_client
            api_client = create_api_client("deepseek")
            property_researcher = PropertyValueResearcher(api_client=api_client)
            self.property_manager = PropertyManager(property_researcher=property_researcher)
            
            self.schema_validator = SchemaValidator(validation_mode="enhanced")
            
            # Generator services
            self.dynamic_generator = DynamicGenerator()
            
            self.logger.info("✅ All pipeline services initialized successfully")
            
        except Exception as e:
            self.logger.error(f"🚨 CRITICAL: Service initialization failed: {e}")
            raise SystemExit("❌ Pipeline initialization failed - cannot continue")
    
    def _validate_system_integrity(self):
        """Validate system integrity before allowing operations"""
        try:
            # Validate materials database exists and is valid
            materials_data = load_materials()
            if not materials_data:
                raise ValueError("Materials database is empty or invalid")
            
            # Run pre-generation validation
            validation_result = self.pre_gen_service.validate_hierarchical()
            
            if not validation_result.success:
                self.logger.error("🚨 System validation failed:")
                for error in validation_result.errors:
                    self.logger.error(f"  💥 {error}")
                raise SystemExit("❌ System integrity validation failed")
            
            self.logger.info("✅ System integrity validation passed")
            
        except Exception as e:
            self.logger.error(f"🚨 System integrity validation failed: {e}")
            raise SystemExit("❌ Cannot proceed with invalid system state")
    
    def execute(self, request: PipelineRequest) -> PipelineResult:
        """
        Execute pipeline operation based on request.
        
        Args:
            request: Unified pipeline request with mode and parameters
            
        Returns:
            PipelineResult with execution results and metrics
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"🚀 Starting {request.mode.value} pipeline")
            
            # Route to appropriate handler
            result = self._route_request(request)
            
            # Calculate execution metrics
            duration = (datetime.now() - start_time).total_seconds()
            result.duration_seconds = duration
            
            self.logger.info(f"✅ Pipeline completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"❌ Pipeline failed after {duration:.2f}s: {e}")
            
            return PipelineResult(
                success=False,
                mode=request.mode,
                materials_processed=[],
                duration_seconds=duration,
                operations_completed=0,
                operations_failed=1,
                results={},
                errors=[str(e)],
                warnings=[]
            )
    
    def _route_request(self, request: PipelineRequest) -> PipelineResult:
        """Route request to appropriate handler based on mode"""
        
        # Generation modes
        if request.mode == PipelineMode.MATERIAL_GENERATION:
            return self._handle_material_generation(request)
        elif request.mode == PipelineMode.BATCH_GENERATION:
            return self._handle_batch_generation(request)
        elif request.mode == PipelineMode.FULL_GENERATION:
            return self._handle_full_generation(request)
        
        # Audit modes
        elif request.mode == PipelineMode.AUDIT_SINGLE:
            return self._handle_audit_single(request)
        elif request.mode == PipelineMode.AUDIT_BATCH:
            return self._handle_audit_batch(request)
        elif request.mode == PipelineMode.AUDIT_ALL:
            return self._handle_audit_all(request)
        
        # Research modes
        elif request.mode == PipelineMode.RESEARCH_PROPERTIES:
            return self._handle_research_properties(request)
        elif request.mode == PipelineMode.DATA_VERIFICATION:
            return self._handle_data_verification(request)
        elif request.mode == PipelineMode.DATA_COMPLETION:
            return self._handle_data_completion(request)
        
        # System modes
        elif request.mode == PipelineMode.VALIDATION:
            return self._handle_system_validation(request)
        elif request.mode == PipelineMode.DEPLOYMENT:
            return self._handle_deployment(request)
        elif request.mode == PipelineMode.TESTING:
            return self._handle_testing(request)
        elif request.mode == PipelineMode.SYSTEM_INFO:
            return self._handle_system_info(request)
        
        else:
            raise ValueError(f"Unknown pipeline mode: {request.mode}")
    
    # =========================================================================
    # GENERATION HANDLERS
    # =========================================================================
    
    def _handle_material_generation(self, request: PipelineRequest) -> PipelineResult:
        """Handle single material generation"""
        if not request.materials or len(request.materials) != 1:
            raise ValueError("Material generation requires exactly one material")
        
        material_name = request.materials[0]
        components = request.components or ["frontmatter"]
        
        results = {}
        errors = []
        
        try:
            # Pre-generation validation
            validation_result = self.pre_gen_service.validate_material(material_name)
            if not validation_result.success:
                errors.extend(validation_result.errors)
            
            # Generate each component
            for component in components:
                try:
                    api_client = create_api_client("deepseek")
                    result = self.dynamic_generator.generate_component(
                        material=material_name,
                        component_type=component,
                        api_client=api_client
                    )
                    results[component] = result
                    
                except Exception as e:
                    errors.append(f"Component {component} failed: {e}")
            
            return PipelineResult(
                success=len(errors) == 0,
                mode=request.mode,
                materials_processed=[material_name],
                duration_seconds=0.0,
                operations_completed=len(results),
                operations_failed=len(errors),
                results=results,
                errors=errors,
                warnings=[]
            )
            
        except Exception as e:
            return PipelineResult(
                success=False,
                mode=request.mode,
                materials_processed=[],
                operations_completed=0,
                operations_failed=1,
                results={},
                errors=[str(e)],
                warnings=[]
            )
    
    def _handle_batch_generation(self, request: PipelineRequest) -> PipelineResult:
        """Handle batch material generation"""
        if not request.materials:
            raise ValueError("Batch generation requires material list")
        
        results = {}
        errors = []
        processed_materials = []
        
        for material_name in request.materials:
            try:
                single_request = PipelineRequest(
                    mode=PipelineMode.MATERIAL_GENERATION,
                    materials=[material_name],
                    components=request.components,
                    auto_fix=request.auto_fix,
                    quick_mode=request.quick_mode
                )
                
                result = self._handle_material_generation(single_request)
                results[material_name] = result
                processed_materials.append(material_name)
                
                if not result.success:
                    errors.extend(result.errors)
                    
            except Exception as e:
                errors.append(f"Material {material_name} failed: {e}")
        
        return PipelineResult(
            success=len(errors) == 0,
            mode=request.mode,
            materials_processed=processed_materials,
            duration_seconds=0.0,
            operations_completed=len(processed_materials),
            operations_failed=len(errors),
            results=results,
            errors=errors,
            warnings=[]
        )
    
    def _handle_full_generation(self, request: PipelineRequest) -> PipelineResult:
        """Handle full system generation (all materials)"""
        materials_data = load_materials()
        all_materials = []
        
        # Extract all material names from materials data
        for category_data in materials_data.get('materials', {}).values():
            for item in category_data.get('items', []):
                if 'name' in item:
                    all_materials.append(item['name'])
        
        # Create batch request for all materials
        batch_request = PipelineRequest(
            mode=PipelineMode.BATCH_GENERATION,
            materials=all_materials,
            components=request.components,
            auto_fix=request.auto_fix,
            quick_mode=request.quick_mode,
            batch_size=request.batch_size
        )
        
        return self._handle_batch_generation(batch_request)
    
    # =========================================================================
    # AUDIT HANDLERS  
    # =========================================================================
    
    def _handle_audit_single(self, request: PipelineRequest) -> PipelineResult:
        """Handle single material audit"""
        if not request.materials or len(request.materials) != 1:
            raise ValueError("Single audit requires exactly one material")
        
        material_name = request.materials[0]
        
        try:
            audit_result = self.material_auditor.audit_material(
                material_name,
                skip_frontmatter=request.quick_mode
            )
            
            fixes_applied = {}
            if request.auto_fix and audit_result.fixable_issues:
                fixes_applied = self.material_auditor.apply_fixes(
                    material_name,
                    audit_result.fixable_issues
                )
            
            return PipelineResult(
                success=audit_result.overall_score >= 70,  # Pass threshold
                mode=request.mode,
                materials_processed=[material_name],
                duration_seconds=0.0,
                operations_completed=1,
                operations_failed=0 if audit_result.overall_score >= 70 else 1,
                results={"audit_score": audit_result.overall_score},
                errors=[],
                warnings=[],
                audit_results={material_name: audit_result},
                fixes_applied=fixes_applied
            )
            
        except Exception as e:
            return PipelineResult(
                success=False,
                mode=request.mode,
                materials_processed=[],
                operations_completed=0,
                operations_failed=1,
                results={},
                errors=[str(e)],
                warnings=[]
            )
    
    def _handle_audit_batch(self, request: PipelineRequest) -> PipelineResult:
        """Handle batch material audit"""
        if not request.materials:
            raise ValueError("Batch audit requires material list")
        
        audit_results = {}
        all_fixes_applied = {}
        errors = []
        processed_materials = []
        
        for material_name in request.materials:
            try:
                single_request = PipelineRequest(
                    mode=PipelineMode.AUDIT_SINGLE,
                    materials=[material_name],
                    auto_fix=request.auto_fix,
                    quick_mode=request.quick_mode
                )
                
                result = self._handle_audit_single(single_request)
                audit_results[material_name] = result.audit_results.get(material_name)
                
                if result.fixes_applied:
                    all_fixes_applied[material_name] = result.fixes_applied
                
                processed_materials.append(material_name)
                
                if not result.success:
                    errors.extend(result.errors)
                    
            except Exception as e:
                errors.append(f"Audit failed for {material_name}: {e}")
        
        return PipelineResult(
            success=len(errors) == 0,
            mode=request.mode,
            materials_processed=processed_materials,
            operations_completed=len(processed_materials),
            operations_failed=len(errors),
            results={"materials_audited": len(processed_materials)},
            errors=errors,
            warnings=[],
            audit_results=audit_results,
            fixes_applied=all_fixes_applied
        )
    
    def _handle_audit_all(self, request: PipelineRequest) -> PipelineResult:
        """Handle audit of all materials"""
        materials_data = load_materials()
        all_materials = []
        
        # Extract all material names
        for category_data in materials_data.get('materials', {}).values():
            for item in category_data.get('items', []):
                if 'name' in item:
                    all_materials.append(item['name'])
        
        # Create batch audit request
        batch_request = PipelineRequest(
            mode=PipelineMode.AUDIT_BATCH,
            materials=all_materials,
            auto_fix=request.auto_fix,
            quick_mode=request.quick_mode,
            generate_report=request.generate_report
        )
        
        return self._handle_audit_batch(batch_request)
    
    # =========================================================================
    # RESEARCH HANDLERS
    # =========================================================================
    
    def _handle_research_properties(self, request: PipelineRequest) -> PipelineResult:
        """Handle property research"""
        try:
            # Determine what to research
            if request.materials and request.properties:
                # Research specific properties for specific materials
                results = self.property_manager.research_properties_for_materials(
                    materials=request.materials,
                    properties=request.properties,
                    confidence_threshold=request.confidence_threshold
                )
            elif request.materials:
                # Research all missing properties for specific materials
                results = self.property_manager.research_missing_properties_for_materials(
                    materials=request.materials,
                    batch_size=request.batch_size,
                    confidence_threshold=request.confidence_threshold
                )
            elif request.properties:
                # Research specific properties for all materials
                results = self.property_manager.research_specific_properties_all_materials(
                    properties=request.properties,
                    batch_size=request.batch_size,
                    confidence_threshold=request.confidence_threshold
                )
            else:
                # Research all missing properties for all materials
                results = self.property_manager.research_all_missing_properties(
                    batch_size=request.batch_size,
                    confidence_threshold=request.confidence_threshold
                )
            
            return PipelineResult(
                success=True,
                mode=request.mode,
                materials_processed=results.get('materials_processed', []),
                operations_completed=results.get('properties_researched', 0),
                operations_failed=results.get('research_failures', 0),
                results=results,
                errors=results.get('errors', []),
                warnings=results.get('warnings', []),
                properties_researched=results.get('research_details', {})
            )
            
        except Exception as e:
            return PipelineResult(
                success=False,
                mode=request.mode,
                materials_processed=[],
                operations_completed=0,
                operations_failed=1,
                results={},
                errors=[str(e)],
                warnings=[]
            )
    
    def _handle_data_verification(self, request: PipelineRequest) -> PipelineResult:
        """Handle data verification"""
        try:
            verification_result = self.pre_gen_service.validate_hierarchical()
            
            return PipelineResult(
                success=verification_result.success,
                mode=request.mode,
                materials_processed=[],
                operations_completed=1,
                operations_failed=0 if verification_result.success else 1,
                results={
                    "validation_passed": verification_result.success,
                    "issues_found": len(verification_result.errors),
                    "warnings": len(verification_result.warnings)
                },
                errors=verification_result.errors,
                warnings=verification_result.warnings
            )
            
        except Exception as e:
            return PipelineResult(
                success=False,
                mode=request.mode,
                materials_processed=[],
                operations_completed=0,
                operations_failed=1,
                results={},
                errors=[str(e)],
                warnings=[]
            )
    
    def _handle_data_completion(self, request: PipelineRequest) -> PipelineResult:
        """Handle data completion analysis"""
        try:
            # Get data completeness report
            completeness_data = self.property_manager.generate_completeness_report()
            
            return PipelineResult(
                success=True,
                mode=request.mode,
                materials_processed=[],
                operations_completed=1,
                operations_failed=0,
                results=completeness_data,
                errors=[],
                warnings=[],
                data_gaps_found=completeness_data.get('gaps_analysis', {})
            )
            
        except Exception as e:
            return PipelineResult(
                success=False,
                mode=request.mode,
                materials_processed=[],
                operations_completed=0,
                operations_failed=1,
                results={},
                errors=[str(e)],
                warnings=[]
            )
    
    # =========================================================================
    # SYSTEM HANDLERS
    # =========================================================================
    
    def _handle_system_validation(self, request: PipelineRequest) -> PipelineResult:
        """Handle system validation"""
        try:
            validation_result = self.pre_gen_service.validate_hierarchical()
            schema_validation = self.schema_validator.validate_system()
            
            return PipelineResult(
                success=validation_result.success and schema_validation.is_valid,
                mode=request.mode,
                materials_processed=[],
                operations_completed=2,
                operations_failed=0 if validation_result.success and schema_validation.is_valid else 1,
                results={
                    "hierarchical_validation": validation_result.success,
                    "schema_validation": schema_validation.is_valid
                },
                errors=validation_result.errors + [e.message for e in schema_validation.errors],
                warnings=validation_result.warnings + [w.message for w in schema_validation.warnings]
            )
            
        except Exception as e:
            return PipelineResult(
                success=False,
                mode=request.mode,
                materials_processed=[],
                operations_completed=0,
                operations_failed=1,
                results={},
                errors=[str(e)],
                warnings=[]
            )
    
    def _handle_deployment(self, request: PipelineRequest) -> PipelineResult:
        """Handle deployment operations"""
        # TODO: Implement deployment logic
        return PipelineResult(
            success=False,
            mode=request.mode,
            materials_processed=[],
            operations_completed=0,
            operations_failed=1,
            results={},
            errors=["Deployment not yet implemented"],
            warnings=[]
        )
    
    def _handle_testing(self, request: PipelineRequest) -> PipelineResult:
        """Handle testing operations"""
        # TODO: Implement testing logic
        return PipelineResult(
            success=False,
            mode=request.mode,
            materials_processed=[],
            operations_completed=0,
            operations_failed=1,
            results={},
            errors=["Testing not yet implemented"],
            warnings=[]
        )
    
    def _handle_system_info(self, request: PipelineRequest) -> PipelineResult:
        """Handle system information requests"""
        try:
            materials_data = load_materials()
            material_count = sum(
                len(category.get('items', []))
                for category in materials_data.get('materials', {}).values()
            )
            
            return PipelineResult(
                success=True,
                mode=request.mode,
                materials_processed=[],
                duration_seconds=0.0,
                operations_completed=1,
                operations_failed=0,
                results={
                    "total_materials": material_count,
                    "categories": len(materials_data.get('materials', {})),
                    "services_initialized": True,
                    "system_valid": True
                },
                errors=[],
                warnings=[]
            )
            
        except Exception as e:
            return PipelineResult(
                success=False,
                mode=request.mode,
                materials_processed=[],
                duration_seconds=0.0,
                operations_completed=0,
                operations_failed=1,
                results={},
                errors=[str(e)],
                warnings=[]
            )


# ============================================================================
# CONVENIENCE FUNCTIONS FOR BACKWARD COMPATIBILITY
# ============================================================================

def create_pipeline() -> UnifiedPipeline:
    """Create and initialize unified pipeline"""
    return UnifiedPipeline()

def audit_material(material_name: str, auto_fix: bool = False, quick_mode: bool = False) -> PipelineResult:
    """Audit single material - convenience function"""
    pipeline = create_pipeline()
    request = PipelineRequest(
        mode=PipelineMode.AUDIT_SINGLE,
        materials=[material_name],
        auto_fix=auto_fix,
        quick_mode=quick_mode
    )
    return pipeline.execute(request)

def generate_material(material_name: str, components: List[str] = None) -> PipelineResult:
    """Generate content for material - convenience function"""
    pipeline = create_pipeline()
    request = PipelineRequest(
        mode=PipelineMode.MATERIAL_GENERATION,
        materials=[material_name],
        components=components or ["frontmatter"]
    )
    return pipeline.execute(request)

def research_properties(materials: List[str] = None, properties: List[str] = None) -> PipelineResult:
    """Research properties - convenience function"""
    pipeline = create_pipeline()
    request = PipelineRequest(
        mode=PipelineMode.RESEARCH_PROPERTIES,
        materials=materials,
        properties=properties
    )
    return pipeline.execute(request)

def validate_system() -> PipelineResult:
    """Validate system - convenience function"""
    pipeline = create_pipeline()
    request = PipelineRequest(mode=PipelineMode.VALIDATION)
    return pipeline.execute(request)


if __name__ == "__main__":
    """CLI interface for unified pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Unified Z-Beam Generator Pipeline")
    parser.add_argument("--mode", required=True, choices=[mode.value for mode in PipelineMode])
    parser.add_argument("--materials", help="Comma-separated list of materials")
    parser.add_argument("--components", help="Comma-separated list of components")
    parser.add_argument("--properties", help="Comma-separated list of properties")
    parser.add_argument("--auto-fix", action="store_true", help="Apply automatic fixes")
    parser.add_argument("--quick", action="store_true", help="Quick mode")
    parser.add_argument("--report", action="store_true", help="Generate report")
    parser.add_argument("--batch-size", type=int, default=10, help="Batch size")
    parser.add_argument("--confidence", type=int, default=70, help="Confidence threshold")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Create request
    request = PipelineRequest(
        mode=PipelineMode(args.mode),
        materials=args.materials.split(',') if args.materials else None,
        components=args.components.split(',') if args.components else None,
        properties=args.properties.split(',') if args.properties else None,
        auto_fix=args.auto_fix,
        quick_mode=args.quick,
        generate_report=args.report,
        batch_size=args.batch_size,
        confidence_threshold=args.confidence,
        verbose=args.verbose
    )
    
    # Execute pipeline
    pipeline = create_pipeline()
    result = pipeline.execute(request)
    
    # Output results
    if result.success:
        print(f"✅ Pipeline completed successfully")
        print(f"   Materials processed: {len(result.materials_processed)}")
        print(f"   Operations completed: {result.operations_completed}")
        print(f"   Duration: {result.duration_seconds:.2f}s")
    else:
        print(f"❌ Pipeline failed")
        print(f"   Operations failed: {result.operations_failed}")
        print(f"   Errors: {len(result.errors)}")
        for error in result.errors:
            print(f"     • {error}")