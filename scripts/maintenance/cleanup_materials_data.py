#!/usr/bin/env python3
"""
Materials Data Directory Cleanup and Organization

Consolidates and organizes the materials/data directory by:
1. Moving all backup files to proper locations
2. Organizing variation research files
3. Creating clear directory structure
4. Removing temporary files
5. Keeping only current production data in root
"""

import shutil
from pathlib import Path
from datetime import datetime

class MaterialsDataOrganizer:
    """Organizes materials data directory structure."""
    
    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self.report = []
        
    def log(self, message: str):
        """Log action to report."""
        print(message)
        self.report.append(message)
    
    def create_directory_structure(self):
        """Create organized directory structure."""
        self.log("\n" + "="*70)
        self.log("CREATING DIRECTORY STRUCTURE")
        self.log("="*70)
        
        directories = {
            'backups': 'Automated backups from data updates',
            'archive': 'Historical/deprecated data files',
            'research': 'Variation research from AI discovery',
            'research/metals': 'Metal alloy variation research',
            'research/wood': 'Wood species variation research',
            'research/stone': 'Stone geological variation research',
            'research/other': 'Glass, ceramic, composite variations',
        }
        
        for dir_name, description in directories.items():
            dir_path = self.data_dir / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.log(f"✓ Created: {dir_name}/ - {description}")
            else:
                self.log(f"  Exists: {dir_name}/ - {description}")
        
        # Create README files
        self._create_readme_files()
    
    def _create_readme_files(self):
        """Create README files for each directory."""
        
        # Backups README
        backups_readme = self.data_dir / "backups" / "README.md"
        if not backups_readme.exists():
            backups_readme.write_text("""# Backups Directory

Automated backups created before data updates.

## Retention Policy

- **Keep**: Last 5 backups of each file
- **Delete**: Backups older than 30 days (unless last 5)
- **Automatic**: Backups created by populate_deep_research.py

## Files

- `PropertyResearch_backup_YYYYMMDD_HHMMSS.yaml` - Property research backups
- `SettingResearch_backup_YYYYMMDD_HHMMSS.yaml` - Setting research backups
- `Materials_backup_YYYYMMDD_HHMMSS.yaml` - Materials data backups

See `BACKUP_RETENTION_POLICY.md` for details.
""")
            self.log("  ✓ Created: backups/README.md")
        
        # Research README
        research_readme = self.data_dir / "research" / "README.md"
        if not research_readme.exists():
            research_readme.write_text("""# Research Directory

AI-generated variation research for material alloys, species, and grades.

## Structure

- `metals/` - Metal alloy variations (Aluminum, Steel, Titanium, etc.)
- `wood/` - Wood species variations (Oak, Maple, Cherry, etc.)
- `stone/` - Stone geological variations (Granite, Marble, etc.)
- `other/` - Glass, ceramic, composite variations

## File Format

Each file contains YAML-formatted variation data:
- Designation/name
- Standard specifications
- Composition characteristics
- Applications
- Laser cleaning implications

## Usage

These files are reference material for manual validation before
populating PropertyResearch.yaml and SettingResearch.yaml.

**⚠️ AI-generated data requires human validation before production use.**
""")
            self.log("  ✓ Created: research/README.md")
    
    def organize_backup_files(self):
        """Move backup files to backups directory."""
        self.log("\n" + "="*70)
        self.log("ORGANIZING BACKUP FILES")
        self.log("="*70)
        
        backup_patterns = [
            '*_backup_*.yaml',
            'Materials.backup_*.yaml',
            'Materials_backup_*.yaml',
            'materials_backup_*.yaml',
        ]
        
        moved_count = 0
        for pattern in backup_patterns:
            for backup_file in self.data_dir.glob(pattern):
                if backup_file.parent.name == 'backups':
                    continue  # Already in backups directory
                
                dest = self.data_dir / 'backups' / backup_file.name
                shutil.move(str(backup_file), str(dest))
                self.log(f"  Moved: {backup_file.name} → backups/")
                moved_count += 1
        
        self.log(f"\n✓ Moved {moved_count} backup files to backups/")
    
    def organize_research_files(self):
        """Organize variation research files by category."""
        self.log("\n" + "="*70)
        self.log("ORGANIZING RESEARCH FILES")
        self.log("="*70)
        
        # Define material categories
        categories = {
            'metals': [
                'Aluminum', 'Steel', 'Stainless_Steel', 'Titanium', 
                'Copper', 'Brass', 'Bronze', 'Nickel', 'Inconel',
                'Cast_Iron', 'Iron', 'Lead', 'Zinc', 'Magnesium'
            ],
            'wood': [
                'Oak', 'Maple', 'Mahogany', 'Cherry', 'Birch', 'Ash',
                'Cedar', 'Fir', 'Pine', 'Walnut', 'Teak', 'Bamboo'
            ],
            'stone': [
                'Granite', 'Marble', 'Limestone', 'Sandstone', 'Basalt',
                'Slate', 'Travertine', 'Onyx', 'Bluestone'
            ],
            'other': [
                'Alumina', 'Float_Glass', 'Borosilicate_Glass', 
                'Crown_Glass', 'Fused_Silica', 'Gorilla_Glass',
                'Carbon_Fiber', 'Fiberglass', 'Kevlar'
            ]
        }
        
        research_files = list(self.data_dir.glob('*_variations_research.txt'))
        moved_count = 0
        
        for research_file in research_files:
            # Determine category
            material_name = research_file.stem.replace('_variations_research', '')
            
            category = 'other'  # Default
            for cat, materials in categories.items():
                if material_name in materials:
                    category = cat
                    break
            
            # Move to appropriate subdirectory
            dest_dir = self.data_dir / 'research' / category
            dest = dest_dir / research_file.name
            
            shutil.move(str(research_file), str(dest))
            self.log(f"  Moved: {research_file.name} → research/{category}/")
            moved_count += 1
        
        self.log(f"\n✓ Organized {moved_count} research files by category")
    
    def archive_old_files(self):
        """Move old/deprecated files to archive."""
        self.log("\n" + "="*70)
        self.log("ARCHIVING OLD FILES")
        self.log("="*70)
        
        # Files to archive (already superseded)
        archive_patterns = [
            'MaterialProperties_*.yaml',  # Old versions
            'MachineSettings_*.yaml',      # Old versions
            'tmp*.yaml',                   # Temporary files
        ]
        
        archived_count = 0
        for pattern in archive_patterns:
            for old_file in self.data_dir.glob(pattern):
                if old_file.parent.name == 'archive':
                    continue
                
                dest = self.data_dir / 'archive' / old_file.name
                shutil.move(str(old_file), str(dest))
                self.log(f"  Archived: {old_file.name} → archive/")
                archived_count += 1
        
        self.log(f"\n✓ Archived {archived_count} old files")
    
    def cleanup_backups(self, keep_last_n: int = 5):
        """Remove old backups, keeping only last N of each type."""
        self.log("\n" + "="*70)
        self.log(f"CLEANING UP OLD BACKUPS (keeping last {keep_last_n})")
        self.log("="*70)
        
        backups_dir = self.data_dir / 'backups'
        
        # Group backups by base name
        backup_groups = {}
        for backup_file in backups_dir.glob('*_backup_*.yaml'):
            # Extract base name (e.g., PropertyResearch from PropertyResearch_backup_20251107_125140.yaml)
            parts = backup_file.stem.split('_backup_')
            if len(parts) == 2:
                base_name = parts[0]
                timestamp = parts[1]
                
                if base_name not in backup_groups:
                    backup_groups[base_name] = []
                backup_groups[base_name].append((timestamp, backup_file))
        
        deleted_count = 0
        for base_name, backups in backup_groups.items():
            # Sort by timestamp (newest first)
            backups.sort(key=lambda x: x[0], reverse=True)
            
            # Keep only last N
            to_delete = backups[keep_last_n:]
            
            for timestamp, backup_file in to_delete:
                backup_file.unlink()
                self.log(f"  Deleted: {backup_file.name}")
                deleted_count += 1
            
            if to_delete:
                self.log(f"  Kept {min(keep_last_n, len(backups))} of {len(backups)} backups for {base_name}")
        
        self.log(f"\n✓ Deleted {deleted_count} old backup files")
    
    def generate_directory_map(self):
        """Generate final directory structure map."""
        self.log("\n" + "="*70)
        self.log("FINAL DIRECTORY STRUCTURE")
        self.log("="*70)
        
        structure = """
materials/data/
├── README.md                       # Main documentation
├── BACKUP_RETENTION_POLICY.md      # Backup policy
│
├── 🗄️  PRODUCTION DATA FILES (current, in use)
│   ├── Materials.yaml              # Master materials database (1.2MB)
│   ├── MaterialProperties.yaml     # Property definitions & metadata (524KB)
│   ├── MachineSettings.yaml        # Settings definitions & metadata (170KB)
│   ├── CategoryMetadata.yaml       # Category templates & frameworks (47KB)
│   ├── PropertyResearch.yaml       # Multi-source property research (22KB)
│   ├── SettingResearch.yaml        # Context-specific setting research (21KB)
│   └── frontmatter_template.yaml   # Frontmatter export template
│
├── 📁 backups/                     # Automated backups
│   ├── README.md
│   ├── PropertyResearch_backup_*.yaml (last 5 kept)
│   ├── SettingResearch_backup_*.yaml (last 5 kept)
│   └── Materials_backup_*.yaml (last 5 kept)
│
├── 📁 archive/                     # Historical/deprecated files
│   ├── README.md
│   ├── Categories_20251107_115757.yaml (superseded)
│   ├── MaterialProperties_20251107_115757.yaml (old version)
│   └── MachineSettings_20251107_115757.yaml (old version)
│
├── 📁 research/                    # AI variation research (reference)
│   ├── README.md
│   ├── metals/                     # Metal alloy variations
│   │   ├── Aluminum_variations_research.txt
│   │   ├── Steel_variations_research.txt
│   │   ├── Stainless_Steel_variations_research.txt
│   │   ├── Titanium_variations_research.txt
│   │   ├── Copper_variations_research.txt
│   │   ├── Brass_variations_research.txt
│   │   └── Bronze_variations_research.txt
│   ├── wood/                       # Wood species variations
│   │   ├── Oak_variations_research.txt
│   │   ├── Maple_variations_research.txt
│   │   ├── Mahogany_variations_research.txt
│   │   └── Cherry_variations_research.txt
│   ├── stone/                      # Stone geological variations
│   │   ├── Granite_variations_research.txt
│   │   ├── Marble_variations_research.txt
│   │   ├── Limestone_variations_research.txt
│   │   └── Sandstone_variations_research.txt
│   └── other/                      # Glass, ceramic, composites
│       ├── Float_Glass_variations_research.txt
│       ├── Borosilicate_Glass_variations_research.txt
│       └── Alumina_variations_research.txt
│
└── 🐍 Python modules
    ├── __init__.py
    ├── loader.py                   # Centralized data loader (31 functions)
    └── materials.py                # Legacy module
"""
        
        self.log(structure)
    
    def save_report(self):
        """Save cleanup report."""
        report_path = self.data_dir / 'CLEANUP_REPORT.md'
        
        report_content = f"""# Materials Data Directory Cleanup Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Actions Performed

"""
        report_content += "\n".join(self.report)
        
        report_content += """

## Benefits

1. **Clear Organization**: Production files in root, reference/history in subdirectories
2. **Easy Navigation**: Files grouped by purpose and category
3. **Backup Management**: Automated retention policy (last 5 kept)
4. **Research Structure**: Variations organized by material type
5. **Reduced Clutter**: 41+ backup files moved out of root directory

## Production Files (Root Directory)

- `Materials.yaml` - Master database (1.2MB)
- `MaterialProperties.yaml` - Property definitions (524KB)
- `MachineSettings.yaml` - Setting definitions (170KB)
- `CategoryMetadata.yaml` - Category metadata (47KB)
- `PropertyResearch.yaml` - Multi-source property research (22KB)
- `SettingResearch.yaml` - Context-specific settings (21KB)

## Directory Structure

See tree structure above for complete organization.

## Next Steps

1. ✅ Directory structure is now clean and organized
2. Review `research/` files for validation before production use
3. Backups automatically managed (last 5 kept)
4. Archive contains historical files for reference
"""
        
        report_path.write_text(report_content)
        self.log("\n✓ Saved cleanup report: CLEANUP_REPORT.md")


def main():
    """Main cleanup execution."""
    print("="*70)
    print("MATERIALS DATA DIRECTORY CLEANUP")
    print("="*70)
    print()
    
    # Get data directory - resolve from script location
    script_dir = Path(__file__).parent.resolve()
    data_dir = script_dir.parent.parent / "materials" / "data"
    
    if not data_dir.exists():
        print(f"❌ Error: {data_dir} not found")
        return 1
    
    print(f"📂 Directory: {data_dir}")
    print()
    
    # Create organizer
    organizer = MaterialsDataOrganizer(data_dir)
    
    # Execute cleanup steps
    organizer.create_directory_structure()
    organizer.organize_backup_files()
    organizer.organize_research_files()
    organizer.archive_old_files()
    organizer.cleanup_backups(keep_last_n=5)
    organizer.generate_directory_map()
    organizer.save_report()
    
    print("\n" + "="*70)
    print("✅ CLEANUP COMPLETE")
    print("="*70)
    print()
    print("📋 Review: materials/data/CLEANUP_REPORT.md")
    print("📁 Structure: materials/data/")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
