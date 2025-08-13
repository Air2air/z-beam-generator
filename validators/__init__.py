"""
Validators Package for Z-Beam Generator

This package contains all validation-related functionality:
- validators/validate.py - Main validation script
- validators/validation_fix_instructions.yaml - Fix guidance for Claude
- validators/validation_prompts.yaml - Detailed validation criteria and error prompts
- validators/legacy_validation/ - Legacy validation modules
"""

# Import validation functions for backward compatibility
try:
    from recovery.recovery_system import MaterialRecoverySystem
    
    def validate_material(subject):
        """Validate a specific material using the recovery system."""
        recovery = MaterialRecoverySystem()
        return recovery._validate_material(subject)
    
    def validate_all_materials():
        """Validate all materials and return reports."""
        recovery = MaterialRecoverySystem()
        return recovery.scan_materials()
        
except ImportError:
    def validate_material(subject):
        print("Recovery system not available")
        return None
        
    def validate_all_materials():
        print("Recovery system not available") 
        return {}

__all__ = ['validate_material', 'validate_all_materials']
