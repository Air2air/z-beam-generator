#!/usr/bin/env python3
"""
Data directory cleanup tool for Z-Beam Generator.
Consolidates backups, removes duplicates, and organizes data files.
"""

import yaml
from pathlib import Path
import shutil
from datetime import datetime
import hashlib


class DataDirectoryCleanup:
    def __init__(self):
        self.data_dir = Path("data")
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
        
    def calculate_file_hash(self, file_path):
        """Calculate SHA256 hash of file for duplicate detection."""
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def analyze_data_directory(self):
        """Analyze current state of data directory."""
        print("=== DATA DIRECTORY ANALYSIS ===")
        
        # Get all files in data directory
        all_files = list(self.data_dir.glob("*"))
        files_by_type = {
            'yaml_files': [],
            'python_files': [],
            'backup_files': [],
            'other_files': [],
            'directories': []
        }
        
        for file_path in all_files:
            if file_path.is_dir():
                files_by_type['directories'].append(file_path)
            elif file_path.suffix == '.yaml':
                if any(keyword in file_path.name.lower() for keyword in ['backup', 'bak']):
                    files_by_type['backup_files'].append(file_path)
                else:
                    files_by_type['yaml_files'].append(file_path)
            elif file_path.suffix == '.py':
                files_by_type['python_files'].append(file_path)
            else:
                files_by_type['other_files'].append(file_path)
        
        # Report findings
        for file_type, files in files_by_type.items():
            print(f"{file_type.replace('_', ' ').title()}: {len(files)}")
            for file_path in sorted(files):
                size_kb = file_path.stat().st_size / 1024 if file_path.is_file() else 0
                print(f"  {file_path.name} ({size_kb:.1f}KB)")
        
        return files_by_type
    
    def identify_duplicate_files(self, files):
        """Identify duplicate files by content hash."""
        print("\n=== DUPLICATE DETECTION ===")
        
        file_hashes = {}
        duplicates = []
        
        for file_path in files:
            if file_path.is_file() and file_path.suffix == '.yaml':
                try:
                    file_hash = self.calculate_file_hash(file_path)
                    if file_hash in file_hashes:
                        duplicates.append({
                            'original': file_hashes[file_hash],
                            'duplicate': file_path,
                            'hash': file_hash
                        })
                        print(f"Duplicate found: {file_path.name} = {file_hashes[file_hash].name}")
                    else:
                        file_hashes[file_hash] = file_path
                except Exception as e:
                    print(f"Error reading {file_path.name}: {e}")
        
        if not duplicates:
            print("No duplicate files found")
        
        return duplicates
    
    def consolidate_backups(self, backup_files):
        """Move backup files to dedicated backup directory."""
        print("\n=== BACKUP CONSOLIDATION ===")
        
        moved_files = []
        for backup_file in backup_files:
            if backup_file.exists():
                # Create a clean backup name
                timestamp = datetime.fromtimestamp(backup_file.stat().st_mtime).strftime("%Y%m%d_%H%M%S")
                
                # Determine backup type and create descriptive name
                if 'categories' in backup_file.name.lower():
                    backup_name = f"Categories_backup_{timestamp}.yaml"
                elif 'materials' in backup_file.name.lower():
                    backup_name = f"Materials_backup_{timestamp}.yaml"
                else:
                    backup_name = f"{backup_file.stem}_backup_{timestamp}.yaml"
                
                backup_destination = self.backup_dir / backup_name
                
                # Avoid overwriting existing backups
                counter = 1
                while backup_destination.exists():
                    name_parts = backup_name.split('.')
                    backup_destination = self.backup_dir / f"{name_parts[0]}_{counter}.{name_parts[1]}"
                    counter += 1
                
                shutil.move(str(backup_file), str(backup_destination))
                moved_files.append((backup_file.name, backup_destination.name))
                print(f"Moved: {backup_file.name} → backups/{backup_destination.name}")
        
        return moved_files
    
    def validate_core_files(self):
        """Validate that core data files are present and valid."""
        print("\n=== CORE FILE VALIDATION ===")
        
        required_files = {
            'materials.yaml': 'Main materials database',
            'Categories.yaml': 'Enhanced categories with field mappings'
        }
        
        validation_results = {}
        
        for filename, description in required_files.items():
            file_path = self.data_dir / filename
            
            if not file_path.exists():
                print(f"❌ Missing: {filename} ({description})")
                validation_results[filename] = {'status': 'missing', 'error': 'File not found'}
                continue
            
            try:
                # Validate YAML syntax
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                
                # Basic structure validation
                if filename == 'materials.yaml':
                    required_sections = ['machineSettingsRanges', 'material_index', 'materials']
                    missing_sections = [s for s in required_sections if s not in data]
                    
                    if missing_sections:
                        print(f"⚠️  {filename}: Missing sections: {missing_sections}")
                        validation_results[filename] = {'status': 'incomplete', 'missing_sections': missing_sections}
                    else:
                        material_count = sum(len(cat_data.get('items', [])) for cat_data in data['materials'].values() if isinstance(cat_data, dict))
                        index_count = len(data['material_index'])
                        
                        if material_count == index_count:
                            print(f"✅ {filename}: Valid ({material_count} materials)")
                            validation_results[filename] = {'status': 'valid', 'material_count': material_count}
                        else:
                            print(f"⚠️  {filename}: Index mismatch ({index_count} indexed, {material_count} actual)")
                            validation_results[filename] = {'status': 'mismatch', 'index_count': index_count, 'actual_count': material_count}
                
                elif filename == 'Categories.yaml':
                    if 'metadata' in data and 'categories' in data:
                        version = data['metadata'].get('version', 'unknown')
                        category_count = len(data['categories'])
                        print(f"✅ {filename}: Valid (v{version}, {category_count} categories)")
                        validation_results[filename] = {'status': 'valid', 'version': version, 'category_count': category_count}
                    else:
                        print(f"⚠️  {filename}: Missing metadata or categories")
                        validation_results[filename] = {'status': 'incomplete', 'error': 'Missing required sections'}
                
            except yaml.YAMLError as e:
                print(f"❌ {filename}: YAML syntax error: {e}")
                validation_results[filename] = {'status': 'invalid', 'error': str(e)}
            except Exception as e:
                print(f"❌ {filename}: Error: {e}")
                validation_results[filename] = {'status': 'error', 'error': str(e)}
        
        return validation_results
    
    def clean_obsolete_files(self):
        """Remove obsolete files that are no longer needed."""
        print("\n=== OBSOLETE FILE CLEANUP ===")
        
        # Files that might be obsolete
        potentially_obsolete = []
        
        # Check for old Categories.yaml (non-enhanced version)
        categories_old = self.data_dir / "Categories.yaml"
        categories_enhanced = self.data_dir / "Categories.yaml"
        
        if categories_old.exists() and categories_enhanced.exists():
            # Compare to see if the old one is truly obsolete
            try:
                with open(categories_old, 'r') as f:
                    old_data = yaml.safe_load(f)
                with open(categories_enhanced, 'r') as f:
                    enhanced_data = yaml.safe_load(f)
                
                # Check if enhanced version has more content
                old_categories = len(old_data.get('categories', {}))
                enhanced_categories = len(enhanced_data.get('categories', {}))
                
                if enhanced_categories >= old_categories:
                    enhanced_version = enhanced_data.get('metadata', {}).get('version', '0')
                    if enhanced_version >= '2.0':
                        potentially_obsolete.append({
                            'file': categories_old,
                            'reason': f'Replaced by Categories.yaml v{enhanced_version}',
                            'action': 'move_to_backup'
                        })
                        
            except Exception as e:
                print(f"Warning: Could not compare Categories files: {e}")
        
        # Report findings
        obsolete_actions = []
        for item in potentially_obsolete:
            file_path = item['file']
            reason = item['reason']
            action = item['action']
            
            print(f"Found obsolete: {file_path.name} - {reason}")
            
            if action == 'move_to_backup':
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"{file_path.stem}_obsolete_{timestamp}.yaml"
                backup_path = self.backup_dir / backup_name
                
                shutil.move(str(file_path), str(backup_path))
                obsolete_actions.append(f"Moved {file_path.name} to backups/{backup_name}")
                print(f"  → Moved to backups/{backup_name}")
        
        if not obsolete_actions:
            print("No obsolete files found")
        
        return obsolete_actions
    
    def generate_cleanup_report(self, analysis, moved_backups, validation_results, obsolete_actions):
        """Generate a comprehensive cleanup report."""
        print("\n" + "="*50)
        print("DATA DIRECTORY CLEANUP REPORT")
        print("="*50)
        
        # Summary statistics
        total_yaml = len(analysis['yaml_files'])
        total_backups_moved = len(moved_backups)
        total_obsolete_removed = len(obsolete_actions)
        
        print(f"YAML files in data/: {total_yaml}")
        print(f"Backup files moved: {total_backups_moved}")
        print(f"Obsolete files handled: {total_obsolete_removed}")
        
        print("\nCORE FILE STATUS:")
        for filename, result in validation_results.items():
            status_icon = "✅" if result['status'] == 'valid' else "⚠️"
            print(f"  {status_icon} {filename}: {result['status']}")
        
        if moved_backups:
            print("\nBACKUPS MOVED:")
            for original, moved in moved_backups:
                print(f"  {original} → {moved}")
        
        if obsolete_actions:
            print("\nOBSOLETE FILES HANDLED:")
            for action in obsolete_actions:
                print(f"  {action}")
        
        # Final directory state
        remaining_files = list(self.data_dir.glob("*.yaml"))
        print(f"\nFINAL STATE: {len(remaining_files)} YAML files in data/")
        for file_path in sorted(remaining_files):
            size_kb = file_path.stat().st_size / 1024
            print(f"  {file_path.name} ({size_kb:.1f}KB)")
        
        print("\n✅ Data directory cleanup completed!")
    
    def run_cleanup(self):
        """Execute the complete cleanup process."""
        print("DATA DIRECTORY CLEANUP STARTING...")
        print(f"Working directory: {self.data_dir.absolute()}")
        print()
        
        # 1. Analyze current state
        analysis = self.analyze_data_directory()
        
        # 2. Find duplicates (for reporting)
        all_yaml_files = analysis['yaml_files'] + analysis['backup_files']
        self.identify_duplicate_files(all_yaml_files)
        
        # 3. Consolidate backups
        moved_backups = self.consolidate_backups(analysis['backup_files'])
        
        # 4. Validate core files
        validation_results = self.validate_core_files()
        
        # 5. Clean obsolete files
        obsolete_actions = self.clean_obsolete_files()
        
        # 6. Generate report
        self.generate_cleanup_report(analysis, moved_backups, validation_results, obsolete_actions)


if __name__ == "__main__":
    cleaner = DataDirectoryCleanup()
    cleaner.run_cleanup()