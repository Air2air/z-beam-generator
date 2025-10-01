#!/usr/bin/env python3
"""
Caption Frontmatter Integration Validation Rules
Defines validation rules to ensure data integrity when caption components
are integrated into frontmatter files.
"""

import sys
from pathlib import Path
from typing import Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class CaptionIntegrationValidator:
    """Validates caption integration with frontmatter files."""
    
    REQUIRED_CAPTION_FIELDS = [
        'beforeText', 'afterText', 'description', 'alt', 
        'technicalAnalysis', 'generation', 'author', 'materialProperties'
    ]
    
    REQUIRED_TECHNICAL_ANALYSIS_FIELDS = [
        'focus', 'uniqueCharacteristics', 'contaminationProfile'
    ]
    
    REQUIRED_GENERATION_FIELDS = [
        'method', 'timestamp', 'generator', 'componentType'
    ]
    
    def __init__(self):
        self.validation_errors = []
        self.validation_warnings = []
    
    def validate_caption_structure(self, frontmatter_data: Dict[str, Any]) -> bool:
        """Validate that caption structure meets requirements."""
        
        self.validation_errors.clear()
        self.validation_warnings.clear()
        
        # Check if caption key exists
        if 'caption' not in frontmatter_data:
            self.validation_errors.append("Missing 'caption' key in frontmatter")
            return False
        
        caption_data = frontmatter_data['caption']
        
        # Validate required fields
        for field in self.REQUIRED_CAPTION_FIELDS:
            if field not in caption_data:
                self.validation_errors.append(f"Missing required caption field: {field}")
        
        # Validate technical analysis structure
        if 'technicalAnalysis' in caption_data:
            self._validate_technical_analysis(caption_data['technicalAnalysis'])
        
        # Validate generation metadata
        if 'generation' in caption_data:
            self._validate_generation_metadata(caption_data['generation'])
        
        # Validate micro image reorganization
        self._validate_micro_image_reorganization(frontmatter_data)
        
        # Validate content quality
        self._validate_content_quality(caption_data)
        
        return len(self.validation_errors) == 0
    
    def _validate_technical_analysis(self, technical_analysis: Dict[str, Any]) -> None:
        """Validate technical analysis structure."""
        
        for field in self.REQUIRED_TECHNICAL_ANALYSIS_FIELDS:
            if field not in technical_analysis:
                self.validation_errors.append(f"Missing technical analysis field: {field}")
        
        # Validate unique characteristics is a list
        if 'uniqueCharacteristics' in technical_analysis:
            if not isinstance(technical_analysis['uniqueCharacteristics'], list):
                self.validation_errors.append("uniqueCharacteristics must be a list")
    
    def _validate_generation_metadata(self, generation: Dict[str, Any]) -> None:
        """Validate generation metadata."""
        
        for field in self.REQUIRED_GENERATION_FIELDS:
            if field not in generation:
                self.validation_errors.append(f"Missing generation field: {field}")
        
        # Validate specific values
        if 'method' in generation:
            if generation['method'] != 'frontmatter_integrated_generation':
                self.validation_warnings.append(f"Unexpected generation method: {generation['method']}")
        
        if 'componentType' in generation:
            if generation['componentType'] != 'ai_caption_frontmatter':
                self.validation_warnings.append(f"Unexpected component type: {generation['componentType']}")
    
    def _validate_micro_image_reorganization(self, frontmatter_data: Dict[str, Any]) -> None:
        """Validate that micro image has been properly reorganized."""
        
        # Check that micro image is not in images section
        if 'images' in frontmatter_data and 'micro' in frontmatter_data['images']:
            self.validation_errors.append("Micro image still present in images.micro - should be moved to caption.imageUrl")
        
        # Check that caption has imageUrl if there are images
        if 'images' in frontmatter_data and 'caption' in frontmatter_data:
            caption = frontmatter_data['caption']
            if 'imageUrl' not in caption:
                self.validation_warnings.append("Caption missing imageUrl - expected for image-based materials")
        
        # Check that hero image is preserved
        if 'images' in frontmatter_data:
            images = frontmatter_data['images']
            if 'hero' not in images:
                self.validation_warnings.append("Hero image missing from images section")
    
    def _validate_content_quality(self, caption_data: Dict[str, Any]) -> None:
        """Validate content quality standards."""
        
        # Check minimum content length
        for text_field in ['beforeText', 'afterText']:
            if text_field in caption_data:
                content = caption_data[text_field]
                if len(content.strip()) < 50:
                    self.validation_warnings.append(f"{text_field} content is very short (< 50 chars)")
                elif len(content.strip()) > 2000:
                    self.validation_warnings.append(f"{text_field} content is very long (> 2000 chars)")
        
        # Check for placeholder text
        placeholder_indicators = ['TODO', 'PLACEHOLDER', 'TBD', 'FIXME']
        for field in ['beforeText', 'afterText', 'description']:
            if field in caption_data:
                content = str(caption_data[field]).upper()
                for indicator in placeholder_indicators:
                    if indicator in content:
                        self.validation_errors.append(f"Placeholder text found in {field}: {indicator}")
    
    def validate_integration_metadata(self, frontmatter_data: Dict[str, Any]) -> bool:
        """Validate integration metadata."""
        
        # Check for integration tracking
        if 'metadata' not in frontmatter_data:
            self.validation_warnings.append("Missing metadata section for tracking integration")
            return True
        
        metadata = frontmatter_data['metadata']
        
        # Check integration flag
        if 'captionIntegrated' not in metadata:
            self.validation_warnings.append("Missing captionIntegrated flag in metadata")
        elif not metadata['captionIntegrated']:
            self.validation_warnings.append("captionIntegrated flag is False")
        
        # Check last updated timestamp
        if 'lastUpdated' not in metadata:
            self.validation_warnings.append("Missing lastUpdated timestamp in metadata")
        
        return True
    
    def get_validation_report(self) -> Dict[str, Any]:
        """Get comprehensive validation report."""
        
        return {
            "valid": len(self.validation_errors) == 0,
            "errors": self.validation_errors.copy(),
            "warnings": self.validation_warnings.copy(),
            "error_count": len(self.validation_errors),
            "warning_count": len(self.validation_warnings),
            "checks_performed": [
                "caption_structure",
                "technical_analysis", 
                "generation_metadata",
                "micro_image_reorganization",
                "content_quality",
                "integration_metadata"
            ]
        }


def validate_frontmatter_file(file_path: Path) -> Dict[str, Any]:
    """Validate a frontmatter file for proper caption integration."""
    
    import yaml
    
    try:
        # Load frontmatter file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse YAML content
        if content.startswith('---'):
            # Extract YAML content between --- markers
            parts = content.split('---', 2)
            if len(parts) >= 2:
                yaml_content = parts[1].strip()
            else:
                yaml_content = content
        else:
            # Pure YAML file
            yaml_content = content
        
        frontmatter_data = yaml.safe_load(yaml_content)
        
        if not frontmatter_data:
            return {
                "valid": False,
                "errors": ["Failed to parse frontmatter YAML"],
                "warnings": [],
                "file_path": str(file_path)
            }
        
        # Validate using validator
        validator = CaptionIntegrationValidator()
        validator.validate_caption_structure(frontmatter_data)
        validator.validate_integration_metadata(frontmatter_data)
        
        report = validator.get_validation_report()
        report["file_path"] = str(file_path)
        report["material_name"] = frontmatter_data.get("name", "Unknown")
        
        return report
        
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Failed to validate file: {str(e)}"],
            "warnings": [],
            "file_path": str(file_path),
            "error_count": 1,
            "warning_count": 0
        }


def validate_all_frontmatter_files() -> Dict[str, Any]:
    """Validate all frontmatter files for caption integration."""
    
    frontmatter_dir = Path("content/components/frontmatter")
    
    if not frontmatter_dir.exists():
        return {
            "valid": False,
            "error": "Frontmatter directory not found",
            "files_processed": 0
        }
    
    results = {
        "files_processed": 0,
        "files_valid": 0,
        "files_with_errors": 0,
        "files_with_warnings": 0,
        "total_errors": 0,
        "total_warnings": 0,
        "file_results": [],
        "summary": {}
    }
    
    # Process all YAML files
    for yaml_file in frontmatter_dir.glob("*.yaml"):
        file_result = validate_frontmatter_file(yaml_file)
        
        results["files_processed"] += 1
        results["file_results"].append(file_result)
        
        if file_result["valid"]:
            results["files_valid"] += 1
        else:
            results["files_with_errors"] += 1
        
        if file_result["warning_count"] > 0:
            results["files_with_warnings"] += 1
        
        results["total_errors"] += file_result["error_count"]
        results["total_warnings"] += file_result["warning_count"]
    
    # Create summary
    results["summary"] = {
        "overall_valid": results["files_with_errors"] == 0,
        "validation_rate": results["files_valid"] / max(results["files_processed"], 1) * 100,
        "files_needing_attention": results["files_with_errors"] + results["files_with_warnings"]
    }
    
    return results


if __name__ == "__main__":
    print("🔍 Running Caption Integration Validation")
    print("=" * 50)
    
    # Validate all frontmatter files
    results = validate_all_frontmatter_files()
    
    print(f"📊 Processed {results['files_processed']} files")
    print(f"✅ Valid: {results['files_valid']}")
    print(f"❌ Errors: {results['files_with_errors']}")
    print(f"⚠️  Warnings: {results['files_with_warnings']}")
    print(f"📈 Validation Rate: {results['summary']['validation_rate']:.1f}%")
    
    if results['files_with_errors'] > 0:
        print("\n❌ Files with errors:")
        for file_result in results['file_results']:
            if not file_result['valid']:
                material_name = file_result.get('material_name', file_result.get('file_path', 'Unknown'))
                print(f"  • {material_name}: {len(file_result['errors'])} errors")
    
    print(f"\n📋 Total errors: {results['total_errors']}")
    print(f"📋 Total warnings: {results['total_warnings']}")
    
    # Exit with appropriate code
    sys.exit(0 if results['summary']['overall_valid'] else 1)