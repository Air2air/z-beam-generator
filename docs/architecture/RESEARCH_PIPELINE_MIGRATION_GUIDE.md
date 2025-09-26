# Research Pipeline Migration Guide

## Overview

This guide provides a comprehensive migration path from the legacy property generation system to the new Research Pipeline architecture. The migration is designed to be gradual, safe, and backwards-compatible, allowing teams to adopt the new system at their own pace while maintaining full functionality.

## Migration Strategy

### Phase-Based Migration Approach

#### Phase 1: Infrastructure Setup (Weeks 1-2)
- Install research pipeline dependencies
- Configure API access and authentication
- Set up caching and monitoring infrastructure
- Validate integration with existing systems

#### Phase 2: Parallel Operation (Weeks 3-4)
- Enable pipeline alongside existing generators
- Test pipeline with subset of materials
- Compare outputs and validate quality
- Fine-tune configuration and thresholds

#### Phase 3: Gradual Rollout (Weeks 5-8)
- Migrate material categories one by one
- Monitor performance and quality metrics
- Address any integration issues
- Train team on new capabilities

#### Phase 4: Full Migration (Weeks 9-10)
- Complete migration to research pipeline
- Deprecate legacy systems (keep as fallback)
- Update documentation and processes
- Celebrate successful migration! 🎉

## Pre-Migration Assessment

### System Readiness Checklist

```python
def assess_migration_readiness():
    """Assess system readiness for research pipeline migration"""
    checklist = {
        "api_access": False,
        "dependencies_installed": False,
        "schema_updated": False,
        "fallback_systems_working": False,
        "monitoring_configured": False,
        "team_trained": False
    }
    
    # API Access
    try:
        # Test API connectivity
        from api.client_manager import ClientManager
        from api.config import APIConfig
        
        client = ClientManager(APIConfig())
        checklist["api_access"] = client.test_connection()
    except Exception as e:
        print(f"❌ API access failed: {e}")
    
    # Dependencies
    try:
        from components.frontmatter.research.research_pipeline import PIPELINE_AVAILABLE
        checklist["dependencies_installed"] = PIPELINE_AVAILABLE
    except ImportError:
        print("❌ Research pipeline dependencies not available")
    
    # Schema
    try:
        import json
        with open('schemas/active/frontmatter.json', 'r') as f:
            schema = json.load(f)
            checklist["schema_updated"] = "PropertyDataMetric" in schema.get("definitions", {})
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
    
    return checklist

# Run assessment
readiness = assess_migration_readiness()
ready_count = sum(readiness.values())
total_count = len(readiness)

print(f"Migration readiness: {ready_count}/{total_count} criteria met")
```

### Current System Analysis

```python
def analyze_current_system():
    """Analyze current property generation patterns"""
    from data.materials import MaterialsData
    
    materials = MaterialsData()
    analysis = {
        "total_materials": 0,
        "property_formats": {"flat": 0, "mixed": 0, "structured": 0},
        "common_properties": {},
        "quality_issues": []
    }
    
    for material_name, material_data in materials.get_all_materials().items():
        analysis["total_materials"] += 1
        
        # Analyze property format
        format_type = determine_property_format(material_data)
        analysis["property_formats"][format_type] += 1
        
        # Count common properties
        for prop_name in material_data.keys():
            if is_material_property(prop_name):
                base_prop = extract_base_property_name(prop_name)
                analysis["common_properties"][base_prop] = analysis["common_properties"].get(base_prop, 0) + 1
    
    return analysis
```

## Migration Implementation

### Step 1: Environment Setup

#### Install Dependencies
```bash
# Install research pipeline dependencies
pip install -r components/frontmatter/research/requirements.txt

# Verify installation
python3 -c "from components.frontmatter.research.research_pipeline import PIPELINE_AVAILABLE; print(f'Pipeline available: {PIPELINE_AVAILABLE}')"
```

#### Configure API Access
```python
# config/api_keys.py
class ResearchAPIConfig:
    """API configuration for research pipeline"""
    
    def __init__(self):
        self.openai_key = os.getenv('OPENAI_API_KEY')
        self.materials_project_key = os.getenv('MATERIALS_PROJECT_KEY')  
        self.nist_key = os.getenv('NIST_API_KEY')
        
        self.validate_keys()
    
    def validate_keys(self):
        """Validate required API keys are present"""
        required_keys = ['openai_key']
        missing_keys = [key for key in required_keys if not getattr(self, key)]
        
        if missing_keys:
            raise ConfigurationError(f"Missing required API keys: {missing_keys}")
```

#### Update Schema
```json
{
  "definitions": {
    "PropertyDataMetric": {
      "type": "object",
      "properties": {
        "value": {"type": ["number", "string"]},
        "unit": {"type": "string"},
        "min": {"type": "number"},
        "max": {"type": "number"},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100}
      },
      "required": ["value"],
      "additionalProperties": false
    }
  }
}
```

### Step 2: Implement Migration Utilities

#### Format Conversion Tool
```python
class PropertyFormatMigrator:
    """Tool for migrating property formats"""
    
    def migrate_material_file(self, material_file_path: str, backup: bool = True) -> bool:
        """Migrate a single material file to structured format"""
        
        if backup:
            self._create_backup(material_file_path)
        
        try:
            # Load existing material data
            with open(material_file_path, 'r') as f:
                content = f.read()
            
            # Extract and parse frontmatter
            parts = content.split('---')
            if len(parts) < 3:
                raise ValueError("Invalid frontmatter structure")
            
            frontmatter = yaml.safe_load(parts[1])
            
            # Migrate properties to structured format
            if 'materialProperties' in frontmatter:
                frontmatter['materialProperties'] = self._migrate_properties_section(
                    frontmatter['materialProperties']
                )
            
            if 'machineSettings' in frontmatter:
                frontmatter['machineSettings'] = self._migrate_properties_section(
                    frontmatter['machineSettings']
                )
            
            # Write updated file
            parts[1] = yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True)
            updated_content = '---'.join(parts)
            
            with open(material_file_path, 'w') as f:
                f.write(updated_content)
            
            print(f"✅ Migrated {material_file_path}")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed for {material_file_path}: {e}")
            if backup:
                self._restore_backup(material_file_path)
            return False
    
    def _migrate_properties_section(self, properties: Dict) -> Dict:
        """Migrate a properties section to structured format"""
        if self._is_already_structured(properties):
            return properties
        
        # Convert flat format to structured format
        return PropertyFormatConverter.legacy_to_structured(properties)
    
    def _is_already_structured(self, properties: Dict) -> bool:
        """Check if properties are already in structured format"""
        for prop_data in properties.values():
            if isinstance(prop_data, dict) and "value" in prop_data:
                return True
        return False

# Usage example
migrator = PropertyFormatMigrator()
migrator.migrate_material_file('content/components/frontmatter/aluminum-laser-cleaning.md')
```

#### Batch Migration Script
```python
def migrate_all_materials(materials_directory: str, dry_run: bool = True):
    """Migrate all material files to structured format"""
    
    migrator = PropertyFormatMigrator()
    results = {"successful": [], "failed": [], "skipped": []}
    
    # Find all material files
    material_files = glob.glob(f"{materials_directory}/**/*-laser-cleaning.md", recursive=True)
    
    print(f"Found {len(material_files)} material files to migrate")
    
    for file_path in material_files:
        material_name = os.path.basename(file_path).replace('-laser-cleaning.md', '')
        
        if dry_run:
            print(f"DRY RUN: Would migrate {material_name}")
            continue
        
        print(f"Migrating {material_name}...")
        
        try:
            success = migrator.migrate_material_file(file_path, backup=True)
            if success:
                results["successful"].append(material_name)
            else:
                results["failed"].append(material_name)
        except Exception as e:
            print(f"❌ Error migrating {material_name}: {e}")
            results["failed"].append(material_name)
    
    # Summary
    print(f"\nMigration Summary:")
    print(f"✅ Successful: {len(results['successful'])}")
    print(f"❌ Failed: {len(results['failed'])}")
    print(f"⏭️ Skipped: {len(results['skipped'])}")
    
    return results

# Run batch migration
results = migrate_all_materials('content/components/frontmatter', dry_run=False)
```

### Step 3: Enable Pipeline Integration

#### Update Generator Configuration
```python
# components/frontmatter/core/dynamic_property_generator.py

class DynamicPropertyGenerator:
    def __init__(self, migration_mode: str = "hybrid"):
        """
        Initialize generator with migration mode
        
        Migration modes:
        - "legacy": Use only legacy systems
        - "hybrid": Try pipeline, fallback to legacy
        - "pipeline": Use only research pipeline
        """
        self.migration_mode = migration_mode
        self._initialize_systems()
    
    def _initialize_systems(self):
        """Initialize systems based on migration mode"""
        
        # Always initialize legacy systems for fallback
        self._initialize_legacy_systems()
        
        # Initialize pipeline if not in legacy-only mode
        if self.migration_mode != "legacy":
            self._initialize_research_pipeline()
    
    def generate_properties_for_material(self, material_name: str, existing_data: Dict = None) -> Dict:
        """Generate properties with migration mode consideration"""
        
        if self.migration_mode == "legacy":
            return self._generate_legacy_properties(material_name, existing_data)
        
        elif self.migration_mode == "pipeline":
            return self._generate_pipeline_properties(material_name, existing_data)
        
        else:  # hybrid mode
            return self._generate_hybrid_properties(material_name, existing_data)
```

#### Migration Configuration
```python
# config/migration_config.py

class MigrationConfig:
    """Configuration for migration process"""
    
    def __init__(self):
        self.migration_phase = os.getenv('MIGRATION_PHASE', 'hybrid')
        self.migrated_materials = set()
        self.migration_exceptions = set()
        
        self._load_migration_status()
    
    def is_material_migrated(self, material_name: str) -> bool:
        """Check if material has been migrated"""
        return material_name in self.migrated_materials
    
    def mark_material_migrated(self, material_name: str):
        """Mark material as successfully migrated"""
        self.migrated_materials.add(material_name)
        self._save_migration_status()
    
    def add_migration_exception(self, material_name: str, reason: str):
        """Add material to migration exceptions"""
        self.migration_exceptions.add(material_name)
        print(f"⚠️ Migration exception for {material_name}: {reason}")
```

### Step 4: Testing and Validation

#### Migration Test Suite
```python
class MigrationTestSuite:
    """Test suite for migration validation"""
    
    def test_format_conversion_accuracy(self):
        """Test accuracy of format conversion"""
        test_cases = [
            {
                "legacy": {"density": 5.68, "densityUnit": "g/cm³", "densityMin": 5.0},
                "expected": {"density": {"value": 5.68, "unit": "g/cm³", "min": 5.0}}
            }
        ]
        
        converter = PropertyFormatConverter()
        
        for test_case in test_cases:
            result = converter.legacy_to_structured(test_case["legacy"])
            assert result == test_case["expected"], f"Conversion failed: {result}"
        
        print("✅ Format conversion accuracy test passed")
    
    def test_pipeline_quality(self):
        """Test pipeline output quality against known materials"""
        test_materials = ["Zirconia", "Aluminum", "Steel"]
        pipeline = ResearchPipelineManager()
        
        for material in test_materials:
            try:
                results = pipeline.execute_complete_pipeline(material, "ceramic")
                
                # Validate structure
                assert "materialProperties" in results
                assert len(results["materialProperties"]) > 0
                
                # Validate quality
                avg_confidence = self._calculate_average_confidence(results["materialProperties"])
                assert avg_confidence >= 50, f"Low confidence for {material}: {avg_confidence}"
                
                print(f"✅ {material}: Pipeline quality test passed")
                
            except Exception as e:
                print(f"❌ {material}: Pipeline quality test failed - {e}")
    
    def test_backwards_compatibility(self):
        """Test that migrated materials work with legacy systems"""
        # Test that structured format can be read by legacy code
        structured_data = {
            "density": {"value": 5.68, "unit": "g/cm³", "confidence": 95}
        }
        
        # Legacy accessor should still work
        density_value = get_property_value(structured_data, "density")
        assert density_value == 5.68
        
        print("✅ Backwards compatibility test passed")
```

#### Quality Assurance Checklist
```python
def migration_quality_check(material_name: str, before: Dict, after: Dict) -> List[str]:
    """Check migration quality and identify issues"""
    issues = []
    
    # Check data preservation
    before_properties = extract_property_names(before)
    after_properties = extract_property_names(after)
    
    missing_properties = before_properties - after_properties
    if missing_properties:
        issues.append(f"Missing properties after migration: {missing_properties}")
    
    # Check value preservation
    for prop_name in before_properties & after_properties:
        before_value = get_legacy_property_value(before, prop_name)
        after_value = get_structured_property_value(after, prop_name)
        
        if before_value != after_value:
            issues.append(f"{prop_name}: Value changed from {before_value} to {after_value}")
    
    # Check structure compliance
    for prop_name, prop_data in after.items():
        if not validate_property_data_metric(prop_data):
            issues.append(f"{prop_name}: Invalid PropertyDataMetric structure")
    
    return issues
```

### Step 5: Monitoring and Rollback

#### Migration Monitoring
```python
class MigrationMonitor:
    """Monitor migration progress and quality"""
    
    def __init__(self):
        self.metrics = {
            "materials_migrated": 0,
            "migration_failures": 0,
            "quality_issues": 0,
            "performance_impact": 0.0
        }
    
    def record_migration(self, material_name: str, success: bool, quality_score: float):
        """Record migration event"""
        if success:
            self.metrics["materials_migrated"] += 1
            if quality_score < 0.8:  # Below 80% quality
                self.metrics["quality_issues"] += 1
        else:
            self.metrics["migration_failures"] += 1
    
    def get_migration_health_score(self) -> float:
        """Calculate overall migration health"""
        total_attempts = self.metrics["materials_migrated"] + self.metrics["migration_failures"]
        if total_attempts == 0:
            return 1.0
        
        success_rate = self.metrics["materials_migrated"] / total_attempts
        quality_rate = 1.0 - (self.metrics["quality_issues"] / max(1, self.metrics["materials_migrated"]))
        
        return (success_rate * 0.7) + (quality_rate * 0.3)
```

#### Rollback Procedures
```python
class MigrationRollback:
    """Handle migration rollbacks if issues occur"""
    
    def __init__(self, backup_directory: str):
        self.backup_directory = backup_directory
    
    def rollback_material(self, material_name: str) -> bool:
        """Rollback a single material to pre-migration state"""
        try:
            backup_path = f"{self.backup_directory}/{material_name}-backup.md"
            current_path = f"content/components/frontmatter/{material_name}-laser-cleaning.md"
            
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, current_path)
                print(f"✅ Rolled back {material_name}")
                return True
            else:
                print(f"❌ No backup found for {material_name}")
                return False
                
        except Exception as e:
            print(f"❌ Rollback failed for {material_name}: {e}")
            return False
    
    def rollback_all_materials(self) -> Dict[str, bool]:
        """Rollback all migrated materials"""
        results = {}
        backup_files = glob.glob(f"{self.backup_directory}/*-backup.md")
        
        for backup_file in backup_files:
            material_name = os.path.basename(backup_file).replace('-backup.md', '')
            results[material_name] = self.rollback_material(material_name)
        
        return results
```

## Migration Best Practices

### Before Migration
1. **Create Complete Backups**: Backup all material files and configuration
2. **Test in Development**: Run complete migration in development environment first
3. **Validate Dependencies**: Ensure all required APIs and services are available
4. **Team Preparation**: Train team on new system capabilities and troubleshooting

### During Migration
1. **Start Small**: Begin with 1-2 materials to validate process
2. **Monitor Closely**: Watch for performance impacts and quality issues
3. **Validate Each Step**: Check outputs at each stage of migration
4. **Keep Communication Open**: Update stakeholders on progress and issues

### After Migration
1. **Performance Monitoring**: Track system performance and response times
2. **Quality Validation**: Regularly check output quality and accuracy
3. **User Training**: Ensure all team members understand new capabilities
4. **Documentation Updates**: Keep documentation current with new features

## Common Migration Issues and Solutions

### Issue 1: API Rate Limiting
**Problem**: Research pipeline hits API rate limits during batch migration
**Solution**: 
```python
# Add rate limiting to research pipeline
import time
from functools import wraps

def rate_limited(calls_per_minute=60):
    def decorator(func):
        calls = []
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [call_time for call_time in calls if now - call_time < 60]
            
            if len(calls) >= calls_per_minute:
                sleep_time = 60 - (now - calls[0])
                time.sleep(sleep_time)
            
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    return decorator
```

### Issue 2: Data Quality Inconsistencies
**Problem**: Pipeline returns different values than existing curated data
**Solution**: 
```python
def validate_against_existing_data(new_data: Dict, existing_data: Dict, tolerance: float = 0.1) -> List[str]:
    """Validate new data against existing curated data"""
    warnings = []
    
    for prop_name in set(new_data.keys()) & set(existing_data.keys()):
        new_value = extract_numeric_value(new_data[prop_name])
        existing_value = extract_numeric_value(existing_data[prop_name])
        
        if new_value and existing_value:
            difference = abs(new_value - existing_value) / existing_value
            if difference > tolerance:
                warnings.append(f"{prop_name}: New value {new_value} differs from existing {existing_value} by {difference:.1%}")
    
    return warnings
```

### Issue 3: Schema Validation Failures
**Problem**: Migrated data fails schema validation
**Solution**:
```python
def fix_schema_violations(data: Dict) -> Dict:
    """Fix common schema validation issues"""
    fixed_data = {}
    
    for key, value in data.items():
        if isinstance(value, dict):
            # Ensure required 'value' field exists
            if 'value' not in value:
                # Try to infer value from legacy format
                if key in data:  # Direct value exists
                    value['value'] = data[key]
            
            # Ensure confidence is integer
            if 'confidence' in value and isinstance(value['confidence'], float):
                value['confidence'] = int(value['confidence'])
            
            # Remove invalid fields
            valid_fields = ['value', 'unit', 'min', 'max', 'confidence']
            value = {k: v for k, v in value.items() if k in valid_fields}
        
        fixed_data[key] = value
    
    return fixed_data
```

## Post-Migration Optimization

### Performance Tuning
```python
# Enable caching for improved performance
cache_config = {
    "enable_property_cache": True,
    "cache_ttl": 3600,  # 1 hour
    "max_cache_size": 1000
}

# Optimize API calls
api_config = {
    "batch_size": 5,  # Process 5 properties at once
    "timeout": 30,
    "retry_attempts": 3
}
```

### Quality Monitoring
```python
def setup_quality_monitoring():
    """Set up ongoing quality monitoring"""
    
    quality_checks = [
        ("confidence_threshold", lambda props: all(p.get("confidence", 0) >= 40 for p in props.values())),
        ("completeness_check", lambda props: len(props) >= 3),
        ("unit_consistency", lambda props: all("unit" in p for p in props.values() if isinstance(p, dict)))
    ]
    
    return quality_checks
```

## Success Metrics

### Migration Success Criteria
- **Completion Rate**: >95% of materials successfully migrated
- **Data Quality**: Average confidence score >70%
- **Performance Impact**: <20% increase in generation time
- **Error Rate**: <5% of generations result in fallback
- **User Satisfaction**: >80% positive feedback on new capabilities

### Long-term Benefits
1. **Improved Data Quality**: Confidence scoring and source tracking
2. **Reduced Manual Work**: Automated property discovery and research
3. **Better Scalability**: Can handle hundreds of new materials efficiently
4. **Enhanced Reliability**: Multiple research sources with fallback mechanisms
5. **Future-Proof Architecture**: Extensible system for new research methods

## Conclusion

The migration to the Research Pipeline system represents a significant architectural enhancement that transforms static property generation into a dynamic, research-driven process. By following this migration guide, teams can safely transition to the new system while maintaining operational continuity and improving data quality.

The key to successful migration is careful planning, thorough testing, and gradual rollout with continuous monitoring. The structured approach outlined in this guide ensures minimal disruption while maximizing the benefits of the enhanced research capabilities.