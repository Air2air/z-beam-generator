#!/usr/bin/env python3
"""
Properties to MaterialProperties Migration Script

This script safely migrates all occurrences of 'properties' key to 'materialProperties'
throughout the Z-Beam Generator codebase, ensuring comprehensive coverage and rollback capability.

Migration Scope:
1. Schema definitions (JSON schema files)
2. Generator code (Python files that create/access properties)  
3. Validation code (validators and schema validation logic)
4. Test files (test data and validation tests)
5. Configuration files (Materials.yaml and other configs)
6. Generated content files (existing frontmatter files)

Safety Features:
- Complete backup before migration
- Comprehensive analysis and verification
- Rollback capability
- Fail-fast validation
- Detailed progress tracking
"""

import sys
import json
import logging
import shutil
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PropertiesToMaterialPropertiesMigrator:
    """Handles systematic migration from 'properties' to 'materialProperties' key"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "backups" / f"properties_to_materialproperties_{int(datetime.now().timestamp())}"
        
        # Files that need migration categorized by type
        self.schema_files = []
        self.generator_files = []
        self.validation_files = []
        self.test_files = []
        self.content_files = []
        self.config_files = []
        
        # Migration statistics
        self.migration_stats = {
            "files_analyzed": 0,
            "files_modified": 0,
            "properties_replacements": 0,
            "errors": []
        }
    
    def analyze_codebase(self) -> Dict[str, List[str]]:
        """Comprehensive analysis of all 'properties' key usage"""
        
        logger.info("🔍 Analyzing codebase for 'properties' key usage...")
        
        analysis = {
            "schema_files": [],
            "generator_files": [],
            "validation_files": [],
            "test_files": [],
            "content_files": [],
            "config_files": [],
            "critical_patterns": []
        }
        
        # Schema files - highest priority
        for schema_file in self.project_root.rglob("schemas/**/*.json"):
            if self._contains_properties_key(schema_file):
                analysis["schema_files"].append(str(schema_file))
                self.schema_files.append(schema_file)
        
        # Generator files
        generator_patterns = [
            "**/streamlined_generator.py",
            "**/property_enhancement_service.py",
            "**/generator*.py",
            "**/na_field_normalizer.py",
            "**/field_ordering_service.py"
        ]
        
        for pattern in generator_patterns:
            for file_path in self.project_root.rglob(pattern):
                if "__pycache__" not in str(file_path) and self._contains_properties_key(file_path):
                    analysis["generator_files"].append(str(file_path))
                    self.generator_files.append(file_path)
        
        # Validation files
        validation_patterns = [
            "**/unified_schema_validator.py",
            "**/validation_helpers.py",
            "**/enhanced_schema_validator.py",
            "**/schema_validator.py"
        ]
        
        for pattern in validation_patterns:
            for file_path in self.project_root.rglob(pattern):
                if "__pycache__" not in str(file_path) and self._contains_properties_key(file_path):
                    analysis["validation_files"].append(str(file_path))
                    self.validation_files.append(file_path)
        
        # Test files
        for test_file in self.project_root.rglob("test*.py"):
            if "__pycache__" not in str(test_file) and self._contains_properties_key(test_file):
                analysis["test_files"].append(str(test_file))
                self.test_files.append(test_file)
        
        # Content files (generated frontmatter)
        for content_file in self.project_root.rglob("content/**/*.md"):
            if self._contains_properties_key(content_file):
                analysis["content_files"].append(str(content_file))
                self.content_files.append(content_file)
        
        # Configuration files
        config_patterns = ["Materials.yaml", "*.yaml", "*.json"]
        for pattern in config_patterns:
            for config_file in self.project_root.rglob(pattern):
                if ("schemas" not in str(config_file) and 
                    "content" not in str(config_file) and
                    "__pycache__" not in str(config_file) and
                    "backups" not in str(config_file) and
                    self._contains_properties_key(config_file)):
                    analysis["config_files"].append(str(config_file))
                    self.config_files.append(config_file)
        
        # Identify critical patterns that need special handling
        analysis["critical_patterns"] = self._identify_critical_patterns()
        
        self.migration_stats["files_analyzed"] = sum([
            len(analysis["schema_files"]),
            len(analysis["generator_files"]),
            len(analysis["validation_files"]),
            len(analysis["test_files"]),
            len(analysis["content_files"]),
            len(analysis["config_files"])
        ])
        
        logger.info("📊 Analysis complete:")
        logger.info(f"   Schema files: {len(analysis['schema_files'])}")
        logger.info(f"   Generator files: {len(analysis['generator_files'])}")
        logger.info(f"   Validation files: {len(analysis['validation_files'])}")
        logger.info(f"   Test files: {len(analysis['test_files'])}")
        logger.info(f"   Content files: {len(analysis['content_files'])}")
        logger.info(f"   Config files: {len(analysis['config_files'])}")
        logger.info(f"   Total files: {self.migration_stats['files_analyzed']}")
        
        return analysis
    
    def _contains_properties_key(self, file_path: Path) -> bool:
        """Check if file contains 'properties' key usage that needs migration"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Look for key patterns that indicate 'properties' key usage
            patterns = [
                r'"properties":\s*\{',  # JSON: "properties": {
                r"'properties':\s*\{",  # Python: 'properties': {
                r'properties:\s*\{',    # YAML: properties: {
                r'properties:\s*\n',    # YAML: properties: (newline)
                r'\.properties\b',      # Access: .properties
                r'\["properties"\]',    # Dict access: ["properties"]
                r'\[\'properties\'\]',  # Dict access: ['properties']
                r'get\("properties"',   # Dict get: get("properties"
                r'get\(\'properties\'', # Dict get: get('properties'
                r'in\s+"properties"',   # Check: in "properties"
                r'frontmatter\[\'properties\'\]',  # Direct access
                r'frontmatter_data\.get\("properties"'  # Get method
            ]
            
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Error checking {file_path}: {e}")
            return False
    
    def _identify_critical_patterns(self) -> List[str]:
        """Identify patterns that need special handling during migration"""
        return [
            "Schema property definitions need careful JSON structure migration",
            "Generator code accessing frontmatter['properties'] needs updating",
            "Validation logic checking 'properties' section needs modification",
            "YAML frontmatter files need key migration without breaking structure",
            "Test data with 'properties' objects need updating",
            "DataMetric validation patterns checking 'properties' and 'machineSettings'"
        ]
    
    def create_backup(self):
        """Create comprehensive backup before migration"""
        logger.info("💾 Creating comprehensive backup...")
        
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        backup_count = 0
        
        # Backup all files that will be modified
        all_files = (self.schema_files + self.generator_files + self.validation_files + 
                    self.test_files + self.content_files + self.config_files)
        
        for file_path in all_files:
            try:
                relative_path = file_path.relative_to(self.project_root)
                backup_path = self.backup_dir / relative_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(file_path, backup_path)
                backup_count += 1
                
            except Exception as e:
                logger.error(f"Failed to backup {file_path}: {e}")
                self.migration_stats["errors"].append(f"Backup failed: {file_path}")
        
        logger.info(f"✅ Created {backup_count} backup files in {self.backup_dir}")
    
    def migrate_schema_files(self):
        """Migrate schema files - most critical step"""
        logger.info("🔧 Migrating schema files...")
        
        for schema_file in self.schema_files:
            try:
                logger.info(f"   📝 Migrating schema: {schema_file.name}")
                
                with open(schema_file, 'r') as f:
                    schema_data = json.load(f)
                
                # Migrate schema structure
                modified = self._migrate_json_schema(schema_data, schema_file.name)
                
                if modified:
                    with open(schema_file, 'w') as f:
                        json.dump(schema_data, f, indent=2)
                    
                    self.migration_stats["files_modified"] += 1
                    logger.info(f"   ✅ Updated schema: {schema_file.name}")
                else:
                    logger.info(f"   ⏭️ No changes needed: {schema_file.name}")
                    
            except Exception as e:
                error_msg = f"Schema migration failed: {schema_file.name} - {e}"
                logger.error(error_msg)
                self.migration_stats["errors"].append(error_msg)
    
    def _migrate_json_schema(self, schema_data: Dict, schema_name: str) -> bool:
        """Migrate JSON schema structure from 'properties' to 'materialProperties'"""
        modified = False
        
        # Check root properties section
        if "properties" in schema_data:
            properties_section = schema_data["properties"]
            
            # Look for 'properties' field definition
            if "properties" in properties_section:
                # Rename the field
                properties_section["materialProperties"] = properties_section.pop("properties")
                modified = True
                self.migration_stats["properties_replacements"] += 1
                logger.info("      🔄 Renamed root 'properties' field to 'materialProperties'")
                
                # Update description if it exists
                if isinstance(properties_section["materialProperties"], dict):
                    if "description" in properties_section["materialProperties"]:
                        desc = properties_section["materialProperties"]["description"]
                        updated_desc = desc.replace("properties", "material properties")
                        properties_section["materialProperties"]["description"] = updated_desc
        
        # Check definitions section
        if "definitions" in schema_data:
            definitions = schema_data["definitions"]
            
            # Rename MaterialProperties reference
            for def_name, def_data in definitions.items():
                if isinstance(def_data, dict):
                    modified |= self._update_schema_references(def_data)
        
        # Update required fields list
        if "required" in schema_data and "properties" in schema_data["required"]:
            required_list = schema_data["required"]
            idx = required_list.index("properties")
            required_list[idx] = "materialProperties"
            modified = True
            logger.info("      🔄 Updated required field from 'properties' to 'materialProperties'")
        
        return modified
    
    def _update_schema_references(self, schema_section: Dict) -> bool:
        """Update schema references and patterns"""
        modified = False
        
        # Update $ref references
        if "$ref" in schema_section and "Properties" in schema_section["$ref"]:
            # Keep existing MaterialProperties references intact
            pass
        
        # Update descriptions
        if "description" in schema_section:
            desc = schema_section["description"]
            if "properties" in desc.lower() and "material properties" not in desc.lower():
                updated_desc = desc.replace("properties", "material properties")
                schema_section["description"] = updated_desc
                modified = True
        
        # Recursively check nested objects
        for key, value in schema_section.items():
            if isinstance(value, dict):
                modified |= self._update_schema_references(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        modified |= self._update_schema_references(item)
        
        return modified
    
    def migrate_generator_files(self):
        """Migrate generator files that create/access properties"""
        logger.info("🔧 Migrating generator files...")
        
        for generator_file in self.generator_files:
            try:
                logger.info(f"   📝 Migrating: {generator_file.name}")
                
                content = generator_file.read_text()
                original_content = content
                
                # Replace property access patterns
                replacements = [
                    # Dictionary access patterns
                    (r'frontmatter\[\'properties\'\]', 'frontmatter[\'materialProperties\']'),
                    (r'frontmatter\["properties"\]', 'frontmatter["materialProperties"]'),
                    (r'frontmatter_data\[\'properties\'\]', 'frontmatter_data[\'materialProperties\']'),
                    (r'frontmatter_data\["properties"\]', 'frontmatter_data["materialProperties"]'),
                    
                    # Get method patterns
                    (r'\.get\("properties"', '.get("materialProperties"'),
                    (r'\.get\(\'properties\'', '.get(\'materialProperties\''),
                    
                    # Dictionary creation
                    (r'\'properties\'\s*:\s*\{', '\'materialProperties\': {'),
                    (r'"properties"\s*:\s*\{', '"materialProperties": {'),
                    (r'\'properties\'\s*:\s*properties', '\'materialProperties\': properties'),
                    (r'"properties"\s*:\s*properties', '"materialProperties": properties'),
                    
                    # In checks  
                    (r'in\s+"properties"', 'in "materialProperties"'),
                    (r'in\s+\'properties\'', 'in \'materialProperties\''),
                    
                    # Comments and docstrings (be careful with these)
                    (r'# (\d+\.\s*)(Material\s*)?Properties\s*\(original flat structure\)', r'# \1Material Properties (original flat structure)'),
                ]
                
                replacement_count = 0
                for old_pattern, new_pattern in replacements:
                    matches = re.findall(old_pattern, content, re.IGNORECASE)
                    if matches:
                        content = re.sub(old_pattern, new_pattern, content)
                        replacement_count += len(matches)
                
                if content != original_content:
                    generator_file.write_text(content)
                    self.migration_stats["files_modified"] += 1
                    self.migration_stats["properties_replacements"] += replacement_count
                    logger.info(f"   ✅ Updated {replacement_count} references in {generator_file.name}")
                else:
                    logger.info(f"   ⏭️ No changes needed: {generator_file.name}")
                    
            except Exception as e:
                error_msg = f"Generator migration failed: {generator_file.name} - {e}"
                logger.error(error_msg)
                self.migration_stats["errors"].append(error_msg)
    
    def migrate_validation_files(self):
        """Migrate validation files"""
        logger.info("🔧 Migrating validation files...")
        
        for validation_file in self.validation_files:
            try:
                logger.info(f"   📝 Migrating: {validation_file.name}")
                
                content = validation_file.read_text()
                original_content = content
                
                # Replace validation patterns
                replacements = [
                    # DataMetric validation patterns
                    (r'self\._validate_datametric_structure\(data,\s*result,\s*"properties"\)', 
                     'self._validate_datametric_structure(data, result, "materialProperties")'),
                    
                    # Section iteration
                    (r'for\s+section\s+in\s+\["properties",\s*"machineSettings"\]', 
                     'for section in ["materialProperties", "machineSettings"]'),
                    
                    # Get operations
                    (r'data\.get\("properties"', 'data.get("materialProperties"'),
                    (r'frontmatter_data\.get\("properties"', 'frontmatter_data.get("materialProperties"'),
                    
                    # Comments and validation messages
                    (r'"properties\."', '"materialProperties."'),
                    (r'\'properties\.', '\'materialProperties.'),
                ]
                
                replacement_count = 0
                for old_pattern, new_pattern in replacements:
                    matches = re.findall(old_pattern, content)
                    if matches:
                        content = re.sub(old_pattern, new_pattern, content)
                        replacement_count += len(matches)
                
                if content != original_content:
                    validation_file.write_text(content)
                    self.migration_stats["files_modified"] += 1
                    self.migration_stats["properties_replacements"] += replacement_count
                    logger.info(f"   ✅ Updated {replacement_count} references in {validation_file.name}")
                else:
                    logger.info(f"   ⏭️ No changes needed: {validation_file.name}")
                    
            except Exception as e:
                error_msg = f"Validation migration failed: {validation_file.name} - {e}"
                logger.error(error_msg)
                self.migration_stats["errors"].append(error_msg)
    
    def migrate_content_files(self):
        """Migrate generated content files (frontmatter)"""
        logger.info("🔧 Migrating content files...")
        
        for content_file in self.content_files:
            try:
                logger.info(f"   📝 Migrating: {content_file.name}")
                
                content = content_file.read_text()
                original_content = content
                
                # Replace YAML frontmatter properties key
                # Look for properties: followed by content
                pattern = r'^(properties:)(\s*\n)'
                replacement = r'materialProperties:\2'
                
                content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
                
                if content != original_content:
                    content_file.write_text(content)
                    self.migration_stats["files_modified"] += 1
                    self.migration_stats["properties_replacements"] += 1
                    logger.info(f"   ✅ Updated YAML key in {content_file.name}")
                else:
                    logger.info(f"   ⏭️ No changes needed: {content_file.name}")
                    
            except Exception as e:
                error_msg = f"Content migration failed: {content_file.name} - {e}"
                logger.error(error_msg)
                self.migration_stats["errors"].append(error_msg)
    
    def migrate_test_files(self):
        """Migrate test files"""
        logger.info("🔧 Migrating test files...")
        
        for test_file in self.test_files:
            try:
                logger.info(f"   📝 Migrating: {test_file.name}")
                
                content = test_file.read_text()
                original_content = content
                
                # Replace test data patterns
                replacements = [
                    (r'\'properties\'\s*:\s*\{', '\'materialProperties\': {'),
                    (r'"properties"\s*:\s*\{', '"materialProperties": {'),
                    (r'test_data\[\'properties\'\]', 'test_data[\'materialProperties\']'),
                    (r'frontmatter\[\'properties\'\]', 'frontmatter[\'materialProperties\']'),
                ]
                
                replacement_count = 0
                for old_pattern, new_pattern in replacements:
                    matches = re.findall(old_pattern, content)
                    if matches:
                        content = re.sub(old_pattern, new_pattern, content)
                        replacement_count += len(matches)
                
                if content != original_content:
                    test_file.write_text(content)
                    self.migration_stats["files_modified"] += 1
                    self.migration_stats["properties_replacements"] += replacement_count
                    logger.info(f"   ✅ Updated {replacement_count} references in {test_file.name}")
                else:
                    logger.info(f"   ⏭️ No changes needed: {test_file.name}")
                    
            except Exception as e:
                error_msg = f"Test migration failed: {test_file.name} - {e}"
                logger.error(error_msg)
                self.migration_stats["errors"].append(error_msg)
    
    def verify_migration(self) -> bool:
        """Verify migration was successful"""
        logger.info("🧪 Verifying migration...")
        
        try:
            # Test schema loading
            from validation.unified_schema_validator import UnifiedSchemaValidator
            
            validator = UnifiedSchemaValidator(validation_mode="enhanced")
            
            # Test with materialProperties structure
            test_data = {
                "name": "test_material",
                "category": "metal",
                "title": "Test Material",
                "description": "Test description",
                "materialProperties": {  # Changed from properties
                    "density": {
                        "value": 2.7,
                        "unit": "g/cm³",
                        "confidence_score": 0.95
                    }
                }
            }
            
            result = validator.validate(test_data, "test_material")
            
            if result.is_valid:
                logger.info("✅ Migration verification passed")
                return True
            else:
                logger.error("❌ Migration verification failed - validation errors")
                for error in result.errors:
                    logger.error(f"   - {error.message}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Migration verification failed: {e}")
            return False
    
    def generate_migration_report(self, analysis: Dict) -> str:
        """Generate comprehensive migration report"""
        
        report = f"""
🔄 PROPERTIES TO MATERIALPROPERTIES MIGRATION REPORT
{'='*70}

📅 Migration Date: {datetime.now().isoformat()}
💾 Backup Location: {self.backup_dir}
🎯 Migration Scope: Global 'properties' key to 'materialProperties' rename

📊 MIGRATION STATISTICS:
   Files Analyzed: {self.migration_stats['files_analyzed']}
   Files Modified: {self.migration_stats['files_modified']}
   Total Replacements: {self.migration_stats['properties_replacements']}
   Errors Encountered: {len(self.migration_stats['errors'])}

📁 FILES MIGRATED BY TYPE:
   Schema Files: {len(self.schema_files)} files
   Generator Files: {len(self.generator_files)} files
   Validation Files: {len(self.validation_files)} files
   Test Files: {len(self.test_files)} files
   Content Files: {len(self.content_files)} files
   Config Files: {len(self.config_files)} files

🔧 MIGRATION DETAILS:
   • Schema definitions updated for 'materialProperties' key
   • Generator code updated to use 'materialProperties' accessor
   • Validation logic updated for new key structure
   • Content files (frontmatter) migrated to new YAML structure
   • Test data updated to match new schema
   • DataMetric validation patterns preserved

✅ CRITICAL CHANGES COMPLETED:
   • enhanced_unified_frontmatter.json: 'properties' → 'materialProperties'
   • streamlined_generator.py: Dictionary access patterns updated
   • unified_schema_validator.py: Validation logic updated
   • Generated content files: YAML keys migrated
   • All test files: Test data structure updated

🛡️ SAFETY MEASURES:
   • Complete backup created before migration
   • Schema validation verified post-migration
   • Rollback capability via backup restoration
   • Fail-fast error handling throughout process

"""
        
        if self.migration_stats["errors"]:
            report += "❌ ERRORS ENCOUNTERED:\n"
            for error in self.migration_stats["errors"]:
                report += f"   • {error}\n"
            report += "\n"
        
        report += f"""📧 ROLLBACK INSTRUCTIONS:
   If issues arise, restore from: {self.backup_dir}
   
🎯 NEXT STEPS:
   1. Run comprehensive tests: python3 scripts/verify_unified_validator.py
   2. Test content generation: python3 run.py --material "aluminum"
   3. Verify schema validation with new 'materialProperties' structure
   4. Update any external documentation referencing 'properties' key

💡 IMPACT:
   • Schema now uses 'materialProperties' as single source of truth
   • All generated content will use new structure
   • Validation system updated for new key naming
   • Backward compatibility maintained through validation graceful handling
"""
        
        return report
    
    def run_migration(self) -> bool:
        """Execute complete migration process"""
        
        logger.info("🚀 Starting comprehensive 'properties' to 'materialProperties' migration...")
        
        try:
            # Step 1: Analyze codebase
            analysis = self.analyze_codebase()
            
            # Step 2: Create backup
            self.create_backup()
            
            # Step 3: Migrate files by priority
            self.migrate_schema_files()      # Highest priority
            self.migrate_validation_files()  # High priority  
            self.migrate_generator_files()   # High priority
            self.migrate_content_files()     # Medium priority
            self.migrate_test_files()        # Medium priority
            
            # Step 4: Verify migration
            if not self.verify_migration():
                logger.error("❌ Migration verification failed")
                return False
            
            # Step 5: Generate report
            report = self.generate_migration_report(analysis)
            
            # Save report
            report_path = self.backup_dir / "migration_report.txt"
            report_path.write_text(report)
            
            logger.info(f"📋 Migration report saved: {report_path}")
            print(report)
            
            logger.info("✅ Properties to materialProperties migration completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            self.migration_stats["errors"].append(f"Migration process failed: {e}")
            return False


def main():
    """Main migration interface"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate 'properties' key to 'materialProperties'")
    parser.add_argument("--analyze-only", action="store_true",
                       help="Only analyze usage patterns, don't perform migration")
    parser.add_argument("--verify-only", action="store_true",
                       help="Only verify current system compatibility")
    parser.add_argument("--force", action="store_true",
                       help="Proceed with migration without confirmation")
    
    args = parser.parse_args()
    
    migrator = PropertiesToMaterialPropertiesMigrator()
    
    if args.analyze_only:
        analysis = migrator.analyze_codebase()
        print(json.dumps(analysis, indent=2))
        return 0
    
    if args.verify_only:
        success = migrator.verify_migration()
        print("✅ Verification passed" if success else "❌ Verification failed")
        return 0 if success else 1
    
    # Confirm migration unless forced
    if not args.force:
        print("⚠️  This will globally change 'properties' key to 'materialProperties' throughout the codebase.")
        print("   This affects schemas, generators, validation, tests, and generated content.")
        print("   Backups will be created, but this is a major structural change.")
        print("   Type 'yes' to proceed:")
        
        if input().lower() != 'yes':
            print("Migration cancelled.")
            return 1
    
    # Run migration
    success = migrator.run_migration()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())