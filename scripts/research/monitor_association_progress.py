#!/usr/bin/env python3
"""Monitor Phase 3 association research progress."""

import yaml
from pathlib import Path
import sys

associations_file = Path('data/associations/DomainAssociations.yaml')
contaminants_file = Path('data/contaminants/Contaminants.yaml')

# Load data
with open(associations_file, 'r') as f:
    associations = yaml.safe_load(f)

with open(contaminants_file, 'r') as f:
    contaminants_data = yaml.safe_load(f)

# Get all contaminants with associations
material_to_contaminants = associations.get('material_to_contaminants', {})
associated_contaminants = set()
for material, contaminant_list in material_to_contaminants.items():
    if isinstance(contaminant_list, list):
        associated_contaminants.update(contaminant_list)

# Total contaminants
all_contaminants = set(contaminants_data.get('contamination_patterns', {}).keys())
total = len(all_contaminants)
complete = len(associated_contaminants)
remaining = total - complete

# Calculate progress
progress_pct = (complete / total * 100) if total > 0 else 0

print("━" * 70)
print("🔬 PHASE 3: ASSOCIATION RESEARCH PROGRESS")
print("━" * 70)
print(f"\n📊 Status:")
print(f"   Contaminants with associations: {complete}/{total} ({progress_pct:.1f}%)")
print(f"   Remaining: {remaining}")
print(f"\n⏱️  Estimated time remaining:")
print(f"   ~{remaining * 30} seconds ({remaining * 30 / 60:.1f} minutes)")
print(f"   @ 30 seconds per contaminant")
print(f"\n📁 Monitor log: tail -f association_research.log")
print("━" * 70)
